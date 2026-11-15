"""Descarga versiones públicas; una actualización puede modificar la historia."""
import datetime as dt
import hashlib
import json
import ssl
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import certifi

ROOT=Path(__file__).resolve().parents[1]
SFC='https://www.superfinanciera.gov.co/loader.php?idFile=1045555&lFuncion=descargar&lServicio=Tools2&lTipo=descargas'
TRM='https://www.datos.gov.co/resource/32sa-8pi3.json'
QUERY={'$select':'valor,unidad,vigenciadesde,vigenciahasta','$where':"vigenciadesde >= '2015-01-01T00:00:00' AND vigenciadesde < '2026-11-01T00:00:00'",'$order':'vigenciadesde ASC','$limit':10000}

def main():
    folder=ROOT/'data'/'raw'; folder.mkdir(parents=True,exist_ok=True)
    context=ssl.create_default_context(cafile=certifi.where())
    files=[('sfc_total_ec_niif.xlsx',SFC),('trm.json',TRM+'?'+urlencode(QUERY))]
    meta={}
    for name,url in files:
        with urlopen(url,timeout=90,context=context) as response:
            content=response.read()
        if name.endswith('xlsx') and not content.startswith(b'PK'):
            raise ValueError('La fuente SFC no retornó un archivo Excel válido')
        if name.endswith('json'):
            rows=json.loads(content)
            if not rows or len(rows)>=10000: raise ValueError('TRM vacía o posiblemente truncada')
        (folder/name).write_bytes(content)
        meta[name]={'url':url,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
    meta['descargado_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    (folder/'manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(meta,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
