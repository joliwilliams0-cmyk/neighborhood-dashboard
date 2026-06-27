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
st.title("🏡 Metro Investment & First-Time Buyer Portfolio")
st.markdown("Evaluating multi-regional community metrics, capital goals, and expansion markets.")

# 2. Expanded 12-City Dataset (Prices, Communities, and Visual Anchors)
@st.cache_data
def load_portfolio_data():
    return pd.DataFrame({
        'Neighborhood': [
            'Seattle, WA', 'Los Angeles, CA', 'Houston, TX', 'Atlanta, GA', 
            'Phoenix, AZ', 'San Antonio, TX', 'Raleigh-Durham, NC', 
            'Hampton Roads, VA', 'Oakland, CA', 'Tampa, FL', 'DC-MD-VA', 'Richmond, VA'
        ],
        'Home_Price': [825000, 785000, 325000, 445000, 415000, 295000, 460000, 310000, 740000, 375000, 680000, 345000],
        'School_Rating': [8, 7, 6, 8, 7, 6, 9, 7, 6, 7, 8, 7],
        'Walkability': [78, 89, 72, 85, 62, 55, 68, 50, 82, 65, 80, 70],
        'Growth_Trend': [4.8, 3.2, 6.4, 7.8, 5.9, 5.1, 8.2, 3.9, 4.1, 7.2, 4.5, 5.6],
        'Community_Vibe': [
            'Tech Hub / Coastal', 'Urban Culture / Entertainment', 'Diverse / Industrial Growth', 'Historic Charm / Creative Hub',
            'Desert Urbanism / Expanding Suburbs', 'Historic Culture / Affordable Living', 'Research Triangle / High-Tech Innovation',
            'Maritime History / Military Hub', 'Bay Area Culture / Arts District', 'Coastal Subtropical / Rapid Influx',
            'Metropolitan / Government & Finance', 'Historic Capital / Emerging Arts'
        ],
        'lat': [47.6062, 34.0617, 29.7420, 33.7621, 33.4484, 29.4241, 35.7796, 36.8508, 37.8044, 27.9506, 38.9072, 37.5407],
        'lon': [-122.3321, -118.2974, -95.3340, -84.3688, -111.9748, -98.4936, -78.6382, -76.2859, -122.2712, -82.4572, -77.0369, -77.4360]
    })

df = load_portfolio_data()

# 3. Sidebar Configuration (Priorities & Goals)
st.sidebar.header("🎯 Investment Strategy & Goals")
st.sidebar.markdown("Define priorities to align with long-term capital goals.")

w_price = st.sidebar.slider("Affordability (Lower Entry Price)", 1, 5, 3)
w_schools = st.sidebar.slider("School System Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability & Infrastructure", 1, 5, 3)
w_growth = st.sidebar.slider("Target Capital Growth (YoY)", 1, 5, 4)

# 4. Math Logic: Dynamic Match Scoring Matrix
price_score = (df['Home_Price'].max() - df['Home_Price']) / (df['Home_Price'].max() - df['Home_Price'].min() + 1) * 100
school_score = (df['School_Rating'] / 10) * 100
walk_score = df['Walkability']
growth_score = (df['Growth_Trend'] / df['Growth_Trend'].max()) * 100

total_weight = w_price + w_schools + w_walk + w_growth
df['Match_Score'] = ((price_score * w_price) + (school_score * w_schools) + (walk_score * w_walk) + (growth_score * w_growth)) / total_weight
df['Match_Score'] = df['Match_Score'].round(1)

# Sort by strongest match
df = df.sort_values(by="Match_Score", ascending=False).reset_index(drop=True)
best_match = df.iloc[0]

# 5. Top Goal Recommendation Banner
st.success(f"🏆 **Top Strategic Goal Match:** **{best_match['Neighborhood']}** (Match Score: {best_match['Match_Score']}%)")
st.info(f"**Community & Rationale:** Profiled as a *'{best_match['Community_Vibe']}'* community. This region offers a baseline price of ${best_match['Home_Price']:,} with an impressive **{best_match['Growth_Trend']}%** growth projection, maximizing asset positioning.")

# 6. High-Level KPI Summary (Top 3 Performing Asset Markets)
st.markdown("---")
st.subheader("📈 Top 3 Alignment Opportunities")
m1, m2, m3 = st.columns(3)
m1.metric(df['Neighborhood'].iloc[0], f"${df['Home_Price'].iloc[0]:,}", f"Match: {df['Match_Score'].iloc[0]}%")
m2.metric(df['Neighborhood'].iloc[1], f"${df['Home_Price'].iloc[1]:,}", f"Match: {df['Match_Score'].iloc[1]}%")
m3.metric(df['Neighborhood'].iloc[2], f"${df['Home_Price'].iloc[2]:,}", f"Match: {df['Match_Score'].iloc[2]}%")

# 7. Multi-Region Map Widget
st.subheader("📍 National Workspace Map Matrix")
view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3.8, pitch=20)
layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position="[lon, lat]",
    get_color="[30, 58, 138, 225]", # Deep corporate blue
    get_radius=60000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nProfile: {Community_Vibe}\nMatch Score: {Match_Score}%"}))

# 8. Portfolio Comparison Charts
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Strategic Market Alignment Rankings")
    fig = px.bar(df, x="Match_Score", y="Neighborhood", orientation='h', color="Match_Score",
                 color_continuous_scale="Viridis", title="Full Index Compatibility (%)")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Asset Value vs. Growth Index")
    fig2 = px.scatter(df, x="Home_Price", y="Growth_Trend", size="Walkability", text="Neighborhood",
                      color="School_Rating", title="Value Matrix (Size = Walkability, Color = Schools)")
    st.plotly_chart(fig2, use_container_width=True)

# 9. Multi-Page Executive PDF Report Builder
def generate_portfolio_pdf(data_frame, top_city, score):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1E3A8A'), spaceAfter=10)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=8)
    
    story = []
    story.append(Paragraph("📊 National Real Estate Expansion Brief", title_style))
    story.append(Paragraph(f"<b>Primary Strategic Recommendation:</b> {top_city} ({score}% Match)", body_style))
    story.append(Spacer(1, 10))
    
    # PDF Data Table Setup
    table_data = [['Target Metro Market', 'Avg Price', 'Schools', 'Walkability', 'Growth %', 'Match Score']]
    for _, row in data_frame.iterrows():
        table_data.append([row['Neighborhood'], f"${row['Home_Price']:,}", str(row['School_Rating']), str(row['Walkability']), f"{row['Growth_Trend']}%", f"{row['Match_Score']}%"])
        
    t = Table(table_data, colWidths=[160, 75, 55, 65, 65, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# PDF Download Placement
st.sidebar.markdown("---")
portfolio_pdf = generate_portfolio_pdf(df, best_match['Neighborhood'], best_match['Match_Score'])
st.sidebar.download_button(
    label="📥 Export 12-City Portfolio PDF",
    data=portfolio_pdf,
    file_name="National_Market_Portfolio.pdf",
    mime="application/pdf"
)
