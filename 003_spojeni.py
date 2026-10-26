import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import os
    import polars as pl

    return os, pl


@app.cell
def _(pl):
    pl.Config.set_tbl_rows(65)
    pl.Config.set_fmt_str_lengths(150)
    pl.Config.set_tbl_width_chars(200)
    pl.Config.set_verbose(False)
    return


@app.cell
def _():
    slovenske = ["S SK 1939", "S SR 1939-1945"]
    return (slovenske,)


@app.cell
def _(pl):
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
    return (projevy,)


@app.cell
def _(pl):
    meta = (
        pl.read_csv(
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
        )
        .with_columns(pl.col("datum").str.to_date(format="%Y-%m-%d", exact=False))
        .with_columns(
            pl.when(pl.col("soubor") == "1996ps_stenprot_006schuz_s006024.htm")
            .then(pl.lit(2006))
            .otherwise(pl.col("obdobi"))
            .alias("obdobi")
        )
    )
    return (meta,)


@app.cell
def _(meta, pl):
    meta.filter(pl.col("prepsano") == False).write_parquet(
        "data/neprepsane_schuze.parquet"
    )
    return


@app.cell
def _(pl):
    df = pl.read_csv("data_raw/schuze/meta_1990snr_stenprot_023schuz_s023008.csv")
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(os):
    try:
        os.makedirs("data")
    except:
        pass
    return


@app.cell
def _(pl, projevy):
    projevy.filter(pl.col("soubor") == "1998ps_stenprot_019schuz_s019364.htm")
    return


@app.cell
def _(pl, projevy):
    zvoleni = (
        projevy.filter(pl.col("mluvci").str.contains("zvolení "))
        .select(pl.col("mluvci"))
        .unique()
        .to_series()
        .to_list()
    )
    return (zvoleni,)


@app.cell
def _(pl, projevy):
    pritomni = (
        projevy.filter(pl.col("mluvci").str.contains("[Pp]řítomn"))
        .select(pl.col("mluvci"))
        .unique()
        .to_series()
        .to_list()
    )
    return (pritomni,)


@app.cell
def _(pritomni, zvoleni):
    nejsou_mluvci = (
        [
            "Přítomni",
            "Za vládu České republiky",
            "Nahoru",
            "Dolů",
            "2",
            "76",
            "Omluveni poslanci",
        ]
        + zvoleni
        + pritomni
    )
    return (nejsou_mluvci,)


@app.cell
def _(nejsou_mluvci):
    nejsou_mluvci
    return


