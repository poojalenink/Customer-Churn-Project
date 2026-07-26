import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit as st
import pandas as pd
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

st.write("Current Working Directory:", os.getcwd())
st.write("BASE_DIR:", BASE_DIR)
st.write("BASE_DIR exists:", BASE_DIR.exists())

st.write("Folders in BASE_DIR:")
st.write(os.listdir(BASE_DIR))

OUTPUTS = BASE_DIR / "outputs"
st.write("Outputs exists:", OUTPUTS.exists())

if OUTPUTS.exists():
    st.write("Files in outputs:")
    st.write(os.listdir(OUTPUTS))

csv_path = OUTPUTS / "cleaned_customer_churn.csv"
st.write("CSV exists:", csv_path.exists())
st.write("CSV path:", csv_path)

if not csv_path.exists():
    st.stop()

df = pd.read_csv(csv_path)
# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="Customer Churn Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CUSTOM CSS (Power BI Style)
# -------------------------------------------------
st.markdown("""
<style>

.main{
    background-color:#F4F7FC;
}

.block-container{
    padding-top:1rem;
}

section[data-testid="stSidebar"]{
    background:#0B2545;
}

section[data-testid="stSidebar"] *{
    color:white;
}

div[data-testid="metric-container"]{
    background:linear-gradient(135deg,#0F4C81,#3A7BD5);
    padding:18px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.2);
}

div[data-testid="metric-container"] label{
    color:white !important;
}

div[data-testid="metric-container"] div{
    color:white !important;
}

h1{
    color:#0B2545;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DASHBOARD TITLE
# -------------------------------------------------
st.markdown("""
<h1 style='text-align:center;'>
🏦 Customer Segmentation & Churn Analytics
</h1>

<h4 style='text-align:center;color:gray;'>
European Banking Customer Churn Dashboard
</h4>

<hr>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD DATASET
# -------------------------------------------------
try:
    df = pd.read_csv("../outputs/cleaned_customer_churn.csv")
except:
    df = pd.read_csv("../outputs/cleaned_customer_churn.csv")

# -------------------------------------------------
# CREATE MISSING COLUMNS
# -------------------------------------------------

if "Age Group" not in df.columns:
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=[0,30,45,60,100],
        labels=["<30","30-45","46-60","60+"]
    )

if "Credit Score Band" not in df.columns:
    df["Credit Score Band"] = pd.cut(
        df["CreditScore"],
        bins=[0,580,700,850],
        labels=["Low","Medium","High"]
    )

if "Balance Segment" not in df.columns:
    df["Balance Segment"] = pd.cut(
        df["Balance"],
        bins=[-1,0,100000,float("inf")],
        labels=[
            "Zero Balance",
            "Low Balance",
            "High Balance"
        ]
    )

if "Churn Status" not in df.columns:
    df["Churn Status"] = df["Exited"].replace({
        0:"Retained",
        1:"Churned"
    })

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.image(
    "https://img.icons8.com/color/240/bank-building.png",
    width=100
)

st.sidebar.title("Dashboard Filters")

st.sidebar.markdown("---")

geography = st.sidebar.multiselect(
    "Geography",
    sorted(df["Geography"].unique()),
    default=sorted(df["Geography"].unique())
)

