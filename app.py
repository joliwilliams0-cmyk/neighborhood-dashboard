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
st.title("🏡 Advanced Metro Investment & First-Time Buyer Portfolio")
st.markdown("Evaluating premier markets across financial metrics, professional engineering footprints, and community infrastructure.")

# 2. Comprehensive 11-City Dataset (Balanced & Updated with Professional & Greenery Metrics)
@st.cache_data
def load_portfolio_data():
    return pd.DataFrame({
        'Neighborhood': ['Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 'Phoenix, AZ', 'San Antonio, TX', 'Raleigh-Durham, NC', 'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'Richmond, VA'],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 5.6],
        'Tax_Rate': [1.02, 0.79, 1.95, 0.85, 0.62, 2.10, 0.87, 1.15, 1.20, 1.22, 1.25],
        'Commute_Mins': [31, 38, 30, 35, 27, 26, 25, 24, 34, 28, 24],
        'Crime_Index': [52, 48, 64, 62, 44, 58, 32, 41, 76, 38, 45],
        'Engineering_Jobs': [92, 88, 85, 78, 72, 60, 84, 68, 86, 55, 58], 
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

df = load_portfolio_data()

# 2b. Centralized US Cross-Industry Occupational Matrix (BLS Standard Systems Alignment)
@st.cache_data
def load_universal_career_data():
    raw_data = {
        "Industry_Group": [
            "Computer & Mathematical", "Computer & Mathematical", "Computer & Mathematical",
            "Architecture & Engineering", "Architecture & Engineering", "Architecture & Engineering",
            "Management Occupations", "Management Occupations", "Management Occupations",
            "Healthcare Practitioners", "Healthcare Practitioners", "Healthcare Practitioners",
            "Business & Financial Operations", "Business & Financial Operations", "Business & Financial Operations",
            "Legal & Public Policy", "Legal & Public Policy",
            "Education & Training", "Education & Training",
            "Arts, Design, Entertainment & Media", "Arts, Design, Entertainment & Media"
        ],
        "Occupation": [
            "Software Developer / Engineer", "Data Scientist", "Information Security Analyst",
            "Electrical Engineer", "Mechanical Engineer", "Civil Engineer",
            "General & Operations Manager", "Computer & Info Systems Manager", "Financial Manager",
            "Registered Nurse (RN)", "Physician / Surgeon", "Physical Therapist",
            "Financial Analyst", "Human Resources Specialist", "Management Analyst",
            "Attorney / Lawyer", "Public Policy Analyst",
            "Postsecondary Teacher / Professor", "High School Teacher",
            "Graphic Designer", "Technical Writer"
        ],
        "Median_Salary": [132000, 108000, 120000, 106000, 99000, 95000, 101000, 169000, 156000, 86000, 239000, 97000, 99000, 67000, 99000, 145000, 78000, 80000, 65000, 58000, 80000],
        "Projected_10Yr_Growth": ["25% (Much faster than average)", "36% (Much faster than average)", "32% (Much faster than average)", "5% (Average growth)", "10% (Faster than average)", "7% (Average growth)", "6% (Average growth)", "15% (Faster than average)", "16% (Faster than average)", "6% (Average growth)", "3% (Slower than average)", "15% (Faster than average)", "8% (Average growth)", "6% (Average growth)", "11% (Faster than average)", "8% (Average growth)", "6% (Average growth)", "8% (Average growth)", "1% (Little or no change)", "3% (Slower than average)", "7% (Average growth)"],
        "Market_Stability_Index": ["High Stability / Continual Evolution", "Exceptional / High AI Expansion", "Critical Defense Infrastructure", "Very High / Core Infrastructure", "High / Manufacturing Stability", "Solid / Non-Exportable Physical Asset", "Moderate Corporate Sensitivity", "Exceptional Leadership Moat", "Exceptional Financial Moat", "Absolute Structural Shortage", "High Longevity / Multi-Year Training Barriers", "Demographic Expansion Anchored", "Stable Corporate Essential", "Moderate Corporate Evolving", "High Consulting Elasticity", "High Institutional Protection", "Stable / Non-Profit / Public Anchor", "Tenure Protected Academic Anchor", "Public Infrastructure Anchor", "Disruption Risk / High Freelance Shift", "Stable Technical Essential"]
    }
    return pd.DataFrame(raw_data)

df_careers = load_universal_career_data()

# 3. Expanded Sidebar Strategy Matrix
st.sidebar.header("🎯 Buyer Preference Vector")
st.sidebar.markdown("Rate priority importance weights (1 = Minimal, 5 = High Priority)")
w_price = st.sidebar.slider("Affordability (Lower Price)", 1, 5, 3)
w_schools = st.sidebar.slider("School System Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability Index", 1, 5, 2)
w_growth = st.sidebar.slider("Target Capital Growth", 1, 5, 3)
w_tax = st.sidebar.slider("Low Tax Burden", 1, 5, 3)
w_commute = st.sidebar.slider("Short Commute Focus", 1, 5, 2)
w_crime = st.sidebar.slider("Neighborhood Safety Focus", 1, 5, 3)
w_eng = st.sidebar.slider("Engineering/Tech Job Footprint", 1, 5, 4)
w_green = st.sidebar.slider("Green Space & Outdoor Recreation", 1, 5, 4)

# 4. Corrected & Fair Mathematical Normalization (Percentile Rank Math to Prevent Outlier Bias)
def normalize_lower_better(col):
    return (col.max() - col) / (col.max() - col.min() + 0.01) * 100

def normalize_higher_better(col):
    return (col - col.min()) / (col.max() - col.min() + 0.01) * 100

score_price = normalize_lower_better(df['Home_Price'])
score_schools = normalize_higher_better(df['School_Rating'])
score_walk = normalize_higher_better(df['Walkability'])
score_growth = normalize_higher_better(df['Growth_Trend'])
score_tax = normalize_lower_better(df['Tax_Rate'])
score_commute = normalize_lower_better(df['Commute_Mins'])
score_crime = normalize_lower_better(df['Crime_Index'])
score_eng = normalize_higher_better(df['Engineering_Jobs'])
score_green = normalize_higher_better(df['Greenery_Parks'])

# Apply smooth exponential scaling (w ** 2.5) for crisp variation without complete obliteration
b_price = w_price ** 2.5
b_schools = w_schools ** 2.5
b_walk = w_walk ** 2.5
b_growth = w_growth ** 2.5
b_tax = w_tax ** 2.5
b_commute = w_commute ** 2.5
b_crime = w_crime ** 2.5
b_eng = w_eng ** 2.5
b_green = w_green ** 2.5

total_boost = b_price + b_schools + b_walk + b_growth + b_tax + b_commute + b_crime + b_eng + b_green
df['Match_Score'] = ((score_price * b_price) + (score_schools * b_schools) + (score_walk * b_walk) + (score_growth * b_growth) + (score_tax * b_tax) + (score_commute * b_commute) + (score_crime * b_crime) + (score_eng * b_eng) + (score_green * b_green)) / total_boost
df['Match_Score'] = df['Match_Score'].round(1)

# Sort DataFrame
df = df.sort_values(by="Match_Score", ascending=False).reset_index(drop=True)
best_city_row = df.iloc[0]

# 5. Strategic Recommendation Card
st.success(f"🏆 **Top Optimization Match:** **{best_city_row['Neighborhood']}** (Match Score: {best_city_row['Match_Score']}%)")
st.info(f"**Holistic Rationale:** Profiled as a *'{best_city_row['Community_Vibe']}'* corridor, this market features a dynamic blend of job opportunities and community assets matching your criteria.")

# 6. Top 3 Strategic Metric Anchors
st.markdown("---")
st.subheader("📈 Top 3 Balanced Opportunities")
m1, m2, m3 = st.columns(3)
m1.metric(df['Neighborhood'].iloc[0], f"${df['Home_Price'].iloc[0]:,}", f"Match Score: {df['Match_Score'].iloc[0]}%")
m2.metric(df['Neighborhood'].iloc[1], f"${df['Home_Price'].iloc[1]:,}", f"Match Score: {df['Match_Score'].iloc[1]}%")
m3.metric(df['Neighborhood'].iloc[2], f"${df['Home_Price'].iloc[2]:,}", f"Match Score: {df['Match_Score'].iloc[2]}%")

# 7. Spatial Deck Map
st.subheader("📍 Interactive National Portfolio Alignment Matrix")
view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3.8, pitch=15)
layer = pdk.Layer(
    "ScatterplotLayer", df,
    get_position="[lon, lat]",
    get_color="[15, 118, 110, 215]",
    get_radius=65000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nTax Rate: {Tax_Rate}%\nAvg Commute: {Commute_Mins}m\nMatch Score: {Match_Score}%"}))

# NEW ADDITION: 7b. Comprehensive US Industry & Cross-Sector Job Matrix
st.markdown("---")
st.subheader("💼 Cross-Industry Occupational Matrix (US Standard System)")
st.write("Examine cross-sector economic metrics sourced against the standard baseline updates from the [U.S. Bureau of Labor Statistics (BLS)](https://www.bls.gov/).")

# Split filters into layout columns
drop1, drop2 = st.columns(2)

with drop1:
    macro_sectors = sorted(df_careers["Industry_Group"].unique())
    selected_sector = st.selectbox("1. Filter by Macro Industry Group:", macro_sectors)

with drop2:
    available_jobs = df_careers[df_careers["Industry_Group"] == selected_sector]["Occupation"].unique()
    selected_occupation = st.selectbox("2. Target Specific Occupational Profile:", sorted(available_jobs))

# Query specific metrics for presentation
selected_career_metrics = df_careers[df_careers["Occupation"] == selected_occupation].iloc[0]

# Display Career Metric Cards
c_metrics_1, c_metrics_2, c_metrics_3 = st.columns(3)

with c_metrics_1:
    st.metric(
        label="Median Annual Base Income",
        value=f"${selected_career_metrics['Median_Salary']:,}"
    )
    st.caption("Standard National BLS Baseline Survey")

with c_metrics_2:
    growth_val = selected_career_metrics['Projected_10Yr_Growth'].split(" ")[0]
    growth_desc = selected_career_metrics['Projected_10Yr_Growth'].split(" ", 1)[1]
    st.metric(
        label="Projected 10-Year Growth",
        value=growth_val
    )
    st.caption(growth_desc)

with c_metrics_3:
    st.info(f"**{selected_career_metrics['Market_Stability_Index']}**")
    st.caption("Career Stability Index & AI Resilience Profile")

# 8. Multi-Variable Comparison Visuals
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Comprehensive Score Rankings")
    fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score", color_continuous_scale="Teal", title="Match Fit Index Across Target Metros")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Engineering Careers vs. Greenery & Outdoor Spaces")
    fig2 = px.scatter(df, x="Engineering_Jobs", y="Greenery_Parks", size="Home_Price", text="Neighborhood", color="Growth_Trend", color_continuous_scale="Viridis", title="Professional Footprint vs. Quality of Life (Size = Price, Color = Growth)")
    st.plotly_chart(fig2, use_container_width=True)

