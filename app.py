import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import numpy as np
import os
import json
import time
import requests
from alphagenome.data import genome
from alphagenome.models import dna_client

# ─── Paths ───────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_datasets")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_results")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─── Tissue Catalog ─────────────────────────────────────────────────────────
TEJIDOS = {
    'Cerebro':   'UBERON:0000955',
    'Corazón':   'UBERON:0000948',
    'Hígado':    'UBERON:0002107',
    'Pulmón':    'UBERON:0002048',
    'Colon':     'UBERON:0001157',
    'Riñón':     'UBERON:0002113',
    'Páncreas':  'UBERON:0001264',
    'Próstata':  'UBERON:0002367',
    'Ovario':    'UBERON:0000992',
    'Mama':      'UBERON:0008367',
    'Piel':      'UBERON:0002097',
    'Adiposo':   'UBERON:0001013',
    'Músculo':   'UBERON:0001134',
    'Tiroides':  'UBERON:0002046',
    'Bazo':      'UBERON:0002106',
}

GENES_RIESGO = {
    'BRCA1 – Cáncer de mama':     (['rs28897672','rs80357382','rs80357914'], 'UBERON:0008367'),
    'APOE – Alzheimer':           (['rs429358','rs7412'],                    'UBERON:0001954'),
    'MTHFR – Homocisteína':       (['rs1801133','rs1801131'],                'UBERON:0002107'),
    'LDLR – Colesterol':          (['rs28942080','rs28942082'],              'UBERON:0002107'),
    'HFE – Hemocromatosis':       (['rs1800562','rs1799945'],                'UBERON:0002107'),
    'CYP2C19 – Fármacos':        (['rs4244285','rs4986893','rs12248560'],   'UBERON:0002107'),
    'TP53 – Cáncer general':      (['rs28934578','rs28934574'],              'UBERON:0000955'),
    'MUTYH – Cáncer de colon':    (['rs34612342','rs36053993'],              'UBERON:0001157'),
    'PCSK9 – Cardiovascular':     (['rs11591147','rs562556'],                'UBERON:0000948'),
}

