def najdi_tituly(jmeno):
    jmeno = jmeno.replace('ml.','mladší').replace('st.','starší')
    tituly = []
    za = None
    if ',' in jmeno:
        tituly_za = ' '.join(jmeno.split(',')[1:])
        za = [t.strip() for t in tituly_za.strip().split(' ') if t != '']
        jmeno = jmeno.split(',')[0]
    pred = [t for t in jmeno.split(' ') if '.' in t]
    jmeno = jmeno.split('.')[-1].strip()
    if za:
        tituly = pred + za
    else:
        tituly = pred
    return {'jmeno_ciste':jmeno,'tituly':tituly}