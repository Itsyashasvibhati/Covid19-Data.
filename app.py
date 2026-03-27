import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="COVID Dashboard", layout="wide")

st.title("🦠 COVID-19 Advanced Dashboard")

# ======================
# LOAD DATA (SAFE WAY)
# ======================
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("covid_19.csv")
        return data
    except:
        st.error("❌ Dataset not found! Check file name.")
        return None

data = load_data()

if data is None:
    st.stop()

# ======================
# DEBUG (IMPORTANT)
# ======================
st.write("Columns in Dataset:", data.columns)

# ======================
# FIX COLUMN NAMES (AUTO DETECT)
# ======================
data.columns = [col.lower() for col in data.columns]

# Try mapping columns safely
date_col = 'date' if 'date' in data.columns else data.columns[0]
country_col = 'location' if 'location' in data.columns else data.columns[1]

# Try common names with safe fallbacks
cases_col = (
    'total_cases' if 'total_cases' in data.columns else
    'confirmed' if 'confirmed' in data.columns else
    'cases' if 'cases' in data.columns else None
)
deaths_col = (
    'total_deaths' if 'total_deaths' in data.columns else
    'deaths' if 'deaths' in data.columns else None
)
vacc_col = (
    'total_vaccinations' if 'total_vaccinations' in data.columns else
    'vaccinations' if 'vaccinations' in data.columns else
    'tests' if 'tests' in data.columns else None
)

# Verify required columns exist before continuing
missing_cols = [c for c in [date_col, country_col, cases_col, deaths_col] if c is None or c not in data.columns]
if missing_cols:
    st.error(f"Missing required columns in dataset: {', '.join([str(c) for c in missing_cols])}")
    st.stop()

# Convert date
data[date_col] = pd.to_datetime(data[date_col], errors='coerce')

# Ensure country values are strings before sorting/selecting
if country_col in data.columns:
    data[country_col] = data[country_col].fillna('Unknown').astype(str)

# Fill remaining nulls with 0 for numeric columns (do after country text fix)
data.fillna(0, inplace=True)

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filters")

country_options = sorted(data[country_col].unique())

country = st.sidebar.selectbox(
    "Select Country",
    country_options
)

filtered = data[data[country_col] == country]

# ======================
# KPI SECTION
# ======================
st.subheader("📊 Key Statistics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Cases", int(filtered[cases_col].max()))
col2.metric("Total Deaths", int(filtered[deaths_col].max()))

if vacc_col:
    col3.metric("Total Vaccinations", int(filtered[vacc_col].max()))
else:
    col3.metric("Vaccination Data", "Not Available")

# ======================
# LINE GRAPH
# ======================
st.subheader("📈 Trend Over Time")

fig1 = px.line(
    filtered,
    x=date_col,
    y=[cases_col, deaths_col],
    title="Cases & Death Trend",
)

st.plotly_chart(fig1, use_container_width=True)

# ======================
# BAR GRAPH
# ======================
st.subheader("🌍 Top Countries")

top = data.groupby(country_col)[cases_col].max().sort_values(ascending=False).head(10)

fig2 = px.bar(
    x=top.index,
    y=top.values,
    labels={'x': 'Country', 'y': 'Cases'},
    title="Top 10 Countries"
)

st.plotly_chart(fig2, use_container_width=True)

# ======================
# PIE CHART
# ======================
st.subheader("🥧 Case Distribution")

latest = filtered.iloc[-1]

pie_data = {
    "Cases": latest[cases_col],
    "Deaths": latest[deaths_col]
}

if vacc_col:
    pie_data["Vaccinated"] = latest[vacc_col]

fig3 = px.pie(
    names=list(pie_data.keys()),
    values=list(pie_data.values()),
    title="Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

# ======================
# SCATTER
# ======================
st.subheader("🔍 Cases vs Deaths")

fig4 = px.scatter(
    filtered,
    x=cases_col,
    y=deaths_col,
    title="Relationship"
)

st.plotly_chart(fig4, use_container_width=True)

# ======================
# AREA CHART
# ======================
st.subheader("📊 Growth Area Chart")

fig5 = px.area(
    filtered,
    x=date_col,
    y=cases_col,
    title="Cases Growth"
)

st.plotly_chart(fig5, use_container_width=True)

# ======================
# MAP (ADVANCED 🔥)
# ======================
st.subheader("🗺️ Global Spread")

latest_global = data.groupby(country_col).last().reset_index()

fig6 = px.choropleth(
    latest_global,
    locations=country_col,
    locationmode="country names",
    color=cases_col,
    title="Global COVID Map"
)

st.plotly_chart(fig6, use_container_width=True)