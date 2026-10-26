import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    import altair as alt
    import marimo as mo
    import re

    return alt, mo, pl, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Co mi přijde zajímavý

    - slovy klasika|řečeno s klasikem
    - citování knih druhých poslanců

    ## Různé výpočty:
    """)
    return


@app.cell
def _(pl):
    lf = pl.scan_parquet(
        "data/*.parquet",
        hidden_file_prefix=["projevy", "mluvci"],
        missing_columns="insert",
    ).with_columns(
        pl.col("mluvci").str.split(" ").list.slice(-2, 2).list.join(" ").alias("jmeno")
    )
    return (lf,)


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
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"Kar\w{1,5} Čap[ek]")
    ).collect()
    return


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"Milan\w{0,5} Kunder")
    ).collect()
    return


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"(?i)orwell")
    ).collect()
    return


@app.cell
def _(lf, pl, zajima):
    def po_letech_abs(dotaz):
        return (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .group_by(pl.col("datum").dt.year())
            .len()
            .sort(by="datum")
            .collect()
            .join(
                pl.DataFrame({"datum": range(1918, 2026)}, schema={"datum": pl.Int32}),
                how="right",
                on="datum",
            )
            .fill_null(0)
        )

    return


@app.cell
def _(lf, pl, zajima):
    def po_letech(dotaz):
        return (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .group_by(pl.col("datum").dt.year())
            .len()
            .join(
                lf.group_by(pl.col("datum").dt.year()).len(),
                how="right",
                on="datum",
            )
            .sort(by="datum")
            .with_columns((pl.col("len") / pl.col("len_right")).alias("r"))
            .filter(pl.col("datum") >= 1918)
            .collect()
            .fill_null(0)
        )

    return (po_letech,)


@app.cell
def _(po_letech):
    po_letech(r"Václ\w{0,5} Hav[el]")
    return


@app.cell
def _(alt, pl, po_letech):
    def graf(co_hledame):
        frejm = po_letech(co_hledame)
        print(f"n={frejm.select(pl.col('len').sum()).item()}")
        return (
            alt.Chart(frejm, title=co_hledame, height=100, width=900)
            .mark_bar()
            .encode(alt.X("datum:Q"), alt.Y("r:Q"))
        )

    return (graf,)


@app.cell
def _(graf):
    graf("(?i)orwell")
    return


@app.cell
def _(graf):
    graf("(?i)velk.{1,10} bratr")
    return


@app.cell
def _(vyzobni):
    vyzobni("(?i)velk.{1,10} bratr")
    return


@app.cell
def _(vyzobni):
    vyzobni("Velk.{1,10} bratr")
    return


@app.cell
def _(vyzobni):
    vyzobni("Orwell")
    return


@app.cell
def _(vyzobni):
    vyzobni("(?i) válka je mír")
    return


@app.cell
def _(graf):
    graf("(?i)Huxley")
    return


@app.cell
def _(graf):
    graf(r"(?i)Vál\w{2,5} s [mM]lok")
    return


@app.cell
def _(graf):
    graf(r"(?i)Továr\w{2,5} na absolutno")
    return


@app.cell
def _(graf):
    graf(r"RUR")
    return


@app.cell
def _(graf):
    graf("R.U.R.")
    return


@app.cell
def _(graf):
    graf(r"Mar(x|xe|xovi|xův|xem)[^\w]")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Mar(x|xe|xovi|xův|xem)[^\w]", nove=True)
    return


@app.cell
def _(graf):
    graf("(?i)hokej")
    return


@app.cell
def _(graf):
    graf(r"Kar\w{1,5} Čap[ek]")
    return


@app.cell
def _(graf):
    graf(r"Milan\w{0,5} Kunder")
    return


@app.cell
def _(graf):
    graf(r"Václ\w{0,5} Hav[el]")
    return


@app.cell
def _(graf):
    graf(r"(?i)bibl")
    return


@app.cell
def _(graf):
    graf(r"(?i)v básni")
    return


@app.cell
def _(graf):
    graf(r"(?i)jak se píše v")
    return


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains(r"Václ\w{0,5} Hav[el]")).sort(
        by="datum"
    ).drop_nulls(subset="datum").collect()
    return


@app.cell
def _(lf, pl, zajima):
    def cele_projevy(dotaz, n=3):
        for radek in (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .sort(by="datum")
            .head(n)
            .collect()
            .iter_rows(named=True)
        ):
            print(f"{radek['mluvci']} {radek['datum']}")
            print(radek["text"])
            print("***")

    return (cele_projevy,)


@app.cell
def _(cele_projevy):
    cele_projevy(r"Václ\w{0,5} Hav[el]")
    return


@app.cell
def _(cele_projevy):
    cele_projevy(r"Milan\w{0,5} Kunder")
    return


@app.cell
def _(cele_projevy):
    cele_projevy(r"Božen\w{0,5} Němcov")
    return


@app.cell
def _(graf):
    graf(r"Božen\w{0,5} Němcov")
    return


@app.cell
def _(graf):
    graf(r"J[uú]li\w{0,5} Fučík")
    return


@app.cell
def _(graf):
    graf(r"Čtyři dohody")
    return


@app.cell
def _(graf):
    graf(r"Měl jsem psa")
    return


@app.cell
def _(graf):
    graf(r"Švejk")
    return


@app.cell
def _(graf):
    graf(r"Dostojev")
    return


@app.cell
def _(graf):
    graf(r"Čechov")
    return


@app.cell
def _(graf):
    graf(r"Tolst")
    return


@app.cell
def _(graf):
    graf(r"Jaros\w{1,5} Haš")
    return


@app.cell
def _(graf):
    graf(r"P")
    return


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"Rowlingov")
    return


@app.cell
def _(graf):
    graf(r"(?i)kafkovsk")
    return


@app.cell
def _(graf):
    graf(r"(?i)haškovsk")
    return


@app.cell
def _(graf):
    graf(r"(?i)k[aá]m[aá]s[ůúu]")
    return


@app.cell
def _(graf):
    graf("Ayn Rand")
    return


@app.cell
def _(graf):
    graf("Nietzch")
    return


@app.cell
def _(graf):
    graf(r"Mein Kampf")
    return


@app.cell
def _(cele_projevy):
    cele_projevy(r"(?i)kafkovsk")
    return


@app.cell
def _(graf):
    graf(r"(?i)kašpár")
    return


@app.cell
def _(graf):
    graf(r"(?i)Fran\w{1,5} Kafk")
    return


@app.cell
def _(graf):
    graf(r"(?i)Jan\w{0,3} Skácel")
    return


@app.cell
def _(graf):
    graf(r"(?i)Jarosl\w{0,5} Seifert")
    return


@app.cell
def _(graf):
    graf(r"(?i)Kar[el]\w{0,5} Kryl")
    return


@app.cell
def _(graf):
    graf(r"(?i)Coelh")
    return


@app.cell
def _(graf):
    graf(r"(?i)Kar[el]\w{0,5} Kryl")
    return


@app.cell
def _(graf):
    graf(r"(?i)sionských mudrc")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)sionských mudrc")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Mein Kampf")
    return


@app.cell
def _(alt, graf):
    alt.vconcat(graf(r"Korán"), graf(r"Bibl(e|í|i[^\w])")).resolve_scale(y="shared")
    return


@app.cell
def _(graf):
    graf(r"Däniken")
    return


@app.cell
def _(graf):
    graf(r"Jáchy\w{0,10} Topol")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Obecné fráze
    """)
    return


