import os
import requests
from bs4 import BeautifulSoup
import time
from requests.exceptions import RequestException, Timeout, ConnectionError

# --- Configuration ---
DOWNLOAD_DIR = "downloads/schuze"
MIN_FILE_SIZE_BYTES = 1024  # Minimum size for a downloaded file to be considered valid
MIN_CONTENT_LENGTH = 1024    # Minimum character length for content before saving
MAX_CONSECUTIVE_ERRORS_CAST = 3  # How many consecutive 404s/small responses/network errors to tolerate for 'cast'
MAX_CONSECUTIVE_ERRORS_SCHUZE = 3  # How many consecutive 404s/small responses/network errors for 'schuze/001.htm'
REQUEST_TIMEOUT = 60         # Timeout for HTTP requests in seconds
MAX_RETRIES = 5            # Max retries for robust_request
BACKOFF_FACTOR = 1         # Exponential backoff factor for retries
REQUEST_DELAY = 0.5        # Delay between requests in seconds to be respectful to the server

# --- Directory Setup ---
try:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True) # exist_ok=True prevents error if dir exists
    print(f"Ensured download directory exists: {DOWNLOAD_DIR}")
except Exception as e:
    print(f"Error creating directory {DOWNLOAD_DIR}: {e}")
    # Exit or handle more gracefully if directory cannot be created

