"""Instantáneas públicas; SFC se consulta agregada por tipo de entidad y municipio."""
import datetime as dt
import hashlib
import json
import ssl
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import certifi

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/territorial/raw'
BASE='https://www.datos.gov.co/resource/'
QUERY={'$select':'fecha_de_corte,tipo_de_entidad,c_digo_del_departamento,c_digo_del_municipio,nombre_del_municipio,sum(cartera_de_cr_ditos) as cartera,count(*) as filas,count(cartera_de_cr_ditos) as filas_con_cartera', '$where':"fecha_de_corte in ('2025-06-30T00:00:00.000','2026-06-30T00:00:00.000')",'$group':'fecha_de_corte,tipo_de_entidad,c_digo_del_departamento,c_digo_del_municipio,nombre_del_municipio','$order':'fecha_de_corte,tipo_de_entidad,c_digo_del_departamento,c_digo_del_municipio,nombre_del_municipio','$limit':10000}
DUP_QUERY={'$select':'fecha_de_corte,tipo_de_entidad,c_digo_de_entidad,c_digo_del_departamento,c_digo_del_municipio,count(*) as n','$where':QUERY['$where'],'$group':'fecha_de_corte,tipo_de_entidad,c_digo_de_entidad,c_digo_del_departamento,c_digo_del_municipio','$having':'count(*)>1','$limit':10}
URLS={'sfc_municipios.json':BASE+'u2wk-tfe3.json?'+urlencode(QUERY),'sfc_duplicados.json':BASE+'u2wk-tfe3.json?'+urlencode(DUP_QUERY),'divipola.json':BASE+'gdxc-w37w.json?'+urlencode({'$limit':5000}),'poblacion_dane.xlsx':'https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaMun-2018-2042_VP.xlsx'}

def main():
    OUT.mkdir(parents=True,exist_ok=True); manifest={}
    for name,url in URLS.items():
        with urlopen(url,timeout=120,context=ssl.create_default_context(cafile=certifi.where())) as response: body=response.read()
        if name.endswith('.json'):
            data=json.loads(body)
            if name=='sfc_duplicados.json' and data: raise ValueError('SFC contiene claves entidad-municipio duplicadas')
            if name!='sfc_duplicados.json' and (not data or len(data)>= (10000 if name.startswith('sfc') else 5000)): raise ValueError('Consulta vacía o truncada: '+name)
        elif not body.startswith(b'PK'): raise ValueError('Proyecciones DANE no son XLSX')
        (OUT/name).write_bytes(body)
        manifest[name]={'url':url,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
        print(name,len(body),flush=True)
    manifest['fecha_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__': main()
