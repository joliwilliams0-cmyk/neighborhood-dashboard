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

# 1. Page Configuration
st.set_page_config(page_title="Executive Real Estate Portfolio", layout="wide")
st.title("🏡 Advanced Metro Investment & Real-Time Localized Income Matcher")
st.markdown("Evaluating premier US markets by blending community infrastructure, property costs, and your **exact career's actual regional earning potential** straight from the BLS.")

# 2. Comprehensive 11-City Real Estate Profile Base Matrix
@st.cache_data
def load_portfolio_base():
    return pd.DataFrame({
        'Neighborhood': ['Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 'Phoenix, AZ', 'San Antonio, TX', 'Raleigh-Durham, NC', 'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'Richmond, VA'],
        # Substrings used to scan and perfectly match the real 'AREA_TITLE' field within your CSV
        'BLS_Search_Term': ['Seattle', 'Los Angeles', 'Houston', 'Atlanta', 'Phoenix', 'San Antonio', 'Raleigh', 'Virginia Beach', 'Oakland', 'Tampa', 'Richmond'],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 5.6],
        'Tax_Rate': [1.02, 0.79, 1.95, 0.85, 0.62, 2.10, 0.87, 1.15, 1.20, 1.22, 1.25],
        'Commute_Mins': [31, 38, 30, 35, 27, 26, 25, 24, 34, 28, 24],
        'Crime_Index': [52, 48, 64, 62, 44, 58, 32, 41, 76, 38, 45],
        'Greenery_Parks': [95, 70, 68, 88, 55, 62, 85, 75, 80, 72, 78], 
        'Community_Vibe': [
            'Tech Hub / Coastal Greenery', 'Urban Culture / Entertainment', 'Diverse / Industrial & Tech Hub',
            'Historic Charm / Creative Hub', 'Desert Urbanism / Expanding Suburbs', 'Historic Culture / Affordable Living',
            'Research Triangle / Innovation Center', 'Maritime History / Military & Defense Tech', 'Bay Area Culture / Arts & Transit',
            'Coastal Subtropical / Rapid Influx', 'Historic Capital / Emerging Arts'
        ],
        'lat': [47.6062, 34.0617, 29.7420, 33.7621, 33.4484, 29.4241, 35.7796, 36.8508, 37.8044, 27.9506, 37.5407],
        'lon': [-122.3321, -118.2974, -95.3340, -84.3688, -111.9748, -98.4936, -78.6382, -76.2859, -122.2712, -82.4572, -77.4360]
    })

# 2b. Master BLS File Processing & Normalization Engine
@st.cache_data
def load_and_parse_bls_data():
    try:
        raw_df = pd.read_csv("bls_careers.csv", low_memory=False)
        raw_df.columns = raw_df.columns.str.strip().str.upper()
        
        # Filter for detailed individual occupations to strip structural macro aggregates
        if 'O_GROUP' in raw_df.columns:
            raw_df = raw_df[raw_df['O_GROUP'].str.lower().str.strip() == 'detailed']
            
        # Standardize standard structural data column conversions
        raw_df['A_MEDIAN'] = raw_df['A_MEDIAN'].astype(str).str.replace(',', '').str.strip()
        raw_df['A_MEDIAN'] = raw_df['A_MEDIAN'].replace('#', '239200') # Handle top-ceiling income identifiers
        raw_df['A_MEDIAN'] = pd.to_numeric(raw_df['A_MEDIAN'], errors='coerce')
        raw_df = raw_df.dropna(subset=['A_MEDIAN', 'OCC_TITLE', 'OCC_CODE'])
        
        # Build clean official cross-industry Group mapping based on standard 2-digit SOC baseline codes
        soc_mapping = {
            '11': 'Management Occupations', '13': 'Business & Financial Operations',
            '15': 'Computer & Mathematical', '17': 'Architecture & Engineering',
            '19': 'Life, Physical, & Social Science', '21': 'Community & Social Service',
            '23': 'Legal Occupations', '25': 'Educational Instruction & Library',
            '27': 'Arts, Design, Entertainment, Sports, & Media', '29': 'Healthcare Practitioners & Technical',
            '31': 'Healthcare Support', '33': 'Protective Service',
            '35': 'Food Preparation & Serving Related', '37': 'Building & Grounds Cleaning & Maintenance',
            '39': 'Personal Care & Service', '41': 'Sales & Related',
            '43': 'Office & Administrative Support', '45': 'Farming, Fishing, & Forestry',
            '47': 'Construction & Extraction', '49': 'Installation, Maintenance, & Repair',
            '51': 'Production / Manufacturing', '53': 'Transportation & Material Moving'
        }
        
        raw_df['Industry_Group'] = raw_df['OCC_CODE'].astype(str).str[:2].map(soc_mapping)
        raw_df['Industry_Group'] = raw_df['Industry_Group'].fillna("Other Specialized Sectors")
        
        return raw_df[['AREA_TITLE', 'Industry_Group', 'OCC_TITLE', 'A_MEDIAN']]
    except Exception as e:
        st.error(f"Error loading bls_careers.csv: {e}")
        # Robust emergency deployment fallback if dataset path breaks
        return pd.DataFrame({
            'AREA_TITLE': ['U.S.', 'U.S.'],
            'Industry_Group': ['Computer & Mathematical', 'Architecture & Engineering'],
            'OCC_TITLE': ['Software Developer', 'Electrical Engineer'],
            'A_MEDIAN': [132000, 106000]
        })

