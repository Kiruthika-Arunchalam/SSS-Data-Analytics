import streamlit as st
import pandas as pd
import plotly.express as px


# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

# ---------------------------
# GRADIENT CSS (🔥 PREMIUM)
# ---------------------------
st.markdown("""
<style>

/* Title */
.title {
    background: linear-gradient(90deg, #667eea, #764ba2, #43cea2);
    padding: 18px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: white;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* Section */
.section {
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    padding: 10px;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-top: 25px;
}

/* Cards */
.card {
    padding: 25px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-weight: bold;
}

/* Card colors */
.card1 { background: linear-gradient(135deg, #667eea, #764ba2); }
.card2 { background: linear-gradient(135deg, #43cea2, #185a9d); }
.card3 { background: linear-gradient(135deg, #36d1dc, #5b86e5); }
.card4 { background: linear-gradient(135deg, #ff758c, #ff7eb3); }

</style>
""", unsafe_allow_html=True)

# ---------------------------
# TITLE
# ---------------------------
st.markdown('<div class="title">SSS DATA ANALYTICS (FEB)</div>', unsafe_allow_html=True)

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1T7O5A61vP1LulBdcTVBsL27bJvLDkM1j"
    return pd.read_csv(url)
    df = load_data()

# ---------------------------
# DATE CLEAN
# ---------------------------
df["Inserted_Date"] = pd.to_datetime(df["Inserted_At"]).dt.strftime('%Y-%m-%d')

# ---------------------------
# FILTERS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

operator = col1.multiselect("Operator", df["Operator_Code"].unique())
service = col2.multiselect("Service", df["Service"].unique())
from_port = col3.multiselect("From Port", df["From_Port"].unique())
to_port = col4.multiselect("To Port", df["To_Port"].unique())

if not operator: operator = df["Operator_Code"].unique()
if not service: service = df["Service"].unique()
if not from_port: from_port = df["From_Port"].unique()
if not to_port: to_port = df["To_Port"].unique()

filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port))
]

# ---------------------------
# KPI CARDS
# ---------------------------
#st.markdown('<div class="section">OVERALL SUMMARY</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">TOTAL OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">TOTAL PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TOTAL TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">TOTAL VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# CHART (NO GRID)
# ---------------------------
st.markdown('<div class="section">DATE WISE OPERATOR DISTRIBUTION</div>', unsafe_allow_html=True)

operator_trend = (
    filtered_df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

fig = px.bar(
    operator_trend,
    x="Inserted_Date",
    y="Count",
    color="Operator_Code",
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Bold
)

# REMOVE GRID 🔥
fig.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)
# ---------------------------
# TOP ROUTES (PROPER COLORS)
# ---------------------------
st.markdown('<div class="section">TOP ROUTES</div>', unsafe_allow_html=True)

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(
    route_df,
    x="Count",
    y="Route",
    orientation="h",
    color="Route",  # 🔥 each route gets unique color
    color_discrete_sequence=px.colors.qualitative.Set2  # clean palette
)

fig_route.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    plot_bgcolor="white",
    showlegend=False  # cleaner UI
)

st.plotly_chart(fig_route, use_container_width=True)
# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">SERVICE DISTRIBUTION (TOP 10)</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

# Top 10 + Others
top10 = service_df.head(10)
others = service_df["Count"][10:].sum()

if others > 0:
    top10.loc[len(top10)] = ["Others", others]

fig_service = px.bar(
    top10,
    x="Count",
    y="Service",
    orientation="h",
    color="Count",
    color_continuous_scale="Tealgrn"   # 🔥 clean gradient
)

fig_service.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    plot_bgcolor="white"
)

st.plotly_chart(fig_service, use_container_width=True)
