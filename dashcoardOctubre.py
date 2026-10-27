import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Ventas Avanzado", layout="wide")

# 1. Cargar Datos
file_path = 'SalidaVentas.xlsx'

@st.cache_data
def load_data():
    data = pd.read_excel(file_path)
    data['Profit Margin %'] = (data['Profit'] / data['Sales']) * 100
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo de Excel: {e}")
    st.stop()

# --- BARRA LATERAL: FILTROS DINÁMICOS ---
st.sidebar.header("🎯 Panel de Control y Filtros")

regiones = ['Todas'] + sorted(list(df['Region'].unique()))
region_sel = st.sidebar.selectbox("Región:", regiones)

if region_sel != 'Todas':
    df_filtered = df[df['Region'] == region_sel]
else:
    df_filtered = df

estados = ['Todos'] + sorted(list(df_filtered['State'].unique()))
estado_sel = st.sidebar.selectbox("Estado:", estados)

if estado_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['State'] == estado_sel]

categorias = ['Todas'] + sorted(list(df_filtered['Category'].unique()))
categoria_sel = st.sidebar.selectbox("Categoría de Producto:", categorias)

if categoria_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['Category'] == categoria_sel]

# --- TITULO PRINCIPAL ---
st.title("📊 Dashboard Interactivo de Ventas y Rentabilidad")
st.markdown("### Explora el rendimiento comercial, márgenes y áreas de oportunidad en tiempo real.")
st.markdown("---")

# --- PESTAÑAS PRINCIPALES ---
resumen_tab, mapa_tab, alertas_tab = st.tabs(["Resumen", "Mapa de ventas", "Alertas"])

with resumen_tab:
    ventas_totales = df_filtered['Sales'].sum()
    ganancias_totales = df_filtered['Profit'].sum()
    margen_promedio = (ganancias_totales / ventas_totales * 100) if ventas_totales != 0 else 0
    transacciones = len(df_filtered)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="💰 Ventas Totales", value=f"${ventas_totales:,.2f}")
    with kpi2:
        st.metric(label="📈 Ganancia/Pérdida Neta", value=f"${ganancias_totales:,.2f}",
                  delta=f"{(ganancias_totales/ventas_totales*100):.1f}% de Margen" if ventas_totales != 0 else "0%")
    with kpi3:
        st.metric(label="🎯 Margen General Promedio", value=f"{margen_promedio:.2f}%")
    with kpi4:
        st.metric(label="📦 Transacciones", value=f"{transacciones:,}")

    st.markdown("---")

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("📌 Ventas y Ganancias por Subcategoría")
        df_sub = df_filtered.groupby('Sub-Category')[['Sales', 'Profit']].sum().reset_index().sort_values(by='Sales', ascending=False)

        fig_sub = px.bar(
            df_sub,
            x='Sub-Category',
            y='Sales',
            color='Profit',
            color_continuous_scale='RdYlGn',
            title="Ventas Totales con Código de Color de Rentabilidad (Profit)",
            labels={'Sales': 'Ventas ($)', 'Profit': 'Ganancias ($)', 'Sub-Category': 'Subcategoría'}
        )
        st.plotly_chart(fig_sub, use_container_width=True)

    with col_der:
        st.subheader("📉 Curva de Impacto del Descuento en la Rentabilidad")
        fig_scatter = px.scatter(
            df_filtered,
            x='Discount',
            y='Profit',
            color='Category',
            hover_data=['State', 'Sub-Category', 'Sales'],
            title="Relación entre Descuento (%) y Ganancia ($)",
            labels={'Discount': 'Descuento', 'Profit': 'Ganancia/Pérdida ($)'},
            opacity=0.7
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Top 10 Productos Más Vendidos por Categoría")

    product_columns = ['Product Name', 'Product', 'Product_Name', 'Product name']
    product_col = next((col for col in product_columns if col in df_filtered.columns), None)

    if product_col:
        df_top_products = (
            df_filtered.groupby([product_col, 'Category'], as_index=False)['Sales']
            .sum()
            .sort_values(by='Sales', ascending=False)
            .head(10)
        )

        fig_top_products = px.bar(
            df_top_products,
            x='Sales',
            y=product_col,
            color='Category',
            orientation='h',
            text_auto='$.2s',
            title='Top 10 productos más vendidos por categoría',
            labels={'Sales': 'Ventas ($)', product_col: 'Producto', 'Category': 'Categoría'}
        )
        fig_top_products.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top_products, use_container_width=True)
    else:
        st.info("No se encontró una columna de producto en los datos para mostrar el top 10.")

with mapa_tab:
    state_abbrev = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
    }

    if 'State' in df_filtered.columns:
        df_map = (
            df_filtered.groupby('State', as_index=False)['Sales']
            .sum()
            .rename(columns={'Sales': 'Ventas'})
            .sort_values('Ventas', ascending=False)
        )
        df_map['CodigoEstado'] = df_map['State'].map(state_abbrev)
        df_map = df_map.dropna(subset=['CodigoEstado']).copy()

        if not df_map.empty:
            fig_map = px.choropleth(
                df_map,
                locations='CodigoEstado',
                locationmode='USA-states',
                color='Ventas',
                scope='usa',
                color_continuous_scale='Viridis',
                title='Ventas por Estado (escala de color)',
                labels={'Ventas': 'Ventas ($)', 'State': 'Estado'},
                hover_name='State',
                hover_data={'Ventas': ':.2f'}
            )
            fig_map.update_layout(
                template='plotly_white',
                geo=dict(bgcolor='white'),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No hay datos geográficos válidos para mostrar el mapa.")
    else:
        st.info("La columna 'State' no está disponible para mostrar el mapa.")

with alertas_tab:
    st.subheader("⚠️ Focos de Alerta (Transacciones con Pérdidas Críticas)")
    df_alertas = df_filtered[df_filtered['Profit'] < 0].sort_values(by='Profit').head(50)

    if not df_alertas.empty:
        st.warning(f"Se encontraron {len(df_alertas)} transacciones con pérdidas bajo los filtros actuales. Mostrando las 50 más críticas:")
        st.dataframe(df_alertas[['State', 'Category', 'Sub-Category', 'Sales', 'Discount', 'Profit', 'Profit Margin %']].style.format({
            'Sales': '${:,.2f}',
            'Discount': '{:.2%}',
            'Profit': '${:,.2f}',
            'Profit Margin %': '{:.2f}%'
        }))
    else:
        st.success("🎉 ¡Felicidades! No se registran pérdidas críticas en la selección actual.")
