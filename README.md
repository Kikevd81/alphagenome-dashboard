# 🧬 AlphaGenome Dashboard

Dashboard interactivo para el análisis de datos genómicos (MyHeritage, 23andMe) usando la API de AlphaGenome de Google DeepMind.

## Características

- **📤 Subida y persistencia de datos**: Sube tu CSV/XLSX de ADN y guárdalo con un nombre para recuperarlo más tarde.
- **🫀 Análisis multitejido**: RNA-seq en hasta 15 tejidos simultáneamente con heatmaps, gráficos radiales e histogramas.
- **🏥 Riesgo de enfermedades**: Escaneo automático de variantes asociadas a BRCA1, APOE, MTHFR, LDLR, HFE, CYP2C19, TP53, MUTYH, PCSK9.
- **📊 Visualizaciones ricas**: Distribución cromosómica, genotipos, mapas de calor, radar, barras, histogramas y más.
- **🔎 Explorador de datos**: Busca variantes por RSID o cromosoma directamente en la interfaz.
- **📏 Umbrales configurables**: Ajusta los umbrales de impacto Alto/Moderado/Bajo a tu criterio.
- **📥 Exportación**: Descarga todos los resultados en Excel.

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Uso en Streamlit Cloud

1. Fork este repositorio.
2. Ve a https://share.streamlit.io/ y conecta el repo.
3. Configura la app apuntando a `app.py`.

## Disclaimer

🔬 Solo para investigación no comercial. No válido para uso clínico.