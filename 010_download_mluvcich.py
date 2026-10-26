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
    Po volbách 2025 zde bude nutné zvýšit rozsah období na range (1,11)
    """)
    return


@app.cell
def _():
    import os
    import polars as pl
    import requests

    return os, pl, requests


@app.cell
def _(os, pl):
    df = pl.read_parquet(os.path.join("data", "projevy.parquet")).sort(by="datum")
    return (df,)


@app.cell
def _(df, pl):
    df.filter(pl.col("mluvci").str.contains("Babiš")).select(
        pl.col(["mluvci", "mluvci_id"])
    ).unique()
    return


@app.cell
def _(df):
    len(df)
    return


@app.cell
def _(df, pl):
    len(df.filter(pl.col("mluvci_id").str.contains("/sqw/detail")))
    return


@app.cell
def _(df, pl):
    df.filter(pl.col("mluvci").str.contains("Marek Benda")).select(
        pl.col(["mluvci", "mluvci_id"])
    ).unique()
    return


@app.cell
def _(df, pl):
    mluvci_raw = df.select(pl.col("mluvci_id")).unique().to_series().to_list()
    return (mluvci_raw,)


@app.cell
def _(mluvci_raw):
    len(mluvci_raw)
    return


@app.cell
def _():
    import random

    return (random,)


@app.cell
def _(mluvci_raw, random):
    random.sample(mluvci_raw, 20)
    return


@app.cell
def _():
    kam = "downloads/poslanectvo"
    return (kam,)


@app.cell
def _(kam, os):
    os.makedirs(kam, exist_ok=True)
    return


@app.cell
def _(kam, os, requests, stazene):
    def stahni_poslance(url):
        if url:
            if not "/sqw/detail.sqw?" in url:
                return None
            else:
                id = url.split("id=")[-1].split("&")[0]
                for dodatek in range(0, 10):
                    soubor = f"{id}_{dodatek}.html"
                    if dodatek == 0:
                        print(f"Stahuji id {id}")
                    if soubor not in stazene:
                        try:
                            if "psp.cz" not in url:
                                url = "https://www.psp.cz" + url
                            if "https://" not in url:
                                url = "https://" + url
                            response = requests.get(url)
                            if response.status_code == 200:
                                with open(
                                    os.path.join(kam, soubor), "w+", encoding="utf-8"
                                ) as poslancododatek:
                                    poslancododatek.write(response.text)
                        except:
                            print(f"chyba: {url}")

    return


@app.cell
def _(kam, os, requests, stazene):
    def stahni_poslance_1(url):
        if url:
            if not '/sqw/detail.sqw?' in url:
                return None
            else:
                id = url.split('id=')[-1].split('&')[0]
                for obdobi in range(1, 10):
                    soubor = f'{id}_{obdobi}.html'
                    if obdobi == 1:
                        print(f'Stahuji id {id}')
                    if soubor not in stazene:
                        try:
                            if 'psp.cz' not in url:
                                url = 'https://www.psp.cz' + url
                            if 'https://' not in url:
                                url = 'https://' + url
                            response = requests.get(f'{url}&o={obdobi}')
                            if response.status_code == 200:
                                with open(os.path.join(kam, soubor), 'w+', encoding='utf-8') as poslancoobdobi:
                                    poslancoobdobi.write(response.text)
                        except Exception as e:
                            print(f'{e}: {url}')

    return (stahni_poslance_1,)


@app.cell
def _(kam, mluvci_raw, os, stahni_poslance_1):
    stazene = set(os.listdir(kam))
    print(f'{len(stazene)} souborů staženo')
    for m in mluvci_raw:
        stahni_poslance_1(m)
    print('hotovo dvacet')
    return (stazene,)


if __name__ == "__main__":
    app.run()
