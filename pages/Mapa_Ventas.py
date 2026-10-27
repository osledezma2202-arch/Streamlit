import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mapa de Ventas por Estado", layout="wide")


@st.cache_data
def load_data():
    data = pd.read_excel("SalidaVentas.xlsx")
    return data


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


df = load_data()

st.title("🗺️ Mapa de Ventas por Estado")
st.markdown("### Visualiza el rendimiento comercial por territorio con una escala de color basada en ventas.")

estados = ["Todos"] + sorted(df["State"].dropna().unique().tolist())
estado_sel = st.sidebar.multiselect("Selecciona estados:", estados, default=["Todos"])

if "Todos" in estado_sel or not estado_sel:
    df_filtered = df.copy()
else:
    df_filtered = df[df["State"].isin(estado_sel)].copy()

ventas_totales = df_filtered["Sales"].sum()
transacciones = len(df_filtered)

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Ventas Totales", f"${ventas_totales:,.2f}")
with col2:
    st.metric("📦 Transacciones", f"{transacciones:,}")

st.markdown("---")

# Agrupar ventas por estado
if "State" not in df_filtered.columns:
    st.error("La columna 'State' no existe en el dataset.")
    st.stop()

df_estado = (
    df_filtered.groupby("State", as_index=False)["Sales"]
    .sum()
    .rename(columns={"Sales": "Ventas"})
    .sort_values("Ventas", ascending=False)
)

df_estado["CodigoEstado"] = df_estado["State"].map(state_abbrev)

df_estado = df_estado.dropna(subset=["CodigoEstado"]).copy()

if df_estado.empty:
    st.warning("No hay estados disponibles con datos válidos para mostrar en el mapa.")
    st.stop()

fig_mapa = px.choropleth(
    df_estado,
    locations="CodigoEstado",
    locationmode="USA-states",
    color="Ventas",
    scope="usa",
    color_continuous_scale="Viridis",
    range_color=(df_estado["Ventas"].min(), df_estado["Ventas"].max()),
    labels={"Ventas": "Ventas ($)", "State": "Estado"},
    title="Ventas por Estado (escala de color)",
    hover_name="State",
    hover_data={"Ventas": ":,.2f"}
)

fig_mapa.update_layout(
    template="plotly_white",
    geo=dict(bgcolor="white"),
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig_mapa, use_container_width=True)

st.markdown("---")

st.subheader("📊 Top 10 Estados por Ventas")

top_estados = df_estado.head(10)

fig_top = px.bar(
    top_estados,
    x="Ventas",
    y="State",
    orientation="h",
    color="Ventas",
    color_continuous_scale="Viridis",
    text_auto='$.2s',
    labels={"State": "Estado", "Ventas": "Ventas ($)"},
    title="Top 10 estados por volumen de ventas"
)

fig_top.update_layout(template="plotly_white", yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_top, use_container_width=True)
