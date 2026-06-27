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
st.title("🏡 Advanced Metro Investment & Localized Income Matcher")
st.markdown("Evaluating premier US markets by blending community infrastructure, home prices, and your **exact career's localized earning potential**.")

# 2. Comprehensive 11-City Dataset with BLS Local Wage Multipliers
# Multipliers are based on BLS regional post-tier variations (e.g., Tech hubs vs. lower cost-of-living areas)
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
        'Wage_Multiplier': [1.22, 1.18, 1.04, 1.02, 0.98, 0.94, 1.06, 0.93, 1.25, 0.91, 0.96],
        'Community_Vibe': [
            'Tech Hub / Coastal Greenery', 'Urban Culture / Entertainment', 'Diverse / Industrial & Tech Hub',
            'Historic Charm / Creative Hub', 'Desert Urbanism / Expanding Suburbs', 'Historic Culture / Affordable Living',
            'Research Triangle / Innovation Center', 'Maritime History / Military & Defense Tech', 'Bay Area Culture / Arts & Transit',
            'Coastal Subtropical / Rapid Influx', 'Historic Capital / Emerging Arts'
        ],
        'lat': [47.6062, 34.0617, 29.7420, 33.7621, 33.4484, 29.4241, 35.7796, 36.8508, 37.8044, 27.9506, 37.5407],
        'lon': [-122.3321, -118.2974, -95.3340, -84.3688, -111.9748, -98.4936, -78.6382, -76.2859, -122.2712, -82.4572, -77.4360]
    })

# 2b. Broadly Diversified US Standard Occupational Data Framework
@st.cache_data
def load_comprehensive_career_data():
    raw_data = {
        "Industry_Group": [
            "Computer & Mathematical", "Computer & Mathematical", "Computer & Mathematical", "Computer & Mathematical", "Computer & Mathematical",
            "Architecture & Engineering", "Architecture & Engineering", "Architecture & Engineering", "Architecture & Engineering", "Architecture & Engineering",
            "Management Occupations", "Management Occupations", "Management Occupations", "Management Occupations", "Management Occupations",
            "Healthcare Practitioners & Technical", "Healthcare Practitioners & Technical", "Healthcare Practitioners & Technical", "Healthcare Practitioners & Technical", "Healthcare Practitioners & Technical",
            "Business & Financial Operations", "Business & Financial Operations", "Business & Financial Operations", "Business & Financial Operations", "Business & Financial Operations",
            "Legal & Public Policy", "Legal & Public Policy", "Legal & Public Policy",
            "Education, Instruction & Library", "Education, Instruction & Library", "Education, Instruction & Library",
            "Arts, Design, Entertainment & Media", "Arts, Design, Entertainment & Media", "Arts, Design, Entertainment & Media",
            "Sales & Related Roles", "Sales & Related Roles", "Sales & Related Roles",
            "Office & Administrative Support", "Office & Administrative Support",
            "Construction & Extraction", "Construction & Extraction",
            "Production & Manufacturing", "Production & Manufacturing"
        ],
        "Occupation": [
            "Software Developer / Engineer", "Data Scientist", "Information Security Analyst", "Computer Systems Analyst", "Network Architect",
            "Electrical Engineer", "Mechanical Engineer", "Civil Engineer", "Aerospace Engineer", "Biomedical Engineer",
            "General & Operations Manager", "Computer & Info Systems Manager", "Financial Manager", "Marketing Manager", "Medical & Health Services Manager",
            "Registered Nurse (RN)", "Physician / Surgeon", "Physical Therapist", "Pharmacist", "Physician Assistant",
            "Financial Analyst", "Human Resources Specialist", "Management Analyst", "Accountant / Auditor", "Market Research Analyst",
            "Attorney / Lawyer", "Paralegal / Legal Assistant", "Public Policy Analyst",
            "Postsecondary Teacher / Professor", "High School Teacher", "Elementary School Teacher",
            "Graphic Designer", "Technical Writer", "Editor / Media Producer",
            "Real Estate Agent / Broker", "Sales Representative (Wholesale/Tech)", "Retail Sales Supervisor",
            "Executive Administrative Assistant", "Customer Service Representative",
            "Construction Electrician", "Construction Project Manager",
            "Machinist / CNC Operator", "Production Plant Supervisor"
        ],
        "National_Median_Salary": [
            132000, 108000, 120000, 103000, 129000,
            106000, 99000, 95000, 130000, 100000,
            101000, 169000, 156000, 140000, 110000,
            86000, 239000, 97000, 136000, 125000,
            99000, 67000, 99000, 79000, 71000,
            145000, 60000, 78000,
            80000, 65000, 63000,
            58000, 80000, 66000,
            68000, 97000, 49000,
            71000, 40000,
            61000, 104000,
            50000, 67000
        ],
        "Projected_10Yr_Growth": [
            "25% (Much faster than average)", "36% (Much faster than average)", "32% (Much faster than average)", "10% (Faster than average)", "4% (Average growth)",
            "5% (Average growth)", "10% (Faster than average)", "7% (Average growth)", "6% (Average growth)", "5% (Average growth)",
            "6% (Average growth)", "15% (Faster than average)", "16% (Faster than average)", "7% (Average growth)", "28% (Much faster than average)",
            "6% (Average growth)", "3% (Slower than average)", "15% (Faster than average)", "3% (Slower than average)", "27% (Much faster than average)",
            "8% (Average growth)", "6% (Average growth)", "11% (Faster than average)", "4% (Average growth)", "13% (Faster than average)",
            "8% (Average growth)", "4% (Average growth)", "6% (Average growth)",
            "8% (Average growth)", "1% (Little or no change)", "1% (Little or no change)",
            "3% (Slower than average)", "7% (Average growth)", "2% (Slower than average)",
            "3% (Slower than average)", "5% (Average growth)", "2% (Slower than average)",
            "-5% (Decline)", "-4% (Decline)",
            "6% (Average growth)", "8% (Average growth)",
            "2% (Slower than average)", "3% (Slower than average)"
        ],
        "Market_Stability_Index": [
            "High Stability / Continual Evolution", "Exceptional / High AI Expansion", "Critical Defense Infrastructure", "Stable System Legacy Integrator", "High Corporate Infrastructure Grip",
            "Very High / Core Infrastructure", "High / Manufacturing Stability", "Solid / Non-Exportable Physical Asset", "Defense & Aerospace Dependent", "High Longevity Medical Tech",
            "Moderate Corporate Sensitivity", "Exceptional Leadership Moat", "Exceptional Financial Moat", "Growth Bound Variable Elasticity", "Absolute Clinical Safety Anchor",
            "Absolute Structural Shortage", "High Longevity / Multi-Year Training Barriers", "Demographic Expansion Anchored", "Highly Regulated Pharmacy Moat", "Extreme Healthcare Demand Expansion",
            "Stable Corporate Essential", "Moderate Corporate Evolving", "High Consulting Elasticity", "Regulatory Compliance Anchor", "Highly Analytical Performance Metrics",
            "High Institutional Protection", "Procedural Process Dependent", "Stable / Non-Profit / Public Anchor",
            "Tenure Protected Academic Anchor", "Public Infrastructure Anchor", "Public Infrastructure Anchor",
            "Disruption Risk / High Freelance Shift", "Stable Technical Essential", "Content & Media Evolution Facing",
            "Commission Heavy / Local Fluidity", "Corporate Revenue Essential", "Automation Vulnerable",
            "High Automation Displacement Risk", "Automation Displacement Risk",
            "Union Anchored Local Infrastructure", "Industrial Construction Footprint",
            "Precision Tooling Specialization", "Operations Floor Anchor"
        ]
    }
    return pd.DataFrame(raw_data)

