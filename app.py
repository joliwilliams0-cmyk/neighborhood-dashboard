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
st.set_page_config(page_title="Executive Real Estate Dashboard", layout="wide")
st.title("🏡 Metro Investment & First-Time Buyer Dashboard")
st.markdown("Evaluating real market trends across Houston, Atlanta, and Los Angeles.")

# 2. Hardcoded Real Market Baseline Data (Houston, Atlanta, LA)
@st.cache_data
def load_metro_data():
    return pd.DataFrame({
        'Neighborhood': ['Houston (East End)', 'Atlanta (Old Fourth Ward)', 'Los Angeles (Koreatown)'],
        'Home_Price': [325000, 445000, 785000],
        'School_Rating': [6, 8, 7],
        'Walkability': [72, 85, 89],
        'Growth_Trend': [6.4, 7.8, 3.2],
        'lat': [29.7420, 33.7621, 34.0617],
        'lon': [-95.3340, -84.3688, -118.2974]
    })

df = load_metro_data()

# 3. Sidebar Interactive Match Score Sliders
st.sidebar.header("🎯 Buyer Priorities (Weighting)")
st.sidebar.markdown("Rate how important each factor is to you (1 = Low, 5 = Critical)")
w_price = st.sidebar.slider("Affordability (Lower Price)", 1, 5, 3)
w_schools = st.sidebar.slider("School System Quality", 1, 5, 3)
w_walk = st.sidebar.slider("Walkability & Transit", 1, 5, 3)
w_growth = st.sidebar.slider("Future Capital Growth", 1, 5, 3)

# 4. Calculate Custom Match Scores Dynamically
# Normalize metrics between 0 and 100 to compute an accurate score
price_score = (df['Home_Price'].max() - df['Home_Price']) / (df['Home_Price'].max() - df['Home_Price'].min() + 1) * 100
school_score = (df['School_Rating'] / 10) * 100
walk_score = df['Walkability']
growth_score = (df['Growth_Trend'] / df['Growth_Trend'].max()) * 100

total_weight = w_price + w_schools + w_walk + w_growth
df['Match_Score'] = ((price_score * w_price) + (school_score * w_schools) + (walk_score * w_walk) + (growth_score * w_growth)) / total_weight
df['Match_Score'] = df['Match_Score'].round(1)

# Identify the winning city
best_city_row = df.loc[df['Match_Score'].idxmax()]
best_city = best_city_row['Neighborhood']

# 5. Top Rationale Card
st.success(f"🏆 **Top Recommendation Based on Your Priorities:** **{best_city}** (Match Score: {best_city_row['Match_Score']}%)")
st.info(f"**Supporting Rationale:** This location perfectly balances your selected criteria. It features an average entry price of ${best_city_row['Home_Price']:,} paired with a strong {best_city_row['Growth_Trend']}% projected appreciation rate and a walkability index of {best_city_row['Walkability']}/100.")

# 6. KPI Metric Layout
st.markdown("---")
m1, m2, m3 = st.columns(3)
m1.metric(df['Neighborhood'].iloc[0], f"${df['Home_Price'].iloc[0]:,}", f"Match: {df['Match_Score'].iloc[0]}%")
m2.metric(df['Neighborhood'].iloc[1], f"${df['Home_Price'].iloc[1]:,}", f"Match: {df['Match_Score'].iloc[1]}%")
m3.metric(df['Neighborhood'].iloc[2], f"${df['Home_Price'].iloc[2]:,}", f"Match: {df['Match_Score'].iloc[2]}%")

# 7. Map Widget (PyDeck Interactive Map)
st.subheader("📍 Interactive Metro Location Matrix")
view_state = pdk.ViewState(latitude=32.0, longitude=-100.0, zoom=3.5, pitch=30)
layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position="[lon, lat]",
    get_color="[211, 47, 47, 200]",
    get_radius=80000,
    pickable=True,
)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Neighborhood}\nAvg Price: ${Home_Price}\nMatch Score: {Match_Score}%"}))

# 8. Chart Visualization Layout
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Personalized Alignment Score")
    fig = px.bar(df, x="Neighborhood", y="Match_Score", color="Neighborhood", text_auto=True, title="Compatibility Ranking")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Price vs. Capital Growth Trajectory")
    fig2 = px.scatter(df, x="Home_Price", y="Growth_Trend", size="Walkability", text="Neighborhood", color="Neighborhood", title="Value Matrix")
    st.plotly_chart(fig2, use_container_width=True)

# 9. Dynamic PDF Generator Tool
def generate_pdf(data_frame, recommendation, score):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1E3A8A'), spaceAfter=15)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=11, leading=16, spaceAfter=10)
    
    story = []
    story.append(Paragraph("🏆 Real Estate Investment Brief", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Top Recommended Market:</b> {recommendation} ({score}% Compatibility Match)", body_style))
    story.append(Spacer(1, 15))
    
    # Data Table Processing
    table_data = [['City Corridor', 'Avg Price', 'Schools', 'Walkability', 'Growth Trend', 'Match Score']]
    for _, row in data_frame.iterrows():
        table_data.append([row['Neighborhood'], f"${row['Home_Price']:,}", str(row['School_Rating']), str(row['Walkability']), f"{row['Growth_Trend']}%", f"{row['Match_Score']}%"])
        
    t = Table(table_data, colWidths=[150, 80, 60, 70, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F3F4F6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download Button Layout
st.sidebar.markdown("---")
pdf_data = generate_pdf(df, best_city, best_city_row['Match_Score'])
st.sidebar.download_button(
    label="📥 Download Executive PDF Report",
    data=pdf_data,
    file_name="Real_Estate_Investment_Brief.pdf",
    mime="application/pdf"
)
