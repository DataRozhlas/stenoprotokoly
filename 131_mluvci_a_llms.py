import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    import altair as alt
    import marimo as mo

    return alt, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Hledáme lidi, kteří začali být mluvní cca po uvedení ChatGPT (prosinec 2022). Proto pracujeme se stenozáznamy ze Sněmoven 2017- a 2021-.

    Háčky:
    - Protože v našich datech chybí zcela jednoznačná identifikace mluvčích (podle změn funkcí se liší jak popisek mluvčího, tak id odkazu), zjednodušíme si to: vyzobneme jméno. (Později si případné shody jmen nebo chyby ve vyzobávání pohlídáme.)
    - Sledujeme pouze poslance a poslankyně, kteří zasedali v obou obdobích a mluvili v obou obdobích.
    - Nezohledňujeme změny funkcí (předseda mluví víc než řadový poslanec apod.)
    """)
    return


@app.cell
def _(pl):
    df = (
        pl.concat(
            [
                pl.read_parquet("data/ps_2017.parquet"),
                pl.read_parquet("data/ps_2021.parquet"),
            ]
        )
        .with_columns(
            pl.col("mluvci")
            .str.split(" ")
            .list.slice(-2, 2)
            .list.join(" ")
            .alias("jmeno")
        )
        .with_columns(pl.col("text").str.len_bytes().alias("rozsah_znaku"))
    )
    return (df,)


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Vytipování skokanů mluvnosti – bez zohlednění toho, jestli jim např. nepřibyla funkce.
    """)
    return


@app.cell
def _(df, pl):
    def rozsahy_projevu_po_letech(zacatek, konec):
        return (
            df.filter(pl.col("datum").dt.year().is_between(zacatek, konec))
            .group_by("jmeno")
            .agg(pl.col("rozsah_znaku").sum())
            .sort(by="rozsah_znaku", descending=True)
        )

    return (rozsahy_projevu_po_letech,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(rozsahy_projevu_po_letech):
    rozsahy_projevu_na_zacatku = rozsahy_projevu_po_letech(2018, 2019)
    rozsahy_projevu_na_konci = rozsahy_projevu_po_letech(2023, 2024)
    return rozsahy_projevu_na_konci, rozsahy_projevu_na_zacatku


@app.cell
def _(pl, rozsahy_projevu_na_konci, rozsahy_projevu_na_zacatku):
    zebricek = (
        rozsahy_projevu_na_zacatku.join(
            rozsahy_projevu_na_konci, how="full", on="jmeno"
        )
        .with_columns(
            (pl.col("rozsah_znaku_right") / pl.col("rozsah_znaku")).alias("rozdil")
        )
        .drop_nulls(subset="rozdil")
        .sort(by="rozdil", descending=True)
    )

    zebricek
    return (zebricek,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A ted se podíváme po zubech na začátku roku 2023. Nejdřív vyselektujeme mluvčí s největším poměrěm mezi slovy pronesenými v letech 23+24 a 18+19 (covid považujme za anomálii).
    """)
    return


@app.cell
def _(pl, zebricek):
    kandidatstvo = zebricek.head(40).select(pl.col("jmeno")).to_series().to_list()
    kandidatstvo
    return (kandidatstvo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rozsahy projevů vytipovaného poslanectva po kvartálech
    """)
    return


@app.cell
def _(alt, df, kandidatstvo, pl):
    alt.Chart(
        df.filter(pl.col("jmeno").is_in(kandidatstvo))
        .with_columns(
            (
                pl.col("datum").dt.year().cast(str)
                + pl.lit("-")
                + pl.col("datum").dt.quarter().cast(str)
            ).alias("kvartal")
        )
        .group_by([pl.col("jmeno"), pl.col("kvartal")])
        .agg(pl.col("rozsah_znaku").len())
        .with_columns(
            pl.when(pl.col("kvartal").is_in(["2023-1", "2023-2", "2023-3"]))
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("nastup_chatgpt")
        ),
        width=600,
        height=100,
    ).mark_bar().encode(
        alt.X("kvartal:N"),
        alt.Y("rozsah_znaku:Q"),
        alt.Row("jmeno:N", header=alt.Header(orient="top"), sort=kandidatstvo),
        alt.Color("nastup_chatgpt:N"),
    ).resolve_scale(y="independent")
    return


if __name__ == "__main__":
    app.run()
