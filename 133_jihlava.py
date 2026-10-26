import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt
    import re
    import simplemma

    return alt, mo, pl, re


@app.cell
def _(pl):
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
                    "titleFontSize": 0,
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Odkdy dokdy
    """)
    return


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).drop_nulls(subset="datum").sort(
        by="datum"
    ).head(10).collect()
    return


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).drop_nulls(subset="datum").sort(
        by="datum", descending=True
    ).head(10).collect()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kolik tam toho je
    """)
    return


@app.cell
def _(lf, pl, zajima):
    rozsah_ve_znacich = (
        lf.filter(pl.col("komora").is_in(zajima))
        .with_columns(pl.col("text").str.len_chars())
        .select(pl.col("text").sum())
        .collect()
        .item()
    )

    print(rozsah_ve_znacich)

    print(rozsah_ve_znacich / 1800)
    return


@app.cell
def _(lf, pl, zajima):
    stats_slova = (
        lf.filter(pl.col("komora").is_in(zajima))
        .drop_nulls(subset="datum")
        .group_by_dynamic(index_column="datum", every="1y")
        .agg(pl.col("text").str.split(" ").list.len().sum())
        .collect()
    )
    return (stats_slova,)


@app.cell
def _(alt, stats_slova):
    slova = (
        alt.Chart(
            stats_slova,
            title="Počty slov pronesených v dolních komorách českého parlamentu",
        )
        .mark_bar(width=4)
        .encode(alt.X("datum:T"), alt.Y("text:Q"))
    )

    slova.save("grafy/jihlava_slova.svg")

    slova
    return


@app.cell
def _(alt, pl, stats_slova):
    slova_babicka = (
        alt.Chart(
            stats_slova.with_columns(pl.col("text") / 67169),
            title=["Kolik celých románů Babička bylo ve sněmovnách proneseno"],
        )
        .mark_bar(width=4)
        .encode(alt.X("datum:T"), alt.Y("text:Q"))
    )

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
def _(alt, pl, zebricek):
    alt.Chart(
        zebricek.filter(pl.col("text") > 1000000),
        title=f"Poslanci a poslankyně, kteří pronesli víc než milion slov",
    ).mark_bar().encode(
        alt.Y(
            "jmeno:N",
            sort=zebricek.head(10)
            .select(pl.col("jmeno"))
            .to_series()
            .to_list(),
        ),
        alt.X("text:Q", axis=alt.Axis(tickCount=3)),
    )
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
def _(alt, pl, vlady_opo_do_grafu):
    alt.Chart(
        vlady_opo_do_grafu.filter(pl.col("vlada_od").dt.year() >= 2010),
        title="Podíl opozice na rozsahu sněmovních projevů (2010-25)",
    ).mark_bar().encode(
        alt.X("vlada_od:T"),
        alt.X2("vlada_do:T"),
        alt.Y(
            "nula:Q",
            axis=alt.Axis(labelExpr="format(datum.value * 100, '.0f') + ' %'"),
        ),
        alt.Y2("podíl_opozice:Q"),
        alt.Color(
            "vlada:N", legend=alt.Legend(title=None, orient="top", columns=2)
        ),
    )
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
def _(alt, podil_zen):
    alt.Chart(
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
def _(alt, lexy_pocet):
    alt.Chart(
        lexy_pocet, title="Počty poslaneckých projevů zmiňujících Lex něco"
    ).mark_bar().encode(alt.X("datum:T"), alt.Y("len:Q"))
    return


@app.cell
def _(alt, lexy, pl):
    alt.Chart(
        lexy.head(12), title="Nejčastěji zmiňované Lexy něco"
    ).mark_bar().encode(
        alt.X("len:Q"),
        alt.Y("lex:N", sort=lexy.select(pl.col("lex")).to_series().to_list()),
    )
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


@app.cell(hide_code=True)
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
def _(alt, pravolevo):
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
                    orient="top",
                    labelExpr="replace(datum.label, '−', '') + '×'",
                ),
            ),
            alt.Color(
                "ktera_snemovna:N",
                legend=alt.Legend(
                    title=None,
                    direction="horizontal",
                    orient="top",
                ),
                scale=alt.Scale(range=["#6B8EAA", "#D55F50"]),
            ),
        )
        .configure_axisX(grid=True, domain=False)
        .configure_axisY(grid=True, domain=False)
        .configure_view(stroke="transparent")
        .resolve_axis(x="independent", y="independent")
        .resolve_scale(y="shared")
    )

    graf_pravolevo
    return


if __name__ == "__main__":
    app.run()