df_base = load_portfolio_base()
bls_data = load_and_parse_bls_data()

# 3. Dynamic Structural Selectbox Filters
st.sidebar.header("💼 Personal Career Earning Metric")
st.sidebar.markdown("Pick your target profession to search live local census files across each region.")

macro_sectors = sorted(bls_data["Industry_Group"].unique())
selected_sector = st.sidebar.selectbox("1. Select Macro Occupational Industry:", macro_sectors)

available_jobs = bls_data[bls_data["Industry_Group"] == selected_sector]["OCC_TITLE"].unique()
selected_occupation = st.sidebar.selectbox("2. Select Your Specific Job Title:", sorted(available_jobs))

# Find the overall national baseline wage strategy
national_subset = bls_data[(bls_data["OCC_TITLE"] == selected_occupation) & (bls_data["AREA_TITLE"].str.contains("U.S.|National|United States", case=False, na=False))]
nat_median = int(national_subset["A_MEDIAN"].iloc[0]) if not national_subset.empty else int(bls_data[bls_data["OCC_TITLE"] == selected_occupation]["A_MEDIAN"].median())

# 4. Extract Real-Time Localized Income Points for each Target City
local_salaries = []
for idx, row in df_base.iterrows():
    search_term = row['BLS_Search_Term']
    # Scan the file dynamically for rows matching the city name and selected occupation title
    match_query = bls_data[(bls_data["OCC_TITLE"] == selected_occupation) & (bls_data["AREA_TITLE"].str.contains(search_term, case=False, na=False))]
    
    if not match_query.empty:
        local_salaries.append(int(match_query["A_MEDIAN"].iloc[0]))
    else:
        # Secure fallback: if data point is missing for a specific micro area, default to national metric
        local_salaries.append(nat_median)

df = df_base.copy()
df["Estimated_Local_Salary"] = local_salaries
df["Affordability_Ratio"] = ((df["Estimated_Local_Salary"] / df["Home_Price"]) * 100).round(2)

# 5. Strategic Weight Alignment Vectors
st.sidebar.markdown("---")
st.sidebar.header("🎯 Target Buyer Weightings")
st.sidebar.markdown("Adjust priorities (1 = Minimal, 5 = Highly Vital Focus)")
w_afford = st.sidebar.slider("Localized Purchase Power (Income-to-Price)", 1, 5, 5)
w_schools = st.sidebar.slider("School System Infrastructure Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability Score Matrix", 1, 5, 2)
w_growth = st.sidebar.slider("Target Real Estate Price Growth Track", 1, 5, 3)
w_tax = st.sidebar.slider("Low Corporate / Property Tax Footprint", 1, 5, 3)
w_commute = st.sidebar.slider("Short Traffic Transit Focus", 1, 5, 2)
w_crime = st.sidebar.slider("Neighborhood Safety Focus Index", 1, 5, 3)
w_green = st.sidebar.slider("Parks & Urban Outdoor Recreation spaces", 1, 5, 4)

# 6. Advanced Mathematical Normalization Calculations
def normalize_lower_better(col):
    return (col.max() - col) / (col.max() - col.min() + 0.01) * 100

def normalize_higher_better(col):
    return (col - col.min()) / (col.max() - col.min() + 0.01) * 100

score_afford = normalize_higher_better(df['Affordability_Ratio'])
score_schools = normalize_higher_better(df['School_Rating'])
score_walk = normalize_higher_better(df['Walkability'])
score_growth = normalize_higher_better(df['Growth_Trend'])
score_tax = normalize_lower_better(df['Tax_Rate'])
score_commute = normalize_lower_better(df['Commute_Mins'])
score_crime = normalize_lower_better(df['Crime_Index'])
score_green = normalize_higher_better(df['Greenery_Parks'])

# Exponential Scaling Logic
b_afford = w_afford ** 2.5
b_schools = w_schools ** 2.5
b_walk = w_walk ** 2.5
b_growth = w_growth ** 2.5
b_tax = w_tax ** 2.5
b_commute = w_commute ** 2.5
b_crime = w_crime ** 2.5
b_green = w_green ** 2.5

