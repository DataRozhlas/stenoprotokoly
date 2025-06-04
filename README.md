Pokud chcete rychle stáhnout a oscrapovat sněmovní stenoprotokoly z posledních let, rovnou vás odkážu na [dílo Ondřeje Kokeše](https://github.com/kokes/od/tree/main/data/steno). Zde nás čeká větší a složitější dobrodružství, ambicí je převést do jakž takž čistých dat vše, co visí ve [Společné česko-slovenské digitální parlamentní knihovně](https://psp.cz/eknih/). Prioritu mají federální a české dolní komory zasedající po roce 1918.

Stažení surových souborů HTML obstarává poměrně neefektivní skript z větší části vygenerovaný v LLMs; optimalizace mi nedává velký smysl, pro většinu use cases stačí spustit ho jedenkrát (již stažené soubory nepřepisuje, což nemusí a může být problematické, na každý pád je dobré o tom vědět). Následné scrapování do parquetů se samotnými projevy a CSVček s daty o schůzích průběžně ladím – během let se mění formáty přepisu, někde jde mluvčí (a tedy začátek nového projevu) identifikovat snadno skrz hledání tučných odkazů, někde je zapotřebí nasadit delikátní filtry rozpoznávající, zda je v prostém textu před dvojtečkou něco, co připomíná jméno. Posledí dílek v pipeline, skript/sešit ```003```, spojuje tyto malé soubory do jednoho.

## To do

- Brute force stahování souborů (ani skript pro scrapování dat) si neporadí s url [Národního výboru 1918](https://www.psp.cz/eknih/1918nvc/stenprot/19181109/19181109_01.htm).
- Chybí Senát.
- Ještě neprocházejí všechny testy scrapování, viz sešit ```004```.
    - Dopsat další testy: délka polí s mluvčími, počet vystoupení v dokumentu atd.
- Při čištění pořešit projevy navazující z předchozího souboru.
- Místo jednoho monolitického souboru uložit zpracovaná data do několika. (Po jednotlivých komoroobdobích?)
- Postahovat dostupná data o lidech, spárovat skrz ```mluvci_id```. (A zjistit, zda by šlo spárovat s Wikidaty.)
- Zjistit u poskytovatele stenoprotokolů nedohlédnuté háčky. (Jak (ne)kompletní či cenzurované jsou?)
- Na konec tohoto dokumentu generovat statistiky.