import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To-do do prezentace

    ### Předělat
    - první a poslední zmínky o věcech

    ### Nové výpočty
    - kdo roztleskává nejčastěji

    ### Vytáhnout obrázky
    - dávné poslankyně, kterým se tleskalo
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt
    import re
    import simplemma

    return alt, mo, pl, re


@app.cell
def _():
    chceme = ["fs", "cnr", "ps", "ns", "pns", "uns"]
    return (chceme,)


@app.cell
def _(chceme, pl):
    lf = (
        pl.scan_parquet(
            "data/projevy.parquet",
        )
        .with_columns(
            pl.col("mluvci")
            .str.split(" ")
            .list.slice(-2, 2)
            .list.join(" ")
            .alias("jmeno"),
            pl.col("mluvci_id").str.split("/sqw/detail.sqw?id=").alias("id"),
            pl.col("text").str.count_matches(" ").alias("pocet_slov"),
        )
        .with_columns(
            pl.when(pl.col("id").len() > 2)
            .then(pl.col("id").list.slice(1).list.join(""))
            .alias("id")
        )
        .filter(pl.col("obdobi") >= 1918)
        .filter(pl.col("komora").is_in(chceme))
        .sort(by="datum")
    )

    lf_mluvci = pl.scan_parquet("data/mluvci.parquet")
    return lf, lf_mluvci


@app.cell
def _(lf):
    lf.tail(10).collect()
    return


@app.cell
def _(lf_mluvci):
    lf_mluvci.tail(10).collect()
    return


@app.cell
def _(lf):
    lf.group_by(["komora", "komora_komplet"]).len().collect().sort(
        by="len", descending=True
    )
    return


@app.cell
def _():
    zajima = ["ps", "fs", "cnr", "ns"]
    return (zajima,)


@app.cell
def _():
    FONT = "JetBrains Mono"
    WIDTH, HEIGHT = 500, 280
    GRID_COLOR = "#DDDDDD"

    COLORS = {
        "violet": {"light": "#DBAAEB", "base": "#A13CC2", "dark": "#8012A5"},
        "pink": {"light": "#FFC6D7", "base": "#FF8FB0", "dark": "#E83985"},
        "yellow": {"light": "#FFE8AA", "base": "#FFC833", "dark": "#D68D19"},
        "teal": {"light": "#C2EDEF", "base": "#4BDDDA", "dark": "#0FA6B6"},
        "blue": {"light": "#CED5FF", "base": "#5A6FF6", "dark": "#3746A4"},
        "red": {"light": "#FFBAB2", "base": "#F66060", "dark": "#C51313"},
        "lightblue": {
            "light": "#D4EBFF",
            "base": "#85B6FF",
            "dark": "#3975D0",
        },
    }

    # Order used for categorical series; the first one is the single-color default.
    PALETTE = [
        COLORS[name]["base"]
        for name in (
            "violet",
            "pink",
            "yellow",
            "teal",
            "blue",
            "red",
            "lightblue",
        )
    ]
    return COLORS, FONT, GRID_COLOR, HEIGHT, PALETTE, WIDTH


@app.cell
def _(COLORS, FONT, GRID_COLOR, HEIGHT, PALETTE, WIDTH, alt):
    def _theme():
        return {
            "config": {
                "font": FONT,
                "background": "white",
                "view": {
                    "stroke": None,
                    "continuousWidth": WIDTH,
                    "continuousHeight": HEIGHT,
                    "discreteWidth": WIDTH,
                    "discreteHeight": HEIGHT,
                },
                "title": {
                    "font": FONT,
                    "subtitleFont": FONT,
                    "anchor": "start",
                    "fontSize": 15,
                    "subtitleFontSize": 12,
                    "offset": 24,  # space between title block and the chart
                    "subtitlePadding": 6,  # space between title and subtitle
                },
                "axis": {
                    "gridColor": GRID_COLOR,
                    # Altair writes each field name into the encoding as an explicit
                    # title, which beats config. So hide titles via styling instead.
                    "titleOpacity": 0,
                    "titleFontSize": 11,
                    "titlePadding": 0,
                    "labelFont": FONT,
                    "titleFont": FONT,
                    "labelFontSize": 11,
                    "domain": False,  # no axis line by default; x re-enables it below
                    # thousands separator: "1,234,567" -> "1 234 567" (digit commas only)
                    "labelExpr": "replace(datum.label, regexp('(\\\\d),(?=\\\\d{3})', 'g'), '$1 ')",
                },
                "axisY": {"tickColor": GRID_COLOR},
                "axisX": {
                    "domain": False,
                    "domainColor": "#000000",
                    "domainWidth": 2,
                    "tickColor": GRID_COLOR,
                },
                "legend": {
                    "labelFont": FONT,
                    "titleFont": FONT,
                    "labelFontSize": 11,
                    "titleFontSize": 12,
                },
                "header": {"labelFont": FONT, "titleFont": FONT},
                "text": {"font": FONT},
                "mark": {"color": PALETTE[0]},
                "area": {"fill": PALETTE[0]},
                "bar": {"fill": PALETTE[0]},
                "line": {"stroke": PALETTE[0]},
                "point": {"stroke": PALETTE[0]},
                "circle": {"fill": PALETTE[0]},
                "square": {"fill": PALETTE[0]},
                "range": {
                    "category": PALETTE,
                    "ordinal": PALETTE,
                    # light -> base -> dark violet for continuous/quantitative color
                    "ramp": [
                        COLORS["violet"]["light"],
                        COLORS["violet"]["base"],
                        COLORS["violet"]["dark"],
                    ],
                    "heatmap": [
                        COLORS["violet"]["light"],
                        COLORS["violet"]["base"],
                        COLORS["violet"]["dark"],
                    ],
                },
            }
        }

    alt.themes.register("custom_theme", _theme)
    alt.themes.enable("custom_theme")
    return


@app.cell
def _(lf, pl):
    zacatek = lf.select(pl.col("datum")).min().collect().item()
    konec = lf.select(pl.col("datum")).max().collect().item()
    return konec, zacatek


@app.cell
def _(konec, pl, zacatek):
    df_rezimy = pl.DataFrame(
        {
            "start": ["1939-09-01", "1948-02-25", str(zacatek)],
            "end": ["1945-05-08", "1989-11-29", str(konec)],
            "co": ["2. světová válka", "komunistický režim", "nic"],
        }
    ).with_columns(pl.col("start").str.to_date(), pl.col("end").str.to_date())

    df_rezimy
    return (df_rezimy,)


