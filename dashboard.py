import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import streamlit as st

#Dashboard Title
st.set_page_config(page_title="Mini Product Performance Dashboard", layout="wide")
st.title("Mini Product Performance Dashboard")
st.markdown("This dashboard analyzes product sales perfonmance by category, region and time")

#Database Connection
conn = sqlite3.connect('product_sales.db')
sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
products_df = pd.read_sql_query("SELECT * FROM products", conn)
customers_df = pd.read_sql_query("SELECT * FROM  customers", conn)

df =(
    sales_df
    .merge(products_df, on='product_id', how='left')
    .merge(customers_df, on='customer_id', how='left')
)
df["sale_date"] = pd.to_datetime(df["sale_date"])
df["total_amount"] = df["quantity"] * df["price"]

#Sidebar Filters
st.sidebar.header("Filters")
categories = st.sidebar.multiselect("Select Categories", options=df["category"].unique(), default=df["category"].unique())
regions = st.sidebar.multiselect("Select Regions", options=df["region"].unique(), default=df["region"].unique())

filtered_df = df[(df["category"].isin(categories)) &  (df["region"].isin(regions))]


#Monthly Revenue Trend
st.subheader("Monthly Revenue Trend")
monthly_revenue = filtered_df.groupby(filtered_df["sale_date"].dt.to_period("M"))["total_amount"].sum().reset_index()
monthly_revenue["sale_date"] = monthly_revenue["sale_date"].dt.to_timestamp()

st.line_chart(monthly_revenue.rename(columns={"sale_date":"index"}).set_index("index")["total_amount"])
st.markdown("Graph: Shows total monthly revenue by selected category and region. Observe if the trend is rising or falling.")

#Category based income
st.subheader("Category Based Income")
category_revenue = filtered_df.groupby("category")["total_amount"].sum()
st.bar_chart(category_revenue)
st.markdown("Graph: You can quickly see which product category generates the most revenue.")

#Top Products (Quantity and Revenue)
st.subheader("Best Selling Products")
top_units = filtered_df.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(5)
st.bar_chart(top_units)
st.markdown("Graph: Displays the top 5 best-selling products by quantity.")

st.subheader("Top Profit Generating Products")
top_revenue = filtered_df.groupby("product_name")["total_amount"].sum().sort_values(ascending=False).head(5)
st.bar_chart(top_revenue)
st.markdown("Graph: Displays the top 5 products generating the highest revenue.")

#Region & Category Combination
st.subheader("Region & Category Combination")
region_category = filtered_df.pivot_table(
    index="region",
    columns="category",
    values="total_amount",
    aggfunc="sum"
).fillna(0)

st.bar_chart(region_category)
st.markdown("Graph: Compares revenue across different regions and categories to identify strong markets.")
