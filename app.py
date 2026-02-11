import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import millify as mf
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Superstore", layout="wide")

# Színek (pasztell)
COLOR_MAIN = "#4C78A8"    # pasztell kék (alap)
COLOR_MAX = "#8E99A8"     # sötétebb pasztell szürke (maximum kiemelés)
COLOR_LIGHT = "#DCE3EA"   # világos neutrális (harmadik szín)

# UI háttér (szürkés Looker feeling)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F2F4F7;
    }

    section[data-testid="stSidebar"] {
        background-color: #E9EDF2;
    }

    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0,0,0,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True)

@st.cache_data
def load():
    df = pd.read_csv("data.csv")
    return df

#streamlit run app.py

df = load()
#st.dataframe(df)

# A new year column is created with value extracted from Order Date.
df["Order_Date_Splitted"] = df["Order Date"].str.split(" ").str[0]
df["Year"] = df["Order_Date_Splitted"].str.split("/").str[2].astype(int)
#df["Year"].dtype

# A days to ship column is added with value is calculated from Order date and Ship date.
df["Ship_Date_Splitted"] = df["Ship Date"].str.split(" ").str[0]
ship_dt = pd.to_datetime(df["Ship_Date_Splitted"], format="%d/%m/%Y", errors="coerce")

df["Ship_Year"] = ship_dt.dt.year + 2
df["Ship_Month"] = ship_dt.dt.month
df["Ship_Day"] = ship_dt.dt.day

df["Ship Date"] = pd.to_datetime(df["Ship_Year"].astype(str) + "-" +df["Ship_Month"].astype(str) + "-" +df["Ship_Day"].astype(str),errors="coerce")
df = df.drop(columns=["Ship_Date_Splitted", "Ship_Year", "Ship_Month", "Ship_Day"])

order_dt = pd.to_datetime(df["Order_Date_Splitted"], format="%d/%m/%Y", errors="coerce")

df["Days_to_Ship"] = (df["Ship Date"] - order_dt).dt.days

df = df.drop(columns=["Order_Date_Splitted"])

#st.dataframe(df)

#Dataset is cleaned as needed

#print(df.isna().sum())
#st.write("Total NaN:", df.isnull().sum().sum())
#st.write("Missing Postal Code (before):", df["Postal Code"].isna().sum())

#st.dataframe(df)
#st.write("Number of rows:", df.shape[0])

# Postal Code hiányzók kitöltése
# A datasetben 11 hiányzó Postal Code van, mind Burlington, Vermont, itt célzott a kitöltés 
missing_postal = df["Postal Code"].isna().sum()
#st.write("Missing Postal Code (before):", missing_postal)

df.loc[(df["City"] == "Burlington") & (df["State"] == "Vermont") & (df["Postal Code"].isna()), "Postal Code"] = 5401

df["Postal Code"] = pd.to_numeric(df["Postal Code"], errors="coerce")

missing_postal_after = df["Postal Code"].isna().sum()
#st.write("Missing Postal Code (after):", missing_postal_after)

# Duplikációk kezelése
df = df.drop_duplicates()

# Dashboard layout tervezése
# Plan the dashboard layout. Based on the following expectations create a wireframe about the dashboard and its layout.
# Arrange the individual diagrams to taste, try to create a uniform look for the colors.
# Wireframe is created.
# Dashboard contains a Superstores title
# Colour usage and appearance are uniformed

st.sidebar.title("Filter")

category_filter = st.sidebar.multiselect("Category",sorted(df["Category"].dropna().unique()),default=sorted(df["Category"].dropna().unique()))
sub_category_filter = st.sidebar.multiselect("Sub-Category",sorted(df["Sub-Category"].dropna().unique()),default=sorted(df["Sub-Category"].dropna().unique()))
segment_filter = st.sidebar.multiselect("Segment",sorted(df["Segment"].dropna().unique()),default=sorted(df["Segment"].dropna().unique()))
region_filter = st.sidebar.multiselect("Region",sorted(df["Region"].dropna().unique()),default=sorted(df["Region"].dropna().unique()))
year_filter = st.sidebar.slider("Year",int(df["Year"].min()),int(df["Year"].max()),(int(df["Year"].min()), int(df["Year"].max())))

df_dashboard = df[(df["Category"].isin(category_filter)) &
    (df["Sub-Category"].isin(sub_category_filter)) &
    (df["Segment"].isin(segment_filter)) &
    (df["Region"].isin(region_filter)) &
    (df["Year"] >= year_filter[0]) &
    (df["Year"] <= year_filter[1])].copy()

# KPI
# The first section need to contain summarized data.
# Visualize the total sales, how much profit was made and how many distinct orders did the store receive?
total_sales = df_dashboard["Sales"].sum()
total_profit = df_dashboard["Profit"].sum()
distinct_orders_count = len(df_dashboard["Order ID"].unique())

total_sales_millify = mf.millify(total_sales, precision=2)
total_profit_millify = mf.millify(total_profit, precision=2)

st.markdown("<h1 style='text-align:center;'>SUPERSTORE</h1>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", total_sales_millify)
col2.metric("Total Profit", total_profit_millify)
col3.metric("Distinct Orders", distinct_orders_count)
col4.metric("Year", year_filter[1])