@app.cell
def _(alt, df_rezimy):
    graf_rezimy = (
        alt.Chart(df_rezimy)
        .mark_rect(opacity=0.5)
        .encode(
            alt.X("start:T"),
            alt.X2("end:T"),
            alt.Color(
                "co:N",
                scale=alt.Scale(range=["#FFE8AA", "#FFBAB2", "white"]),
                legend=None,
            ),
        )
    )

    graf_rezimy
    return (graf_rezimy,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Odkdy dokdy
    """)
    return


@app.cell
def _(chceme, lf, pl):
    lf.filter(pl.col("komora").is_in(chceme)).drop_nulls(subset="datum").sort(
        by="datum"
    ).head(10).collect()
    return


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).drop_nulls(subset="datum").sort(
        by="datum", descending=True
    ).head(10).collect()
    return


@app.cell
def _(lf, pl):
    lf.group_by("komora").agg(pl.col("datum").dt.year().unique()).collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kolik tam toho je
    """)
    return


@app.cell
def _(chceme, lf, pl):
    rozsah_ve_znacich = (
        lf.filter(pl.col("komora").is_in(chceme))
        .with_columns(pl.col("text").str.len_chars())
        .select(pl.col("text").sum())
        .collect()
        .item()
    )

    print(rozsah_ve_znacich)

    print(rozsah_ve_znacich / 1800)
    return