gender = st.sidebar.multiselect(
    "Gender",
    sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

age_group = st.sidebar.multiselect(
    "Age Group",
    list(df["Age Group"].dropna().unique()),
    default=list(df["Age Group"].dropna().unique())
)

credit_band = st.sidebar.multiselect(
    "Credit Score Band",
    list(df["Credit Score Band"].dropna().unique()),
    default=list(df["Credit Score Band"].dropna().unique())
)

balance_segment = st.sidebar.multiselect(
    "Balance Segment",
    list(df["Balance Segment"].dropna().unique()),
    default=list(df["Balance Segment"].dropna().unique())
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------

filtered_df = df[
    (df["Geography"].isin(geography)) &
    (df["Gender"].isin(gender)) &
    (df["Age Group"].isin(age_group)) &
    (df["Credit Score Band"].isin(credit_band)) &
    (df["Balance Segment"].isin(balance_segment))
]

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

st.markdown("## 📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Total Customers",
        f"{len(filtered_df):,}"
    )

with col2:
    churn_rate = filtered_df["Exited"].mean() * 100
    st.metric(
        "📉 Churn Rate",
        f"{churn_rate:.2f}%"
    )

with col3:
    avg_balance = filtered_df["Balance"].mean()
    st.metric(
        "💰 Avg Balance",
        f"${avg_balance:,.0f}"
    )

with col4:
    avg_credit = filtered_df["CreditScore"].mean()
    st.metric(
        "⭐ Avg Credit Score",
        f"{avg_credit:.0f}"
    )

st.markdown("---")

# =====================================================
# CHURN RATE BY GEOGRAPHY
# =====================================================

geo = (
    filtered_df
    .groupby("Geography")["Exited"]
    .mean()
    .reset_index()
)

fig1 = px.bar(
    geo,
    x="Geography",
    y="Exited",
    color="Geography",
    text_auto=".1%",
    title="Churn Rate by Geography",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig1.update_layout(
    template="plotly_white",
    title_x=0.25,
    yaxis_title="Churn Rate"
)

# =====================================================
# CHURN RATE BY AGE GROUP
# =====================================================

age = (
    filtered_df
    .groupby("Age Group")["Exited"]
    .mean()
    .reset_index()
)

fig2 = px.bar(
    age,
    x="Age Group",
    y="Exited",
    color="Age Group",
    text_auto=".1%",
    title="Churn Rate by Age Group",
    color_discrete_sequence=px.colors.sequential.Blues
)

fig2.update_layout(
    template="plotly_white",
    title_x=0.20,
    yaxis_title="Churn Rate"
)

# =====================================================
# DISPLAY BOTH CHARTS
# =====================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with right:
    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.markdown("---")

# =====================================================
# GENDER-WISE CHURN
# =====================================================

gender_df = (
    filtered_df
    .groupby("Gender")["Exited"]
    .mean()
    .reset_index()
)

fig3 = px.pie(
    gender_df,
    names="Gender",
    values="Exited",
    hole=0.55,
    title="Gender-wise Churn Rate",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig3.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig3.update_layout(
    template="plotly_white",
    title_x=0.25
)

# =====================================================
# CREDIT SCORE BAND ANALYSIS
# =====================================================

credit = (
    filtered_df
    .groupby("Credit Score Band")["Exited"]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    credit,
    x="Credit Score Band",
    y="Exited",
    color="Credit Score Band",
    text_auto=".1%",
    title="Churn by Credit Score Band",
    color_discrete_sequence=px.colors.sequential.Teal
)

fig4.update_layout(
    template="plotly_white",
    title_x=0.18,
    yaxis_title="Churn Rate"
)

# =====================================================
# DISPLAY FIRST ROW
# =====================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with right:
    st.plotly_chart(
        fig4,
        use_container_width=True
    )

st.markdown("---")

# =====================================================
# BALANCE SEGMENT ANALYSIS
# =====================================================

balance = (
    filtered_df
    .groupby("Balance Segment")["Exited"]
    .mean()
    .reset_index()
)

fig5 = px.bar(
    balance,
    x="Balance Segment",
    y="Exited",
    color="Balance Segment",
    text_auto=".1%",
    title="Churn by Balance Segment",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig5.update_layout(
    template="plotly_white",
    title_x=0.20,
    yaxis_title="Churn Rate"
)

# =====================================================
# ACTIVE MEMBER ANALYSIS
# =====================================================

active = (
    filtered_df
    .groupby("IsActiveMember")["Exited"]
    .mean()
    .reset_index()
)

active["Member Status"] = active["IsActiveMember"].replace({
    0: "Inactive",
    1: "Active"
})

fig6 = px.bar(
    active,
    x="Member Status",
    y="Exited",
    color="Member Status",
    text_auto=".1%",
    title="Active Members vs Churn",
    color_discrete_sequence=px.colors.qualitative.Safe
)

fig6.update_layout(
    template="plotly_white",
    title_x=0.22,
    yaxis_title="Churn Rate"
)

# =====================================================
# DISPLAY SECOND ROW
# =====================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig5,
        use_container_width=True
    )

with right:
    st.plotly_chart(
        fig6,
        use_container_width=True
    )

st.markdown("---")

# =====================================================
# PRODUCTS VS CHURN
# =====================================================

products = (
    filtered_df
    .groupby("NumOfProducts")["Exited"]
    .mean()
    .reset_index()
)

fig7 = px.line(
    products,
    x="NumOfProducts",
    y="Exited",
    markers=True,
    title="Products Owned vs Churn Rate"
)

fig7.update_traces(
    line=dict(width=4)
)

fig7.update_layout(
    template="plotly_white",
    title_x=0.22,
    xaxis_title="Number of Products",
    yaxis_title="Churn Rate"
)

# =====================================================
# BALANCE VS SALARY
# =====================================================

fig8 = px.scatter(
    filtered_df,
    x="Balance",
    y="EstimatedSalary",
    color="Churn Status",
    size="CreditScore",
    hover_data=[
        "CustomerId",
        "Age",
        "Geography"
    ],
    title="Balance vs Estimated Salary",
    color_discrete_sequence=["#2E86DE", "#E74C3C"]
)

fig8.update_layout(
    template="plotly_white",
    title_x=0.20
)

# =====================================================
# DISPLAY FIRST ROW
# =====================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig7,
        use_container_width=True
    )

with right:
    st.plotly_chart(
        fig8,
        use_container_width=True
    )

st.markdown("---")

# =====================================================
# CUSTOMER DISTRIBUTION BY COUNTRY
# =====================================================

country = (
    filtered_df["Geography"]
    .value_counts()
    .reset_index()
)

country.columns = ["Geography", "Customers"]

fig9 = px.bar(
    country,
    x="Geography",
    y="Customers",
    color="Geography",
    text="Customers",
    title="Customer Distribution by Country",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig9.update_layout(
    template="plotly_white",
    title_x=0.20
)

# =====================================================
# CHURN STATUS DISTRIBUTION
# =====================================================

status = (
    filtered_df["Churn Status"]
    .value_counts()
    .reset_index()
)

status.columns = ["Status", "Customers"]

fig10 = px.pie(
    status,
    names="Status",
    values="Customers",
    hole=0.55,
    title="Customer Churn Distribution",
    color_discrete_sequence=["#2ECC71", "#E74C3C"]
)

fig10.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig10.update_layout(
    template="plotly_white",
    title_x=0.25
)

# =====================================================
# DISPLAY SECOND ROW
# =====================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig9,
        use_container_width=True
    )

with right:
    st.plotly_chart(
        fig10,
        use_container_width=True
    )

st.markdown("---")

# =====================================================
# CUSTOMER DATA TABLE
# =====================================================

st.markdown("## 📋 Customer Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)

# =====================================================
# DOWNLOAD FILTERED DATA
# =====================================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_customer_churn.csv",
    mime="text/csv"
)

st.markdown("---")

# =====================================================
# BUSINESS INSIGHTS
# =====================================================

st.markdown("## 📊 Key Business Insights")

highest_geo = (
    filtered_df.groupby("Geography")["Exited"]
    .mean()
    .idxmax()
)

highest_age = (
    filtered_df.groupby("Age Group")["Exited"]
    .mean()
    .idxmax()
)

highest_credit = (
    filtered_df.groupby("Credit Score Band")["Exited"]
    .mean()
    .idxmax()
)

st.info(f"""
**Highest Churn Geography:** {highest_geo}

**Highest Risk Age Group:** {highest_age}

**Highest Risk Credit Band:** {highest_credit}
""")

# =====================================================
# RECOMMENDATIONS
# =====================================================

st.markdown("## 💡 Business Recommendations")

st.success("""
• Focus customer retention campaigns in high-churn regions.

• Improve engagement among inactive customers.

• Provide personalized offers to high-value customers.

• Monitor customers with low credit scores.

• Encourage customers to use multiple banking products.

• Build loyalty programs for long-term customers.
""")

st.markdown("---")

# =====================================================
# DASHBOARD SUMMARY
# =====================================================

st.markdown("## 📈 Dashboard Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Countries",
        filtered_df["Geography"].nunique()
    )

with col2:
    st.metric(
        "Male Customers",
        len(filtered_df[filtered_df["Gender"]=="Male"])
    )

with col3:
    st.metric(
        "Female Customers",
        len(filtered_df[filtered_df["Gender"]=="Female"])
    )

st.markdown("---")

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div style='text-align:center;
background-color:#0B2545;
padding:18px;
border-radius:10px;
color:white;'>

<h3>Customer Segmentation & Churn Pattern Analytics</h3>

<p>
Developed by <b>Pooja Lenin</b>
</p>

<p>
Python | Pandas | Plotly | Streamlit
</p>

<p>
© 2026 All Rights Reserved
</p>

</div>
""", unsafe_allow_html=True)

st.balloons()

st.success("✅ Dashboard Loaded Successfully")