@app.cell
def _(lf, pl):
    def vyzobni(hledani, nove=False):
        return (
            lf.filter(pl.col("text").str.contains(hledani))
            .with_columns(
                pl.col("text")
                .str.replace_all(hledani, "\u0000")  # sentinel delimiter
                .str.split("\u0000")
                .list.slice(0, 1)
                .list.join(" ")
                .str.strip_chars()
                .str.slice(-30, 30)
                .alias("pred"),
                pl.col("text")
                .str.replace_all(hledani, "\u0000")  # sentinel delimiter
                .str.split("\u0000")
                .list.slice(1, 1)
                .list.join(" ")
                .str.strip_chars()
                .alias("po"),
            )
            .select(pl.col(["mluvci", "datum", "pred", "po", "jmeno"]))
            .sort(by="datum", descending=nove)
            .collect()
        )

    return (vyzobni,)


@app.cell
def _(vyzobni):
    vyzobni(r"román")
    return


@app.cell
def _():
    testy_jmen = [
        "a politolog Milan Znoj v deníku Právo ze dne 14. prosince 2010 v článku nazvaném Zase ten správný obraz, kde píše: Chystaný zákon ani tolik nehodlá pomáhat obětem, jako hodlá vytvářet ten správný obraz o komunistické době a za tímto účelem umožňuje konstruovat protikomunistický odboj. Zákon by tak vytvářel novou podobu let 1948 až 1989. Ne však takovou, jakou skutečně ona léta byla. O výkladu doby minulé by nakonec rozhodoval Ústav pro studium totalitních režimů, Archiv bezpečnostních složek a Ministerstvo obrany na základě interpretace zde předloženého návrhu zákona. Chci zde na tomto místě upozornit, popřípadě vznést dotazy na to, co je vlastně skutečným cílem předloženého návrhu zákona o údajném třetím odboji. Nejde v první řadě o přepisování minulosti a o zkreslení let 1948 až 1989? Není dalším cílem zvýraznit postavení Ústavu pro studium totalitních režimů? Jeho důležitost, podstata a nenahraditelnost v dalším období? Případná nová vláda si totiž po legitimizování tohoto návrhu zákona nebude moci Ústav pro studium totalitních režimů dovolit zrušit, protože by to mohlo být posuzováno jako neúcta k veteránům údajného třetího odboje. Ústav pro studium totalitních režimů společně s Archivem bezpečnostních složek a Ministerstvem obrany tak bude vytvářet nový pohled na minulost. Vznikne tak vlastně arbitr složený ze tří institucí a ten bude určovat správný obraz o letech 1948 až 1989. Není proto divu, že proti návrhu zákona o tzv. protikomunistickém odboji jsou historici, filozofové i mnozí další akademičtí a vědečtí pracovníci. Kromě toho zcela logicky tento návrh zákona rozděluje i veřejnost. V neposlední řadě jsou proti také někteří z historiků samotného Ústavu pro studium totalitních režimů, protože si uvědomují chybu zákona, jehož cílem není uznání lidí, kteří nějakým způsobem trpěli, ale jehož prvotním cílem je v uvozovkách správný výklad dějin, rozumí se v duchu Ústavu pro studium totalitních režimů. Na závěr svého vystoupení chci požádat předkladatele návrhu zákona o údajném třetím odboji, aby stále neutíkali do minulosti a ke kritice režimu před rokem 1989. Všechny tyto spory nás odvádějí od problémů, které trápí naši republiku. Je potřebné, abychom se zaměřili na současnost, na řešení toho, co bolí a zajímá občany v jejich každodenním životě. Myslet na zabezpečení lidí, na to, aby se ne svou vinou dostávali na hranici chudoby. Řešme tedy společně tyto i další problémy a nezabředávejme opakovaně do minulosti, protože minulost již nezměníme, ale změnit můžeme zítřek. Z výše uvedených důvodů navrhuji tento zákon, sněmovní tisk 204, na zamítnutí. Děkuji za pozornost. (Potlesk poslanců KSČM.)",
        "Joseph Paul Overton popsal metodu, jak probíhá manipulace s veřejným míněním v otevřených demokratických společnostech",
        "pana Bělohradského, který říká, že oligarcha dělá všechno ve svůj prospěch. A vlastně Aristoteles říkal, že politici jsou elity národa. A pan Bělohradský v tom rozhovoru říká, že já mám šanci, protože teď dělám všechno pro tento stát a pro lidi, přejít z toho oligarchy na tu elitu, jako jste vy. Tak mi držte palce a snad to dokážu. (Smích v sále, potlesk.)",
    ]
    return (testy_jmen,)