@app.cell
def _(chceme, lf, pl):
    stats_slova = (
        lf.filter(pl.col("komora").is_in(chceme))
        .drop_nulls(subset="datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("text").str.split(" ").list.len().sum())
        .collect()
    )
    return (stats_slova,)


@app.cell
def _(pl, stats_slova):
    miliony = stats_slova.select(pl.col("text")).sum().item()
    print(miliony)
    miliony = round(miliony/1000000,0)
    return (miliony,)


@app.cell
def _(alt, graf_rezimy, miliony, stats_slova, uloz_graf):
    slova = graf_rezimy + (
        alt.Chart(
            stats_slova,
            title=alt.Title(
                "Počty slov pronesených v dolních komorách českého parlamentu",
                subtitle=["", f"Celkem {miliony:.0f} milionů slov"],
            ),
        )
        .mark_bar(width=4)
        .encode(alt.X("datum:T"), alt.Y("text:Q"))
    )

    uloz_graf(slova)

    slova
    return


@app.cell
def _(lf, pl):
    babicek = round(lf.with_columns(pl.col("text").str.count_matches(" ")).select(
        pl.col("text")
    ).sum().collect().item() / 67169,0)
    return (babicek,)


@app.function
def get_var_name(var, scope=None):
    if scope is None:
        scope = globals()
    for name, value in scope.items():
        if value is var:
            return name
    return None


@app.cell
def _():
    import vl_convert as vlc

    def uloz_graf(nazev_grafu):
        spec = nazev_grafu.to_dict(validate=False)
        svg = vlc.vegalite_to_svg(spec)
        open(
            f"grafy/jihlava_{get_var_name(nazev_grafu)}.svg",
            "w",
            encoding="utf-8",
        ).write(svg)
        print("Uloženo")

    return (uloz_graf,)


@app.cell
def _(alt, babicek, graf_rezimy, pl, stats_slova, uloz_graf):
    slova_babicka = graf_rezimy + (
        alt.Chart(
            stats_slova.with_columns(pl.col("text") / 67169),
            title=alt.Title(
                ["Kolik celých románů Babička bylo ve sněmovnách proneseno"],
                subtitle=["", f"Celkem {babicek:.0f} Babiček"],
            ),
        )
        .mark_bar(width=4)
        .encode(alt.X("datum:T"), alt.Y("text:Q"))
    )

    uloz_graf(slova_babicka)

    slova_babicka
    return


@app.cell
def _(lf, pl):
    zebricek = (
        lf.group_by("jmeno")
        .agg(pl.col("text").str.count_matches(" ").sum())
        .collect()
        .sort(by="text", descending=True)
        .filter(~pl.col("jmeno").is_in(["a to", "Předseda (zvoní)"]))
    )

    zebricek
    return (zebricek,)


@app.cell
def _(alt, pl, uloz_graf, zebricek):
    slova_milionari = (
        alt.Chart(
            zebricek.filter(pl.col("text") > 1000000),
            title=f"Poslanci a poslankyně, kteří pronesli víc než milion slov",
        )
        .mark_bar()
        .encode(
            alt.Y(
                "jmeno:N",
                sort=zebricek.head(10)
                .select(pl.col("jmeno"))
                .to_series()
                .to_list(),
            ),
            alt.X("text:Q", axis=alt.Axis(tickCount=3)),
        )
    )

    uloz_graf(slova_milionari)

    slova_milionari
    return


@app.cell
def _(lf, pl):
    zebricek2k = (
        lf.filter(pl.col("datum").dt.year() < 2001)
        .group_by("jmeno")
        .agg(pl.col("text").str.count_matches(" ").sum())
        .collect()
        .sort(by="text", descending=True)
        .filter(~pl.col("jmeno").is_in(["a to", "Předseda (zvoní)"]))
    )

    zebricek2k
    return


@app.cell
def _(pl):
    vlady = [
        {
            "vlada": "1992 první vláda V. Klause",
            "vlada_od": "2. 7. 1992",
            "vlada_do": "4. 7. 1996",
        },
        {
            "vlada": "1996 druhá vláda V. Klause",
            "vlada_od": "4. 7. 1996",
            "vlada_do": "2. 1. 1998",
        },
        {
            "vlada": "1998 vláda J. Tošovského",
            "vlada_od": "2. 1. 1998",
            "vlada_do": "22. 7. 1998",
        },
        {
            "vlada": "2002 vláda M. Zemana",
            "vlada_od": "22. 7. 1998",
            "vlada_do": "15. 7. 2002",
            "koalice_kandidatka": ["ČSSD"],
            "opozice_kandidatka": ["ODS", "US", "KDU-ČSL", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2002 vláda V. Špidly",
            "vlada_od": "15. 7. 2002",
            "vlada_do": "4. 8. 2004",
            "koalice_kandidatka": ["ČSSD", "US", "K"],
            "opozice_kandidatka": ["ODS", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2004 vláda S. Grosse",
            "vlada_od": "4. 8. 2004",
            "vlada_do": "25. 4. 2005",
            "koalice_kandidatka": ["ČSSD", "US", "K"],
            "opozice_kandidatka": ["ODS", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2005 vláda J. Paroubka",
            "vlada_od": "25. 4. 2005",
            "vlada_do": "4. 9. 2006",
            "koalice_kandidatka": ["ČSSD", "US", "K"],
            "opozice_kandidatka": ["ODS", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2006 první vláda M. Topolánka",
            "vlada_od": "4. 9. 2006",
            "vlada_do": "9. 1. 2007",
            "koalice_kandidatka": ["ODS"],
            "opozice_kandidatka": ["ČSSD", "KSČM", "KDU-ČSL", "SZ"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2007 druhá vláda M. Topolánka",
            "vlada_od": "9. 1. 2007",
            "vlada_do": "8. 5. 2009",
            "koalice_kandidatka": ["ODS", "KDU-ČSL", "SZ"],
            "opozice_kandidatka": ["ČSSD", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2009 vláda J. Fischera",
            "vlada_od": "8. 5. 2009",
            "vlada_do": "13. 7. 2010",
        },
        {
            "vlada": "2010 vláda P. Nečase",
            "vlada_od": "13. 7. 2010",
            "vlada_do": "10. 7. 2013",
            "koalice_kandidatka": ["ODS", "TOP09", "VV"],
            "opozice_kandidatka": ["ČSSD", "KSČM"],
            "koalice_navrhovatel": [],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2013 vláda J. Rusnoka",
            "vlada_od": "10. 7. 2013",
            "vlada_do": "29. 1. 2014",
        },
        {
            "vlada": "2014 vláda B. Sobotky",
            "vlada_od": "29. 1. 2014",
            "vlada_do": "13. 12. 2017",
            "koalice_kandidatka": ["ANO2011", "KDU-ČSL", "ČSSD"],
            "koalice_navrhovatel": [],
            "opozice_kandidatka": ["KSČM", "ODS", "TOP09", "Usvit"],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2017 první vláda A. Babiše",
            "vlada_od": "13. 12. 2017",
            "vlada_do": "27. 6. 2018",
            "koalice_kandidatka": ["ANO2011"],
            "koalice_navrhovatel": [],
            "opozice_kandidatka": [
                "ČSSD",
                "TOP09",
                "KDU-ČSL",
                "STAN",
                "Piráti",
                "ODS",
                "SPD",
                "KSČM",
            ],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2018 druhá vláda A. Babiše",
            "vlada_od": "27. 6. 2018",
            "vlada_do": "17. 12. 2021",
            "koalice_kandidatka": ["ČSSD", "ANO2011"],
            "koalice_navrhovatel": [],
            "opozice_kandidatka": [
                "TOP09",
                "KDU-ČSL",
                "STAN",
                "Piráti",
                "ODS",
                "SPD",
                "KSČM",
            ],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2021 vláda P. Fialy s Piráty",
            "vlada_od": "17. 12. 2021",
            "vlada_do": "30. 9. 2024",
            "koalice_kandidatka": ["SPOLU"],
            "koalice_navrhovatel": [
                "STAN",
                "ODS",
                "KDU-ČSL",
                "TOP09",
                "Piráti",
            ],
            "opozice_kandidatka": ["ANO2011", "SPD"],
            "opozice_navrhovatel": [],
        },
        {
            "vlada": "2024 vláda P. Fialy bez Pirátů",
            "vlada_od": "1. 10. 2024",
            "vlada_do": "30. 9. 2025",
            "koalice_kandidatka": ["SPOLU"],
            "koalice_navrhovatel": ["STAN", "ODS", "KDU-ČSL", "TOP09"],
            "opozice_kandidatka": ["ANO2011", "SPD"],
            "opozice_navrhovatel": ["Piráti"],
        },
    ]

    vlady = (
        pl.DataFrame(vlady, infer_schema_length=None)
        .with_columns(pl.col(["vlada_od", "vlada_do"]).str.to_date())
        .with_columns(
            pl.col(
                [
                    "koalice_kandidatka",
                    "koalice_navrhovatel",
                    "opozice_kandidatka",
                    "opozice_navrhovatel",
                ]
            ).list.join(separator="*")
        )
    )

    vlady = (
        vlady.group_by("vlada")
        .agg(
            pl.date_ranges(pl.col("vlada_od"), pl.col("vlada_do"), "1d").alias(
                "datum"
            )
        )
        .explode("datum")
        .join(vlady, how="left", on="vlada")
        .filter(~pl.col("koalice_kandidatka").is_null())
        .explode("datum")
    )

    vlady
    return (vlady,)


@app.cell
def _(lf, lf_mluvci, pl, vlady):
    df_vlady = (
        lf.join(lf_mluvci, on=["id", "obdobi"], how="left")
        .filter(pl.col("obdobi") >= 1996)
        .collect()
        .join(vlady, how="left", on="datum")
        .with_columns(
            pl.when(pl.col("mluvci_id").str.contains("vlada.cz"))
            .then(pl.lit("vláda"))
            .when(
                pl.col("koalice_kandidatka").str.contains(pl.col("kandidatka"))
                | pl.col("koalice_kandidatka").str.contains(
                    pl.col("navrhovatel")
                )
            )
            .then(pl.lit("vláda"))
            .when(
                pl.col("koalice_navrhovatel").str.contains(
                    pl.col("navrhovatel")
                )
                | pl.col("koalice_navrhovatel").str.contains(
                    pl.col("kandidatka")
                )
            )
            .then(pl.lit("vláda"))
            .when(
                pl.col("opozice_kandidatka").str.contains(pl.col("kandidatka"))
                | pl.col("opozice_kandidatka").str.contains(
                    pl.col("navrhovatel")
                )
            )
            .then(pl.lit("opozice"))
            .when(
                pl.col("opozice_navrhovatel").str.contains(
                    pl.col("navrhovatel")
                )
                | pl.col("opozice_navrhovatel").str.contains(
                    pl.col("kandidatka")
                )
            )
            .then(pl.lit("opozice"))
            .alias("vlada_opo")
        )
        .sort(by="datum")
    )
    return (df_vlady,)


@app.cell
def _(df_vlady, pl, vlady):
    vlady_opo_do_grafu = (
        df_vlady.with_columns(pl.col("text").str.count_matches(" "))
        .group_by(["vlada", "vlada_opo"])
        .agg(pl.col("text").sum())
        .sort(by=["vlada"])
        .pivot(index="vlada", on="vlada_opo")
        .with_columns(
            (
                pl.col("null")
                / (pl.col("null") + pl.col("vláda") + pl.col("opozice"))
            ).alias("podil_null")
        )
        .with_columns(
            (
                pl.col("opozice")
                / (pl.col("null") + pl.col("vláda") + pl.col("opozice"))
            ).alias("podíl_opozice")
        )
        .filter(pl.col("podil_null") < 0.05)
        .join(
            vlady.unique(subset="vlada", keep="first").select(
                pl.col(["vlada", "vlada_od", "vlada_do"])
            ),
            how="left",
            on="vlada",
        )
        .with_columns(pl.lit(0).alias("nula"))
    )

    vlady_opo_do_grafu.sample(1)
    return (vlady_opo_do_grafu,)


@app.cell
def _(alt, pl, uloz_graf, vlady_opo_do_grafu):
    slova_podil_opozice = (
        alt.Chart(
            vlady_opo_do_grafu.filter(pl.col("vlada_od").dt.year() >= 2010),
            title="Podíl opozice na rozsahu sněmovních projevů (2010-25)",
        )
        .mark_bar()
        .encode(
            alt.X("vlada_od:T"),
            alt.X2("vlada_do:T"),
            alt.Y(
                "nula:Q",
                axis=alt.Axis(
                    labelExpr="format(datum.value * 100, '.0f') + ' %'"
                ),
            ),
            alt.Y2("podíl_opozice:Q"),
            alt.Color(
                "vlada:N",
                legend=alt.Legend(title=None, orient="top", columns=2),
            ),
        )
    )

    uloz_graf(slova_podil_opozice)

    slova_podil_opozice
    return


@app.cell
def _(lf, pl):
    obdobi_snemoven = lf.group_by("obdobi").agg(
        pl.col("datum").min().alias("obdobi_od"),
        pl.col("datum").max().alias("obdobi_do"),
    )
    return (obdobi_snemoven,)


@app.cell
def _(obdobi_snemoven):
    obdobi_snemoven.collect()
    return


@app.cell
def _(lf, obdobi_snemoven, pl):
    podil_zen = (
        lf.filter(~pl.col("mluvci").is_null())
        .with_columns(
            pl.when(
                pl.col("mluvci").str.contains(r"ová[^\w]")
                | pl.col("mluvci").str.ends_with("á")
                | pl.col("mluvci").str.contains("oslankyně")
                | pl.col("mluvci").str.contains("sedkyně ")
            )
            .then(pl.lit("f"))
            .otherwise(pl.lit("m"))
            .alias("gender_naivni")
        )
        .group_by(["obdobi", "gender_naivni"])
        .agg(pl.col("pocet_slov").sum())
        .join(obdobi_snemoven, how="left", on="obdobi")
        .collect()
        .pivot(index="obdobi", on="gender_naivni")
        .with_columns(
            (
                pl.col("pocet_slov_f")
                / ((pl.col("pocet_slov_f")) + pl.col("pocet_slov_m"))
            ).alias("podil_zen")
        )
        .rename({"obdobi_od_m": "od", "obdobi_do_m": "do"})
        .with_columns(pl.lit(0).alias("nula"))
        .sort(by="obdobi")
    )

    podil_zen
    return (podil_zen,)


@app.cell
def _(alt, graf_rezimy, podil_zen, uloz_graf):
    slova_podil_zen = graf_rezimy + alt.Chart(
        podil_zen, title="Podíl žen na celkovém rozsahu sněmovních projevů"
    ).mark_bar().encode(
        alt.X("od:T"),
        alt.X2("do:T"),
        alt.Y(
            "nula:Q",
            axis=alt.Axis(labelExpr="format(datum.value * 100, '.0f') + ' %'"),
        ),
        alt.Y2(
            "podil_zen:Q",
        ),
    )

    uloz_graf(slova_podil_zen)

    slova_podil_zen
    return


@app.cell
def _(lf, pl):
    top_zeny = (
        lf.filter(~pl.col("mluvci").is_null())
        .with_columns(
            pl.when(
                pl.col("jmeno").str.contains(r"ová[^\w]")
                | pl.col("jmeno").str.ends_with("á")
                | pl.col("jmeno").str.contains("oslankyně")
                | pl.col("jmeno").str.contains("sedkyně ")
            )
            .then(pl.lit("f"))
            .otherwise(pl.lit("m"))
            .alias("gender_naivni")
        )
        .group_by("jmeno")
        .agg(pl.col("text").str.count_matches(" ").sum())
        .sort(by="text", descending=True)
        .collect()
    )

    top_zeny
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Slova-skokani
    """)
    return


@app.cell
def _(pl):
    def ocisti(liny_frejm):
        return liny_frejm.with_columns(
            pl.col("text")
            .str.replace_all(
                r"[^\w\s]",
                "",
            )
            .str.to_lowercase()
        )

    return (ocisti,)


@app.cell
def _(pl):
    def zgrupni_a_pores_cetnost(liny_frejm):

        frejm_pracovni = (
            liny_frejm.with_columns(pl.col("text").str.split(" "))
            .explode("text")
            .group_by("text")
            .len()
            .sort(by="len", descending=True)
        )
        celkem = frejm_pracovni.collect().select(pl.col("len")).sum().item()

        return liny_frejm.with_columns(
            (pl.col("len") / celkem).alias("podil")
        ).collect()

    return


@app.cell
def _(lf, ocisti, pl):
    ocisti(lf.filter(pl.col("obdobi") == 1918)).collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lex
    """)
    return


@app.cell
def _(re):
    def najdi_lexy(retezec):
        return [
            x.replace("lex", "Lex")
            .replace("Ukrajinu", "Ukrajina")
            .replace("Ukrajině", "Ukrajina")
            .replace("Ukrajinou", "Ukrajina")
            .replace("Ukrajiny", "Ukrajina")
            .replace("plynu", "plyn")
            for x in re.findall(r"[Ll]ex \w{1,20}-{0,1}\w{1,20}", retezec)
        ]

    return (najdi_lexy,)


@app.cell
def _(najdi_lexy):
    najdi_lexy("lex honza, Lex Blbec")
    return


@app.cell
def _(lf, najdi_lexy, pl):
    lexy = (
        lf.filter(pl.col("text").str.contains(r" [Ll]ex "))
        .with_columns(
            pl.col("text")
            .map_elements(najdi_lexy, return_dtype=pl.List(pl.String))
            .alias("lex")
        )
        .explode("lex", empty_as_null=True)
        .filter(pl.col("lex").is_not_null())
        .group_by("lex")
        .len()
        .sort(by="len", descending=True)
        .collect()
    )
    return (lexy,)


@app.cell
def _(lexy):
    lexy
    return


@app.cell
def _(lf, pl):
    lexy_pocet = (
        lf.filter(pl.col("text").str.contains(r" [Ll]ex "))
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .sort(by="datum")
        .collect()
    )
    return (lexy_pocet,)


@app.cell
def _(lexy_pocet):
    lexy_pocet.sort(by="len")
    return


@app.cell
def _(alt, graf_rezimy, lexy_pocet, uloz_graf):
    historie_lexu = graf_rezimy + alt.Chart(
        lexy_pocet, title="Počty poslaneckých projevů zmiňujících Lex něco"
    ).mark_bar(width=4).encode(alt.X("datum:T"), alt.Y("len:Q"))

    uloz_graf(historie_lexu)

    historie_lexu
    return


@app.cell
def _(alt, lexy, pl, uloz_graf):
    zebricek_lexu = (
        alt.Chart(lexy.head(12), title="Nejčastěji zmiňované Lexy něco")
        .mark_bar()
        .encode(
            alt.X("len:Q"),
            alt.Y(
                "lex:N", sort=lexy.select(pl.col("lex")).to_series().to_list()
            ),
        )
    )

    uloz_graf(zebricek_lexu)

    zebricek_lexu
    return


@app.cell
def _(lf, najdi_lexy, pl):
    lexy_mluvci = (
        lf.filter(pl.col("text").str.contains(r" [Ll]ex "))
        .with_columns(
            pl.col("text")
            .map_elements(najdi_lexy, return_dtype=pl.List(pl.String))
            .alias("lex")
        )
        .explode("lex", empty_as_null=True)
        .filter(pl.col("lex").is_not_null())
        .group_by("lex")
        .agg(pl.col("jmeno").unique().len(), pl.col("datum").unique().len())
        .sort(by="jmeno", descending=True)
        .collect()
    )
    return (lexy_mluvci,)


@app.cell
def _(lexy_mluvci, pl):
    lexy_mluvci.filter(pl.col("jmeno") == 1).sort(by="datum", descending=True)
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("lex lečo")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex Nacher")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex Metelk")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex Česká")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex dvojčata")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex korouhv")).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains("ex prima")).collect()
    return


@app.cell
def _(alt, lexy_mluvci, pl):
    alt.Chart(
        lexy_mluvci.filter(pl.col("jmeno") == 1).filter(pl.col("datum") > 1)
    )
    return


@app.cell
def _():
    ## Smích, potlesk, bučení
    return


@app.cell
def _(lf, pl):
    def zavorka(
        retezec,
        doslova=True,
        frejm=lf.drop_nulls(subset="datum"),
        epocha="datum",
        delka="1y",
    ):

        frejm = (
            frejm.with_columns(
                pl.col("mluvci")
                .str.split("(")
                .list.slice(1)
                .list.eval(pl.element().str.split(")").list.first())
                .list.eval(
                    pl.element().str.to_lowercase().str.strip_chars(),
                    parallel=True,
                )
                .alias("poznamky_mluvci")
            )
            .with_columns(
                pl.col("text")
                .str.split("(")
                .list.slice(1)
                .list.eval(pl.element().str.split(")").list.first())
                .list.eval(
                    pl.element().str.to_lowercase().str.strip_chars(),
                    parallel=True,
                )
                .alias("poznamky_text")
            )
            .with_columns(
                (
                    pl.col("komora").cast(str)
                    + pl.lit("-")
                    + pl.col("obdobi").cast(str)
                    + pl.lit("-")
                    + pl.col("schuze").cast(str)
                    + pl.lit("-")
                    + pl.col("cast").cast(str)
                    + pl.lit("-")
                    + pl.col("poradi").cast(str)
                ).alias("id")
            )
        )

        prislusne_projevy = (
            frejm.explode("poznamky_text")
            .explode("poznamky_mluvci")
            .filter(
                pl.col("poznamky_text").str.contains(retezec, literal=doslova)
                | pl.col("poznamky_mluvci").str.contains(
                    retezec, literal=doslova
                )
            )
            .sort(by="datum")
        )

        if epocha == "datum":
            projevu_celkem = (
                frejm.sort(by="datum")
                .group_by_dynamic(index_column="datum", every=delka)
                .agg(pl.col("id").len())
            )

            prislusne_projevy = prislusne_projevy.group_by_dynamic(
                index_column="datum", every=delka
            ).agg(pl.col("id").len())

        elif epocha == "obdobi":
            projevu_celkem = frejm.group_by("obdobi").agg(pl.col("id").len())
            prislusne_projevy = prislusne_projevy.group_by("obdobi").agg(
                pl.col("id").len()
            )

        return (
            prislusne_projevy.join(projevu_celkem, how="right", on=epocha)
            .with_columns((pl.col("id") / pl.col("id_right")).alias("podil"))
            .sort(by=epocha)
            .collect()
        )

    return (zavorka,)


@app.function
def obrat(cislo):
    if cislo >= 1:
        return cislo
    if cislo < 1:
        return -(1 / cislo)


@app.cell
def _(lf, pl):
    smich_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("smích")
            | pl.col("poznamky_text").str.contains("pobavení")
            | pl.col("poznamky_text").str.contains("veselí")
        )
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (smich_po_letech,)


@app.cell
def _(alt, graf_rezimy, smich_po_letech, uloz_graf):
    smich_kolikrat = graf_rezimy + alt.Chart(
        smich_po_letech,
        title="Kolikrát je v přepisech zachycen smích, pobavení a veselí",
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label,'','') + '×'",
            ),
        ),
    )

    uloz_graf(smich_kolikrat)

    smich_kolikrat
    return


