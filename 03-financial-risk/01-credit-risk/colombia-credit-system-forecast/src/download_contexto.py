"""Fuentes SFC por tipo de entidad y serie IPC DANE; guarda manifiesto de versión."""
import datetime as dt
import hashlib
import json
import ssl
from pathlib import Path
from urllib.request import urlopen
import certifi

RAW=Path(__file__).resolve().parents[1]/'data/territorial/raw'
BASE='https://www.superfinanciera.gov.co/loader.php?idFile={}&lFuncion=descargar&lServicio=Tools2&lTipo=descargas'
URLS={'sfc_bancos.xlsx':BASE.format('1017725'),'sfc_financiamiento.xlsx':BASE.format('1017880'),'sfc_corporaciones.xlsx':BASE.format('1017894'),'sfc_cooperativas.xlsx':BASE.format('1017801'),'ipc_dane_oct2026.xlsx':'https://www.dane.gov.co/files/operaciones/IPC/oct2026/anex-IPC-Indices-oct2026.xlsx'}

def main():
    RAW.mkdir(parents=True,exist_ok=True); manifest={}
    for name,url in URLS.items():
        with urlopen(url,timeout=90,context=ssl.create_default_context(cafile=certifi.where())) as r: content=r.read()
        if not content.startswith(b'PK'): raise ValueError('No es XLSX: '+name)
        (RAW/name).write_bytes(content)
        manifest[name]={'url':url,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
        print(name,len(content),flush=True)
    manifest['descargado_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    (RAW/'contexto_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()
