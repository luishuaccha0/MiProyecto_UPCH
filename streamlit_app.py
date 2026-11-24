"""Arborización en Lima | Aplicación Streamlit. Toda la lógica y UI se generan en Python."""
from html import escape
from math import ceil
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datos_app import cargar, MESES, ABR, nombre, ARCHIVOS

st.set_page_config(page_title='Arborización en Lima | Huella Verde',page_icon='🌳',layout='wide',initial_sidebar_state='collapsed')
COL=['#A5D9B5','#C5E4D0','#8FC69E','#E8D8CA','#F5E5AD','#C0E1F0','#D3E5B5','#E8D5C3']
DARK='#274035'; GREEN='#43805C'; MINT='#8FC69E'; GRAY='#607568'; BG='#F5F8F4'
# CSS/SVG incluidos como cadenas de Python; no hay frontend JS ni archivos HTML externos.
st.markdown('''<style>
.stApp{background:#F5F8F4;color:#263B32} [data-testid="stHeader"]{background:transparent} [data-testid="stToolbar"]{display:none}
.block-container{max-width:1500px;padding:1.1rem 2rem 2.5rem} h1,h2,h3{letter-spacing:-.035em;color:#263B32} h1{font-size:2.15rem} h2{font-size:1.65rem} p{color:#526B5C} 
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid #DDE9DF;border-radius:18px;box-shadow:0 5px 20px #294A3510}
[data-testid="stMetric"]{background:white;padding:1rem;border:1px solid #DFE9E0;border-radius:14px} [data-testid="stMetricLabel"]{color:#607568} [data-testid="stMetricValue"]{font-size:1.7rem;color:#263B32}
.stButton>button{border:1px solid #DDE9DF;border-radius:12px;min-height:2.7rem;font-weight:600} .stButton>button:hover{border-color:#8FC69E;background:#E8F3EA;color:#274035} .stButton>button[kind="primary"]{background:#43805C;color:white}
[data-testid="stSegmentedControl"]{background:#EDF4ED;border-radius:14px;padding:5px} [data-testid="stSegmentedControl"] button{font-size:.84rem;border-radius:10px} .eyebrow{font-size:.73rem;letter-spacing:.09em;font-weight:750;color:#43805C;text-transform:uppercase;margin:0 0 5px}
.brand{display:flex;align-items:center;gap:12px;line-height:1.15;margin-top:4px}.brand-icon{background:#DCEFE0;border-radius:15px;width:44px;height:44px;display:grid;place-items:center;flex-shrink:0}.brand-icon svg{width:26px;height:32px}.brand strong{font-size:1.25rem;letter-spacing:-.03em}.brand small{display:block;font-size:.77rem;color:#607568;margin-top:4px}
.hero{position:relative;overflow:hidden;background:linear-gradient(115deg,#fff,#EDF5EF);border:1px solid #E0EAE1;border-radius:22px;padding:2rem 2.1rem 1.6rem;min-height:225px}.hero h1{font-size:clamp(1.7rem,3vw,2.65rem);line-height:1.08;max-width:730px;margin:.65rem 0}.hero p{font-size:1rem;max-width:650px;line-height:1.6;position:relative;z-index:1}.hero svg{position:absolute;right:0;bottom:0;width:28%;max-width:330px;opacity:.65}.pill{display:inline-block;border:1px solid #CBE5D0;background:#F2F9F3;color:#43805C;padding:5px 11px;font-size:.73rem;font-weight:650;border-radius:999px}.kpi{background:white;border:1px solid #DDE9DF;border-radius:15px;padding:15px 17px;box-shadow:0 5px 15px #294A3509;min-height:124px}.kpi-top{display:flex;align-items:center;justify-content:space-between;gap:6px}.kpi-label{font-size:.69rem;letter-spacing:.06em;text-transform:uppercase;font-weight:750;color:#607568}.kpi-icon{width:32px;height:32px;background:#E4F2E7;border-radius:10px;display:grid;place-items:center}.kpi-value{font-size:1.8rem;font-weight:750;line-height:1.2;margin-top:13px;letter-spacing:-.04em;overflow-wrap:anywhere}.kpi-sub{font-size:.78rem;color:#607568;margin-top:4px}
.rank{margin:16px 0 20px}.rank-label{display:flex;justify-content:space-between;gap:8px;font-size:.85rem;font-weight:650;margin-bottom:6px}.rank-track{height:7px;background:#EAF0EA;border-radius:100px;overflow:hidden}.rank-fill{height:100%;border-radius:100px}.tree-card{text-align:center;padding:14px 4px 8px}.tree-card svg{height:68px;width:68px}.tree-card small{color:#607568;display:block;font-size:.85rem}.forest{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;padding:25px 15px;border-radius:17px;background:#F5F8F4;border:1px solid #DFE9E0;max-height:480px;overflow-y:auto}.forest svg{width:24px;height:30px;flex:none}.note{background:#F1F6F1;border:1px solid #DFE9E0;border-radius:13px;padding:13px 16px;color:#526B5C;font-size:.83rem;line-height:1.5}.year-card{padding:3px 2px}.year-card strong{font-size:1.1rem}.year-card .line{display:flex;justify-content:space-between;font-size:.82rem;margin-top:7px}.year-head{display:flex;justify-content:space-between;align-items:center}.foot{font-size:.75rem;color:#718277;border-top:1px solid #DDE9DF;padding-top:12px;margin-top:22px}
@media(max-width:700px){.block-container{padding:1rem}.hero{padding:1.25rem}.hero svg{opacity:.2}.kpi-value{font-size:1.4rem}}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner='Cargando fuentes de datos…')
def fuentes(): return cargar()
try:
    anual,programa,repo,huella,resumen,comp,metodos,raw=fuentes()
except Exception as e:
    st.error(f'No se pudieron cargar los archivos de la carpeta datos: {e}');st.stop()

def fmt(v,d=0):
    if pd.isna(v): return 'Sin dato'
    return f'{v:,.{d}f}'.replace(',','\u202f').replace('.',',')
def esc(s): return escape(str(s))
def html(s): st.markdown(s,unsafe_allow_html=True)
def tree(color=MINT,opacity=1):
    return f'<svg viewBox="0 0 48 62" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="opacity:{opacity}"><rect x="21" y="47" width="6" height="12" rx="1" fill="#DCC9B8"/><path d="M24 2 L7 28 H15 L2 48 H46 L33 28 H41 Z" fill="{color}"/></svg>'
def eyebrow(s): html(f'<div class="eyebrow">{esc(s)}</div>')
def note(s): html(f'<div class="note">{esc(s)}</div>')
def kpi(label,val,sub='',icon='🌳'):
    html(f'<div class="kpi"><div class="kpi-top"><span class="kpi-label">{esc(label)}</span><span class="kpi-icon">{icon}</span></div><div class="kpi-value">{esc(val)}</div><div class="kpi-sub">{esc(sub)}</div></div>')
def rankbars(series,n=5):
    s=series.dropna().sort_values(ascending=False).head(n);mx=max(s.max(),1) if len(s) else 1
    for i,(d,v) in enumerate(s.items()):
        html(f'<div class="rank"><div class="rank-label"><span>#{i+1} · {esc(nombre(d))}</span><span>{fmt(v)} árboles</span></div><div class="rank-track"><div class="rank-fill" style="width:{max(0,v/mx*100):.2f}%;background:{COL[i%len(COL)]}"></div></div></div>')
def layout(fig,ylab='',height=370,legend=False):
    fig.update_layout(height=height,margin=dict(l=12,r=20,t=25,b=15),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Arial',size=12,color=DARK),hoverlabel=dict(bgcolor='#fff',font_color=DARK),showlegend=legend,legend=dict(orientation='h',y=1.10,x=0),yaxis_title=ylab)
    fig.update_xaxes(showgrid=False,showline=True,linecolor='#DCE7DD',zeroline=False)
    fig.update_yaxes(gridcolor='#E7EEE8',zeroline=False,rangemode='tozero')
    return fig

def plot(fig): st.plotly_chart(fig,use_container_width=True,theme=None,config={'displaylogo':False,'responsive':True,'modeBarButtonsToRemove':['lasso2d','select2d']})
def linechart(df, col='arboles', label='Árboles plantados',area=True, height=360):
    s=df.sort_values('mes');x=[ABR[int(m)-1] for m in s.mes];y=s[col].tolist()
    fig=go.Figure(go.Scatter(x=x,y=y,mode='lines+markers+text',name=label,line=dict(color=MINT,width=3),marker=dict(size=16,color=[COL[(int(m)-1)%len(COL)] for m in s.mes],line=dict(color='white',width=2)),text=[fmt(v) if pd.notna(v) else '' for v in y],textposition='top center',cliponaxis=False,fill='tozeroy' if area else None,fillcolor='rgba(165,217,181,.19)',connectgaps=False,hovertemplate='%{x}: %{y:,.2f}<extra>'+label+'</extra>'))
    fig.update_xaxes(categoryorder='array',categoryarray=ABR)
    return layout(fig,label,height)

def goto(page): st.session_state['pagina']=page
PAGES=['Dashboard','Evolución anual','Mensual','Distritos','Bosque virtual','Huella Verde']
if 'pagina' not in st.session_state: st.session_state.pagina='Dashboard'
a,b=st.columns([1.05,2.4],vertical_alignment='center')
with a: html(f'<div class="brand"><span class="brand-icon">{tree(GREEN)}</span><div><strong>Arborización en Lima</strong><small>SERPAR · Plan Verde Metropolitano</small></div></div>')
with b: st.segmented_control('Navegación',PAGES,key='pagina',selection_mode='single',label_visibility='collapsed',format_func=lambda x:dict(zip(PAGES,['◉ Dashboard','▥ Evolución anual','▦ Mensual','♧ Distritos','♠ Bosque virtual','❋ Huella Verde']))[x])
page=st.session_state.pagina or 'Dashboard'
st.divider()

if page=='Dashboard':
    total=anual.arboles.sum();record=anual.loc[anual.arboles.idxmax()];latest=anual.loc[anual.anio.idxmax()];ranking=repo.groupby('distrito').arboles.sum(min_count=1).sort_values(ascending=False)
    html(f'''<div class="hero"><span class="pill">● Registro histórico 2020–2026</span><h1>Transformación ecológica de Lima Metropolitana</h1><p>Explora el programa de arborización y sus relaciones ambientales. <strong>{fmt(total)} árboles</strong> registrados en el programa histórico, con información distrital y estimaciones de Huella Verde.</p><svg viewBox="0 0 320 220"><circle cx="175" cy="115" r="80" fill="#C5E4D0"/><circle cx="100" cy="145" r="64" fill="#A5D9B5"/><circle cx="257" cy="153" r="55" fill="#D9ECD9"/><path d="M100 177 V220 M175 157 V220 M257 183 V220" stroke="#E8DED0" stroke-width="15" stroke-linecap="round"/></svg></div>''')
    c1,c2,_=st.columns([1,1,2.4]);c1.button('🌳 Explorar distritos',on_click=goto,args=('Distritos',),type='primary',use_container_width=True);c2.button('▥ Ver gráfico anual',on_click=goto,args=('Evolución anual',),use_container_width=True)
    for c,k in zip(st.columns(4), [('Total árboles plantados',fmt(total),'CSV programa · 2020–2026','🌳'),(f'Año récord ({int(record.anio)})',fmt(record.arboles),f'{fmt(record.cumplimiento,2)} % de cumplimiento','🏅'),('Distrito líder (2026)',nombre(ranking.index[0]),f'{fmt(ranking.iloc[0])} árboles · CSV distritos','♛'),('Avance 2026',fmt(latest.cumplimiento)+' %',f'{fmt(latest.arboles)} árboles · CSV programa','↗')]):
        with c:kpi(*k)
    l,r=st.columns([1.85,1])
    with l:
        with st.container(border=True):
            st.subheader('Top distritos con mayor arborización (2026)');st.caption('Registro distrital del repositorio · enero a setiembre');rankbars(ranking);st.button('Ver los 42 distritos',key='all_dist',on_click=goto,args=('Distritos',),use_container_width=True);st.caption('42 distritos incluidos en el CSV; Miraflores no figura.')
    with r:
        with st.container(border=True):
            st.subheader('Impacto ambiental estimado');st.caption('Excel Huella Verde 2026 · agosto, último mes con plantaciones positivas en esta fuente.')
            h=resumen[(resumen.anio==2026)&(resumen.mes==8)].iloc[0]
            kpi('Captura potencial de CO₂',fmt(h.captura/1000,2)+' t/mes','Cohorte anual · equivalente teórico','🍃');kpi('Oxígeno potencial',fmt(h.o2/1000,2)+' t/mes','No es producción medida','◉');st.button('Abrir análisis Huella Verde',on_click=goto,args=('Huella Verde',),type='primary',use_container_width=True)
    note('Fuentes diferenciadas: el histórico usa el CSV del programa; el ranking usa el CSV distrital; los indicadores ambientales usan los Excel. No se suman fuentes que registran los mismos árboles.')

elif page=='Evolución anual':
    with st.container(border=True):
        eyebrow('Gráfico de arbolado');st.header('Evolución anual de arborización (2020–2026)');st.caption('Altura de cada copa proporcional al total informado por año. Fuente: programa_arborizacion.csv.')
        modo=st.segmented_control('Vista',['Árboles plantados','Meta estimada vs. plantados'],default='Árboles plantados',key='annual_mode')
        x=anual.anio.astype(str).tolist();y=anual.arboles.tolist();f=go.Figure()
        if modo=='Meta estimada vs. plantados':
            f.add_bar(x=x,y=y,name='Plantados',marker_color=MINT,text=[fmt(v) for v in y],textposition='outside',cliponaxis=False)
            f.add_bar(x=x,y=anual.meta_estimada,name='Meta inferida',marker_color='#E8D8CA',hovertemplate='%{x}<br>Meta inferida: %{y:,.0f}<extra></extra>');f.update_layout(barmode='group')
        else:
            for i,(a,v) in enumerate(zip(x,y)):
                f.add_trace(go.Scatter(x=[a,a],y=[0,v],mode='lines',line=dict(color='#DCC9B8',width=10),hoverinfo='skip',showlegend=False))
            f.add_trace(go.Scatter(x=x,y=y,mode='markers+text',marker=dict(size=46,color=COL[:len(x)],line=dict(color='white',width=2)),text=[fmt(v) for v in y],textposition='top center',cliponaxis=False,hovertemplate='%{x}<br>%{y:,.0f} árboles<extra></extra>'))
        f.update_yaxes(range=[0,max(y+anual.meta_estimada.dropna().tolist() if modo=='Meta estimada vs. plantados' else y)*1.16]);plot(layout(f,'Árboles',435,modo=='Meta estimada vs. plantados'))
        note('2026: enero a setiembre en CSV. Meta estimada = árboles plantados ÷ (cumplimiento / 100); es una inferencia a partir del porcentaje redondeado, no una meta oficial publicada.')
    for start in range(0,len(anual),4):
        for c,(_,row) in zip(st.columns(4),anual.iloc[start:start+4].iterrows()):
            with c,st.container(border=True):
                html(f'<div class="year-card"><div class="year-head"><strong>{int(row.anio)}</strong><span class="pill">{fmt(row.cumplimiento,2)} %</span></div><div class="line"><span>Árboles plantados</span><b>{fmt(row.arboles)}</b></div><div class="line"><span>Meta inferida</span><b>{fmt(row.meta_estimada)}</b></div></div>')

elif page=='Mensual':
    with st.container(border=True):
        eyebrow('Análisis estacional');st.header('Distribución mensual de plantación');st.caption('Compara los registros por mes. Los meses sin registro no se convierten en cero.')
        c1,c2=st.columns([1,2]);a=c1.selectbox('Año',list(range(2026,2019,-1)),key='mes_year');opciones=['CSV programa']+(['Excel Huella Verde'] if a>=2023 else [])+(['CSV distritos'] if a==2026 else []);src=c2.selectbox('Fuente de datos',opciones,key='mes_src')
        df=programa[programa.anio==a] if src=='CSV programa' else resumen[resumen.anio==a] if src=='Excel Huella Verde' else repo[repo.anio==a].groupby('mes',as_index=False).arboles.sum(min_count=1)
        df=df[df.arboles.notna()];plot(linechart(df,height=390))
        if len(df):
            peak=df.loc[df.arboles.idxmax()];note(f'Pico de registro en esta fuente: {MESES[int(peak.mes)-1]}, con {fmt(peak.arboles)} árboles. Un pico de registros no demuestra por sí solo una temporada óptima de siembra.')
        if a>=2023:
            with st.expander('Comparar fuentes para este año'):
                z=comp[comp.anio==a];f=go.Figure()
                for col,label,color in [('csv_programa','CSV programa',GREEN),('excel','Excel Huella Verde','#B7D9C0'),('csv_distritos','CSV distritos','#E8D8CA')]:
                    if z[col].notna().any():f.add_bar(x=[ABR[int(m)-1] for m in z.mes],y=z[col],name=label,marker_color=color)
                plot(layout(f,'Árboles',330,True));st.dataframe(z.assign(mes=z.mes.map(lambda i:MESES[i-1])),hide_index=True,use_container_width=True);note('Las diferencias se conservan tal como aparecen en los documentos. Un cero en Excel no confirma ausencia de plantaciones.')

elif page=='Distritos':
    with st.container(border=True):
        eyebrow('Bosque pictórico de distritos');st.header('Arborización por distrito en Lima');st.caption('Selecciona una tarjeta para abrir sus registros mensuales e indicadores ambientales.')
        a,b,c=st.columns([1,1,2]);year=a.selectbox('Año',[2026,2025,2024,2023],key='dist_year');src=b.selectbox('Fuente',['CSV distritos','Excel Huella Verde'] if year==2026 else ['Excel Huella Verde'],key='dist_src');query=c.text_input('Buscar distrito',placeholder='Ej. Ancón o Cercado de Lima')
        d=repo[repo.anio==year] if src=='CSV distritos' else huella[huella.anio==year]
        sums=d.groupby('distrito').arboles.sum(min_count=1);a,b=st.columns(2);fil=a.selectbox('Mostrar',['Todos','Con plantaciones positivas','Cero registrado','Sin dato']);order=b.selectbox('Orden',['Alfabético','Mayor arborización','Menor arborización'])
        if fil=='Con plantaciones positivas':sums=sums[sums>0]
        elif fil=='Cero registrado':sums=sums[sums==0]
        elif fil=='Sin dato':sums=sums[sums.isna()]
        from datos_app import clave
        sums=sums[[clave(query) in clave(nombre(k)) for k in sums.index]]
        if order=='Alfabético':sums=sums.reindex(sorted(sums.index,key=nombre))
        else:sums=sums.sort_values(ascending=order=='Menor arborización')
        st.caption(f'{len(sums)} distritos mostrados · {year} · {src}'+(' · distribución estimada por población' if year==2023 else ''))
        @st.dialog('Detalle distrital',width='large')
        def detalle(k):
            st.subheader(nombre(k));st.caption(f'{year} · {src}');dd=d[d.distrito==k];st.metric('Árboles del periodo',fmt(dd.arboles.sum(min_count=1)));plot(linechart(dd,height=280))
            h=huella[(huella.anio==year)&(huella.distrito==k)].sort_values('mes')
            if not h.empty:
                last=h.iloc[-1];st.caption('Indicadores del Excel · población de diciembre (estimada), no suma de habitantes mensuales.');u,v=st.columns(2);u.metric('Población estimada (dic.)',fmt(last.poblacion));v.metric('Árboles / 1 000 hab. (fuente seleccionada)',fmt(dd.arboles.sum(min_count=1)/last.poblacion*1000,2));st.dataframe(h[['mes','poblacion','arboles','co2_resp','o2','captura']].assign(mes=lambda t:t.mes.map(lambda m:MESES[m-1])),hide_index=True,use_container_width=True);note('La tabla ambiental usa Excel, incluso cuando la tarjeta usa CSV. 2023: la distribución es estimada y la captura de CO₂ no está disponible.')
        for start in range(0,len(sums),4):
            for i,(col,(k,v)) in enumerate(zip(st.columns(4),sums.iloc[start:start+4].items()),start):
                with col,st.container(border=True):
                    html(f'<div class="tree-card">{tree(COL[i%len(COL)])}<small>{fmt(v)} árboles</small></div>');st.button(nombre(k),key=f'district_{year}_{k}',use_container_width=True) and detalle(k)
        if sums.empty:st.info('No hay distritos que coincidan con el filtro.')
        note('Los ceros son valores registrados en la fuente y no prueban que un distrito carezca de árboles. Los 43 distritos del Excel incluyen Miraflores; el CSV incluye 42.')

elif page=='Bosque virtual':
    with st.container(border=True):
        eyebrow('Pictograma interactivo');st.header('Simulador de densidad de bosque urbano');st.caption('Representación visual del número de plantaciones registradas, no de la densidad por superficie ni de árboles vivos.')
        c1,c2,c3=st.columns([1,1.5,1]);scale=c1.selectbox('1 icono representa',[1000,2500,5000,10000,25000],index=3,format_func=lambda v:fmt(v)+' árboles');period=c2.selectbox('Periodo',['Total acumulado (2020–2026)']+list(anual.anio.astype(int)),format_func=str);n=anual.arboles.sum() if isinstance(period,str) else anual.loc[anual.anio==period,'arboles'].iloc[0];c3.metric('Árboles en pantalla',fmt(n))
        full,rest=divmod(int(n),scale);icons=''.join(tree(COL[i%len(COL)]) for i in range(full));icons+=tree(COL[full%len(COL)],.3) if rest else ''
        html(f'<div class="forest" role="img" aria-label="{full} iconos completos y {rest} árboles restantes">{icons}</div>');st.caption(f'{fmt(full)} iconos completos × {fmt(scale)} árboles'+(f' + 1 icono tenue que representa los {fmt(rest)} restantes.' if rest else '.'))
        note('Fuente: CSV programa de arborización. Las plantaciones de diferentes años se acumulan como registros; no se supone supervivencia.')
        st.button('Ver análisis ambiental',type='primary',on_click=goto,args=('Huella Verde',))

elif page=='Huella Verde':
    with st.container(border=True):
        eyebrow('Relación población · arborización · ambiente');st.header('Huella Verde de Lima Metropolitana (2023–2026)');st.caption('Análisis de los cuatro Excel autorizados. Los indicadores conservan las definiciones y unidades originales.')
        c1,c2,c3=st.columns([1,1.5,1]);year=c1.selectbox('Año',[2026,2025,2024,2023],key='hv_year');names=sorted(huella[huella.anio==year].distrito.unique(),key=nombre);k=c2.selectbox('Ámbito',['Lima Metropolitana']+names,format_func=lambda v:v if v=='Lima Metropolitana' else nombre(v));month=c3.selectbox('Mes de referencia',list(range(1,13)),index=7 if year==2026 else 11,format_func=lambda m:MESES[m-1]);s=(resumen[resumen.anio==year] if k=='Lima Metropolitana' else huella[(huella.anio==year)&(huella.distrito==k)]).sort_values('mes');m=s[s.mes==month].iloc[0];upto=s[s.mes<=month];trees=upto.arboles.sum(min_count=1)
        for col,args in zip(st.columns(4),[('Población estimada',fmt(m.poblacion),MESES[month-1],'◉'),('Plantaciones acumuladas',fmt(trees),'Enero a '+MESES[month-1],'🌳'),('CO₂ respiratorio',fmt(m.co2_resp/1000,2)+' t/mes','Estimado · biogénico','◌'),('O₂ '+('asociado al mes' if year==2023 else 'potencial'),fmt(m.o2/1000,2)+' t/mes','Estimación teórica','🍃')]):
            with col:kpi(*args)
        if year==2023:note('2023: el reparto distrital se estimó proporcionalmente a la población; O₂ asociado solo a los árboles plantados ese mes. No se dispone de captura potencial de CO₂ en ese Excel.')
        else:note('2024–2026: O₂ y captura son equivalentes mensuales teóricos de los árboles acumulados en el año a capacidad de un año. No son flujos observados; no se deben interpretar como compensación climática.')
    l,r=st.columns(2)
    with l,st.container(border=True):
        st.subheader('Plantaciones por mes');plot(linechart(s,height=310))
    with r,st.container(border=True):
        st.subheader('Población estimada por mes');f=go.Figure(go.Scatter(x=ABR,y=s.poblacion,mode='lines+markers',line=dict(color=GREEN,width=3),marker=dict(color=MINT,size=8),hovertemplate='%{x}: %{y:,.0f} habitantes<extra></extra>'));plot(layout(f,'Habitantes',310))
    with st.container(border=True):
        st.subheader('Relaciones ambientales');l,r=st.columns(2)
        with l:
            st.markdown('**CO₂ respiratorio y captura potencial**')
            if year==2023:st.info('Captura de CO₂ no disponible para 2023. No se sustituye por O₂.')
            else:
                f=go.Figure();f.add_scatter(x=ABR,y=s.co2_resp/1000,name='CO₂ respiratorio',mode='lines+markers',line=dict(color='#B89778'));f.add_scatter(x=ABR,y=s.captura/1000,name='Captura potencial',mode='lines+markers',line=dict(color=GREEN));f=layout(f,'t/mes',330,True);f.update_yaxes(type='log',rangemode='normal',title='t/mes · escala logarítmica');plot(f);st.caption('Los valores cero no aparecen en escala logarítmica; consultar tabla.')
                st.metric('Captura potencial de CO₂ · '+MESES[month-1],fmt(m.captura/1000,3)+' t/mes')
        with r:
            st.markdown('**Oxígeno estimado / potencial**');f=go.Figure(go.Scatter(x=ABR,y=s.o2/1000,mode='lines+markers',fill='tozeroy',line=dict(color='#7DB8D3'),fillcolor='rgba(192,225,240,.45)'));plot(layout(f,'t/mes',330));st.caption('Oxígeno y CO₂ son sustancias distintas. No se restan para calcular una compensación.')
    with st.container(border=True):
        st.subheader('Población vs. arborización por distrito');d=huella[(huella.anio==year)&(huella.mes<=month)];agg=d.groupby('distrito').arboles.sum(min_count=1).rename('arboles').to_frame().join(d[d.mes==month].set_index('distrito').poblacion);agg['intensidad']=agg.arboles/agg.poblacion*1000;agg['nombre']=[nombre(i) for i in agg.index];f=go.Figure(go.Scatter(x=agg.poblacion,y=agg.arboles,mode='markers',text=agg.nombre,customdata=agg.intensidad,marker=dict(color=agg.intensidad,colorscale=['#E2F0E2','#8FC69E','#43805C'],size=12,showscale=True,colorbar=dict(title='Árb./1000 hab.')),hovertemplate='%{text}<br>Población: %{x:,.0f}<br>Plantaciones: %{y:,.0f}<br>Por 1000 hab.: %{customdata:.2f}<extra></extra>'));f=layout(f,'Árboles acumulados',380);f.update_xaxes(title='Población estimada del mes');plot(f);st.caption('Relación descriptiva, no causal. En 2023 los árboles se asignaron proporcionalmente a población, por lo que la relación es parte del método de estimación.')
        st.dataframe(agg[['nombre','poblacion','arboles','intensidad']].sort_values('intensidad',ascending=False),column_config={'nombre':'Distrito','poblacion':st.column_config.NumberColumn('Habitantes estimados',format='%d'),'arboles':st.column_config.NumberColumn('Árboles acumulados',format='%d'),'intensidad':st.column_config.NumberColumn('Árboles / 1000 hab.',format='%.2f')},hide_index=True,use_container_width=True)
    with st.expander('Metodología original del Excel seleccionado'):
        st.dataframe(metodos[year],hide_index=True,use_container_width=True);note('CO₂ respiratorio biogénico: no equivale a emisiones fósiles ni a huella climática neta. La capacidad teórica no demuestra captura real.')
    with st.expander('Descargar datos de la selección'):
        tabla=s.copy();tabla['mes']=tabla.mes.map(lambda m:MESES[m-1]);st.dataframe(tabla,hide_index=True,use_container_width=True);st.download_button('Descargar CSV de indicadores',tabla.to_csv(index=False).encode('utf-8-sig'),f'huella_verde_{year}.csv','text/csv')

with st.expander('Fuentes, control de calidad y descarga de datos'):
    st.markdown('**Comparación de los registros de árboles entre fuentes, sin conciliación artificial.**')
    summary=comp.groupby('anio')[['csv_programa','excel','csv_distritos']].sum(min_count=1).reset_index();summary['diferencia_excel_csv']=summary.excel-summary.csv_programa;st.dataframe(summary,hide_index=True,use_container_width=True)
    detail=comp.copy();detail['mes']=detail.mes.map(lambda m:MESES[m-1]);st.dataframe(detail,hide_index=True,use_container_width=True);st.download_button('Descargar comparación mensual',detail.to_csv(index=False).encode('utf-8-sig'),'comparacion_fuentes.csv','text/csv')
    note('CSV programa: total histórico y cumplimiento. CSV distritos: distribución 2026. Excel Huella Verde: población estimada, plantaciones y relaciones ambientales 2023–2026. Los meses vacíos del CSV se conservan; los ceros del Excel se mantienen como están. No se emplea el Excel de población descartado.')
    for year,filename in ARCHIVOS.items():
        st.caption(filename)
    st.caption('Repositorio: programa_arborizacion.csv · distribucion_distritos.csv')
html('<div class="foot">Arborización en Lima · Proyecto académico de visualización de datos · Fuentes proporcionadas por el usuario; estimaciones ambientales referenciales.</div>')