@app.cell
def _(lf, pl):
    lf.with_columns(
        pl.col("text")
        .str.split("(")
        .list.slice(1)
        .list.eval(pl.element().str.split(")").list.first())
        .list.eval(
            pl.element().str.to_lowercase().str.strip_chars(),
            parallel=True,
        )
        .alias("poznamky_text")
    ).explode("poznamky_text").filter(
        pl.col("poznamky_text").str.contains("smích")
        | pl.col("poznamky_text").str.contains("pobavení")
        | pl.col("poznamky_text").str.contains("veselí")
    ).filter(pl.col("datum").dt.year().is_between(1947, 1960)).collect()
    return


@app.cell
def _():
    return


@app.cell
def _(lf, pl):
    zebricek_smichu25 = (
        lf.with_columns(
            pl.col("mluvci")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_mluvci")
        )
        .with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .filter(pl.col("obdobi") == 2025)
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("smích")
            | pl.col("poznamky_text").str.contains("pobavení")
            | pl.col("poznamky_text").str.contains("veselí")
        )
        .group_by("jmeno")
        .len()
        .join(
            lf.filter(pl.col("obdobi") == 2025)
            .with_columns(pl.col("text").str.count_matches(" "))
            .group_by("jmeno")
            .agg(pl.col("text").sum().alias("slov_celkem")),
            how="left",
            on="jmeno",
        )
        .with_columns((pl.col("slov_celkem") / pl.col("len")).alias("r"))
        .sort(by="len", descending=True)
        .collect()
    )

    zebricek_smichu25
    return (zebricek_smichu25,)


