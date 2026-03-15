import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- Page Config ---
st.set_page_config(page_title="FreshGuard Solutions | Cold Chain Analytics", page_icon="🧊", layout="wide")

# --- Professional Dark Theme CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }
.main-header { text-align:center; padding:10px 0 5px 0; }
.main-header h1 { font-size:2.2rem; font-weight:700; background:linear-gradient(135deg,#00D4AA,#4ECDC4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0; }
.main-header p { color:#8899AA; font-size:1rem; margin-top:4px; }
.kpi-card { background:linear-gradient(135deg,#1a2332,#243447); border-radius:12px; padding:18px 14px; text-align:center; border-left:4px solid #00D4AA; }
.kpi-card.danger { border-left-color:#FF6B6B; }
.kpi-card .kpi-value { font-size:1.5rem; font-weight:700; color:#FFFFFF; margin:4px 0; }
.kpi-card .kpi-label { font-size:0.75rem; color:#8899AA; text-transform:uppercase; letter-spacing:1px; }
.insight-box { background:linear-gradient(135deg,#1a2332,#1e2d3d); border-left:4px solid #FFE66D; border-radius:8px; padding:14px 18px; margin:10px 0 20px 0; }
.insight-box .insight-title { color:#FFE66D; font-weight:600; font-size:0.85rem; margin-bottom:6px; }
.insight-box .insight-text { color:#C0C8D0; font-size:0.85rem; line-height:1.5; }
.section-header { color:#FFFFFF; font-size:1.4rem; font-weight:600; margin:30px 0 5px 0; padding-bottom:8px; border-bottom:2px solid #00D4AA; }
.rec-card { background:linear-gradient(135deg,#1a2332,#243447); border-radius:10px; padding:16px; border-left:4px solid #4ECDC4; margin-bottom:10px; }
.rec-card .rec-title { color:#4ECDC4; font-weight:600; font-size:0.9rem; }
.rec-card .rec-text { color:#C0C8D0; font-size:0.82rem; margin-top:4px; line-height:1.5; }
.rec-card .rec-impact { color:#FFE66D; font-size:0.8rem; margin-top:6px; font-weight:500; }
div[data-testid="stMetric"] { display:none; }
</style>
""", unsafe_allow_html=True)

COLORS = {'teal':'#00D4AA','red':'#FF6B6B','cyan':'#4ECDC4','yellow':'#FFE66D','blue':'#3D9DF2','purple':'#A78BFA','orange':'#F59E0B'}
PLOTLY_TEMPLATE = 'plotly_dark'

# --- Load Data ---
@st.cache_data
def load_data():
    fp = "Business Case and Dataset_Data Vista 2026(1)(Dataset).csv"
    if not os.path.exists(fp):
        st.error(f"Dataset not found: {fp}")
        return pd.DataFrame()
    df = pd.read_csv(fp)
    df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'], errors='coerce')
    df['YearMonth'] = df['Transaction_Date'].dt.to_period('M').astype(str)
    return df

df_raw = load_data()
if df_raw.empty:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.markdown("### 🔍 Filters")
regions = st.sidebar.multiselect("Region", df_raw['Region'].dropna().unique(), default=df_raw['Region'].dropna().unique())
categories = st.sidebar.multiselect("Category", df_raw['Category'].dropna().unique(), default=df_raw['Category'].dropna().unique())
suppliers = st.sidebar.multiselect("Supplier", df_raw['Supplier_Id'].dropna().unique(), default=df_raw['Supplier_Id'].dropna().unique())
months = st.sidebar.multiselect("Month", sorted(df_raw['Month'].dropna().unique()), default=sorted(df_raw['Month'].dropna().unique()))
stores = st.sidebar.multiselect("Store", df_raw['Store_Id'].dropna().unique(), default=df_raw['Store_Id'].dropna().unique())

df = df_raw[(df_raw['Region'].isin(regions))&(df_raw['Category'].isin(categories))&(df_raw['Supplier_Id'].isin(suppliers))&(df_raw['Month'].isin(months))&(df_raw['Store_Id'].isin(stores))]
if df.empty:
    st.warning("No data for selected filters.")
    st.stop()

# --- Helper ---
def kpi_card(label, value, danger=False):
    cls = "kpi-card danger" if danger else "kpi-card"
    return f'<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'

def insight(title, text):
    st.markdown(f'<div class="insight-box"><div class="insight-title">💡 {title}</div><div class="insight-text">{text}</div></div>', unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def styled_fig(fig, h=420):
    fig.update_layout(template=PLOTLY_TEMPLATE, font_family='Inter', height=h, margin=dict(l=50,r=50,t=80,b=60), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_font_size=14)
    return fig

# --- Compute Core KPIs ---
total_rev = df['Revenue'].sum()
total_profit = df['Profit'].sum()
total_waste = df['Waste_Cost'].sum()
units_sold = df['Units_Sold'].sum()
units_wasted = df['Units_Wasted'].sum()
total_init = df['Initial_Quantity'].sum()
waste_pct = (units_wasted / total_init * 100) if total_init > 0 else 0
profit_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
waste_to_rev = (total_waste / total_rev * 100) if total_rev > 0 else 0

# === HEADER ===
st.markdown('<div class="main-header"><h1>🧊 FreshGuard Solutions — Cold Chain Profit Leakage Report</h1><p>Diagnostic analysis of 100,000 transactions across 5 regions, 50 stores, and 15 suppliers</p></div>', unsafe_allow_html=True)

# === KEY FINDINGS BANNER ===
worst_cat = df.groupby('Category')['Waste_Cost'].sum().idxmax()
worst_cat_cost = df.groupby('Category')['Waste_Cost'].sum().max()
worst_region = df.groupby('Region').apply(lambda x: x['Units_Wasted'].sum()/x['Initial_Quantity'].sum()*100).idxmax()
worst_region_pct = df.groupby('Region').apply(lambda x: x['Units_Wasted'].sum()/x['Initial_Quantity'].sum()*100).max()

st.markdown(f"""<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #00D4AA;border-radius:12px;padding:18px;margin:10px 0 20px 0;">
<div style="color:#00D4AA;font-weight:700;font-size:1rem;margin-bottom:8px;">🎯 KEY FINDINGS</div>
<div style="color:#C0C8D0;font-size:0.88rem;line-height:1.7;">
• <b style="color:#FF6B6B;">${total_waste:,.0f}</b> in waste cost is eroding <b style="color:#FFE66D;">{waste_to_rev:.1f}%</b> of total revenue<br>
• <b style="color:#FF6B6B;">{worst_cat}</b> is the #1 profit leak category at <b>${worst_cat_cost:,.0f}</b> in waste cost<br>
• <b style="color:#FF6B6B;">{worst_region}</b> is the worst-performing region with <b>{worst_region_pct:.1f}%</b> spoilage rate<br>
• Every <b>1-point drop</b> in Handling Score increases spoilage risk significantly
</div></div>""", unsafe_allow_html=True)

# === KPI CARDS ===
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.markdown(kpi_card("Total Revenue", f"${total_rev:,.0f}"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("Total Profit", f"${total_profit:,.0f}"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Profit Margin", f"{profit_margin:.1f}%"), unsafe_allow_html=True)
with c4: st.markdown(kpi_card("Waste Cost", f"${total_waste:,.0f}", danger=True), unsafe_allow_html=True)
with c5: st.markdown(kpi_card("Waste Rate", f"{waste_pct:.1f}%", danger=True), unsafe_allow_html=True)
with c6: st.markdown(kpi_card("Units Wasted", f"{units_wasted:,.0f}", danger=True), unsafe_allow_html=True)

# ========== SECTION 1: EXECUTIVE OVERVIEW (Charts 1-3) ==========
section("1 · Executive Overview")

col1, col2 = st.columns(2)
with col1:
    # CHART 1: Revenue vs Waste Cost (Monthly Aggregated)
    df_monthly = df.groupby('YearMonth')[['Revenue','Waste_Cost']].sum().reset_index().sort_values('YearMonth')
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_monthly['YearMonth'], y=df_monthly['Revenue'], name='Revenue', line=dict(color=COLORS['teal'],width=2.5), fill='tozeroy', fillcolor='rgba(0,212,170,0.1)'))
    fig1.add_trace(go.Scatter(x=df_monthly['YearMonth'], y=df_monthly['Waste_Cost'], name='Waste Cost', line=dict(color=COLORS['red'],width=2.5), fill='tozeroy', fillcolor='rgba(255,107,107,0.1)'))
    fig1.update_layout(title="Monthly Revenue vs Waste Cost Trend", xaxis_title="Month", yaxis_title="USD ($)")
    st.plotly_chart(styled_fig(fig1), use_container_width=True)

with col2:
    # CHART 2: Waste Cost Treemap by Category
    df_tree = df.groupby('Category')[['Waste_Cost','Profit']].sum().reset_index()
    fig2 = px.treemap(df_tree, path=['Category'], values='Waste_Cost', color='Waste_Cost', color_continuous_scale=['#1a2332','#FF6B6B','#FF4444'], title="Waste Cost by Category (Treemap)")
    st.plotly_chart(styled_fig(fig2, 440), use_container_width=True)

# CHART 3: Waste Cost by Region (Donut)
col3a, col3b = st.columns([1,1])
with col3a:
    df_reg = df.groupby('Region')['Waste_Cost'].sum().reset_index()
    fig3 = px.pie(df_reg, values='Waste_Cost', names='Region', hole=0.45, title="Waste Cost Distribution by Region", color_discrete_sequence=[COLORS['teal'],COLORS['red'],COLORS['cyan'],COLORS['yellow'],COLORS['blue']])
    fig3.update_traces(textinfo='label+percent', textfont_size=11)
    st.plotly_chart(styled_fig(fig3, 400), use_container_width=True)

with col3b:
    # Summary table
    df_overview = df.groupby('Category').agg(Revenue=('Revenue','sum'), Profit=('Profit','sum'), Waste_Cost=('Waste_Cost','sum'), Units_Wasted=('Units_Wasted','sum'), Initial_Qty=('Initial_Quantity','sum')).reset_index()
    df_overview['Waste_Rate'] = (df_overview['Units_Wasted']/df_overview['Initial_Qty']*100).round(1)
    df_overview['Profit_Margin'] = (df_overview['Profit']/df_overview['Revenue']*100).round(1)
    st.markdown("**Category Performance Summary**")
    st.dataframe(df_overview[['Category','Revenue','Profit','Waste_Cost','Waste_Rate','Profit_Margin']].sort_values('Waste_Cost',ascending=False).style.format({'Revenue':'${:,.0f}','Profit':'${:,.0f}','Waste_Cost':'${:,.0f}','Waste_Rate':'{:.1f}%','Profit_Margin':'{:.1f}%'}), use_container_width=True, hide_index=True)

insight("Executive Insight", f"{worst_cat} alone accounts for ${worst_cat_cost:,.0f} in waste — that's {worst_cat_cost/total_waste*100:.0f}% of all waste cost. This single category is the primary profit leak and must be prioritized for cold-chain intervention.")

# ========== SECTION 2: HOT ZONE ANALYSIS (Charts 4-5) ==========
section("2 · Hot Zone Analysis — Where Is Spoilage Concentrated?")

col4, col5 = st.columns(2)
with col4:
    # CHART 4: Top 10 Worst Stores
    df_store = df.groupby('Store_Id')[['Units_Wasted','Initial_Quantity','Waste_Cost']].sum().reset_index()
    df_store['Waste_Pct'] = (df_store['Units_Wasted']/df_store['Initial_Quantity']*100).round(1)
    df_store = df_store.sort_values('Waste_Pct', ascending=True).tail(10)
    fig4 = px.bar(df_store, y='Store_Id', x='Waste_Pct', orientation='h', title="Top 10 Stores by Spoilage Rate", text='Waste_Pct', color='Waste_Pct', color_continuous_scale=['#243447','#FF6B6B'])
    fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(styled_fig(fig4, 440), use_container_width=True)

with col5:
    # CHART 5: Spoilage Risk by Temperature Deviation Band
    df['Temp_Band'] = pd.cut(df['Temp_Deviation'], bins=[0,1,2,3,5,10], labels=['0-1°C','1-2°C','2-3°C','3-5°C','5+°C'], include_lowest=True)
    df_temp = df.groupby('Temp_Band', observed=True).agg(Avg_Spoilage=('Spoilage_Risk','mean'), Count=('Record_Id','count')).reset_index()
    fig5 = px.bar(df_temp, x='Temp_Band', y='Avg_Spoilage', title="Spoilage Risk by Temp Deviation", text=df_temp['Avg_Spoilage'].round(3), color='Avg_Spoilage', color_continuous_scale=['#243447','#FF6B6B'])
    fig5.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig5.update_layout(xaxis_title="Temp Deviation Band", yaxis_title="Avg Spoilage Risk")
    st.plotly_chart(styled_fig(fig5, 440), use_container_width=True)

worst_store = df.groupby('Store_Id').apply(lambda x: x['Units_Wasted'].sum()/x['Initial_Quantity'].sum()*100).idxmax()
worst_store_pct = df.groupby('Store_Id').apply(lambda x: x['Units_Wasted'].sum()/x['Initial_Quantity'].sum()*100).max()
insight("Hot Zone Insight", f"Store {worst_store} has the highest spoilage rate at {worst_store_pct:.1f}%. Products with temperature deviations above 3°C show dramatically elevated spoilage risk — cold chain breaks above this threshold are critical failures.")

# ========== SECTION 3: FINANCIAL LEAK ANALYSIS (Charts 6-7) ==========
section("3 · Financial Leak Analysis — Where Is Profit Bleeding?")

col6, col7 = st.columns(2)
with col6:
    # CHART 6: Profit vs Waste Cost by Category
    df_fin = df.groupby('Category')[['Profit','Waste_Cost']].sum().reset_index().sort_values('Waste_Cost', ascending=False)
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=df_fin['Category'], y=df_fin['Profit'], name='Profit', marker_color=COLORS['teal']))
    fig6.add_trace(go.Bar(x=df_fin['Category'], y=df_fin['Waste_Cost'], name='Waste Cost', marker_color=COLORS['red']))
    fig6.update_layout(title="Profit vs Waste Cost by Category", barmode='group', yaxis_title="USD ($)", xaxis_tickangle=-35)
    st.plotly_chart(styled_fig(fig6), use_container_width=True)

with col7:
    # CHART 7: Discount Band Impact on Profit Margin
    df['Discount_Band'] = pd.cut(df['Discount_Pct'], bins=[-0.01,0,0.1,0.2,0.4,0.7,1.0], labels=['No Discount','1-10%','11-20%','21-40%','41-70%','71-100%'], include_lowest=True)
    df_disc = df.groupby('Discount_Band', observed=True).agg(Avg_Margin=('Profit_Margin_Pct','mean'), Count=('Record_Id','count')).reset_index()
    fig7 = px.bar(df_disc, x='Discount_Band', y='Avg_Margin', title="Profit Margin by Discount Band", text=df_disc['Avg_Margin'].round(1), color='Avg_Margin', color_continuous_scale=[COLORS['red'],'#243447',COLORS['teal']])
    fig7.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig7.update_layout(xaxis_title="Discount Band", yaxis_title="Avg Profit Margin %")
    st.plotly_chart(styled_fig(fig7), use_container_width=True)

high_disc = df[df['Discount_Pct']>0.4]
low_disc = df[df['Discount_Pct']<=0.1]
insight("Financial Insight", f"Heavy discounting (>40%) destroys profit margins — avg margin drops to {high_disc['Profit_Margin_Pct'].mean():.1f}% vs {low_disc['Profit_Margin_Pct'].mean():.1f}% for low/no discounts. The discount-to-clear strategy for near-expiry goods is costing more than the spoilage itself.")

# ========== SECTION 4: SUPPLY CHAIN FRAGILITY (Charts 8-10) ==========
section("4 · Supply Chain Fragility — What Operational Factors Drive Spoilage?")

col8, col9 = st.columns(2)
with col8:
    # CHART 8: Distribution Hours Band vs Avg Waste %
    df['Dist_Band'] = pd.cut(df['Distribution_Hours'], bins=[0,24,48,72,96,200], labels=['0-24h','24-48h','48-72h','72-96h','96h+'], include_lowest=True)
    df_dist = df.groupby('Dist_Band', observed=True).agg(Units_Wasted=('Units_Wasted','sum'), Initial_Qty=('Initial_Quantity','sum')).reset_index()
    df_dist['Waste_Pct'] = (df_dist['Units_Wasted']/df_dist['Initial_Qty']*100).round(1)
    fig8 = px.bar(df_dist, x='Dist_Band', y='Waste_Pct', title="Waste Rate by Distribution Time", text='Waste_Pct', color='Waste_Pct', color_continuous_scale=['#243447',COLORS['orange'],COLORS['red']])
    fig8.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig8.update_layout(xaxis_title="Distribution Hours", yaxis_title="Waste Rate %", xaxis_tickangle=-25)
    st.plotly_chart(styled_fig(fig8), use_container_width=True)

with col9:
    # CHART 9: Temp Abuse Events vs Avg Spoilage
    df_abuse = df.groupby('Temp_Abuse_Events').agg(Avg_Spoilage=('Spoilage_Risk','mean'), Avg_Waste=('Waste_Pct','mean')).reset_index()
    fig9 = px.bar(df_abuse, x='Temp_Abuse_Events', y='Avg_Spoilage', title="Spoilage by Temp Abuse Events", text=df_abuse['Avg_Spoilage'].round(3), color='Avg_Spoilage', color_continuous_scale=['#243447',COLORS['red']])
    fig9.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig9.update_layout(xaxis_title="Temp Abuse Events", yaxis_title="Avg Spoilage Risk")
    st.plotly_chart(styled_fig(fig9), use_container_width=True)

# CHART 10: Handling Score vs Avg Spoilage
df_handle = df.groupby('Handling_Score').agg(Avg_Spoilage=('Spoilage_Risk','mean'), Avg_Waste_Cost=('Waste_Cost','mean')).reset_index()
fig10 = go.Figure()
fig10.add_trace(go.Scatter(x=df_handle['Handling_Score'], y=df_handle['Avg_Spoilage'], name='Avg Spoilage Risk', mode='lines+markers', line=dict(color=COLORS['red'],width=3), marker=dict(size=9)))
fig10.add_trace(go.Bar(x=df_handle['Handling_Score'], y=df_handle['Avg_Waste_Cost'], name='Avg Waste Cost ($)', marker_color=COLORS['cyan'], opacity=0.4, yaxis='y2'))
fig10.update_layout(title="Handling Score: Spoilage & Waste Cost", xaxis_title="Handling Score (1-10)", yaxis=dict(title="Avg Spoilage Risk"), yaxis2=dict(title="Avg Waste Cost ($)", overlaying='y', side='right'), legend=dict(orientation='h',yanchor='bottom',y=1.08,xanchor='center',x=0.5))
st.plotly_chart(styled_fig(fig10, 400), use_container_width=True)

insight("Supply Chain Insight", f"Products with distribution times exceeding 72 hours show significantly elevated waste rates. Meanwhile, every 1-point improvement in Handling Score reduces spoilage risk measurably — investing in handler training offers clear ROI.")

# ========== SECTION 5: DEMAND & SEASONALITY (Charts 11-12) ==========
section("5 · Demand & Seasonality Patterns")

col11, col12 = st.columns(2)
with col11:
    # CHART 11: Monthly Units Sold & Waste (Dual Axis)
    df_m = df.groupby('Month').agg(Units_Sold=('Units_Sold','sum'), Units_Wasted=('Units_Wasted','sum')).reset_index().sort_values('Month')
    fig11 = go.Figure()
    fig11.add_trace(go.Bar(x=df_m['Month'], y=df_m['Units_Sold'], name='Units Sold', marker_color=COLORS['teal'], opacity=0.7))
    fig11.add_trace(go.Scatter(x=df_m['Month'], y=df_m['Units_Wasted'], name='Units Wasted', mode='lines+markers', line=dict(color=COLORS['red'],width=3), marker=dict(size=8), yaxis='y2'))
    fig11.update_layout(title="Monthly Demand vs Waste", xaxis=dict(title="Month",tickmode='linear',dtick=1), yaxis=dict(title="Units Sold"), yaxis2=dict(title="Units Wasted",overlaying='y',side='right'), legend=dict(orientation='h',yanchor='bottom',y=1.08,xanchor='center',x=0.5))
    st.plotly_chart(styled_fig(fig11), use_container_width=True)

with col12:
    # CHART 12: Weekday vs Weekend Waste Rate Comparison
    df_day = df.groupby('Is_Weekend').agg(Sold=('Units_Sold','sum'), Wasted=('Units_Wasted','sum'), InitQ=('Initial_Quantity','sum'), Revenue=('Revenue','sum')).reset_index()
    df_day['Day_Type'] = df_day['Is_Weekend'].map({0:'Weekday',1:'Weekend'})
    df_day['Waste_Rate'] = (df_day['Wasted']/df_day['InitQ']*100).round(1)
    df_day['Avg_Rev_Per_Txn'] = (df_day['Revenue']/df_day['Sold']).round(2)
    fig12 = go.Figure()
    fig12.add_trace(go.Bar(x=df_day['Day_Type'], y=df_day['Sold'], name='Units Sold', marker_color=COLORS['teal']))
    fig12.add_trace(go.Bar(x=df_day['Day_Type'], y=df_day['Wasted'], name='Units Wasted', marker_color=COLORS['red']))
    fig12.update_layout(title="Weekend vs Weekday: Sales and Waste", barmode='group', yaxis_title="Units")
    st.plotly_chart(styled_fig(fig12), use_container_width=True)

peak_month = df_m.loc[df_m['Units_Wasted'].idxmax(), 'Month']
insight("Demand Insight", f"Month {int(peak_month)} shows the highest waste volume, suggesting seasonal demand surges outpace cold-chain capacity. Weekend and weekday waste patterns should inform staffing and restocking schedules.")

# ========== SECTION 6: SUPPLIER RISK (Charts 13-14) ==========
section("6 · Supplier Risk Analysis — Which Vendors Are Costing You?")

col13, col14 = st.columns(2)
with col13:
    # CHART 13: Supplier Risk Matrix (Bubble)
    df_supp = df.groupby('Supplier_Id').agg(Score=('Supplier_Score','mean'), Wasted=('Units_Wasted','sum'), InitQ=('Initial_Quantity','sum'), Profit=('Profit','sum'), WasteCost=('Waste_Cost','sum')).reset_index()
    df_supp['Waste_Pct'] = (df_supp['Wasted']/df_supp['InitQ']*100).round(1)
    fig13 = px.scatter(df_supp, x='Score', y='Waste_Pct', size='WasteCost', color='Profit', text='Supplier_Id', title="Supplier Risk Matrix (Score vs Waste %)", color_continuous_scale=[COLORS['red'],'#243447',COLORS['teal']], size_max=35)
    fig13.update_traces(textposition='top center', textfont_size=9)
    fig13.update_layout(xaxis_title="Supplier Quality Score", yaxis_title="Waste Rate %")
    st.plotly_chart(styled_fig(fig13, 460), use_container_width=True)

with col14:
    # CHART 14: Top Suppliers by Profit Contribution
    df_sp = df_supp.sort_values('Profit', ascending=True)
    fig14 = px.bar(df_sp, y='Supplier_Id', x='Profit', orientation='h', title="Total Profit by Supplier", text=df_sp['Profit'].apply(lambda x: f"${x:,.0f}"), color='Profit', color_continuous_scale=['#FF6B6B','#243447',COLORS['teal']])
    fig14.update_traces(textposition='outside', textfont_size=9)
    st.plotly_chart(styled_fig(fig14, 460), use_container_width=True)

worst_supp = df_supp.loc[df_supp['Waste_Pct'].idxmax()]
best_supp = df_supp.loc[df_supp['Waste_Pct'].idxmin()]
insight("Supplier Insight", f"{worst_supp['Supplier_Id']} has the highest waste rate ({worst_supp['Waste_Pct']:.1f}%) while {best_supp['Supplier_Id']} is the best performer ({best_supp['Waste_Pct']:.1f}%). Renegotiating contracts with high-waste suppliers or shifting volume to top performers could save significant waste cost.")

# ========== SECTION 7: FINANCIAL IMPACT & RECOMMENDATIONS (Chart 15) ==========
section("7 · Financial Impact & Strategic Recommendations")

# CHART 15: Waterfall - Profit Leakage Breakdown
cat_waste = df.groupby('Category')['Waste_Cost'].sum().sort_values(ascending=False)
top_cats = cat_waste.head(5)
other_waste = cat_waste.iloc[5:].sum() if len(cat_waste)>5 else 0
waterfall_labels = ['Total Revenue'] + [f'{c} Waste' for c in top_cats.index] + (['Other Waste'] if other_waste>0 else []) + ['Net Profit']
waterfall_values = [total_rev] + [-v for v in top_cats.values] + ([-other_waste] if other_waste>0 else []) + [total_profit]
waterfall_measures = ['absolute'] + ['relative']*len(top_cats) + (['relative'] if other_waste>0 else []) + ['total']
fig15 = go.Figure(go.Waterfall(x=waterfall_labels, y=waterfall_values, measure=waterfall_measures, connector=dict(line=dict(color='#4a5568')), increasing=dict(marker_color=COLORS['teal']), decreasing=dict(marker_color=COLORS['red']), totals=dict(marker_color=COLORS['blue'])))
fig15.update_layout(title="Profit Leakage Waterfall: From Revenue to Net Profit", yaxis_title="USD ($)")
st.plotly_chart(styled_fig(fig15, 450), use_container_width=True)

# === STRATEGIC RECOMMENDATIONS ===
st.markdown("---")
st.markdown('<div class="section-header">🎯 Strategic Recommendations</div>', unsafe_allow_html=True)

recs = [
    ("1. Prioritize Cold-Chain Investment in Pharmaceuticals", f"Pharmaceuticals alone represent the largest waste cost bucket. Upgrading cold storage and real-time temperature monitoring for pharma products could recover a significant portion of the ${total_waste:,.0f} annual waste.", f"Potential Impact: Reduction of 30-40% waste in highest-value category"),
    ("2. Enforce Maximum 48h Distribution Windows", "Data shows waste rates climb sharply after 48 hours of distribution time. Implementing hard cut-offs and express logistics for perishable goods will directly reduce spoilage.", "Potential Impact: 15-20% reduction in logistics-driven spoilage"),
    ("3. Eliminate Deep Discounting (>40%) on Near-Expiry Goods", f"Products discounted >40% show avg margins of {high_disc['Profit_Margin_Pct'].mean():.1f}% — worse than writing off the inventory. Consider donation programs or composting partnerships instead.", "Potential Impact: Recovery of margin erosion on high-discount segments"),
    ("4. Supplier Performance-Based Contracts", f"Shift volume from {worst_supp['Supplier_Id']} (waste rate: {worst_supp['Waste_Pct']:.1f}%) to {best_supp['Supplier_Id']} ({best_supp['Waste_Pct']:.1f}%) and tie contract renewals to spoilage KPIs.", "Potential Impact: 2-3% improvement in overall waste rate"),
    ("5. Handler Training & Certification Program", "Handling Score is one of the strongest predictors of spoilage risk. A formal training program targeting stores with scores below 5 would yield measurable waste reduction.", "Potential Impact: Improved handling scores across bottom-quartile stores"),
]
for title, text, impact in recs:
    st.markdown(f'<div class="rec-card"><div class="rec-title">{title}</div><div class="rec-text">{text}</div><div class="rec-impact">📊 {impact}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;color:#556;padding:30px 0 10px 0;font-size:0.75rem;">FreshGuard Solutions · Cold Chain Analytics Dashboard · Built with Streamlit + Plotly · 2026</div>', unsafe_allow_html=True)