EXPLICACIONES_RIESGO = {
    'BRCA1 – Cáncer de mama': 'Produce proteínas que reparan el ADN. Variantes aquí pueden aumentar la probabilidad de desarrollar cáncer de mama y ovario.',
    'APOE – Alzheimer': 'Ayuda a transportar el colesterol. Ciertas variantes están muy asociadas con un mayor riesgo de desarrollar Alzheimer en el futuro.',
    'MTHFR – Homocisteína': 'Procesa la Vitamina B9 (folato). Variantes pueden causar problemas leves de circulación o deficiencia vitamínica.',
    'LDLR – Colesterol': 'Elimina el "colesterol malo" (LDL) de la sangre. Sus variantes predisponen a tener el colesterol alto de forma hereditaria.',
    'HFE – Hemocromatosis': 'Regula cuánto hierro de la dieta absorbe el cuerpo. Mutaciones hacen que acumules un exceso de hierro.',
    'CYP2C19 – Fármacos': 'Controla a qué velocidad tu hígado procesa medicamentos (ej: antidepresivos, omeprazol). Determina la dosis que necesitas.',
    'TP53 – Cáncer general': 'Conocido como el "guardián del genoma". Previene que las células crezcan sin control. Sus variantes elevan el riesgo de varios cánceres.',
    'MUTYH – Cáncer de colon': 'Repara pequeños errores en el ADN. Variantes en este gen aumentan el riesgo de desarrollar pólipos y cáncer de colon.',
    'PCSK9 – Cardiovascular': 'Controla la cantidad de receptores de colesterol. Variantes aquí alteran tu riesgo de sufrir problemas de corazón.'
}

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaGenome Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #0e1117; }
    
    h1 { 
        background: linear-gradient(135deg, #00d9ff, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem !important;
    }
    h2 { color: #00b8d4; }
    h3 { color: #e0e0e0; }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .stMetric:hover { transform: translateY(-2px); }
    .stMetric label { color: white !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 28px !important; }
    .stMetric [data-testid="stMetricDelta"] { color: #e0e0e0 !important; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1d23;
        border-radius: 8px;
        padding: 8px 16px;
        color: #aaa;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #151820 100%);
        border-right: 1px solid #2a2d35;
    }
    
    .saved-dataset-card {
        background: linear-gradient(135deg, #1a1d23, #22252d);
        border: 1px solid #2a2d35;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 6px 0;
        transition: border-color 0.2s;
    }
    .saved-dataset-card:hover { border-color: #667eea; }
    
    .hero-card {
        background: linear-gradient(135deg, #1a1d23, #22252d);
        border: 1px solid #2a2d35;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .hero-card:hover { transform: translateY(-4px); border-color: #667eea; }
    .hero-card h3 { margin-bottom: 8px; }
    .hero-card p  { color: #999; font-size: 0.9rem; }
    
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-high   { background: #ff444433; color: #ff6b6b; border: 1px solid #ff444455; }
    .badge-medium { background: #ffbb3333; color: #ffc107; border: 1px solid #ffbb3355; }
    .badge-low    { background: #00C85133; color: #69f0ae; border: 1px solid #00C85155; }
</style>
""", unsafe_allow_html=True)

# ─── Helper Functions ────────────────────────────────────────────────────────

def get_gene_symbols(rsids):
    if not rsids: return {}
    try:
        url = 'https://myvariant.info/v1/query'
        data = {'q': ','.join(rsids), 'scopes': 'dbsnp.rsid', 'fields': 'dbsnp.gene.symbol'}
        res = requests.post(url, data=data).json()
        mapping = {}
        for r in res:
            if 'query' in r and 'dbsnp' in r and 'gene' in r['dbsnp']:
                sym = r['dbsnp']['gene'].get('symbol')
                if sym: mapping[r['query']] = sym
        return mapping
    except:
        return {}

def list_saved_datasets():
    """Return list of (name, filepath) tuples for saved datasets."""
    datasets = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith('.csv'):
            name = f.replace('.csv', '')
            datasets.append((name, os.path.join(DATA_DIR, f)))
    return datasets

def save_dataset(name, df_raw):
    """Save a raw DataFrame to disk under a given name."""
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()
    path = os.path.join(DATA_DIR, f"{safe}.csv")
    df_raw.to_csv(path, index=False)
    return path

def list_saved_results():
    """Return list of (name, filepath) for saved analysis results."""
    results = []
    for f in sorted(os.listdir(RESULTS_DIR)):
        if f.endswith('.xlsx'):
            name = f.replace('.xlsx', '')
            results.append((name, os.path.join(RESULTS_DIR, f)))
    return results

def save_results(name, df_results):
    """Persist analysis results."""
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()
    path = os.path.join(RESULTS_DIR, f"{safe}.xlsx")
    df_results.to_excel(path, index=False)
    return path

def parse_dna_file(uploaded_file_or_path):
    """Parse a MyHeritage / 23andMe file into a clean DataFrame."""
    if isinstance(uploaded_file_or_path, str):
        if uploaded_file_or_path.endswith('.xlsx'):
            df_raw = pd.read_excel(uploaded_file_or_path, dtype=str)
        else:
            df_raw = pd.read_csv(uploaded_file_or_path, comment='#', sep=',', dtype=str)
    else:
        if uploaded_file_or_path.name.endswith('.xlsx'):
            df_raw = pd.read_excel(uploaded_file_or_path, dtype=str)
        else:
            df_raw = pd.read_csv(uploaded_file_or_path, comment='#', sep=',', dtype=str)
    
    df_raw.columns = [c.strip().strip('"').lower() for c in df_raw.columns]
    if 'result' in df_raw.columns:
        df_raw = df_raw.rename(columns={'result': 'genotype'})
    
    # Clean quotes from values
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip('"')
    
    return df_raw

def filter_heterozygous(df_raw):
    """Filter to only heterozygous SNP variants."""
    df = df_raw.dropna(subset=['rsid', 'chromosome', 'position', 'genotype']).copy()
    df = df[df['rsid'].str.startswith('rs')]
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    df = df.dropna(subset=['position'])
    df['position'] = df['position'].astype(int)
    df = df[df['genotype'].str.len() == 2]
    df = df[~df['genotype'].str.contains('-')]
    df = df[df['genotype'].apply(lambda g: g[0] != g[1])]
    return df

def classify_impact(val, thresholds):
    """Classify an impact value into Alto/Moderado/Bajo."""
    if val >= thresholds[1]:
        return 'Alto'
    elif val >= thresholds[0]:
        return 'Moderado'
    return 'Bajo'

def run_multitissue_analysis(model, df_variants, tissues_selected, max_vars, progress_container):
    """Run RNA-seq analysis across selected tissues. Returns a DataFrame."""
    subset = df_variants.head(max_vars).copy()
    resultados = []
    total_ops = len(subset) * len(tissues_selected)
    current_op = 0
    
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    for _, row in subset.iterrows():
        rsid     = row['rsid']
        chrom    = 'chr' + str(row['chromosome'])
        pos      = int(row['position'])
        genotype = row['genotype']
        ref_allele = genotype[0]
        alt_allele = genotype[1]
        
        MITAD = 262144
        start = max(0, pos - MITAD)
        end   = start + 524288
        
        fila = {
            'rsid': rsid,
            'cromosoma': chrom,
            'posicion': pos,
            'genotipo': genotype,
        }
        
        for tissue_name in tissues_selected:
            ontology = TEJIDOS[tissue_name]
            current_op += 1
            pct = current_op / total_ops
            progress_bar.progress(pct)
            status_text.text(f"[{current_op}/{total_ops}] {rsid} → {tissue_name}...")
            
            try:
                interval = genome.Interval(chromosome=chrom, start=start, end=end)
                variant  = genome.Variant(
                    chromosome=chrom, position=pos,
                    reference_bases=ref_allele, alternate_bases=alt_allele
                )
                output = model.predict_variant(
                    interval=interval, variant=variant,
                    ontology_terms=[ontology],
                    requested_outputs=[dna_client.OutputType.RNA_SEQ]
                )
                ref_vals = output.reference.rna_seq.values
                alt_vals = output.alternate.rna_seq.values
                impacto  = float(np.abs(alt_vals - ref_vals).max())
                fila[tissue_name] = round(impacto, 6)
            except Exception as e:
                fila[tissue_name] = None
        
        resultados.append(fila)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Análisis multitejido completado. Buscando genes...")
    
    gene_map = get_gene_symbols([r['rsid'] for r in resultados])
    for r in resultados:
        sym = gene_map.get(r['rsid'])
        r['gen_asociado'] = sym if sym else 'Desconocido'
        r['etiqueta_grafico'] = f"{r['rsid']} (Gen: {sym})" if sym else r['rsid']
        
    time.sleep(0.5)
    
    return pd.DataFrame(resultados)

def run_disease_risk_analysis(model, df_all_variants, progress_container):
    """Scan for known disease-risk variants and score them."""
    resultados = []
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    total = sum(1 for rsids, _ in GENES_RIESGO.values() for _ in rsids)
    current = 0
    
    for enfermedad, (rsids, tejido) in GENES_RIESGO.items():
        df_filt = df_all_variants[df_all_variants['rsid'].isin(rsids)]
        
        for rs in rsids:
            current += 1
            progress_bar.progress(current / total)
            
            match = df_filt[df_filt['rsid'] == rs]
            if match.empty:
                resultados.append({
                    'enfermedad': enfermedad, 'rsid': rs,
                    'estado': 'No encontrado', 'genotipo': '-',
                    'impacto': 0.0
                })
                continue
            
            row = match.iloc[0]
            genotype = row['genotype']
            
            if len(genotype) != 2 or genotype[0] == genotype[1] or '-' in genotype:
                resultados.append({
                    'enfermedad': enfermedad, 'rsid': rs,
                    'estado': f'Homocigoto ({genotype})', 'genotipo': genotype,
                    'impacto': 0.0
                })
                continue
            
            chrom = 'chr' + str(row['chromosome'])
            pos   = int(row['position'])
            status_text.text(f"[{current}/{total}] {enfermedad}: {rs}...")
            
            MITAD = 262144
            start = max(0, pos - MITAD)
            end   = start + 524288
            
            try:
                interval = genome.Interval(chromosome=chrom, start=start, end=end)
                variant  = genome.Variant(
                    chromosome=chrom, position=pos,
                    reference_bases=genotype[0], alternate_bases=genotype[1]
                )
                output = model.predict_variant(
                    interval=interval, variant=variant,
                    ontology_terms=[tejido],
                    requested_outputs=[dna_client.OutputType.RNA_SEQ]
                )
                impacto = float(np.abs(
                    output.alternate.rna_seq.values - output.reference.rna_seq.values
                ).max())
                resultados.append({
                    'enfermedad': enfermedad, 'rsid': rs,
                    'estado': 'Heterocigoto', 'genotipo': genotype,
                    'impacto': round(impacto, 8)
                })
            except Exception as e:
                resultados.append({
                    'enfermedad': enfermedad, 'rsid': rs,
                    'estado': f'Error: {e}', 'genotipo': genotype,
                    'impacto': 0.0
                })
    
    progress_bar.progress(1.0)
    status_text.text("✅ Análisis de riesgo completado.")
    time.sleep(0.5)
    
    return pd.DataFrame(resultados)


# ═══════════════════════════════════════════════════════════════════════════════
# ██  HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("# 🧬 AlphaGenome Dashboard")
st.markdown(
    "<p style='text-align:center; color:#888; margin-top:-10px;'>"
    "Análisis genómico avanzado con IA de Google DeepMind · Solo investigación</p>",
    unsafe_allow_html=True
)

# ═══════════════════════════════════════════════════════════════════════════════
# ██  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image(
        "https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/"
        "alphagenome-ai-for-better-understanding-the-genome/thumb.jpg",
        width=250
    )
    st.markdown("## ⚙️ Configuración")
    
    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        value="AIzaSyAu36KLIL87KOPFRMs9GSBloshKrHvq6mE"
    )
    
    st.markdown("---")
    
    # ── Data Source ──────────────────────────────────────────────────────────
    st.markdown("### 📂 Datos de ADN")
    
    data_source = st.radio(
        "Origen de datos:",
        ["📤 Subir nuevo archivo", "💾 Cargar guardado"],
        label_visibility="collapsed"
    )
    
    active_df_raw = None
    active_dataset_name = None
    
    if data_source == "📤 Subir nuevo archivo":
        uploaded_file = st.file_uploader(
            "CSV / XLSX de MyHeritage o 23andMe",
            type=["csv", "xlsx"]
        )
        if uploaded_file:
            dataset_name = st.text_input(
                "💾 Nombre para guardar este dataset:",
                value=uploaded_file.name.rsplit('.', 1)[0],
                help="El archivo se guardará con este nombre para que puedas cargarlo después sin volver a subirlo."
            )
            
            if st.button("💾 Guardar dataset", use_container_width=True):
                try:
                    df_temp = parse_dna_file(uploaded_file)
                    uploaded_file.seek(0)  # reset for later use
                    save_dataset(dataset_name, df_temp)
                    st.success(f"Guardado como '{dataset_name}'")
                except Exception as e:
                    st.error(f"Error guardando: {e}")
            
            try:
                active_df_raw = parse_dna_file(uploaded_file)
                uploaded_file.seek(0)
                active_dataset_name = dataset_name
                st.success(f"✅ {uploaded_file.name} ({len(active_df_raw)} filas)")
            except Exception as e:
                st.error(f"Error leyendo: {e}")
    else:
        saved = list_saved_datasets()
        if saved:
            names = [n for n, _ in saved]
            chosen = st.selectbox("Dataset guardado:", names)
            path = dict(saved)[chosen]
            try:
                active_df_raw = parse_dna_file(path)
                active_dataset_name = chosen
                st.success(f"✅ {chosen} ({len(active_df_raw)} filas)")
            except Exception as e:
                st.error(f"Error cargando: {e}")
        else:
            st.info("No hay datasets guardados aún.")
    
    st.markdown("---")
    
    # ── Analysis Configuration ──────────────────────────────────────────────
    st.markdown("### 🔬 Configuración del análisis")
    
    max_variants = st.slider(
        "Máx. variantes a analizar",
        min_value=1, max_value=100, value=5,
        help="Cada variante × cada tejido = 1 llamada a la API. Empieza con pocos para probar."
    )
    
    selected_tissues = st.multiselect(
        "🫀 Tejidos a analizar",
        list(TEJIDOS.keys()),
        default=['Cerebro', 'Corazón', 'Hígado', 'Colon', 'Mama'],
        help="Selecciona los tejidos para el análisis multitejido."
    )
    
    st.markdown("---")
    st.markdown("### 📏 Umbrales de impacto")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        threshold_low = st.number_input("Moderado ≥", value=2.0, step=0.5, format="%.1f")
    with col_t2:
        threshold_high = st.number_input("Alto ≥", value=5.0, step=0.5, format="%.1f")
    
    st.markdown("---")
    
    # ── Chromosome Filter ───────────────────────────────────────────────────
    filter_chrom = st.multiselect(
        "🧲 Filtrar cromosomas (vacío = todos)",
        [str(i) for i in range(1,23)] + ['X', 'Y'],
        default=[]
    )
    
    st.markdown("---")
    st.info("🔬 **Nota**: Solo para investigación no comercial. No válido para uso clínico.")

# ═══════════════════════════════════════════════════════════════════════════════
# ██  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

if active_df_raw is None:
    # ── Welcome Screen ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Sube un archivo de ADN o carga uno guardado en la barra lateral para comenzar.")
    
    st.markdown("## 📊 Capacidades de la plataforma")
    
    cards = [
        ("🧬", "Expresión génica", "Analiza el impacto de tus variantes en la expresión de genes en hasta 15 tejidos diferentes"),
        ("✂️", "Splicing", "Identifica cómo tus variantes afectan el procesamiento alternativo del ARN"),
        ("🔬", "Epigenética", "Estudia modificaciones de histonas y accesibilidad de la cromatina"),
        ("🏥", "Riesgo de enfermedades", "Escanea variantes de riesgo conocidas (BRCA1, APOE, MTHFR, etc.)"),
        ("📊", "Visualizaciones", "Heatmaps multitejido, gráficos radiales, distribución cromosómica y más"),
        ("💾", "Persistencia", "Guarda tus datos de ADN con nombre para recuperarlos en cualquier momento"),
    ]
    
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(
                f"<div class='hero-card'>"
                f"<h2 style='margin:0; font-size:2.5rem;'>{icon}</h2>"
                f"<h3>{title}</h3>"
                f"<p>{desc}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
    
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
        ],
        "Estado": ["✅ Activo", "🔜 Próximamente", "🔜 Próximamente", "🔜 Próximamente",
                   "🔜 Próximamente", "🔜 Próximamente", "🔜 Próximamente"]
    })
    st.dataframe(df_info, use_container_width=True, hide_index=True)

else:
    # ── Parse & Filter ──────────────────────────────────────────────────────
    try:
        df_het = filter_heterozygous(active_df_raw)
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        st.stop()
    
    if filter_chrom:
        df_het = df_het[df_het['chromosome'].isin(filter_chrom)]
    
    # ── Stats Banner ────────────────────────────────────────────────────────
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("📁 Total filas", f"{len(active_df_raw):,}")
    with col_s2:
        st.metric("🧬 Heterocigotas", f"{len(df_het):,}")
    with col_s3:
        chrom_count = df_het['chromosome'].nunique() if not df_het.empty else 0
        st.metric("🔢 Cromosomas", str(chrom_count))
    with col_s4:
        st.metric("🎯 A analizar", str(min(max_variants, len(df_het))))
    
    st.divider()
    
    # ── Tabs ────────────────────────────────────────────────────────────────
    tab_overview, tab_multitissue, tab_disease, tab_explore, tab_history, tab_export = st.tabs([
        "📊 Vista general",
        "🫀 Análisis multitejido",
        "🏥 Riesgo enfermedades",
        "🔎 Explorar datos",
        "📂 Resultados guardados",
        "📥 Exportar"
    ])
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 1: Overview
    # ════════════════════════════════════════════════════════════════════════
    with tab_overview:
        st.markdown("## 📊 Vista general de tu archivo genómico")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Chromosome distribution
            chrom_counts = df_het['chromosome'].value_counts()
            # Sort chromosomes numerically
            chrom_order = sorted(
                chrom_counts.index,
                key=lambda x: int(x) if x.isdigit() else (23 if x=='X' else 24)
            )
            chrom_counts = chrom_counts.reindex(chrom_order)
            
            fig_chrom = go.Figure(data=[
                go.Bar(
                    x=['chr'+str(c) for c in chrom_counts.index],
                    y=chrom_counts.values,
                    marker=dict(
                        color=chrom_counts.values,
                        colorscale='Viridis',
                        showscale=False
                    ),
                    hovertemplate='%{x}: %{y} variantes<extra></extra>'
                )
            ])
            fig_chrom.update_layout(
                title="Distribución de variantes heterocigotas por cromosoma",
                xaxis_title="Cromosoma",
                yaxis_title="Nº variantes",
                height=400,
                template="plotly_dark",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_chrom, use_container_width=True)
        
        with col_b:
            # Genotype distribution pie
            genotype_counts = df_het['genotype'].value_counts().head(15)
            fig_geno = go.Figure(data=[
                go.Pie(
                    labels=genotype_counts.index,
                    values=genotype_counts.values,
                    hole=0.45,
                    marker=dict(colors=px.colors.qualitative.Set3),
                    textinfo='label+percent',
                    hovertemplate='%{label}: %{value} variantes (%{percent})<extra></extra>'
                )
            ])
            fig_geno.update_layout(
                title="Top 15 genotipos heterocigotos",
                height=400,
                template="plotly_dark",
                showlegend=False
            )
            st.plotly_chart(fig_geno, use_container_width=True)
        
        # Position density scatter
        if not df_het.empty:
            sample_size = min(2000, len(df_het))
            df_sample = df_het.sample(n=sample_size, random_state=42)
            df_sample['chrom_num'] = df_sample['chromosome'].apply(
                lambda x: int(x) if x.isdigit() else (23 if x=='X' else 24)
            )
            
            fig_scatter = px.scatter(
                df_sample,
                x='position', y='chrom_num',
                color='chromosome',
                hover_data=['rsid', 'genotype'],
                title="Mapa de posición genómica (muestra aleatoria)",
                labels={'position': 'Posición (bp)', 'chrom_num': 'Cromosoma'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_scatter.update_layout(
                height=350,
                template="plotly_dark",
                showlegend=False,
                yaxis=dict(tickvals=list(range(1,25)),
                          ticktext=[str(i) for i in range(1,23)] + ['X','Y'])
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 2: Multi-tissue Analysis
    # ════════════════════════════════════════════════════════════════════════
    with tab_multitissue:
        st.markdown("## 🫀 Análisis de expresión génica multitejido (RNA-seq)")
        
        if not selected_tissues:
            st.warning("Selecciona al menos un tejido en la barra lateral.")
        else:
            st.markdown(
                f"**Configuración actual**: {max_variants} variantes × "
                f"{len(selected_tissues)} tejidos = "
                f"**{max_variants * len(selected_tissues)} llamadas API**"
            )
            
            result_name = st.text_input(
                "💾 Nombre para los resultados:",
                value=f"multitejido_{active_dataset_name}",
                key="mt_name"
            )
            
            if st.button("🚀 Ejecutar análisis multitejido", type="primary", use_container_width=True):
                progress_area = st.container()
                model = dna_client.create(api_key)
                df_mt = run_multitissue_analysis(model, df_het, selected_tissues, max_variants, progress_area)
                
                st.session_state['mt_results'] = df_mt
                save_results(result_name, df_mt)
                st.success(f"Resultados guardados como '{result_name}'.")
            
            if 'mt_results' in st.session_state and not st.session_state['mt_results'].empty:
                df_mt = st.session_state['mt_results']
                tissue_cols = [c for c in df_mt.columns if c in TEJIDOS]
                
                if tissue_cols:
                    # ── Metrics row ─────────────────────────────────────────
                    df_mt['impacto_max'] = df_mt[tissue_cols].max(axis=1)
                    df_mt['tejido_max']  = df_mt[tissue_cols].idxmax(axis=1)
                    df_mt['categoria']   = df_mt['impacto_max'].apply(
                        lambda v: classify_impact(v, [threshold_low, threshold_high])
                    )
                    
                    alto  = (df_mt['categoria'] == 'Alto').sum()
                    medio = (df_mt['categoria'] == 'Moderado').sum()
                    bajo  = (df_mt['categoria'] == 'Bajo').sum()
                    
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("🧬 Analizadas", str(len(df_mt)))
                    with mc2:
                        st.metric("🔴 Alto impacto", str(alto))
                    with mc3:
                        st.metric("🟡 Moderado", str(medio))
                    with mc4:
                        st.metric("🟢 Bajo", str(bajo))
                    
                    st.divider()
                    
                    # ── Heatmap ─────────────────────────────────────────────
                    st.markdown("### 🗺️ Mapa de calor multitejido")
                    
                    heat_data = df_mt.set_index('etiqueta_grafico')[tissue_cols].apply(pd.to_numeric, errors='coerce')
                    
                    fig_heat = px.imshow(
                        heat_data,
                        color_continuous_scale="YlOrRd",
                        labels=dict(x="Tejido", y="Variante", color="Impacto"),
                        aspect="auto"
                    )
                    fig_heat.update_layout(
                        height=max(300, len(df_mt) * 40 + 100),
                        template="plotly_dark",
                        title="Impacto por variante y tejido"
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                    
                    # ── Charts row ──────────────────────────────────────────
                    col_r1, col_r2 = st.columns(2)
                    
                    with col_r1:
                        # Bar chart: Top variants by max impact
                        df_sorted = df_mt.sort_values('impacto_max', ascending=True)
                        colors = df_sorted['categoria'].map({
                            'Alto': '#ff4444', 'Moderado': '#ffbb33', 'Bajo': '#00C851'
                        })
                        fig_bar = go.Figure(data=[
                            go.Bar(
                                y=df_sorted['etiqueta_grafico'],
                                x=df_sorted['impacto_max'],
                                orientation='h',
                                marker_color=colors,
                                hovertemplate='%{y}: impacto=%{x:.4f}<br>Tejido: ' +
                                    df_sorted['tejido_max'] + '<extra></extra>'
                            )
                        ])
                        fig_bar.update_layout(
                            title="Ranking de variantes por impacto máximo",
                            xaxis_title="Impacto máximo",
                            height=max(300, len(df_mt) * 35 + 100),
                            template="plotly_dark"
                        )
                        # Add threshold lines
                        fig_bar.add_vline(x=threshold_low, line_dash="dash",
                                        line_color="#ffbb33", annotation_text="Moderado")
                        fig_bar.add_vline(x=threshold_high, line_dash="dash",
                                        line_color="#ff4444", annotation_text="Alto")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col_r2:
                        # Radar chart: tissue impact profile for top variant
                        top_var = df_mt.sort_values('impacto_max', ascending=False).iloc[0]
                        radar_vals = [float(top_var.get(t, 0) or 0) for t in tissue_cols]
                        radar_vals.append(radar_vals[0])  # close the polygon
                        
                        fig_radar = go.Figure(data=[
                            go.Scatterpolar(
                                r=radar_vals,
                                theta=tissue_cols + [tissue_cols[0]],
                                fill='toself',
                                fillcolor='rgba(102, 126, 234, 0.3)',
                                line=dict(color='#667eea', width=2),
                                name=top_var['etiqueta_grafico']
                            )
                        ])
                        fig_radar.update_layout(
                            title=f"Perfil de tejidos: {top_var['etiqueta_grafico']}",
                            polar=dict(
                                bgcolor='#0e1117',
                                radialaxis=dict(gridcolor='#333'),
                                angularaxis=dict(gridcolor='#333')
                            ),
                            height=400,
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # ── Tissue averages ─────────────────────────────────────
                    st.markdown("### 📊 Impacto medio por tejido")
                    tissue_means = heat_data.mean().sort_values(ascending=False)
                    fig_tmean = go.Figure(data=[
                        go.Bar(
                            x=tissue_means.index,
                            y=tissue_means.values,
                            marker=dict(
                                color=tissue_means.values,
                                colorscale='Turbo',
                                showscale=True,
                                colorbar=dict(title="Impacto medio")
                            )
                        )
                    ])
                    fig_tmean.update_layout(
                        xaxis_title="Tejido",
                        yaxis_title="Impacto medio",
                        height=350,
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_tmean, use_container_width=True)
                    
                    # ── Pie chart: impact categories ────────────────────────
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        fig_pie = go.Figure(data=[
                            go.Pie(
                                labels=['Alto', 'Moderado', 'Bajo'],
                                values=[alto, medio, bajo],
                                marker=dict(colors=['#ff4444', '#ffbb33', '#00C851']),
                                hole=0.5,
                                textinfo='label+value+percent'
                            )
                        ])
                        fig_pie.update_layout(
                            title="Distribución de categorías de impacto",
                            height=350,
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col_p2:
                        # Impact distribution histogram
                        all_impacts = heat_data.values.flatten()
                        all_impacts = all_impacts[~np.isnan(all_impacts)]
                        fig_hist = go.Figure(data=[
                            go.Histogram(
                                x=all_impacts,
                                nbinsx=30,
                                marker_color='#667eea',
                                opacity=0.8
                            )
                        ])
                        fig_hist.add_vline(x=threshold_low, line_dash="dash",
                                          line_color="#ffbb33", annotation_text="Moderado")
                        fig_hist.add_vline(x=threshold_high, line_dash="dash",
                                          line_color="#ff4444", annotation_text="Alto")
                        fig_hist.update_layout(
                            title="Histograma de todos los impactos",
                            xaxis_title="Impacto",
                            yaxis_title="Frecuencia",
                            height=350,
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # ── Data table ──────────────────────────────────────────
                    st.markdown("### 📋 Tabla completa de resultados")
                    st.dataframe(
                        df_mt.sort_values('impacto_max', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 3: Disease Risk
    # ════════════════════════════════════════════════════════════════════════
    with tab_disease:
        st.markdown("## 🏥 Análisis de riesgo de enfermedades")
        st.markdown(
            "Escaneo de variantes asociadas a enfermedades conocidas "
            "(BRCA1, APOE, MTHFR, LDLR, HFE, CYP2C19, TP53, MUTYH, PCSK9)."
        )
        
        result_name_d = st.text_input(
            "💾 Nombre para los resultados:",
            value=f"riesgo_{active_dataset_name}",
            key="dr_name"
        )
        
        if st.button("🚀 Ejecutar análisis de riesgo", type="primary", use_container_width=True):
            progress_area = st.container()
            model = dna_client.create(api_key)
            # Use unfiltered heterozygous set (no chrom filter) for disease risk
            df_all_het = filter_heterozygous(active_df_raw)
            df_dr = run_disease_risk_analysis(model, df_all_het, progress_area)
            
            st.session_state['dr_results'] = df_dr
            save_results(result_name_d, df_dr)
            st.success(f"Resultados guardados como '{result_name_d}'.")
        
        if 'dr_results' in st.session_state and not st.session_state['dr_results'].empty:
            df_dr = st.session_state['dr_results']
            
            # ── Summary cards ───────────────────────────────────────────
            found     = df_dr[df_dr['estado'] == 'Heterocigoto']
            not_found = df_dr[df_dr['estado'] == 'No encontrado']
            homo      = df_dr[df_dr['estado'].str.startswith('Homocigoto')]
            
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("🟢 Heterocigoto (analizables)", str(len(found)))
            with rc2:
                st.metric("⚪ Homocigoto / Normal", str(len(homo)))
            with rc3:
                st.metric("❌ No encontrado", str(len(not_found)))
            
            st.divider()
            
            if not found.empty:
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    # Bar chart by disease
                    found = found.copy()
                    found['explicacion'] = found['enfermedad'].map(EXPLICACIONES_RIESGO)
                    
                    fig_dis = px.bar(
                        found.sort_values('impacto', ascending=True),
                        y='enfermedad', x='impacto',
                        color='impacto',
                        color_continuous_scale='OrRd',
                        orientation='h',
                        hover_data={'rsid': True, 'genotipo': True, 'impacto': ':.4f', 'explicacion': True},
                        title="Impacto por gen/enfermedad"
                    )
                    fig_dis.update_layout(
                        height=max(300, len(found)*40+100),
                        template="plotly_dark",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_dis, use_container_width=True)
                
                with col_d2:
                    # Radar for diseases
                    disease_names = found['enfermedad'].unique()
                    radar_vals_d = [found[found['enfermedad']==d]['impacto'].max() for d in disease_names]
                    radar_vals_d.append(radar_vals_d[0])
                    
                    fig_rad_d = go.Figure(data=[
                        go.Scatterpolar(
                            r=radar_vals_d,
                            theta=list(disease_names) + [disease_names[0]],
                            fill='toself',
                            fillcolor='rgba(255, 68, 68, 0.2)',
                            line=dict(color='#ff4444', width=2),
                        )
                    ])
                    fig_rad_d.update_layout(
                        title="Perfil de riesgo de enfermedades",
                        polar=dict(
                            bgcolor='#0e1117',
                            radialaxis=dict(gridcolor='#333'),
                            angularaxis=dict(gridcolor='#333')
                        ),
                        height=400,
                        template="plotly_dark",
                        showlegend=False
                    )
                    st.plotly_chart(fig_rad_d, use_container_width=True)
            
            st.markdown("### 📋 Tabla completa explicada")
            
            # Add descriptions to the table
            df_show = df_dr.copy()
            df_show['¿Qué significa este gen?'] = df_show['enfermedad'].map(EXPLICACIONES_RIESGO)
            
            st.dataframe(df_show, use_container_width=True, hide_index=True)
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 4: Data Explorer
    # ════════════════════════════════════════════════════════════════════════
    with tab_explore:
        st.markdown("## 🔎 Explorador de datos crudos")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_rsid = st.text_input("Buscar por RSID (ej: rs3131972):", key="search_rsid")
        with col_f2:
            search_chrom = st.selectbox(
                "Filtrar cromosoma:",
                ["Todos"] + sorted(
                    df_het['chromosome'].unique(),
                    key=lambda x: int(x) if x.isdigit() else 99
                ),
                key="search_chrom"
            )
        
        df_filtered = df_het.copy()
        if search_rsid:
            df_filtered = df_filtered[df_filtered['rsid'].str.contains(search_rsid, case=False)]
        if search_chrom != "Todos":
            df_filtered = df_filtered[df_filtered['chromosome'] == search_chrom]
        
        st.markdown(f"**{len(df_filtered):,}** variantes encontradas")
        st.dataframe(
            df_filtered.head(500),
            use_container_width=True,
            hide_index=True
        )
        
        if len(df_filtered) > 500:
            st.info(f"Mostrando las primeras 500 de {len(df_filtered):,}. Usa los filtros para reducir.")
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 5: Saved Results
    # ════════════════════════════════════════════════════════════════════════
    with tab_history:
        st.markdown("## 📂 Resultados de análisis guardados")
        
        saved_results = list_saved_results()
        
        if not saved_results:
            st.info("Aún no hay resultados guardados. Ejecuta un análisis para generar resultados.")
        else:
            for name, path in saved_results:
                with st.expander(f"📊 {name}", expanded=False):
                    try:
                        df_saved = pd.read_excel(path)
                        st.dataframe(df_saved, use_container_width=True, hide_index=True)
                        
                        # Quick viz if it has tissue columns
                        tissue_cols = [c for c in df_saved.columns if c in TEJIDOS]
                        if tissue_cols and 'rsid' in df_saved.columns:
                            heat_data_s = df_saved.set_index('rsid')[tissue_cols].apply(pd.to_numeric, errors='coerce')
                            fig_h = px.imshow(
                                heat_data_s,
                                color_continuous_scale="YlOrRd",
                                labels=dict(x="Tejido", y="Variante", color="Impacto"),
                                aspect="auto"
                            )
                            fig_h.update_layout(height=300, template="plotly_dark")
                            st.plotly_chart(fig_h, use_container_width=True)
                        
                        # Download button
                        buf = BytesIO()
                        df_saved.to_excel(buf, index=False)
                        st.download_button(
                            f"📥 Descargar {name}.xlsx",
                            data=buf.getvalue(),
                            file_name=f"{name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{name}"
                        )
                    except Exception as e:
                        st.error(f"Error cargando {name}: {e}")
    
    # ════════════════════════════════════════════════════════════════════════
    #  TAB 6: Export
    # ════════════════════════════════════════════════════════════════════════
    with tab_export:
        st.markdown("## 📥 Exportar")
        
        st.markdown("### Datos crudos filtrados")
        buf_raw = BytesIO()
        df_het.to_excel(buf_raw, index=False)
        st.download_button(
            "📊 Descargar variantes heterocigotas (Excel)",
            data=buf_raw.getvalue(),
            file_name=f"variantes_heterocigotas_{active_dataset_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if 'mt_results' in st.session_state and not st.session_state['mt_results'].empty:
            st.markdown("### Resultados multitejido")
            buf_mt = BytesIO()
            st.session_state['mt_results'].to_excel(buf_mt, index=False)
            st.download_button(
                "🫀 Descargar análisis multitejido (Excel)",
                data=buf_mt.getvalue(),
                file_name=f"multitejido_{active_dataset_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        if 'dr_results' in st.session_state and not st.session_state['dr_results'].empty:
            st.markdown("### Resultados riesgo enfermedades")
            buf_dr = BytesIO()
            st.session_state['dr_results'].to_excel(buf_dr, index=False)
            st.download_button(
                "🏥 Descargar análisis de riesgo (Excel)",
                data=buf_dr.getvalue(),
                file_name=f"riesgo_{active_dataset_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ═══════════════════════════════════════════════════════════════════════════════
# ██  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #555; padding: 10px;'>"
    "AlphaGenome Dashboard v2.0 · Powered by Google DeepMind AlphaGenome · "
    "Solo investigación no comercial</div>",
    unsafe_allow_html=True
)
