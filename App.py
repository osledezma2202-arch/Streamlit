%%writefile app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Análisis de Pérdidas - West Region", layout="wide")

# Cargar datos
file_path = 'SalidaVentas.xlsx'
df = pd.read_excel(file_path)

# Filtrar estados de interés
estados_disponibles = ['Oregon', 'Arizona', 'Colorado']
df_perdidas = df[df['State'].isin(estados_disponibles)].copy()

st.title("🔍 Diagnóstico de Pérdidas y Descuentos")
st.markdown("### Estados bajo análisis: Oregon, Arizona y Colorado")

# Barra lateral de filtros
st.sidebar.header("Filtros de Análisis")
estados_seleccionados = st.sidebar.multiselect(
    "Selecciona los Estados:",
    options=estados_disponibles,
    default=estados_disponibles
)

# Filtrar el dataframe según selección
if estados_seleccionados:
    df_filtrado = df_perdidas[df_perdidas['State'].isin(estados_seleccionados)]
else:
    df_filtrado = df_perdidas

# Métricas Clave (KPIs)
ventas_totales = df_filtrado['Sales'].sum()
perdidas_totales = df_filtrado['Profit'].sum()
descuento_medio = df_filtrado['Discount'].mean() * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas Totales", f"${ventas_totales:,.2f}")
with col2:
    st.metric("Ganancia/Pérdida Total", f"${perdidas_totales:,.2f}", delta=f"{perdidas_totales:,.2f}", delta_color="inverse")
with col3:
    st.metric("Descuento Promedio", f"{descuento_medio:.2f}%")

st.markdown("---")

# Secciones de Visualizaciones
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📌 Subcategorías con Pérdidas Netas")
    # Calcular pérdidas
    perdidas_sub = df_filtrado.groupby(['State', 'Sub-Category'])['Profit'].sum().reset_index()
    perdidas_sub = perdidas_sub[perdidas_sub['Profit'] < 0].sort_values(by='Profit')
    
    if not perdidas_sub.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=perdidas_sub,
            x='Sub-Category',
            y='Profit',
            hue='State',
            palette='muted',
            ax=ax1
        )
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("Pérdidas Acumuladas ($)")
        plt.xlabel("Subcategoría")
        st.pyplot(fig1)
    else:
        st.info("No hay pérdidas registradas para la selección actual.")

with col_graf2:
    st.subheader("📉 Impacto de Descuentos en la Rentabilidad")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=df_filtrado,
        x='Discount',
        y='Profit',
        hue='State',
        alpha=0.7,
        palette='Set2',
        ax=ax2
    )
    ax2.axhline(0, color='red', linestyle='--', alpha=0.6)
    plt.xlabel("Descuento (% decimal)")
    plt.ylabel("Ganancia / Pérdida ($)")
    st.pyplot(fig2)

# Tabla de datos interactiva
st.markdown("### 📋 Detalle de Transacciones Seleccionadas")
st.dataframe(df_filtrado[['State', 'Category', 'Sub-Category', 'Sales', 'Quantity', 'Discount', 'Profit']].head(100))
