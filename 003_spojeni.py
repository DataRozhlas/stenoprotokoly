import os
import polars as pl

try:
    os.makedirs("data")
except:
    pass

slovenske = ["S SK 1939", "S SR 1939-1945"]

projevy = pl.read_ndjson(
    "data_raw/schuze/prepis_*.ndjson",
    ignore_errors=True,
    schema=pl.Schema(
        {
            "mluvci": pl.String,
            "soubor": pl.String,
            "mluvci_id": pl.String,
            "text": pl.String,
            "poradi": pl.Int32,
        }
    ),
)

meta = pl.read_csv(
    "data_raw/schuze/meta_*.csv",
    schema=pl.Schema(
        {
            "komora": pl.String,
            "obdobi": pl.Int32,
            "schuze": pl.Int32,
            "cast": pl.Int32,
            "soubor": pl.String,
            "datum": pl.String,
            "komora_komplet": pl.String,
            "schuze_komplet": pl.String,
            "prepsano": pl.Boolean,
            "autorizovano": pl.Boolean,
        }
    ),
).with_columns(pl.col("datum").str.to_date(format="%Y-%m-%d", exact=False))

df = (
    projevy.join(meta, on="soubor", how="left")
    .filter(~pl.col("komora_komplet").str.contains("SNR"))
    .filter(~pl.col("komora_komplet").str.contains("NR SR"))
    .filter(~pl.col("komora_komplet").is_in(slovenske))
    .sort(by=["datum", "poradi"])
)

df.write_parquet("data/projevy.parquet", use_pyarrow=True)