@app.cell
def _(alt, pl, uloz_graf, zebricek_smichu25):
    graf_zebricek_smichu_25 = (
        alt.Chart(
            zebricek_smichu25.head(10),
            title=alt.Title(
                "Kdo nejvíckrát rozesmál současnou Sněmovnu",
                subtitle=["", "Hledáme smích, pobavení a veselí."],
            ),
        )
        .mark_bar()
        .encode(
            alt.Y(
                "jmeno:N",
                sort=zebricek_smichu25.head(10)
                .select(pl.col("jmeno"))
                .to_series()
                .to_list(),
            ),
            alt.X(
                "len:Q",
                axis=alt.Axis(
                    labelExpr="replace(datum.label,'','') + '×'", tickCount=5
                ),
            ),
        )
    )

    uloz_graf(graf_zebricek_smichu_25)

    graf_zebricek_smichu_25
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("jmeno") == "Michael Canov").filter(
        pl.col("obdobi") == 2025
    ).collect()
    return


@app.cell
def _():
    return


@app.cell
def _(alt, pl, uloz_graf, zebricek_smichu25):
    graf_zebricek_smichu_25r = (
        alt.Chart(
            zebricek_smichu25.filter(
                ~pl.col("jmeno").is_in(["Richard Brabec", "Michael Canov"])
            )
            .sort(by="r", descending=False)
            .head(10),
            title=alt.Title(
                "Největší šprýmařstvo současné Sněmovny",
                subtitle=["", "Počet pronesených slov na jeden smích v sále."],
            ),
        )
        .mark_bar()
        .encode(
            alt.Y(
                "jmeno:N",
                sort=zebricek_smichu25.sort(by="r", descending=False)
                .head(10)
                .select(pl.col("jmeno"))
                .to_series()
                .to_list(),
            ),
            alt.X("r:Q", axis=alt.Axis(tickCount=5)),
        )
    )

    uloz_graf(graf_zebricek_smichu_25r)

    graf_zebricek_smichu_25r
    return