df_base = load_portfolio_data()
df_careers = load_comprehensive_career_data()

# 3. Streamlit Layout: Occupational Selectors at the Top level
st.sidebar.header("💼 Personal Career Anchor")
st.sidebar.markdown("Choose your industry and career profile below to customize the home buying calculations to your regional income.")

macro_sectors = sorted(df_careers["Industry_Group"].unique())
selected_sector = st.sidebar.selectbox("1. Industry Sector Group:", macro_sectors)

available_jobs = df_careers[df_careers["Industry_Group"] == selected_sector]["Occupation"].unique()
selected_occupation = st.sidebar.selectbox("2. Specific Professional Profile:", sorted(available_jobs))

# Pull base career statistics
career_stats = df_careers[df_careers["Occupation"] == selected_occupation].iloc[0]
nat_median = career_stats["National_Median_Salary"]

# 4. Dynamically Apply Local Matrix Multipliers
df = df_base.copy()
df["Estimated_Local_Salary"] = (nat_median * df["Wage_Multiplier"]).astype(int)
# Dynamic Affordability Ratio: Local annual salary divided by property cost expressed as a percentage metric
df["Affordability_Ratio"] = ((df["Estimated_Local_Salary"] / df["Home_Price"]) * 100).round(2)

# 5. Strategic Buyer Weight Configuration
st.sidebar.markdown("---")
st.sidebar.header("🎯 Buyer Preference Vector")
st.sidebar.markdown("Rate priority importance weights (1 = Minimal, 5 = High Priority)")
w_afford = st.sidebar.slider("Career Income-to-Home Affordability", 1, 5, 5)
w_schools = st.sidebar.slider("School System Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability Index", 1, 5, 2)
w_growth = st.sidebar.slider("Target Capital Growth", 1, 5, 3)
w_tax = st.sidebar.slider("Low Tax Burden", 1, 5, 3)
w_commute = st.sidebar.slider("Short Commute Focus", 1, 5, 2)
w_crime = st.sidebar.slider("Neighborhood Safety Focus", 1, 5, 3)
w_green = st.sidebar.slider("Green Space & Outdoor Recreation", 1, 5, 4)