@app.cell
def _(os, pl, projevy):
    try:
        import pickle

        with open(os.path.join("testy", "testy.pickle"), "rb") as testy_import:
            testy = pickle.load(testy_import)

        for t in testy:
            vysledek = projevy.filter(
                (
                    (pl.col("mluvci").str.contains(t["kdo"]))
                    & (pl.col("text").str.contains(t["co"]))
                )
            )

            if len(vysledek) != 1:
                print(f"❌ {t['kdy']}, {t['co']}")
                if t.get("problem"):
                    print(f"({t['problem']})")
            else:
                print(f"✔️ {t['kdy']}, {t['co']}")

    except:
        pass
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Chyba zde ještě neznamená, že je něco špatně – některá data se vyplňují právě až při spojování a čištění.
    """)
    return


@app.cell
def _(meta, nejsou_mluvci, pl, projevy, slovenske):
    # .filter(
    #    ~(pl.col("text").str.starts_with("(pokračuje") | pl.col("text").str.starts_with("(Pokračuje")) #  | pl.col("text").str.ends_with("hodin)") | pl.col("text").str.ends_with("hodin.)")
    df_1 = (
        projevy.join(meta, on="soubor", how="left")
        .filter(~pl.col("mluvci").is_in(nejsou_mluvci, nulls_equal=True))
        .filter(~pl.col("komora_komplet").str.contains("SNR"))
        .filter(~pl.col("komora_komplet").str.contains("NR SR"))
        .filter(~pl.col("komora_komplet").is_in(slovenske))
        .with_columns(pl.col("text").str.replace_many(["   ", "  "], [" "]))
        .with_columns(
            pl.col("text")
            .str.replace("\\([Pp]okračuje .{3,30}\\)", "")
            .str.strip_chars()
        )
        .sort(by=["komora_komplet", "schuze", "cast", "poradi"])
        .with_columns(
            pl.when(pl.col("mluvci").is_null())
            .then(pl.lit(False))
            .otherwise(pl.lit(True))
            .alias("mluvci_jisty")
        )
        .with_columns(pl.col("mluvci").forward_fill())
        .with_columns(
            (pl.col("mluvci") != pl.col("mluvci").shift(1)).alias("mluvci_changed")
        )
        .with_columns(
            pl.when(pl.col("mluvci_changed") | pl.col("mluvci_id").is_not_null())
            .then(pl.col("mluvci_id"))
            .otherwise(None)
            .forward_fill()
            .alias("mluvci_id")
        )
        .drop("mluvci_changed")
    )  # Create a helper column to track when mluvci changes  # Forward fill mluvci_id only when mluvci hasn't changed
    return (df_1,)


@app.cell
def _(df_1):
    df_1.write_parquet("data/projevy.parquet", use_pyarrow=True)
    return


@app.cell
def _(df_1, pl):
    komory = df_1.select(pl.col("komora")).unique().to_series().to_list()
    return (komory,)


@app.cell
def _(df_1, pl):
    df_1.select(pl.col(["komora_komplet", "komora"])).unique().sort(by="komora_komplet")
    return


@app.cell
def _(komory):
    komory
    return


@app.cell
def _(df_1, pl):
    df_1.filter(pl.col("soubor") == "1998ps_stenprot_019schuz_s019364.htm").select(
        pl.col("text")
    )
    return


@app.cell
def _(df_1, komory, pl):
    for k in komory:
        obdobi = (
            df_1.filter(pl.col("komora") == k)
            .select(pl.col("obdobi"))
            .unique()
            .to_series()
            .to_list()
        )
        for o in obdobi:
            # print(f"Období: {o}")
            df_1.filter(pl.col("komora") == k).filter(pl.col("obdobi") == o).sort(
                by=["datum", "schuze", "cast", "poradi"]
            ).write_parquet(f"data/{k}_{o}.parquet")
    # print(f"""Komory: {("\n- ").join(komory)}""")
    return


@app.cell
def _(df_1):
    len(df_1)
    return


@app.cell
def _(meta):
    len(meta)
    return


@app.cell
def _(meta, pl):
    bez_data = meta.filter(pl.col("datum").is_null())
    print(f"Bez data: {len(bez_data)}")
    return (bez_data,)


@app.cell
def _(bez_data, pl):
    bez_data.filter(pl.col("prepsano") == True)
    return


@app.cell
def _(bez_data):
    bez_data.sort(by="obdobi").tail(30)
    return


@app.cell
def _(meta, pl):
    bez_komory = meta.filter(pl.col("komora_komplet").is_null())
    print(f"Bez komory: {len(bez_komory)}")
    return


@app.cell
def _(meta, pl):
    bez_obdobi = meta.filter(pl.col("obdobi").is_null())
    print(f"Bez období: {len(bez_obdobi)}")
    return


@app.cell
def _(meta, pl):
    bez_data_1 = meta.filter(pl.col("datum").is_null()).sample(30)
    print(len(bez_data_1))
    return


@app.cell
def _(meta, pl):
    meta.filter(pl.col("datum").is_null()).sample(30)
    return


@app.cell
def _():
    import altair as alt

    return (alt,)


@app.cell
def _(df_1, pl):
    df_1.filter(pl.col("datum").dt.year() == 1976)
    return


if __name__ == "__main__":
    app.run()