total_boost = b_afford + b_schools + b_walk + b_growth + b_tax + b_commute + b_crime + b_green
df['Match_Score'] = ((score_afford * b_afford) + (score_schools * b_schools) + (score_walk * b_walk) + (score_growth * b_growth) + (score_tax * b_tax) + (score_commute * b_commute) + (score_crime * b_crime) + (score_green * b_green)) / total_boost
df['Match_Score'] = df['Match_Score'].round(1)

# Sort Results
df = df.sort_values(by="Match_Score", ascending=False).reset_index(drop=True)
best_city_row = df.iloc[0]

# 7. Presentation & Recommendation Output Cards
st.success(f"🏆 **Top Match for a '{selected_occupation}':** **{best_city_row['Neighborhood']}** (Match Score: {best_city_row['Match_Score']}%)")

c_metrics_1, c_metrics_2, c_metrics_3 = st.columns(3)
with c_metrics_1:
    st.metric(label="Target Profession Profile", value=selected_occupation[:30])
    st.caption(f"US National Median: ${nat_median:,}")
with c_metrics_2:
    st.metric(label="Actual Salary in Top Metro", value=f"${best_city_row['Estimated_Local_Salary']:,}")
    st.caption("Extracted from Regional Data Rows")
with c_metrics_3:
    st.metric(label="Purchase-to-Income Ratio", value=f"{best_city_row['Affordability_Ratio']}%")
    st.caption("Annual Income divided by Home Price")

st.markdown("---")
st.subheader("📊 Dynamic Cross-Metro Asset Rankings")
st.write("Notice how changing your profession updates individual city incomes directly from your database, recalculating the match standings in real time:")

display_df = df[['Neighborhood', 'Home_Price', 'Estimated_Local_Salary', 'Affordability_Ratio', 'School_Rating', 'Growth_Trend', 'Match_Score']].copy()
display_df.columns = ['Metro Corridor', 'Median Real Estate Price', 'Actual Local Salary', 'Earning-to-Asset Coverage (%)', 'School Rating', 'Growth Trajectory (%)', 'Total Profile Match Fit']
st.dataframe(display_df, use_container_width=True, hide_index=True)

# 8. Spatial Mapping
view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3.8, pitch=15)
layer = pdk.Layer(
    "ScatterplotLayer", df,
    get_position="[lon, lat]",
    get_color="[15, 118, 110, 215]",
    get_radius=65000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nActual Local Salary: ${Estimated_Local_Salary}\nAffordability Cover: {Affordability_Ratio}%\nMatch Score: {Match_Score}%"}))

# 9. Visual Data Analytics Plots
col_plot_a, col_plot_b = st.columns(2)
with col_plot_a:
    st.subheader("Adjusted Strategy Ranking Values")
    fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score", color_continuous_scale="Teal", title="Match Fit Index via Database Wage Lookups")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col_plot_b:
    st.subheader("Local Market Buying Power Sizing")
    fig2 = px.scatter(df, x="Estimated_Local_Salary", y="Home_Price", size="Match_Score", text="Neighborhood", color="Growth_Trend", color_continuous_scale="Viridis", title="Earnings vs Property Price (Size = Profile Compatibility)")
    st.plotly_chart(fig2, use_container_width=True)

# 10. Dynamic Report Engine
def generate_advanced_pdf(data_frame, top_city, score, occupation_title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F766E'), spaceAfter=8)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9, leading=13, spaceAfter=6)
    
    story = []
    story.append(Paragraph(f"📊 Live Localized Investment & Real Estate Analysis Summary", title_style))
    story.append(Paragraph(f"<b>Occupational Strategy Filter:</b> {occupation_title} | <b>Optimal Investment Vector:</b> {top_city} ({score}% Match)", body_style))
    story.append(Spacer(1, 8))
    
    table_data = [['Market Corridor', 'Home Cost', 'Local Base Wage', 'Afford %', 'Schools', 'Growth %', 'Tax %', 'Match Fit']]
    for _, row in data_frame.iterrows():
        table_data.append([
            row['Neighborhood'], f"${row['Home_Price']:,}", f"${row['Estimated_Local_Salary']:,}", f"{row['Affordability_Ratio']}%", str(row['School_Rating']), f"{row['Growth_Trend']}%", f"{row['Tax_Rate']}%", f"{row['Match_Score']}%"
        ])
        
    t = Table(table_data, colWidths=[115, 60, 65, 50, 45, 50, 45, 45])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download Hook Setup
advanced_pdf = generate_advanced_pdf(df, best_city_row['Neighborhood'], best_city_row['Match_Score'], selected_occupation)
st.sidebar.download_button(label="📥 Export Live Localized Report", data=advanced_pdf, file_name="Real_Time_Metro_Analysis.pdf", mime="application/pdf")