@app.cell
def _(lf, pl):
    potlesk_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("tlesk")
            | pl.col("poznamky_text").str.contains("aplaus")
        )
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (potlesk_po_letech,)


@app.cell
def _(alt, graf_rezimy, potlesk_po_letech, uloz_graf):
    potlesk_aplaus = graf_rezimy + alt.Chart(
        potlesk_po_letech, title="Kolikrát se v sále tleskalo a aplaudovalo"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    uloz_graf(potlesk_aplaus)

    potlesk_aplaus
    return


@app.cell
def _(pl, zavorka):
    pravolevo = (
        zavorka(
            "(potlesk zleva|potlesk na levici|potlesk z levé|potlesk vlevo)",
            doslova=False,
            delka="3mo",
        )
        .with_columns(pl.col("podil").alias("zleva"))
        .select(pl.col(["datum", "zleva"]))
        .join(
            zavorka(
                "(potlesk zprava|potlesk na pravici|potlesk z pravé|potlesk vpravo)",
                doslova=False,
                delka="3mo",
            )
            .with_columns(pl.col("podil").alias("zprava"))
            .select(pl.col(["datum", "zprava"])),
            on="datum",
            how="full",
        )
        .with_columns(
            (pl.col("zprava") / pl.col("zleva"))
            .map_elements(obrat, return_dtype=pl.Float64)
            .alias("pravo-levo")
        )
        .filter(pl.col("datum").dt.year() >= 1993)
        .with_columns(
            pl.when(pl.col("datum") >= pl.date(2025, 10, 1))
            .then(pl.lit("současná"))
            .otherwise(pl.lit("předchozí"))
            .alias("ktera_snemovna")
        )
    )

    pravolevo.drop_nulls().sort(by="pravo-levo")
    return (pravolevo,)


@app.cell
def _():
    return


@app.cell
def _(alt, pravolevo, uloz_graf):
    graf_pravolevo = (
        alt.Chart(
            pravolevo.to_pandas(),
            title=alt.Title(
                "Odkud zní ve Sněmovně potlesk",
                subtitle=[
                    "⠀",
                    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀← častěji se tleská zleva ~ častěji se tleská zprava →",
                ],
            ),
        )
        .mark_bar(height=2.5)
        .encode(
            alt.Y("datum:T", axis=alt.Axis(title=None, tickCount=10)),
            alt.X(
                "pravo-levo:Q",
                scale=alt.Scale(domain=[-45, 45]),
                axis=alt.Axis(
                    title="← častěji se tleská zleva ~ častěji se tleská zprava →",
                    titleAlign="right",
                    titleX=270,
                    tickCount=7,
                    orient="top",
                    labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'",
                ),
            ),
            alt.Color(
                "ktera_snemovna:N",
                legend=alt.Legend(
                    title=None,
                    direction="horizontal",
                    orient="top",
                ),
            ),
        )
        .configure_axisX(grid=True, domain=False)
        .configure_axisY(grid=True, domain=False)
        .configure_view(stroke="transparent")
        .resolve_axis(x="independent", y="independent")
        .resolve_scale(y="shared")
    )

    uloz_graf(graf_pravolevo)

    graf_pravolevo
    return


@app.cell
def _(lf, pl):
    slava_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(pl.col("poznamky_text").str.contains("sláva"))
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (slava_po_letech,)


@app.cell
def _(alt, graf_rezimy, slava_po_letech):
    slava = graf_rezimy + alt.Chart(
        slava_po_letech, title="Kolikrát zaznělo v sále „sláva!“"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    slava
    return


@app.cell
def _(lf, pl):
    at_zije_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(pl.col("poznamky_text").str.contains("ať žij"))
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )

    at_zije_po_letech.sort(by="len", descending=True)
    return (at_zije_po_letech,)


@app.cell
def _(alt, at_zije_po_letech, graf_rezimy, uloz_graf):
    at_zije = graf_rezimy + alt.Chart(
        at_zije_po_letech, title="Kolikrát zaznělo v sále „ať žije/í!“"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    uloz_graf(at_zije)

    at_zije
    return


@app.cell
def _(lf, pl):
    lf.with_columns(
        pl.col("text")
        .str.split("(")
        .list.slice(1)
        .list.eval(pl.element().str.split(")").list.first())
        .list.eval(
            pl.element().str.to_lowercase().str.strip_chars(),
            parallel=True,
        )
        .alias("poznamky_text")
    ).explode("poznamky_text").filter(
        pl.col("poznamky_text").str.contains("ať žij")
    ).drop_nulls("datum").sort(by="datum").tail(3).collect()
    return


@app.cell
def _(lf, pl):
    hanba_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("hanba")
            | pl.col("poznamky_text").str.contains("ostuda")
        )
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (hanba_po_letech,)


@app.cell
def _(alt, graf_rezimy, hanba_po_letech, uloz_graf):
    hanba_ostuda = graf_rezimy + alt.Chart(
        hanba_po_letech, title="Kolikrát zaznělo v sále „hanba“ nebo „ostuda“"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    uloz_graf(hanba_ostuda)

    hanba_ostuda
    return


@app.cell
def _(lf, pl):
    krik_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("křik")
            | pl.col("poznamky_text").str.contains("hluk")
            | pl.col("poznamky_text").str.contains("rámus")
        )
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (krik_po_letech,)


@app.cell
def _(alt, graf_rezimy, krik_po_letech, uloz_graf):
    krik = graf_rezimy + alt.Chart(
        krik_po_letech, title="Kolikrát byl v sále hluk, křik či rámus"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    uloz_graf(krik)

    krik
    return


@app.cell
def _(lf, pl):
    buceni_po_letech = (
        lf.with_columns(
            pl.col("text")
            .str.split("(")
            .list.slice(1)
            .list.eval(pl.element().str.split(")").list.first())
            .list.eval(
                pl.element().str.to_lowercase().str.strip_chars(),
                parallel=True,
            )
            .alias("poznamky_text")
        )
        .explode("poznamky_text")
        .filter(
            pl.col("poznamky_text").str.contains("bučení")
            | pl.col("poznamky_text").str.contains("bučí")
        )
        .drop_nulls("datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .len()
        .collect()
    )
    return (buceni_po_letech,)


@app.cell
def _(buceni_po_letech):
    buceni_po_letech
    return


@app.cell
def _(alt, buceni_po_letech, graf_rezimy, uloz_graf):
    buceni = graf_rezimy + alt.Chart(
        buceni_po_letech, title="Kolikrát se v sále bučelo"
    ).mark_bar(width=4).encode(
        alt.X("datum:T"),
        alt.Y(
            "len:Q",
            axis=alt.Axis(
                labelExpr="replace(datum.label, regexp('(\d),(?=\d{3})', 'g'), '$1 ') + '×'"
            ),
        ),
    )

    uloz_graf(buceni)

    buceni
    return


@app.cell
def _(lf, pl):
    lf.with_columns(
        pl.col("text")
        .str.split("(")
        .list.slice(1)
        .list.eval(pl.element().str.split(")").list.first())
        .list.eval(
            pl.element().str.to_lowercase().str.strip_chars(),
            parallel=True,
        )
        .alias("poznamky_text")
    ).explode("poznamky_text").filter(
        pl.col("poznamky_text").str.contains("bučení")
        | pl.col("poznamky_text").str.contains("bučí")
    ).sort(by="datum").collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dlouhověkkost
    """)
    return


@app.cell
def _(lf, pl):
    porevolucni = (
        lf.filter(pl.col("datum").dt.year() >= 1990)
        .select(pl.col("jmeno"))
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return (porevolucni,)


@app.cell
def _(lf, pl):
    lf.group_by("jmeno").agg(pl.col("datum").min().alias("od")).join(
        lf.group_by("jmeno").agg(pl.col("datum").max().alias("do")),
        how="left",
        on="jmeno",
    ).with_columns((pl.col("do") - pl.col("od")).alias("t")).sort(
        by="t", descending=True
    ).collect()
    return


@app.cell
def _(lf, pl):
    lf.select(pl.col("komora")).unique().collect().to_series().to_list()
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("komora") == "uns").select(
        pl.col("komora_komplet")
    ).unique().collect().to_series().to_list()
    return


@app.cell
def _(lf, pl):
    benduv_start = (
        lf.filter(pl.col("jmeno") == "Marek Benda")
        .select(pl.col("datum"))
        .min()
        .collect()
        .item()
    )
    benduv_start
    return (benduv_start,)


@app.cell
def _(lf, pl):
    bendovy_komory = (
        lf.filter(pl.col("jmeno") == "Marek Benda")
        .select(pl.col("komora_komplet"))
        .unique()
        .collect()
        .to_series()
        .to_list()
    )

    bendovy_komory
    return (bendovy_komory,)


@app.cell
def _(lf, pl, porevolucni):
    lf.filter(pl.col("datum").dt.year() >= 1990).filter(
        pl.col("jmeno").is_in(porevolucni)
    ).group_by("jmeno").agg(pl.col("datum").min().alias("od")).join(
        lf.group_by("jmeno").agg(pl.col("datum").max().alias("do")),
        how="left",
        on="jmeno",
    ).with_columns((pl.col("do") - pl.col("od")).alias("t")).sort(
        by="t", descending=True
    ).collect()
    return


@app.cell
def _(bendovy_komory, benduv_start, lf, pl):
    lf.filter(pl.col("datum") >= benduv_start).filter(
        pl.col("komora_komplet").is_in(bendovy_komory)
    ).filter(
        ~pl.col("jmeno").str.contains_any(
            ["bez mučení", "Návrh zní", "hlasování", "z místa"]
        )
    ).select(pl.col("jmeno")).unique().collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Minulost-budoucnost
    """)
    return


@app.cell
def _(re):
    def vroce(retezec):
        roky = []
        fraze = [
            r"[Rr]ok \d{2,4}(?!\sKč|\skorun)",
            r"[Vv] roce \d{2,4}(?!\sKč|\skorun)",
            r"[Rr]oku \d{2,4}(?!\sKč|\skorun)",
            r"[Rr]okem \d{2,4}(?!\sKč|\skorun)",
        ]
        for f in fraze:
            nalezy = re.findall(f, retezec)
            pridej = [int(re.search(r"\d{2,4}", x).group()) for x in nalezy]
            pridej = [
                int(f"19{x}")
                if 18 <= x < 100
                else int(f"20{x}")
                if x < 17
                else x
                for x in pridej
            ]
            roky += pridej

        roky = [x for x in roky if 1300 < x < 2500]
        roky.sort()
        return roky

    return (vroce,)


@app.cell
def _(lf, pl, vroce):
    vyvoj_let = (
        lf.drop_nulls(subset=["datum"])
        .with_columns(
            pl.col("text")
            .map_elements(vroce, return_dtype=pl.List(pl.Int32))
            .alias("roky")
        )
        .explode("roky")
        .with_columns(
            (pl.col("roky") - pl.col("datum").dt.year()).alias("rozdil")
        )
        .filter(pl.col("rozdil").is_between(-100, 100))
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("rozdil").mean())
    ).collect()
    return (vyvoj_let,)


@app.cell
def _(lf, pl, vroce):
    vyvoj_let_all = (
        lf.drop_nulls(subset=["datum"])
        .with_columns(
            pl.col("text")
            .map_elements(vroce, return_dtype=pl.List(pl.Int32))
            .alias("roky")
        )
        .explode("roky")
        .with_columns(
            (pl.col("roky") - pl.col("datum").dt.year()).alias("rozdil")
        )
        .filter(pl.col("rozdil").is_between(-100, 100))
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("rozdil"))
    ).collect()
    return (vyvoj_let_all,)


