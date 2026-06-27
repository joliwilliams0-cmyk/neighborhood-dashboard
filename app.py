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
st.markdown("Evaluating 11 premier markets using core financial, community safety, and infrastructure metrics.")

# 2. Comprehensive 11-City Dataset (Prices, Growth, Taxes, Commutes, and Crime Indexes)
# Crime Index scale: Lower numbers indicate significantly safer environments/lower crime rates.
@st.cache_data
def load_portfolio_data():
    return pd.DataFrame({
        'Neighborhood': [
            'Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 
            'Phoenix, AZ', 'San Antonio, TX', 'Raleigh-Durham, NC', 
            'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'Richmond, VA'
        ],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 5.6],
        'Tax_Rate': [1.02, 0.79, 1.95, 0.85, 0.62, 2.10, 0.87, 1.15, 1.20, 1.22, 1.25], # Combined Effective Property Tax %
        'Commute_Mins': [31, 38, 30, 35, 27, 26, 25, 24, 34, 28, 24], # Avg local commute duration
        'Crime_Index': [52, 48, 64, 62, 44, 58, 32, 41, 76, 38, 45], # Scaled Index (Lower = Safer)
        'Community_Vibe': [
            'Tech Hub / Coastal', 'Urban Culture / Entertainment', 'Diverse / Industrial Growth', 'Historic Charm / Creative Hub',
            'Desert Urbanism / Expanding Suburbs', 'Historic Culture / Affordable Living', 'Research Triangle / High-Tech Innovation',
            'Maritime History / Military Hub', 'Bay Area Culture / Arts District', 'Coastal Subtropical / Rapid Influx',
            'Historic Capital / Emerging Arts'
        ],
        'lat': [47.6062, 34.0617, 29.7420, 33.7621, 33.4484, 29.4241, 35.7796, 36.8508, 37.8044, 27.9506, 37.5407],
        'lon': [-122.3321, -118.2974, -95.3340, -84.3688, -111.9748, -98.4936, -78.6382, -76.2859, -122.2712, -82.4572, -77.4360]
    })

df = load_portfolio_data()

# 3. Expanded Sidebar Strategy Matrix (Weights & Filters)
st.sidebar.header("🎯 Buyer Preference Vector")
st.sidebar.markdown("Rate priority importance weights (1 = Minimal, 5 = High Priority)")

w_price = st.sidebar.slider("Affordability (Lower Price)", 1, 5, 3)
w_schools = st.sidebar.slider("School System Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability Index", 1, 5, 2)
w_growth = st.sidebar.slider("Target Capital Growth", 1, 5, 4)
w_tax = st.sidebar.slider("Low Tax Burden", 1, 5, 3)
w_commute = st.sidebar.slider("Short Commute Focus", 1, 5, 2)
w_crime = st.sidebar.slider("Neighborhood Safety Focus (Low Crime)", 1, 5, 4)

# 4. Advanced Alignment Math (With Exponential Boosting for Sharp Variation)
# Low Values are Preferred for Price, Taxes, Commute, and Crime
score_price = ((df['Home_Price'].max() - df['Home_Price']) / (df['Home_Price'].max() - df['Home_Price'].min() + 1)) * 100
score_schools = (df['School_Rating'] / 10) * 100
score_walk = df['Walkability']
score_growth = (df['Growth_Trend'] / df['Growth_Trend'].max()) * 100
score_tax = ((df['Tax_Rate'].max() - df['Tax_Rate']) / (df['Tax_Rate'].max() - df['Tax_Rate'].min() + 0.1)) * 100
score_commute = ((df['Commute_Mins'].max() - df['Commute_Mins']) / (df['Commute_Mins'].max() - df['Commute_Mins'].min() + 1)) * 100
score_crime = ((df['Crime_Index'].max() - df['Crime_Index']) / (df['Crime_Index'].max() - df['Crime_Index'].min() + 1)) * 100

