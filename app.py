import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Configuración de página
st.set_page_config(
    page_title="AlphaGenome Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado estilo moderno oscuro
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    h1 {color: #00d9ff; text-align: center; font-weight: 700;}
    h2 {color: #00b8d4;}
    .stMetric {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; padding: 15px;}
    .stMetric label {color: white !important;}
    .stMetric .css-1wivap2 {color: white !important; font-size: 32px !important;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 🧬 AlphaGenome Dashboard")
st.markdown("### Análisis genómico avanzado con IA | Uso no comercial")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/alphagenome-ai-for-better-understanding-the-genome/thumb.jpg", width=250)
    st.markdown("## ⚙️ Configuración")
    
    api_key = st.text_input("API Key de AlphaGenome", type="password", value="AIzaSyAu36KLIL87KOPFRMs9GSBloshKrHvq6mE")
    
    st.markdown("---")
    st.markdown("### Archivos de entrada")
    uploaded_file = st.file_uploader("Sube tu archivo CSV/XLSX de MyHeritage o 23andMe", type=["csv", "xlsx"])
    
    if uploaded_file:
        st.success(f"✅ Archivo cargado: {uploaded_file.name}")
    
    st.markdown("---")
    st.markdown("### Tipos de análisis")
    
    analisis = st.multiselect(
        "Selecciona qué analizar:",
        ["RNA-seq (Tejidos)", "CAGE (Promotores)", "ATAC (Cromatina)", "DNase", 
         "Histonas (Epigenética)", "TF Binding", "Splicing", "Contact Maps"],
        default=["RNA-seq (Tejidos)", "Splicing"]
    )
    
    st.markdown("---")
    st.info("🔬 **Nota**: Solo para investigación no comercial. No válido para uso clínico.")

# Contenido principal
if not uploaded_file:
    st.info("👈 Sube tu archivo de ADN en la barra lateral para comenzar el análisis")
    
    # Demo - mostrar capacidades
    st.markdown("## 📊 Capacidades de la plataforma")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🧬 Expresión génica")
        st.write("Analiza cómo tus variantes afectan la expresión de genes en 17 tejidos diferentes")
    
    with col2:
        st.markdown("### ✂️ Splicing alternativo")
        st.write("Descubre cómo tus variantes modifican el procesamiento del ARN")
    
    with col3:
        st.markdown("### 🔬 Epigenética")
        st.write("Estudia modificaciones de histonas y accesibilidad de la cromatina")
    
    st.divider()
    
    st.markdown("## 🎯 Tipos de análisis disponibles")
    
    df_info = pd.DataFrame({
        "Análisis": ["RNA-seq", "CAGE", "ATAC/DNase", "CHIP_HISTONE", "CHIP_TF", "SPLICE_SITES", "CONTACT_MAPS"],
        "Qué mide": [
            "Expresión génica por tejido",
            "Actividad de promotores (inicio transcripción)",
            "Accesibilidad de la cromatina",
            "Modificaciones epigenéticas de histonas",
            "Factores de transcripción que se unen al ADN",
            "Sitios de splicing alternativo del ARN",
            "Plegamiento 3D del ADN en el núcleo"
        ],
        "Utilidad clínica": [
            "Riesgo de enfermedades, respuesta a fármacos",
            "Regulación de genes, identificación de enhancers",
            "Expresión génica, detección de reguladores",
            "Cáncer, desarrollo, memoria celular",
            "Mutaciones en TF asociadas a enfermedad",
            "Enfermedades genéticas, cáncer",
            "Organización cromosómica, regulación a distancia"
        ]
    })
    
    st.dataframe(df_info, use_container_width=True, hide_index=True)
    
else:
    # Cargar datos
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"✅ Archivo cargado: {len(df)} variantes detectadas")
    
    # Métricas principales (simuladas - aquí conectarías con la API real)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🧬 Variantes analizadas", "127", delta="5 alto impacto")
    with col2:
        st.metric("🔴 Impacto alto", "5", delta="+2 vs población")
    with col3:
        st.metric("🟡 Impacto moderado", "23", delta="Normal")
    with col4:
        st.metric("🟢 Bajo impacto", "99", delta="-5 vs población")
    
    st.divider()
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumen", "🧬 RNA-seq", "✂️ Splicing", "🔬 Epigenética", "📥 Exportar"])
    
    with tab1:
        st.markdown("## 📊 Resumen del análisis genómico")
        
        # Gráfico de ejemplo (aquí usarías datos reales de la API)
        fig_resumen = go.Figure(data=[
            go.Bar(name='Alto', x=['Cerebro', 'Corazón', 'Hígado', 'Pulmón', 'Colon'], y=[5, 3, 4, 2, 6], marker_color='#ff4444'),
            go.Bar(name='Moderado', x=['Cerebro', 'Corazón', 'Hígado', 'Pulmón', 'Colon'], y=[12, 15, 10, 8, 14], marker_color='#ffbb33'),
            go.Bar(name='Bajo', x=['Cerebro', 'Corazón', 'Hígado', 'Pulmón', 'Colon'], y=[30, 28, 35, 40, 25], marker_color='#00C851')
        ])
        fig_resumen.update_layout(
            title="Distribución de impacto de variantes por tejido",
            barmode='stack',
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig_resumen, use_container_width=True)
        
        st.markdown("### 🎯 Variantes de mayor impacto")
        df_top = pd.DataFrame({
            "RSID": ["rs3131972", "rs114525117", "rs12184325"],
            "Cromosoma": ["chr1", "chr1", "chr1"],
            "Posición": [752721, 759036, 754105],
            "Genotipo": ["AG", "AG", "CT"],
            "Tejido más afectado": ["Próstata", "Mama", "Próstata"],
            "Impacto máximo": [3.5, 7.0, 4.0],
            "Tipo": ["RNA-seq", "RNA-seq", "RNA-seq"]
        })
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("## 🧬 Análisis de expresión génica (RNA-seq)")
        
        # Aquí irían los datos reales del análisis multitejido
        st.info("🔄 Conectando con AlphaGenome API para análisis RNA-seq...")
        
        # Simular mapa de calor
        import numpy as np
        tejidos = ['cerebro', 'corazon', 'higado', 'pulmon', 'colon', 'rinon', 'prostata', 'tiroides']
        variantes_muestra = ['rs3131972', 'rs12184325', 'rs114525117', 'rs11240777', 'rs1110052']
        
        data_heat = np.random.rand(len(variantes_muestra), len(tejidos)) * 5
        
        fig_heat = px.imshow(
            data_heat,
            x=tejidos,
            y=variantes_muestra,
            color_continuous_scale="RdYlGn_r",
            labels=dict(x="Tejido", y="Variante", color="Impacto"),
            title="Mapa de calor - Impacto de expresión génica"
        )
        fig_heat.update_layout(height=500, template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with tab3:
        st.markdown("## ✂️ Análisis de splicing alternativo")
        st.info("Analizando sitios de splicing, uso de sitios y uniones de exones...")
        
        # Gráfico de splicing simulado
        fig_splice = go.Figure(data=[
            go.Scatter(x=[1, 2, 3, 4, 5], y=[0.2, 0.8, 0.3, 0.9, 0.4], mode='lines+markers', name='Uso de sitio', line=dict(color='#00d9ff', width=3))
        ])
        fig_splice.update_layout(
            title="Cambios en uso de sitios de splicing",
            xaxis_title="Posición en el gen",
            yaxis_title="Proporción de uso",
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig_splice, use_container_width=True)
    
    with tab4:
        st.markdown("## 🔬 Análisis epigenético")
        st.markdown("### ATAC-seq / DNase (Accesibilidad de cromatina)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Regiones abiertas afectadas", "12")
        with col2:
            st.metric("Modificaciones de histonas", "8")
        
        st.markdown("### Modificaciones de histonas detectadas")
        df_histonas = pd.DataFrame({
            "Variante": ["rs3131972", "rs114525117"],
            "Modificación": ["H3K27ac", "H3K4me3"],
            "Tejido": ["Cerebro", "Hígado"],
            "Cambio": ["+2.1", "-1.8"]
        })
        st.dataframe(df_histonas, use_container_width=True, hide_index=True)
    
    with tab5:
        st.markdown("## 📥 Exportar resultados")
        
        st.markdown("### Formatos disponibles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Crear Excel simulado
            buffer = BytesIO()
            df_export = pd.DataFrame({
                "rsid": ["rs3131972", "rs114525117"],
                "impacto_max": [3.5, 7.0],
                "tejido": ["Prostata", "Mama"]
            })
            df_export.to_excel(buffer, index=False)
            
            st.download_button(
                label="📊 Descargar Excel completo",
                data=buffer.getvalue(),
                file_name="alphagenome_analisis_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            st.download_button(
                label="📄 Descargar informe PDF",
                data="Informe simulado",
                file_name="alphagenome_informe.pdf",
                mime="application/pdf"
            )

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>AlphaGenome Dashboard v1.0 | "
    "Powered by Google DeepMind AlphaGenome | Solo investigación no comercial</div>",
    unsafe_allow_html=True
)