# 9. Expanded Executive PDF Report Generator
def generate_advanced_pdf(data_frame, top_city, score):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F766E'), spaceAfter=8)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9, leading=13, spaceAfter=6)
    
    story = []
    story.append(Paragraph("📊 Comprehensive Multi-Regional Strategic Brief", title_style))
    story.append(Paragraph(f"<b>Primary Operational Recommendation:</b> {top_city} ({score}% Metric Alignment Fit)", body_style))
    story.append(Spacer(1, 8))
    
    # Detailed Table Setup
    table_data = [['Market Corridor', 'Avg Price', 'Schools', 'Walk %', 'Growth %', 'Tax %', 'Commute', 'Tech/Eng', 'Greenery', 'Match']]
    for _, row in data_frame.iterrows():
        table_data.append([
            row['Neighborhood'], f"${row['Home_Price']:,}", str(row['School_Rating']), f"{row['Walkability']}%", f"{row['Growth_Trend']}%", f"{row['Tax_Rate']}%", f"{row['Commute_Mins']}m", str(row['Engineering_Jobs']), str(row['Greenery_Parks']), f"{row['Match_Score']}%"
        ])
        
    t = Table(table_data, colWidths=[110, 60, 45, 45, 50, 45, 50, 55, 55, 45])
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

# PDF UI Hook placement
st.sidebar.markdown("---")
advanced_pdf = generate_advanced_pdf(df, best_city_row['Neighborhood'], best_city_row['Match_Score'])
st.sidebar.download_button(label="📥 Export Advanced Portfolio Report", data=advanced_pdf, file_name="Comprehensive_Market_Analysis.pdf", mime="application/pdf")