# --- Helper Function: Delete Small Files ---
def delete_small_files(directory, min_size):
    """Deletes files smaller than min_size in the specified directory."""
    print(f"Checking for and deleting files smaller than {min_size} bytes in {directory}...")
    deleted_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.getsize(file_path) < min_size:
                    os.remove(file_path)
                    print(f"Deleted: {file_path} (size: {os.path.getsize(file_path)} bytes)")
                    deleted_count += 1
            except FileNotFoundError:
                print(f"File not found during size check (already deleted?): {file_path}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    print(f"Finished deleting small files. Total deleted: {deleted_count}")

# Clean up small files before starting to ensure accurate 'stazene' set
delete_small_files(DOWNLOAD_DIR, MIN_FILE_SIZE_BYTES)

# Populate the set of already downloaded files
# This assumes all downloaded files are directly in DOWNLOAD_DIR and have the correct filename format
stazene = set(os.listdir(DOWNLOAD_DIR))
print(f"Found {len(stazene)} already downloaded files in {DOWNLOAD_DIR}.")

# --- Helper Function: Robust HTTP Request ---
def robust_request(url, max_retries=MAX_RETRIES, timeout=REQUEST_TIMEOUT, backoff_factor=BACKOFF_FACTOR):
    """Makes a robust HTTP request with retries and timeout handling."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except (Timeout, ConnectionError) as e:
            print(
                f"Network error on attempt {attempt + 1}/{max_retries} for {url}: {e}"
            )
            if attempt < max_retries - 1:
                wait_time = backoff_factor * (2**attempt)  # Exponential backoff
                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts. Skipping {url}")
                return None
        except requests.exceptions.HTTPError as e:
            # Handle 404 specifically, but let other HTTP errors pass through
            if e.response.status_code == 404:
                # For 404, we don't retry, just return the response to indicate 404
                return e.response
            else:
                print(f"HTTP error for {url}: {e}")
                return None # For other HTTP errors, treat as failure
        except RequestException as e:
            print(f"General request error for {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")
            return None

# --- Extract Initial Keys from Main Page ---
print("Extracting initial keys from www.psp.cz/eknih/index.htm...")
try:
    main_page_response = requests.get("https://www.psp.cz/eknih/index.htm")
    main_page_response.raise_for_status()
    odkazy = BeautifulSoup(main_page_response.text, "html.parser").find_all("a")
except RequestException as e:
    print(f"Error fetching main page: {e}. Exiting.")
    exit() # Cannot proceed without initial keys

klice = []
for o in odkazy:
    href = o.get("href", "")
    if ("/eknih/" in href) and ("1" in href or "0" in href) and ("cnr" in href or "nr" not in href):
        # Extract the part after 'eknih/' and before the next '/'
        parts = href.split("eknih/")[-1].split("/")
        if parts:
            klice.append(parts[0])

# Remove duplicates by converting to set and back to list
klice = list(set(klice))
print(f"Initial keys found: {len(klice)}")

# --- Extend Keys with Specific Rules ---
# This list defines how certain keys (e.g., 'fs') should be expanded into more specific paths.
# Each tuple is (suffix_to_match, replacement_path_segment)
rozsireni_rules = [
    ('ps', 'ps/psse'), # společné schůze Sněmovny a Senátu
    ('fs', 'fs/slsn'), # Sněmovna lidu Národního shromáždění
    ('fs', 'fs/sl'), # Sněmovna lidu Národního shromáždění
    ('fs', 'fs/sn'),   # Sněmovna národů Národního shromáždění
    ('ns', 'ns/ps'),   # prvorepubliková sněmovna
    ('ns', 'ns/se'),   # prvorepublikový senát
]

initial_klice_count = len(klice)
# Iterate over a copy of klice because we are modifying it inside the loop
for k in list(klice):
    for kratke, dlouhe in rozsireni_rules:
        if k.endswith(kratke):
            # Construct the new key by replacing the short suffix with the long path segment
            new_klic_part = k.replace(kratke, dlouhe)
            if new_klic_part not in klice:
                klice.append(new_klic_part)
                print(f"Added extended key: {new_klic_part} (from {k})")

print(f"Total keys after extension: {len(klice)} (added {len(klice) - initial_klice_count} new keys)")

# Sort keys in reverse to start from the most recent
klice.sort()
klice = klice[::-1]
print("\nKeys to process (most recent first):\n" + '\n'.join(klice))

# --- Main Download Loop ---
for klic in klice:
    print(f"\n--- Processing key: {klic} ---")
    schuze = 1
    consecutive_errors_schuze = 0 # Counter for consecutive errors for schuze/001.htm

    while True: # Outer loop for schuze (sessions)
        cast = 1
        consecutive_errors_cast = 0 # Counter for consecutive errors for 'cast' parts

        # Inner loop: increment cast (parts of a session) until MAX_CONSECUTIVE_ERRORS_CAST is reached
        while True:
            url = f"https://www.psp.cz/eknih/{klic}/stenprot/{schuze:003}schuz/s{schuze:003}{cast:003}.htm"
            filename = url.split("eknih/")[-1].replace("/", "_")

            if filename in stazene:
                print(f"Already downloaded: {filename}")
                cast += 1
                consecutive_errors_cast = 0 # Reset counter if we found an existing file
                continue # Move to the next 'cast' part

            print(f"Attempting to download: {url}")
            protokol = robust_request(url)
            time.sleep(REQUEST_DELAY) # Small delay to be respectful to the server

            if protokol is None:
                print(f"Skipping {filename} due to persistent network errors after retries.")
                consecutive_errors_cast += 1
            else:
                odpoved = protokol.status_code
                content_length = len(protokol.text) if hasattr(protokol, 'text') else 0

                if odpoved == 404:
                    print(f"404 Not Found for cast part: {filename}")
                    consecutive_errors_cast += 1
                elif odpoved == 200 and content_length <= MIN_CONTENT_LENGTH:
                    print(f"Content too small for {filename} ({content_length} bytes).")
                    consecutive_errors_cast += 1
                elif odpoved == 200 and content_length > MIN_CONTENT_LENGTH:
                    consecutive_errors_cast = 0 # Reset counter if successful
                    try:
                        file_path = os.path.join(DOWNLOAD_DIR, filename)
                        with open(file_path, "w+", encoding="windows-1250", errors='ignore') as soubor_s_protokolem:
                            soubor_s_protokolem.write(protokol.text)
                        print(f"Successfully saved: {filename} (size: {content_length} bytes)")
                        stazene.add(filename) # Add to set of downloaded files
                    except Exception as e:
                        print(f"Error saving file {filename}: {e}")
                else:
                    print(f"Unexpected status code {odpoved} for {filename}.")
                    consecutive_errors_cast += 1

            if consecutive_errors_cast >= MAX_CONSECUTIVE_ERRORS_CAST:
                print(f"Reached {MAX_CONSECUTIVE_ERRORS_CAST} consecutive errors for cast. Breaking inner loop.")
                break # Break inner 'cast' loop

            cast += 1

        # After inner 'cast' loop breaks, increment 'schuze' and test the next 'schuze'
        schuze += 1

        # Test if the first part of the new 'schuze' (sXXX001.htm) also returns 404 or small content
        test_url = f"https://www.psp.cz/eknih/{klic}/stenprot/{schuze:003}schuz/s{schuze:003}001.htm"
        test_filename = test_url.split("eknih/")[-1].replace("/", "_")

        if test_filename in stazene:
            print(f"Already downloaded test file: {test_filename}. Continuing to next schuze.")
            consecutive_errors_schuze = 0 # Reset if we found an existing file
            continue # Continue to the next 'schuze'

        print(f"Testing for next schuze existence: {test_url}")
        test_protokol = robust_request(test_url)

        if test_protokol is None:
            print(f"Network error testing {test_url}. Assuming more data exists for now, but this might prolong the loop.")
            # If network error, we can't reliably determine if it's a 404 or small content.
            # For robustness, we continue, but it's a trade-off.
            continue

        test_odpoved = test_protokol.status_code
        test_content_length = len(test_protokol.text) if hasattr(test_protokol, 'text') else 0

        if test_odpoved == 404:
            print(f"404 Not Found for test URL: {test_url}. Incrementing schuze error counter.")
            consecutive_errors_schuze += 1
        elif test_odpoved == 200 and test_content_length <= MIN_CONTENT_LENGTH:
            print(f"Content too small for test URL: {test_url} ({test_content_length} bytes). Incrementing schuze error counter.")
            consecutive_errors_schuze += 1
        else:
            consecutive_errors_schuze = 0 # Reset counter if successful or other status code
            # If test_protokol.status_code is 200 and content is sufficient, this schuze exists.
            print(f"Next schuze ({schuze}) exists (status: {test_odpoved}). Continuing.")

        if consecutive_errors_schuze >= MAX_CONSECUTIVE_ERRORS_SCHUZE:
            print(f"Reached {MAX_CONSECUTIVE_ERRORS_SCHUZE} consecutive errors for schuze. Breaking outer loop for key {klic}.")
            break # Break outer 'schuze' loop

print("\n--- Script Finished ---")