st.divider()#dashboard tagolását segíti, ez egy vizuális elválasztó vonal a dashboardon

# Top 10 products by sales
# Visualize the top 10 products by sales. Use bar chart to show the products and their total sales value!
# Horizontal bar chart is used to visualize top 10 products.
# Products are ordered by sales, most frequented product is located at the top of chart

top10_products_sales = (df_dashboard.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10).sort_values(ascending=True))
top1_product_sales = top10_products_sales[top10_products_sales == top10_products_sales.max()]

# Top 10 products by profit
# Visualize the top 10 products by profit. Use bar chart to show the products and their sum of profit value.
# Horizontal bar chart is used to visualize top 10 products
# Products are ordered by profit, most frequented product is located at the top of chart

top10_products_profit = (df_dashboard.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(10).sort_values(ascending=True))
top1_product_profit = top10_products_profit[top10_products_profit == top10_products_profit.max()]

# Average shipping days
# Visualize the average number of days it takes to ship an Order.
# Plotly indicator is used for visualization.
# The displayable range of indicator chart is the minimum and maximum value of Days to ship column.

avg_days_to_ship = df_dashboard["Days_to_Ship"].mean()
min_days_to_ship = df_dashboard["Days_to_Ship"].min()
max_days_to_ship = df_dashboard["Days_to_Ship"].max()

avg_days_value = round(avg_days_to_ship, 1)

gauge = go.Figure(go.Indicator(mode="gauge+number",value=avg_days_value,title={"text": "Average Shipping Days"},gauge={"axis": {"range": [min_days_to_ship, max_days_to_ship]},"bar": {"color": COLOR_MAIN}}))
gauge.update_layout(margin=dict(l=10, r=10, t=40, b=10))#a grafikon körüli margókat állítjuk be

# Sales trends
# Visualize the sales trends for different product categories over the year.
# Show the annual sum of sales values per product groups, broken down by year.
# Stacked bar chart is used, where the years are shown on the x axis and sales value is on y axis.
# Product categories are furniture, office suppliers and technology.

sales_by_year_category = (df_dashboard.groupby(["Year", "Category"])["Sales"].sum().reset_index())

years = sorted(df_dashboard["Year"].unique())

furniture_df = (sales_by_year_category[sales_by_year_category["Category"] == "Furniture"].sort_values("Year"))
office_df = (sales_by_year_category[sales_by_year_category["Category"] == "Office Supplies"].sort_values("Year"))
technology_df = (sales_by_year_category[sales_by_year_category["Category"] == "Technology"].sort_values("Year"))

furniture_values = furniture_df["Sales"].values
office_values = office_df["Sales"].values
technology_values = technology_df["Sales"].values

# DASHBOARD LAYOUT = Z forma

# Row 1: Top 10 Sales + Top 10 Profit (ugyanaz a méret)
# Row 2: Average Shipping Days (középre)
# Row 3: Sales Trends (teljes szélesség)

row1_left, row1_right = st.columns(2)

with row1_left:
    st.subheader("Top 10 Products by Sales")

    fig_sales, ax_sales = plt.subplots(figsize=(9, 5))
    ax_sales.barh(top10_products_sales.index, top10_products_sales.values, color=COLOR_MAIN)
    ax_sales.barh(top1_product_sales.index, top1_product_sales.values, color=COLOR_MAX)

    ax_sales.set_title("Top 10 Products by Sales", fontsize=14)
    ax_sales.set_xlabel("Total Sales (USD)", fontsize=11)
    ax_sales.set_ylabel("Product Name", fontsize=11)
    ax_sales.tick_params(labelsize=10)

    plt.tight_layout()
    st.pyplot(fig_sales)
    plt.clf() #letörli az előző ábrát a memóriából


with row1_right:
    st.subheader("Top 10 Products by Profit")

    fig_profit, ax_profit = plt.subplots(figsize=(9, 5))
    ax_profit.barh(top10_products_profit.index, top10_products_profit.values, color=COLOR_MAIN)
    ax_profit.barh(top1_product_profit.index, top1_product_profit.values, color=COLOR_MAX)

    ax_profit.set_title("Top 10 Products by Profit", fontsize=14)
    ax_profit.set_xlabel("Total Profit (USD)", fontsize=11)
    ax_profit.set_ylabel("Product Name", fontsize=11)
    ax_profit.tick_params(labelsize=10)

    plt.tight_layout()
    st.pyplot(fig_profit)
    plt.clf()

#menjen középre

left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    st.subheader("Average Shipping Days")
    st.plotly_chart(gauge, use_container_width=True)


# 3. sor:Trend legyen az utolsó, teljes szélességben
st.subheader("Sales Trends by Category")
sales_trend = (df_dashboard.groupby(["Year", "Category"])["Sales"].sum().reset_index())
sales_trend["Year"] = sales_trend["Year"].astype(str)

fig_trend = px.bar(sales_trend,x="Year",y="Sales",color="Category",barmode="stack",title="",color_discrete_map={"Furniture": COLOR_MAIN,"Office Supplies": COLOR_LIGHT,"Technology": COLOR_MAX})

fig_trend.update_layout(margin=dict(l=10, r=10, t=10, b=10),legend_title_text="Category")

st.plotly_chart(fig_trend, use_container_width=True)
