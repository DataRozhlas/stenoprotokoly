import polars as pl
import re


def clean_and_split_string(input_string):
    # Use regular expression to find all words, ignoring non-word characters
    words = re.findall(r"\b\w+\b", input_string)
    return words


pl.scan_parquet("data_raw/smazat_projevy.parquet").with_columns(
    pl.col("datum").dt.year().alias("rok")
).filter(pl.col("rok") >= 1918).select(
    pl.col(["rok", "komora_komplet", "text"])
).with_columns(
    pl.col("text")
    .map_elements(clean_and_split_string, return_dtype=pl.List(pl.String))
    .alias("slova")
).explode(
    "slova"
).sink_parquet(
    "data_raw/slova.parquet"
)