# 6. Mathematical Normalization (Including Dynamic Local Income-to-Home Price Affordability)
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

# Exponential Scaling for crisp variations
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

# 7. Strategic Recommendation Dashboard Elements
st.success(f"🏆 **Top Optimization Match For Your Profile:** **{best_city_row['Neighborhood']}** (Match Score: {best_city_row['Match_Score']}%)")

# Interactive summary grid of current chosen career pathing
col_job_a, col_job_b, col_job_c = st.columns(3)
with col_job_a:
    st.metric(label="Selected Career Target", value=selected_occupation)
    st.caption(f"Macro Field: {selected_sector}")
with col_job_b:
    st.metric(label="National Median Base", value=f"${nat_median:,}")
    st.caption(f"10-Yr Growth Track: {career_stats['Projected_10Yr_Growth']}")
with col_job_c:
    st.metric(label="Local Estimated Salary (In Top City)", value=f"${best_city_row['Estimated_Local_Salary']:,}")
    st.caption(f"Stability Moat: {career_stats['Market_Stability_Index']}")

st.markdown("---")
st.subheader("📊 Dynamic Metric Index Across Markets")
st.write("Notice how changing your career updates the Estimated Local Salaries and reshuffles the match order below based on localized spending power.")

# 8. Interactive Regional Table Presentation
display_df = df[['Neighborhood', 'Home_Price', 'Estimated_Local_Salary', 'Affordability_Ratio', 'School_Rating', 'Growth_Trend', 'Tax_Rate', 'Match_Score']].copy()
display_df.columns = ['Metro Corridor', 'Median Home Price', 'Estimated Regional Income', 'Income-to-Price Ratio (%)', 'School Grade', 'Growth Momentum (%)', 'Property Tax (%)', 'Match Score']
st.dataframe(display_df, use_container_width=True, hide_index=True)

# 9. Spatial Pydeck Projection Map Matrix
view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3.8, pitch=15)
layer = pdk.Layer(
    "ScatterplotLayer", df,
    get_position="[lon, lat]",
    get_color="[15, 118, 110, 215]",
    get_radius=65000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nEst. Local Salary: ${Estimated_Local_Salary}\nAffordability Ratio: {Affordability_Ratio}%\nMatch Score: {Match_Score}%"}))

# 10. Multi-Variable Visual Comparison Plots
c1, c2 = st.columns(2)
with c1:
    st.subheader("Dynamic Match Rankings")
    fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score", color_continuous_scale="Teal", title="Match Fit Index via Local Income Stream Adjustments")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Local Income Streams vs. Median Real Estate Costs")
    fig2 = px.scatter(df, x="Estimated_Local_Salary", y="Home_Price", size="Match_Score", text="Neighborhood", color="Growth_Trend", color_continuous_scale="Viridis", title="Buying Power Spread Map (Bubble Size = Total Profile Match)")
    st.plotly_chart(fig2, use_container_width=True)

# 11. PDF Report Generation Framework Engine
def generate_advanced_pdf(data_frame, top_city, score, occupation_title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F766E'), spaceAfter=8)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9, leading=13, spaceAfter=6)
    
    story = []
    story.append(Paragraph(f"📊 Comprehensive Regional Real Estate Analysis Profile", title_style))
    story.append(Paragraph(f"<b>Target Career Benchmark:</b> {occupation_title} | <b>Top Recommended Metro Selection:</b> {top_city} ({score}% Match)", body_style))
    story.append(Spacer(1, 8))
    
    table_data = [['Market Corridor', 'Avg Price', 'Local Income', 'Afford %', 'Schools', 'Growth %', 'Tax %', 'Match']]
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

# PDF UI Layout Hooks
advanced_pdf = generate_advanced_pdf(df, best_city_row['Neighborhood'], best_city_row['Match_Score'], selected_occupation)
st.sidebar.download_button(label="📥 Export Career-Aligned Portfolio Report", data=advanced_pdf, file_name="Career_Aligned_Real_Estate_Analysis.pdf", mime="application/pdf")