@app.cell
def _(re):
    def jmeno(retezec):
        match = re.search(
            r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]*+(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]*+)*\b",
            retezec,
        )
        return match.group(0) if match else None

    return (jmeno,)


@app.cell
def _(jmeno, testy_jmen):
    jmeno(testy_jmen[0])
    return


@app.cell
def _(jmeno, pl, vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ").with_columns(
        pl.col("po").map_elements(jmeno, return_dtype=str)
    ).group_by("po").len().sort(by="len", descending=True)
    return


@app.cell
def _(graf):
    graf(r"(?i)filo[zs]o(f|fa|fem) ")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ").group_by("jmeno").len().sort(
        by="len", descending=True
    )
    return


@app.cell
def _(jmeno, pl, vyzobni):
    vyzobni(r"(?i)spisovate(l|le|lem|li|lka|lky|lkou|lce) ").with_columns(
        pl.col("po").map_elements(jmeno, return_dtype=str)
    ).group_by("po").len().sort(by="len", descending=True)
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Wells")
    return


@app.cell
def _(graf):
    graf(r"H.{1,20}Wells")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)jak (napsal|napsala|píše)")
    return


@app.cell
def _(vyzobni):
    vyzobni(
        r"(?i)[vz] (knize|knížce|knihy|publikac[ie]{0,1}|románu{0,1}|povíd[kc]|manifestu{0,1})"
    )
    return


@app.cell
def _(vyzobni):
    vyzobni(r"na blogu")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i) ocituji")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)leporel")
    return


@app.cell
def _(graf):
    graf(r"(?i) ocituji")
    return


@app.cell
def _(graf):
    graf("(i?)(slovy klasika|řečeno s klasikem|jak říká klasik|jak praví klasik)")
    return


@app.cell
def _(graf):
    graf("(i?)(slovy básníka)")
    return


@app.cell
def _(graf):
    graf(r" verše ")
    return


