import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To-do:
    - " Neprošlo opravou po digitalizaci !" a absence data v 1990snr_stenprot_023schuz_s023008.htm
    - Někde, např. zde: [https://www.psp.cz/eknih/1954ns/stenprot/021schuz/s021001.htm](https://www.psp.cz/eknih/1954ns/stenprot/021schuz/s021001.htm) není mluvčí označen jménem, jen jako "Předseda".
    - Brajgl v 1920ns_ps_stenprot_182schuz_s182001.htm.
    - Procedurální věci v 1945pns_stenprot_003schuz_s003001.htm
    """)
    return


@app.cell
def _():
    import os
    import csv
    import json
    import random
    from bs4 import BeautifulSoup
    import concurrent.futures

    return BeautifulSoup, concurrent, csv, json, os


@app.cell
def _(os):
    kam = "data_raw/schuze"

    try:
        os.makedirs(kam)
    except:
        pass
    return (kam,)


@app.cell
def _():
    import re

    return (re,)


@app.cell
def _():
    # re.search(r"\d{1,2}\. \w{4,12} [12]\d{3}", "zxz").group()
    return


@app.cell
def _():
    mesice = {
        "ledna": 1,
        "února": 2,
        "března": 3,
        "dubna": 4,
        "května": 5,
        "června": 6,
        "července": 7,
        "srpna": 8,
        "září": 9,
        "října": 10,
        "listopadu": 11,
        "prosince": 12,
    }

    funkce = [
        "předseda",
        "předsedkyně",
        "předs.",
        "místopředseda",
        "místopředsedkyně",
        "podpředseda",
        "podpředsedkyněposlanec",
        "poslankyně",
        "posl.",
        "ministr",
        "ministryně",
        "zpravodaj",
        "zpravodajka",
        "zástupce",
        "zástupkyně",
        "sen.",
        "senátor",
        "senátorka",
        "společná",
        "společná",
        "tajemník",
        "tajemnice",
        "ministerský",
        "ministerská",
        "guvernér",
    ]
    return funkce, mesice


@app.cell
def _():
    from collections import OrderedDict

    return (OrderedDict,)


@app.cell
def _(BeautifulSoup, OrderedDict, funkce, mesice, os, re):
    def oscrapovani_stenozaznamu(soubor, zdroj=False):

        print(f"Scrapuji soubor {soubor}")

        if "/" in soubor:
            soubor = soubor.replace("/", "_")

        def ziskej_metadata(soubor):
            if "psse" not in soubor:
                komora_kratce = soubor.split("_")[0][4:]
            else:
                komora_kratce = "psse"
            obdobi = soubor.split("_")[0][0:4]
            schuze = soubor.split("_")[-1][1:4]
            cast = soubor.split("_")[-1][-7:-4]

            return komora_kratce, int(obdobi), int(schuze), int(cast.removesuffix("."))

        def najdi_datum(polivka):

            surove_datum = ""
            if polivka.find(class_="date"):
                surove_datum = (
                    polivka.find(class_="date").text.replace("\xa0", " ").lower()
                )
            if surove_datum == "":
                try:
                    surove_datum = re.search(
                        r"\d{1,2}\. \w{4,12} [12]\d{3}", polivka.text.split("Minulý")
                    ).group()
                    if zdroj == True:
                        print("Vytahuji surové datum z textu.")
                except:
                    surove_datum = polivka.find("a", href="../index.htm").text.lower()

            try:
                rok = int(surove_datum.split(" ")[-1])
                mesic = surove_datum.split(" ")[-2]
                den = int(surove_datum.split(" ")[-3].removesuffix("."))
                return f"{rok}-{mesice[mesic]:02}-{den:02}"
            except:
                return None

        def najdi_komoru_a_schuzi(polivka):
            odkazy = polivka.find_all("a")
            komora, schuze = None, None
            try:
                komora = soup.find("h1").text.strip()
            except:
                komora = soup.find(id="breadcrumb").find_all("a")[1].text.strip()
            finally:
                pass
            for a in odkazy:
                if "href" in a.attrs:
                    if "./index.htm" in a["href"]:
                        schuze = a.text.strip()
            return komora, schuze

        def ciste_odstavce(seznam):
            return (
                " ".join(seznam)
                .replace("\xa0", " ")
                .replace("***", "")
                .removeprefix(":")
                .strip()
            )

        def serad_metadata(slovnik):
            poradi_metadat = [
                "komora",
                "obdobi",
                "schuze",
                "cast",
                "soubor",
                "datum",
                "komora_komplet",
                "schuze_komplet",
                "prepsano",
                "autorizovano",
            ]
            vystupni_slovnik = OrderedDict()
            for p in poradi_metadat:
                try:
                    vystupni_slovnik[p] = slovnik[p]
                except:
                    vystupni_slovnik[p] = None
            return vystupni_slovnik

        metadata = ziskej_metadata(soubor)

        slovnik_metadata = {
            "komora": metadata[0],
            "obdobi": metadata[1],
            "schuze": metadata[2],
            "cast": metadata[3],
            "soubor": soubor,
        }

        if "1996ps" in soubor:
            parsovatko = "html5lib"  # kvůli 1996ps_stenprot_016schuz_s016005.htm aj., odkazy začínají mimo odstavce
        else:
            parsovatko = "lxml"

        with open(
            os.path.join("downloads/schuze/", soubor), "r", encoding="windows-1250"
        ) as schuze:
            schuze = schuze.read().replace("\n", " ")
            soup = BeautifulSoup(schuze, parsovatko)

        projevy = []

        if "nebyl dosud přepsán. Prosím, zkuste později." in soup.text:
            slovnik_metadata["prepsano"] = False
            return serad_metadata(slovnik_metadata), projevy

        if ("Neprošlo jazykovou korekturou, neautorizováno" in soup.text) or (
            "Neprošlo opravou po digitalizaci" in soup.text
        ):
            slovnik_metadata["autorizovano"] = False

        slovnik_metadata["datum"] = najdi_datum(soup)
        slovnik_metadata["komora_komplet"], slovnik_metadata["schuze_komplet"] = (
            najdi_komoru_a_schuzi(soup)
        )

        if "NS RČS" in soup.find(id="breadcrumb").text:
            if "Senát" in [a.text for a in soup.find(id="breadcrumb").find_all("a")]:
                slovnik_metadata["komora_komplet"] += ", Senát"
                slovnik_metadata["komora"] = "se"
            elif "Poslanecká sněmovna" in [
                a.text for a in soup.find(id="breadcrumb").find_all("a")
            ]:
                slovnik_metadata["komora_komplet"] += ", Poslanecká sněmovna"
                slovnik_metadata["komora"] = "ps"

        slovnik_metadata["prepsano"] = True
        slovnik_metadata["autorizovano"] = True

        orez = 130

        uz_byl_tucnej = False
        poradi = 1
        projev = {"mluvci": None, "poradi": poradi, "soubor": soubor, "mluvci_id": None}
        odstavce = []

        vsechny_odstavce = soup.find_all("p")

        zacatek_dokumentu = 5
        for index, p in enumerate(vsechny_odstavce[0:7]):
            if (
                ("Minulý" in p.text)
                and ("Dolů" in p.text)
                and ("Další" in p.text)
                and (len(p.text.strip()) < 60)
            ):
                zacatek_dokumentu = index + 1

        for p in vsechny_odstavce[zacatek_dokumentu:-10]:
            if zdroj == True:
                print("____" + p.text[0:orez])

            if (
                ("1992fs_sl" in soubor)
                or ("1992fs_sn" in soubor)
                or ("1990fs_slsn" in soubor)
            ):  # ("1990fs_sl" in soubor)
                if (
                    (":" in p.text.strip()[0 : orez - 30])
                    and (': "' not in p.text.strip()[0 : orez - 28])
                    and (
                        len([l for l in p.text.strip().split(":")[0] if l.isupper()])
                        > 1
                    )
                    and (len(p.text.split(":")) > 1)
                ):
                    if "A" <= p.text.split(":")[1].strip() <= "Ž":
                        projev["text"] = ciste_odstavce(odstavce)
                        if projev["text"] != "":
                            poradi += 1
                            projevy.append(projev)
                        projev = {}
                        odstavce = []
                        uz_byl_tucnej = True
                        projev["poradi"] = poradi
                        projev["soubor"] = soubor
                        projev["mluvci"] = p.text.split(":")[0].strip()
                        projev["mluvci_id"] = None
                        odstavce.append(" ".join(p.text.split(":")[1:]).strip())

                    else:
                        odstavce.append(p.text.strip())

                else:
                    odstavce.append(p.text.strip())

            else:
                if zdroj:
                    if p.find("b"):
                        print("TUČNÉ")

                if (
                    ":" in p.text.strip()[0:orez]
                    and (
                        p.find(
                            "b",
                            string=lambda text: (
                                (text.strip() in p.text.strip()[0:orez])
                                and (len(text.strip()) >= 3)
                                if text
                                else False
                            ),
                        )
                        or p.find(
                            "u",
                            string=lambda text: (
                                (text.strip() in p.text.strip()[0:orez])
                                and (len(text.strip()) >= 3)
                                if text
                                else False
                            ),
                        )
                    )
                    and (
                        "výsledkem:"
                        not in p.text  # kvůli 2006se_stenprot_015schuz_s015018.htm
                    )
                ):
                    pocitadlo_zvyrazneni = 0
                    prvni_tucne_je_druhe_tucne = False
                    zadna_zminka_o_funkci = True

                    if (
                        len(p.find_all("b")) > 1
                    ):  # kvůli 1920ns_se_stenprot_195schuz_s195001.htm
                        if zdroj == True:
                            print("počítám tučnost")
                        for tucne in p.find_all("b"):
                            if tucne.text.strip() in p.text.strip()[0:orez]:
                                pocitadlo_zvyrazneni += 1
                        if (
                            p.find_all("b")[0].text.strip()
                            == p.find_all("b")[1].text.strip()
                        ):  # kvůli 1996ps_stenprot_021schuz_s021021.htm
                            prvni_tucne_je_druhe_tucne = True
                        for f in funkce:
                            if (
                                f == p.text.strip().split(" ")[0].strip().lower()
                            ):  # kvůli 1948ns_stenprot_054schuz_s054003.htm: Podpředseda Valo: Ďalším prihláseným rečníkom je pán posl. Navračič. Prosím, aby sa ujal slova.
                                if zdroj == True:
                                    print(f.upper())
                                zadna_zminka_o_funkci = False
                    if (
                        (pocitadlo_zvyrazneni > 1)
                        & (prvni_tucne_je_druhe_tucne == False)
                        & (zadna_zminka_o_funkci == True)
                    ):
                        if zdroj == True:
                            print("dvakrát, bez akce")
                        odstavce.append(p.text.strip())

                    else:
                        if zdroj == True:
                            print("mluvčí (: + a/b)")

                        if (
                            ("resoluční návrh" in p.text.lower())
                            or ("pozměňovací návrh" in p.text.lower())
                            or ("doplňovací návrh" in p.text.lower())
                        ) and ("192" in soubor):
                            odstavce.append(p.text.strip())
                            # kvůli 1920ns_ps_stenprot_078schuz_s078006.htm

                        else:
                            projev["text"] = ciste_odstavce(odstavce)
                            if projev["text"] != "":
                                poradi += 1
                                projevy.append(projev)
                            projev = {}
                            odstavce = []
                            projev["poradi"] = poradi
                            projev["soubor"] = soubor
                            projev["mluvci"] = p.text.split(":")[0].strip()
                            try:
                                projev["mluvci_id"] = p.find("a")["href"]
                            except:
                                if zdroj == True:
                                    print("nenalezeno id mluvčích")
                                projev["mluvci_id"] = None
                            odstavce.append(
                                p.text.replace(projev["mluvci"], "").strip()
                            )

                elif (
                    p.find("b")
                    and (len(p.text.strip()) < 100)
                    and (p.text.strip().endswith(":"))
                ):
                    projev["text"] = ciste_odstavce(odstavce)
                    if projev["text"] != "":
                        poradi += 1
                        projevy.append(projev)
                    projev = {}
                    odstavce = []
                    projev["poradi"] = poradi
                    projev["soubor"] = soubor
                    projev["mluvci"] = p.find("b").text.replace(":", "").strip()

                elif p.find(
                    "a"
                ):  ## častá chyba, viz testy: je odkaz, není dvojtečka. kód se tu zbytečně duplikuje, whatever
                    if zdroj == True:
                        print("ODKAZ")
                    if (
                        p.text.strip().startswith(p.find("a").text.strip())
                        and (p.find("a").get("id") != "_d")
                        and (p.find("a").get("name") != "OLE_LINK1")
                    ):
                        if p.find("a").text.strip().startswith("Hlasování"):
                            odstavce.append(p.text.strip())

                        else:
                            # p.find("a").get("name") != "OLE_LINK1" kvůli 1946uns_stenprot_087schuz_s087005.htm

                            if zdroj == True:
                                print("mluvčí p.find(a)")

                            projev["text"] = ciste_odstavce(odstavce)
                            if projev["text"] != "":
                                poradi += 1
                                projevy.append(projev)
                            projev = {}
                            odstavce = []
                            projev["poradi"] = poradi
                            projev["soubor"] = soubor
                            projev["mluvci"] = p.find("a").text.strip()
                            try:
                                projev["mluvci_id"] = p.find("a")["href"]
                            except:
                                projev["mluvci_id"] = None
                            odstavce.append(
                                p.text.replace(projev["mluvci"], "").strip()
                            )

                    else:
                        odstavce.append(p.text.strip())

                else:
                    odstavce.append(p.text.strip())

        projev["text"] = ciste_odstavce(odstavce)
        projevy.append(projev)

        return serad_metadata(slovnik_metadata), projevy

    return (oscrapovani_stenozaznamu,)


@app.cell
def _(csv, json, kam, os, oscrapovani_stenozaznamu):
    def html2data(soubor):

        ciste = oscrapovani_stenozaznamu(soubor)
        soubor = soubor.replace(".htm", "")

        with open(
            os.path.join(kam, f"prepis_{soubor}.ndjson"), "w+", encoding="utf-8"
        ) as export:
            for projev in ciste[1]:
                export.write(json.dumps(projev) + "\n")

        with open(
            os.path.join(kam, f"meta_{soubor}.csv"), "w+", newline="", encoding="utf-8"
        ) as export_file:
            fieldnames = ciste[0].keys()
            writer = csv.DictWriter(
                export_file, fieldnames=fieldnames, quoting=csv.QUOTE_STRINGS
            )
            writer.writeheader()
            writer.writerow(ciste[0])

    return (html2data,)


@app.cell(disabled=True)
def _():
    # oscrapovani_stenozaznamu("2021ps_stenprot_139schuz_b18300000.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(html2data):
    html2data("1990snr_stenprot_023schuz_s023008.htm")
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("1996ps_psse_stenprot_001schuz_s001003.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("1990fs_slsn_stenprot_007schuz_s007024.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("1990fs_slsn_stenprot_019schuz_s019110.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("1990fs_slsn_stenprot_004schuz_s004013.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("2006ps_stenprot_048schuz_s048369.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("2021ps_stenprot_140schuz_s140050.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("2021ps_stenprot_140schuz_s140050.htm", zdroj=True)
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("1981fs_slsn_stenprot_013schuz_s013001.htm")
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("2017ps_stenprot_029schuz_s029109.htm")
    return


@app.cell(disabled=True)
def _(oscrapovani_stenozaznamu):
    oscrapovani_stenozaznamu("2017ps_stenprot_029schuz_s029109.htm", zdroj=True)
    return


@app.cell
def _(html2data):
    def process_file(soubor):
        try:
            html2data(soubor)
        except Exception as e:
            print(f"{soubor}: {e}")

    return (process_file,)


@app.cell
def _(concurrent, os, process_file):
    directory = "downloads/schuze"
    files = [f for f in os.listdir(directory)]
    # print(", ".join(files))
    print(f"{len(files)} stažených stenoprotokolů celkem")
    oscrapovane = {
        f.split(".")[0].replace("meta_", "").replace("prepis_", "")
        for f in os.listdir("data_raw/schuze")
    }
    # print(", ".join(oscrapovane))
    files = [
        f for f in files if f.split(".")[0] not in oscrapovane
    ]  # files = [f for f in files if "199" in f]
    # files = [f for f in files if ('1992fs_sl' in f) or ('1990fs_sl' in f)]
    total_files = len(files)
    print(f"{total_files} stenoprotokolů nových")

    batch_size = 8

    # Process files in batches to reduce memory usage and improve progress tracking
    for i in range(0, total_files, batch_size):
        batch = files[i : i + batch_size]

        # Use ProcessPoolExecutor for CPU-bound tasks or ThreadPoolExecutor for I/O-bound tasks
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map is more memory efficient than list comprehension for large batches
            futures = {executor.submit(process_file, f): f for f in batch}

            for j, future in enumerate(concurrent.futures.as_completed(futures), 1):
                try:
                    future.result()  # Get the result to raise any exceptions
                except Exception as e:
                    print(f"Error processing file {futures[future]}: {e}")

                # # Update progress every batch_size files
                # if (i + j) % batch_size == 0:
                #    print(f"{i + j}/{total_files}")
    return


if __name__ == "__main__":
    app.run()