# Apply an exponential power (w ** 3) to create strong mathematical separation when a slider is pushed to 5
b_price = w_price ** 3
b_schools = w_schools ** 3
b_walk = w_walk ** 3
b_growth = w_growth ** 3
b_tax = w_tax ** 3
b_commute = w_commute ** 3
b_crime = w_crime ** 3

total_boost = b_price + b_schools + b_walk + b_growth + b_tax + b_commute + b_crime
df['Match_Score'] = (
    (score_price * b_price) + (score_schools * b_schools) + (score_walk * b_walk) + 
    (score_growth * b_growth) + (score_tax * b_tax) + (score_commute * b_commute) + (score_crime * b_crime)
) / total_boost
df = df.sort_values(by="Match_Score", ascending=False).reset_index(drop=True)
best_city_row = df.iloc[0]

# 5. Strategic Recommendation Card
# 5. Strategic Recommendation Card 
st.success(f"🏆 **Top Optimization Match:** **{best_city_row['Neighborhood']}** (Match Score: {best_city_row['Match_Score']}%)") 
st.info(f"**Holistic Rationale:** Profiled as a *'{best_city_row['Community_Vibe']}'* hub, this corridor hits your goals beautifully with an entry price of ${best_city_row['Home_Price']:,}, a {best_city_row['Tax_Rate']}% property tax rate, an average commute of {best_city_row['Commute_Mins']} mins, and an elite safety rating.")
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
    "ScatterplotLayer",
    df,
    get_position="[lon, lat]",
    get_color="[15, 118, 110, 215]", # Clean turquoise profile color
    get_radius=65000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nTax Rate: {Tax_Rate}%\nAvg Commute: {Commute_Mins}m\nMatch Score: {Match_Score}%"}))

# 8. Multi-Variable Comparison Visuals
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Comprehensive Score Rankings")
    fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score",
                 color_continuous_scale="Teal", title="Match Fit Index Across Target Metros")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Tax Load vs. Community Safety Matrix")
    fig2 = px.scatter(df, x="Tax_Rate", y="Crime_Index", size="Home_Price", text="Neighborhood",
                      color="Commute_Mins", color_continuous_scale="Plasma", 
                      title="Risk Indexing Grid (Size = Home Price, Color = Commute)")
    st.plotly_chart(fig2, use_container_width=True)

# 9. Expanded Executive PDF Report Generator
def generate_advanced_pdf(data_frame, top_city, score):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#0F766E'), spaceAfter=8)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9, leading=13, spaceAfter=6)
    
    story = []
    story.append(Paragraph("📊 Comprehensive Multi-Regional Strategic Brief", title_style))
    story.append(Paragraph(f"<b>Primary Operational Recommendation:</b> {top_city} ({score}% Metric Alignment Fit)", body_style))
    story.append(Spacer(1, 8))
    
    # Detailed Table Setup
    table_data = [['Market Corridor', 'Avg Price', 'Schools', 'Walk %', 'Growth %', 'Tax Rate %', 'Commute', 'Crime Idx', 'Match']]
    for _, row in data_frame.iterrows():
        table_data.append([
            row['Neighborhood'], f"${row['Home_Price']:,}", str(row['School_Rating']), 
            f"{row['Walkability']}%", f"{row['Growth_Trend']}%", f"{row['Tax_Rate']}%", 
            f"{row['Commute_Mins']}m", str(row['Crime_Index']), f"{row['Match_Score']}%"
        ])
        
    t = Table(table_data, colWidths=[115, 65, 45, 45, 50, 55, 50, 50, 45])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# PDF UI Hook placement
st.sidebar.markdown("---")
advanced_pdf = generate_advanced_pdf(df, best_match['Neighborhood'], best_match['Match_Score'])
st.sidebar.download_button(
    label="📥 Export Advanced Portfolio Report",
    data=advanced_pdf,
    file_name="Comprehensive_Market_Analysis.pdf",
    mime="application/pdf"
)