@app.cell
def _(vyzobni):
    vyzobni("verše")
    return


@app.cell
def _(graf):
    graf(r"(?i)absurdn.{0,10} drama")
    return


@app.cell
def _(graf):
    graf(r"(?i)červen.{0,10} knihovn")
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Antika
    """)
    return


@app.cell
def _(graf):
    graf(r"Odys{1,2}e")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Odys{1,2}e")
    return


@app.cell
def _(graf):
    graf(r"Sisyf")
    return


@app.cell
def _(graf):
    graf(r"Herkul")
    return


@app.cell
def _(graf):
    graf(r"(?i)prométh")
    return


@app.cell
def _(graf):
    graf(r"(?i)penelop")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)penelop")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fantasy a scifi
    """)
    return


@app.cell
def _(graf):
    graf(r"Harry\w{0,5} Potter")
    return


@app.cell
def _(graf):
    graf(r"Rowling")
    return


@app.cell
def _(graf):
    graf(r"Pán\w{0,5} prsten")
    return


@app.cell
def _(graf):
    graf("Tolkien")
    return


@app.cell
def _(graf):
    graf(r"Pratchet")
    return


@app.cell
def _(graf):
    graf(r"Stanis\w{2,6} Lem")
    return


@app.cell
def _(graf):
    graf(r"(?i)společenstv\w{1,5} prsten")
    return


@app.cell
def _(graf):
    graf(r"Frodo")
    return


@app.cell
def _(graf):
    graf(r"apitán\w{0,4} Nem")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"apitán\w{0,4} Nem")
    return


@app.cell
def _(graf):
    graf(r"verneov")
    return


@app.cell
def _(graf):
    graf(r"verneov")
    return


@app.cell
def _(graf):
    graf(r"Vern[ea][^\w]")
    return


@app.cell
def _(graf):
    graf(r"Star Trek")
    return


@app.cell
def _(graf):
    graf(r"Solaris")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Solaris")
    return


@app.cell
def _(graf):
    graf(r"kolem světa za")
    return


@app.cell
def _(graf):
    graf(r"mil pod mořem")
    return


@app.cell
def _(vyzobni):
    vyzobni("mil pod mořem")
    return


@app.cell
def _(graf):
    graf("Saruman")
    return


@app.cell
def _(graf):
    graf("Darth Vader")
    return


@app.cell
def _(graf):
    graf(r"(?i)hvězd\w{1,2} smrt")
    return


@app.cell
def _(graf):
    graf(r"(?i)stopař\w{1,5} průvodce")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dětská literatura
    """)
    return


@app.cell
def _(graf):
    graf("(?i)stolečku,{0,1} prostři")
    return


@app.cell
def _(graf):
    graf(r"Rychl.{0,10} šíp")
    return


@app.cell
def _(graf):
    graf(r"[Ff]oglar")
    return


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"pejs\w{0,5} [as] kočičk")
    return


@app.cell
def _(graf):
    graf(r"[Oo]tesán[ek]")
    return


@app.cell
def _(graf):
    graf(r"(?i)císař.{1,10} nové šat")
    return


@app.cell
def _(graf):
    graf(r"(?i)kocourkov")
    return


@app.cell
def _(graf):
    graf(r"(?i)bratrstv.{1,10} kočičí")
    return


@app.cell
def _(graf):
    graf(r"Alen.{0,13} [řŘ]íši div")
    return


@app.cell
def _(vyzobni):
    vyzobni(r"Alen.{0,13} [řŘ]íši div")
    return


@app.cell
def _(graf):
    graf("Vinnet")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Detektivky
    """)
    return


@app.cell
def _(graf):
    graf(r"Sherl.{0,10} Holmes")
    return


@app.cell
def _(graf):
    graf(r"Poirot")
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Klasika
    """)
    return


@app.cell
def _(graf):
    graf(r"(?i)don quijo")
    return


@app.cell
def _(graf):
    graf(r"(?i)boj.{0,10} s větrnými ml")
    return


@app.cell
def _(graf):
    graf(r"Jekyll.{0,13} Hyde")
    return


@app.cell
def _(graf):
    graf(r"Souostroví Gulag")
    return


@app.cell
def _(graf):
    graf(r"Solženicin")
    return


@app.cell
def _(graf):
    graf(r"Peroutk")
    return


@app.cell
def _(graf):
    graf(r"vlevo dole")
    return


@app.cell
def _(graf):
    graf("Machiavelli")
    return


@app.cell
def _(graf):
    graf("Faust")
    return


@app.cell
def _(graf):
    graf("Mefisto")
    return


@app.cell
def _(graf):
    graf("Saturnin")
    return


if __name__ == "__main__":
    app.run()
