import requests, pandas as pd, sys, time, json
from pathlib import Path
D = Path(sys.argv[1]); D.mkdir(parents=True, exist_ok=True)
CACHE = D / "_cache"; CACHE.mkdir(exist_ok=True)
IND = {
 "economia": {"NY.GDP.PCAP.PP.KD":"pib_pc_ppa","NV.AGR.TOTL.ZS":"agricultura_pib","NV.IND.TOTL.ZS":"industria_pib","NE.TRD.GNFS.ZS":"comercio_pib","FP.CPI.TOTL.ZG":"inflacion","NE.GDI.TOTL.ZS":"inversion_pib"},
 "salud": {"SP.DYN.LE00.IN":"esperanza_vida","SP.DYN.IMRT.IN":"mortalidad_infantil","SH.XPD.CHEX.GD.ZS":"gasto_salud_pib","SP.DYN.TFRT.IN":"fecundidad","SH.DYN.NMRT":"mortalidad_neonatal"},
 "educacion_digital": {"SE.SEC.ENRR":"matricula_secundaria","SE.TER.ENRR":"matricula_terciaria","IT.NET.USER.ZS":"usuarios_internet","IT.CEL.SETS.P2":"celulares_100hab","SE.PRM.CMPT.ZS":"finalizacion_primaria"},
 "sociedad": {"SP.POP.GROW":"crecimiento_poblacion","SP.URB.TOTL.IN.ZS":"urbanizacion","SP.POP.DPND":"dependencia","SL.TLF.CACT.FE.ZS":"particip_laboral_mujer","SP.POP.65UP.TO.ZS":"poblacion_65mas"},
 "ambiente_energia": {"EN.GHG.CO2.PC.CE.AR5":"co2_pc","EG.USE.ELEC.KH.PC":"electricidad_pc","EG.FEC.RNEW.ZS":"renovables_energia","AG.LND.FRST.ZS":"bosque_pct","EN.ATM.PM25.MC.M3":"pm25"},
}
session = requests.Session()
def get(url, params):
    for i in range(3):
        try:
            r = session.get(url, params=params, timeout=60); r.raise_for_status(); return r.json()
        except (requests.RequestException, ValueError) as e:
            if i == 2: print("ERROR", url, e, flush=True); return None
            pause = 2 ** i; print("REINTENTO", url, f"en {pause}s:", e, flush=True); time.sleep(pause)

def fetch_indicator(code):
    cache = CACHE / f"{code}.json"
    if cache.exists():
        try:
            with cache.open() as f: return json.load(f)
        except (OSError, json.JSONDecodeError): print("CACHE INVALIDO", code, flush=True)
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}"
    params = {"format":"json", "date":"2015:2022", "per_page":1000, "page":1}
    first = get(url, params)
    if not first or len(first) < 2 or first[1] is None: return None
    records = list(first[1])
    for page in range(2, int(first[0].get("pages", 1)) + 1):
        time.sleep(.5); params["page"] = page; response = get(url, params)
        if not response or len(response) < 2 or response[1] is None: print("PAGINA SIN DATOS", code, page, flush=True); continue
        records.extend(response[1])
    with cache.open("w") as f: json.dump(records, f)
    return records

cresult = get("https://api.worldbank.org/v2/country", {"format":"json", "per_page":400})
c = cresult[1] if cresult and len(cresult) > 1 else []
meta = pd.DataFrame([{"iso3":x["id"],"pais":x["name"],"region":x["region"]["value"],"ingreso":x["incomeLevel"]["value"]} for x in c if x["region"]["value"]!="Aggregates"], columns=["iso3","pais","region","ingreso"])
rows = []
for g, d in IND.items():
    for code, nom in d.items():
        r = fetch_indicator(code)
        if not r: print("SIN DATOS", code, flush=True); continue
        df = pd.DataFrame([{"iso3":x["countryiso3code"],"anio":int(x["date"]),"valor":x["value"]} for x in r if x["value"] is not None and x["countryiso3code"]])
        if df.empty: print("SIN DATOS", code, flush=True); continue
        df = df.sort_values("anio").groupby("iso3").tail(1); df["variable"]=nom; df["grupo"]=g; df["codigo"]=code; rows.append(df); print(code, nom, len(df), flush=True)
long = pd.concat(rows) if rows else pd.DataFrame(columns=["iso3","anio","valor","variable","grupo","codigo"])
long.to_csv(D / "indicadores_wb_largo.csv", index=False); meta.to_csv(D / "paises_meta.csv", index=False)