@app.cell
def _(vyvoj_let_all):
    vyvoj_let_all_grupnuto = (
        vyvoj_let_all.explode("rozdil").group_by(["datum", "rozdil"]).len()
    )
    vyvoj_let_all_grupnuto
    return (vyvoj_let_all_grupnuto,)


@app.cell
def _(alt, graf_rezimy, pl, uloz_graf, vyvoj_let_all_grupnuto):
    letopocty_vsechny = graf_rezimy + alt.Chart(
        vyvoj_let_all_grupnuto.filter(pl.col("len") >= 3),
        title=alt.Title(
            [
                "Rozdíly mezi aktuálním letopočtem",
                "a letopočty zmíněnými v projevech",
            ],
            subtitle=[
                "",
                "Nahoru = zmíněný letopočet je v budoucnosti,",
                "dolů = zmíněný letopočet je v minulosti",
            ],
        ),
    ).mark_point(filled=True).encode(
        alt.X("datum:T"),
        alt.Y(
            "rozdil:Q",
            axis=alt.Axis(
                # title="dolů = minulost, nahoru = budoucnost",
                # titleOpacity=1,
                labelExpr="datum.label + ' let'",
            ),
        ),
        alt.Size("len:Q", legend=None),
    )

    uloz_graf(letopocty_vsechny)

    letopocty_vsechny
    return


