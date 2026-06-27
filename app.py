import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pydeck as pdk
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. LUXURY PAGE CONFIGURATION
st.set_page_config(page_title="Institutional Real Estate Terminal", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #050505; color: #E0E0E0; font-family: 'Helvetica Neue', sans-serif; }
    .stMetric { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    h1, h2, h3 { color: #C5A059 !important; }
</style>""", unsafe_allow_html=True)

st.title("🏛️ Institutional Metro Investment Terminal")
st.markdown("Precision market intelligence for the sophisticated buyer. Integrating BLS wage data with regional infrastructure metrics.")

# 2. DATA ENGINE
@st.cache_data
def load_and_parse_bls_data():
    try:
        # Utilize the uniform dataset
        df = pd.read_csv("cleaned_cities_uniform_2.csv")
        df.columns = df.columns.str.strip().str.upper()
        df['A_MEDIAN'] = pd.to_numeric(df['A_MEDIAN'].astype(str).str.replace(',', '').str.replace('#', '239200'), errors='coerce')
        df['AREA_TITLE'] = df['AREA_TITLE'].str.strip().str.lower()
        df['OCC_TITLE'] = df['OCC_TITLE'].str.strip()
        return df
    except Exception as e:
        st.error(f"Critical Data Error: {e}")
        return pd.DataFrame()

bls_data = load_and_parse_bls_data()

@st.cache_data
def load_portfolio_base():
    return pd.DataFrame({
        'Neighborhood': ['Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 'Phoenix, AZ', 'San Antonio, TX', 'Raleigh-Durham, NC', 'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'Richmond, VA'],
        'BLS_Search_Term': ['seattle', 'los angeles', 'houston', 'atlanta', 'phoenix', 'san antonio', 'raleigh', 'virginia beach', 'oakland', 'tampa', 'richmond'],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 5.6],
        'Tax_Rate': [1.02, 0.79, 1.95, 0.85, 0.62, 2.10, 0.87, 1.15, 1.20, 1.22, 1.25],
        'Commute_Mins': [31, 38, 30, 35, 27, 26, 25, 24, 34, 28, 24],
        'Crime_Index': [52, 48, 64, 62, 44, 58, 32, 41, 76, 38, 45],
        'lat': [47.6062, 34.0617, 29.7420, 33.7621, 33.4484, 29.4241, 35.7796, 36.8508, 37.8044, 27.9506, 37.5407],
        'lon': [-122.3321, -118.2974, -95.3340, -84.3688, -111.9748, -98.4936, -78.6382, -76.2859, -122.2712, -82.4572, -77.4360]
    })

df_base = load_portfolio_base()

# 3. SIDEBAR CONTROLS
st.sidebar.header("💼 Investment Strategy")
selected_occupation = st.sidebar.selectbox("Select Target Occupation:", sorted(bls_data['OCC_TITLE'].unique()))

st.sidebar.markdown("---")
st.sidebar.subheader("Mathematical Weighting")
w_afford = st.sidebar.slider("Affordability Weight", 1, 5, 5)
w_growth = st.sidebar.slider("Growth Trend Weight", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability Weight", 1, 5, 2)
w_school = st.sidebar.slider("School Quality Weight", 1, 5, 3)

# 4. SALARY MATCHING LOGIC
def get_local_salary(city_term, occupation):
    match = bls_data[
        (bls_data['AREA_TITLE'].str.contains(city_term, case=False, na=False)) & 
        (bls_data['OCC_TITLE'] == occupation)
    ]
    return int(match['A_MEDIAN'].iloc[0]) if not match.empty else int(bls_data[bls_data['OCC_TITLE'] == occupation]['A_MEDIAN'].median())

df = df_base.copy()
df['Estimated_Local_Salary'] = df['BLS_Search_Term'].apply(lambda x: get_local_salary(x, selected_occupation))
df['Affordability_Ratio'] = (df['Estimated_Local_Salary'] / df['Home_Price'] * 100).round(2)

# 5. CALCULATE FIT SCORE
df['Match_Score'] = (
    (df['Affordability_Ratio'] / df['Affordability_Ratio'].max() * w_afford) +
    (df['Growth_Trend'] / df['Growth_Trend'].max() * w_growth) +
    (df['Walkability'] / df['Walkability'].max() * w_walk) +
    (df['School_Rating'] / df['School_Rating'].max() * w_school)
) / (w_afford + w_growth + w_walk + w_school) * 100

df = df.sort_values('Match_Score', ascending=False)
best_city = df.iloc[0]

# 6. DASHBOARD VIEW
st.success(f"### 🏆 Primary Acquisition Target: {best_city['Neighborhood']} (Fit Score: {best_city['Match_Score']:.1f}%)")

c1, c2, c3 = st.columns(3)
c1.metric("Local Median Salary", f"${best_city['Estimated_Local_Salary']:,}")
c2.metric("Median Property Price", f"${best_city['Home_Price']:,}")
c3.metric("Affordability Coverage", f"{best_city['Affordability_Ratio']}%")

st.subheader("Market Competitive Landscape")
st.dataframe(df[['Neighborhood', 'Estimated_Local_Salary', 'Home_Price', 'Affordability_Ratio', 'Walkability', 'Match_Score']], use_container_width=True)

# 7. VISUALS
fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score", color_continuous_scale="Mint", title="Investment Fit (%)")
st.plotly_chart(fig, use_container_width=True)
