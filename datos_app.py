"""Carga y normalización de las seis fuentes físicas autorizadas (cinco grupos)."""
from pathlib import Path
import unicodedata
import pandas as pd

BASE = Path(__file__).resolve().parent / 'datos'
MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Setiembre','Octubre','Noviembre','Diciembre']
ABR = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Set','Oct','Nov','Dic']
ARCHIVOS = {2023:'Huella_Verde_Comparacion_2023_actualizado.xlsx', **{a:f'Huella_Verde_Comparacion_{a}.xlsx' for a in (2024,2025,2026)}}

def clave(x):
    return ''.join(c for c in unicodedata.normalize('NFD', str(x).strip().upper()) if unicodedata.category(c) != 'Mn')

def mes(x):
    k=clave(x).replace('SEPTIEMBRE','SETIEMBRE')
    return {clave(m):i for i,m in enumerate(MESES,1)}.get(k)

def distrito(x):
    k=clave(x)
    return {'CERCADO':'LIMA','CERCADO DE LIMA':'LIMA','LURIGANCHO - CHOSICA':'LURIGANCHO','LURIGANCHO-CHOSICA':'LURIGANCHO'}.get(k,k)

NOMBRES={'LIMA':'Cercado de Lima','ANCON':'Ancón','JESUS MARIA':'Jesús María','LURIGANCHO':'Lurigancho-Chosica','LURIN':'Lurín','PACHACAMAC':'Pachacámac','RIMAC':'Rímac','SAN MARTIN DE PORRES':'San Martín de Porres','SANTA MARIA DEL MAR':'Santa María del Mar','VILLA MARIA DEL TRIUNFO':'Villa María del Triunfo'}
def nombre(x):
    return NOMBRES.get(x,str(x).title().replace(' De ',' de ').replace(' Del ',' del '))
def num(x):
    return pd.to_numeric(x.astype(str).str.replace(',','',regex=False).str.replace('%','',regex=False).str.strip(),errors='coerce')

def cargar(base=BASE):
    p=pd.read_csv(base/'programa_arborizacion.csv',encoding='utf-8-sig'); p.columns=p.columns.str.strip().str.upper()
    anual=pd.DataFrame({'anio':num(p.METAS.str.extract(r'(20\d{2})')[0]).astype(int),'arboles':num(p['CANTIDAD ARBOLES PLANTADOS']),'cumplimiento':num(p['CUMPLIMIENTO %'])})
    # Estimación inversa: los porcentajes de fuente están redondeados.
    anual['meta_estimada']=anual.arboles.div(anual.cumplimiento.where(anual.cumplimiento>0)/100)
    anual['meta_estimada']=anual.meta_estimada.round()
    programa=pd.concat([pd.DataFrame({'anio':anual.anio,'mes':i,'arboles':num(p[m.upper()])}) for i,m in enumerate(MESES,1)],ignore_index=True).sort_values(['anio','mes'])
    r=pd.read_csv(base/'distribucion_distritos.csv',encoding='utf-8-sig');r.columns=r.columns.str.strip().str.upper();r['mes']=r.MES.map(mes);r=r[r.mes.notna()].copy()
    ds=[c for c in r.columns if c not in ['ITEM','AÑO','MES','TOTAL','mes']]
    repo=pd.concat([pd.DataFrame({'anio':num(r['AÑO']).astype(int),'mes':r.mes.astype(int),'distrito':distrito(c),'arboles':num(r[c])}) for c in ds],ignore_index=True)
    distritos=[]; resumenes=[]; metodos={}; arboles_raw={}; raw={}
    for a,f in ARCHIVOS.items():
        hojas=pd.read_excel(base/f,sheet_name=None,engine='openpyxl'); raw[a]=hojas
        d=hojas['Comparacion_distrital']; s=hojas['Resumen_Lima_mensual']; metodos[a]=hojas['Metodologia'];arboles_raw[a]=hojas['Datos_arboles_SERPAR']
        # Hojas con semántica diferente en 2023: no extrapolar captura ni acumulados.
        q=pd.DataFrame({'anio':a,'mes':d.iloc[:,1].map(mes),'distrito':d.iloc[:,2].map(distrito),'ubigeo':d.iloc[:,3].astype(str),'poblacion':num(d.iloc[:,4]),'co2_resp':num(d.iloc[:,6]),'arboles':num(d.iloc[:,7]),'o2':num(d.iloc[:,8 if a==2023 else 9]),'captura':float('nan') if a==2023 else num(d.iloc[:,10]),'acumulado':float('nan') if a==2023 else num(d.iloc[:,8])})
        distritos.append(q)
        t=pd.DataFrame({'anio':a,'mes':s.iloc[:,1].map(mes),'poblacion':num(s.iloc[:,2]),'co2_resp':num(s.iloc[:,3]),'arboles':num(s.iloc[:,4]),'o2':num(s.iloc[:,5 if a==2023 else 6]),'captura':float('nan') if a==2023 else num(s.iloc[:,7]),'acumulado':float('nan') if a==2023 else num(s.iloc[:,5])})
        resumenes.append(t)
    huella=pd.concat(distritos,ignore_index=True).sort_values(['anio','distrito','mes']); resumen=pd.concat(resumenes,ignore_index=True).sort_values(['anio','mes'])
    comp=programa.merge(resumen[['anio','mes','arboles']].rename(columns={'arboles':'excel'}),on=['anio','mes'],how='inner').rename(columns={'arboles':'csv_programa'})
    dist_total=repo.groupby(['anio','mes'],as_index=False).arboles.sum(min_count=1).rename(columns={'arboles':'csv_distritos'})
    comp=comp.merge(dist_total,on=['anio','mes'],how='left');comp['diferencia_excel_csv']=comp.excel-comp.csv_programa
    return anual,programa,repo,huella,resumen,comp,metodos,raw