@app.cell
def _(alt, graf_rezimy, uloz_graf, vyvoj_let):
    prumerny_letopocet = graf_rezimy + alt.Chart(
        vyvoj_let,
        title=alt.Title(
            [
                "Průměrný rozdíl mezi aktuálním letopočtem",
                "a letopočty zmíněnými v projevech",
            ],
        ),
    ).mark_bar(width=4).encode(
        alt.X("datum:T", axis=alt.Axis(title=None)),
        alt.Y(
            "rozdil:Q",
            axis=alt.Axis(
                title=None,
                labelExpr="datum.label + ' let'",
            ),
        ),
    )

    uloz_graf(prumerny_letopocet)

    prumerny_letopocet
    return


@app.cell
def _(lf, pl, vroce):
    lf.drop_nulls(subset=["datum"]).with_columns(
        pl.col("text")
        .map_elements(vroce, return_dtype=pl.List(pl.Int32))
        .alias("roky")
    ).explode("roky").filter(pl.col("roky") == 2000).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(r"(?i)(roce 2000|roku 2000|rok 2000)")
    ).sort(by="datum").drop_nulls(subset="datum").group_by_dynamic(
        index_column="datum", every="1y"
    ).len().collect()
    return


@app.cell
def _(alt, graf_rezimy, lf, pl, uloz_graf):
    y2k = graf_rezimy + alt.Chart(
        lf.filter(
            pl.col("text").str.contains(r"(?i)(roce 2000|roku 2000|rok 2000)")
        )
        .sort(by="datum")
        .drop_nulls(subset="datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("text").unique().len())
        .collect(),
        title="Zmínky o roce 2000 v poslaneckých projevech",
    ).mark_bar(width=4).encode(alt.X("datum:T"), alt.Y("text:Q"))

    uloz_graf(y2k)

    y2k
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(r"(?i)(roce 2000|roku 2000|rok 2000)")
    ).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(
            r"(?i)(roce 2026|roku 2026|rok 2026|rokem 2026)"
        )
    ).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(
            r"(?i)(roce 2030|roku 2030|rok 2030|rokem 2030)"
        )
    ).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(
            r"(?i)(roce 2050|roku 2050|rok 2050|rokem 2050)"
        )
    ).collect()
    return


@app.cell
def _(lf, pl):
    lf.filter(
        pl.col("text").str.contains(
            r"(?i)(roce 2100|roku 2100|rok 2100|rokem 2100)"
        )
    ).collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Témata
    """)
    return


@app.cell
def _(lf, pl):
    celkem_slov = (
        lf.with_columns(pl.col("text").str.count_matches(" ").alias("slov"))
        .sort(by="datum")
        .drop_nulls(subset="datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("slov").sum())
    )

    celkem_slov.collect()
    return (celkem_slov,)


@app.cell
def _(lf, pl):
    def hledej(slovo):
        return lf.filter(pl.col("text").str.contains(slovo)).collect()

    return


@app.cell
def _(celkem_slov, lf, pl):
    def hledej_a_zgrupni(slovo):
        return (
            lf.filter(pl.col("text").str.contains(slovo))
            .sort(by="datum")
            .drop_nulls(subset="datum")
            .group_by_dynamic(index_column="datum", every="1y")
            .len()
            .join(celkem_slov, how="left", on="datum")
            .with_columns((pl.col("len") / pl.col("slov")).alias("r"))
            .collect()
        )

    return (hledej_a_zgrupni,)


@app.cell
def _(hledej_a_zgrupni):
    elektrina = hledej_a_zgrupni(r"(?i)[^\w]elekt[řr]")
    return (elektrina,)


@app.cell
def _(alt, elektrina):
    alt.Chart(elektrina).mark_bar(size=4).encode(
        alt.X("datum:T"), alt.Y("r:Q")
    )
    return


@app.cell
def _(hledej_a_zgrupni):
    menstruace = hledej_a_zgrupni(r"(?i)(menstru|měsíčk)")
    return (menstruace,)


@app.cell
def _(alt, menstruace):
    alt.Chart(menstruace).mark_bar(size=4).encode(
        alt.X("datum:T"), alt.Y("r:Q")
    )
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains(r"(?i)menstru")).collect()
    return


@app.cell
def _(hledej_a_zgrupni):
    jihlava = hledej_a_zgrupni(r"(?i)jihlav")
    return (jihlava,)


@app.cell
def _(alt, jihlava):
    alt.Chart(jihlava).mark_bar(size=4).encode(alt.X("datum:T"), alt.Y("r:Q"))
    return


@app.cell
def _(hledej_a_zgrupni):
    ai = hledej_a_zgrupni(r"(?i)uměl(á|ou|é) intelig")
    return (ai,)


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains(r"(?i)uměl(á|ou|é) intelig")).collect()
    return


@app.cell
def _(ai, alt):
    alt.Chart(ai).mark_bar(size=4).encode(alt.X("datum:T"), alt.Y("r:Q"))
    return


if __name__ == "__main__":
    app.run()
