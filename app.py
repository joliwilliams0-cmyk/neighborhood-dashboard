import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. LUXURY CONFIGURATION
st.set_page_config(page_title="Institutional Real Estate Terminal", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #050505; color: #E0E0E0; font-family: 'Helvetica Neue', sans-serif; }
    h1, h2, h3 { color: #C5A059 !important; }
</style>""", unsafe_allow_html=True)

st.title("🏛️ Institutional Metro Investment Terminal")

# 2. DATA ENGINE WITH BLS KEY LOGIC
@st.cache_data
def load_and_parse_bls_data():
    try:
        df = pd.read_csv("cleaned_cities_uniform.csv")
        df.columns = df.columns.str.strip().str.upper()
        
        # BLS Data Key Logic: Handle *, **, and # symbols
        df['A_MEDIAN'] = df['A_MEDIAN'].astype(str).str.strip()
        df.loc[df['A_MEDIAN'].isin(['*', '**']), 'A_MEDIAN'] = np.nan
        df['A_MEDIAN'] = df['A_MEDIAN'].str.replace(',', '').str.replace('#', '239200')
        df['A_MEDIAN'] = pd.to_numeric(df['A_MEDIAN'], errors='coerce')
        
        df['AREA_TITLE'] = df['AREA_TITLE'].str.strip().str.lower()
        df['OCC_TITLE'] = df['OCC_TITLE'].str.strip()
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

bls_data = load_and_parse_bls_data()

# 3. PORTFOLIO BASE
@st.cache_data
def load_portfolio_base():
    return pd.DataFrame({
        'Neighborhood': ['Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 'Phoenix, AZ', 
                         'San Antonio, TX', 'Raleigh-Durham, NC', 'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'Richmond, VA'],
        'BLS_Search_Term': ['seattle', 'los angeles', 'houston', 'atlanta', 'phoenix', 'san antonio', 'raleigh', 'virginia beach', 'oakland', 'tampa', 'richmond'],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 5.6]
    })

df_base = load_portfolio_base()

# 4. SALARY MATCHING LOGIC
def get_local_salary(city_term, occupation):
    match = bls_data[
        (bls_data['AREA_TITLE'].str.contains(city_term, case=False, na=False)) & 
        (bls_data['OCC_TITLE'] == occupation)
    ]
    if not match.empty:
        val = match['A_MEDIAN'].iloc[0]
        return val if pd.notnull(val) else "No Data"
    else:
        nat_median = bls_data[bls_data['OCC_TITLE'] == occupation]['A_MEDIAN'].median()
        return int(nat_median) if pd.notnull(nat_median) else "No Data"

# 5. UI INTEGRATION
selected_occupation = st.sidebar.selectbox("Select Target Occupation:", sorted(bls_data['OCC_TITLE'].dropna().unique()))

df = df_base.copy()
df['Estimated_Local_Salary'] = df['BLS_Search_Term'].apply(lambda x: get_local_salary(x, selected_occupation))

# Handle display of 'No Data' in calculations
df['Display_Salary'] = df['Estimated_Local_Salary'].apply(lambda x: f"${x:,}" if isinstance(x, (int, float)) else "No Data")
df_calc = df[df['Estimated_Local_Salary'] != "No Data"].copy()

if not df_calc.empty:
    df_calc['Affordability_Ratio'] = (df_calc['Estimated_Local_Salary'] / df_calc['Home_Price'] * 100).round(2)
    st.subheader("Market Competitive Landscape")
    st.dataframe(df[['Neighborhood', 'Display_Salary', 'Home_Price']], use_container_width=True)
else:
    st.warning("Insufficient salary data for this occupation in the selected markets.")
