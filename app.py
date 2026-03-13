import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset you processed in your notebook
df = pd.read_csv('customer_shopping_behavior.csv')

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

st.title("🛒 Consumer Behavior Analytics in Retail")
st.markdown("Interactive analysis based on SQL & Power BI approach")

# Sidebar for Interaction
st.sidebar.header("Filter Data")
selected_category = st.sidebar.multiselect(
    "Select Category", 
    options=df['Category'].unique(), 
    default=df['Category'].unique()
)

# Filter logic
filtered_df = df[df['Category'].isin(selected_category)]

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(filtered_df))
col2.metric("Avg Purchase (USD)", f"${filtered_df['Purchase Amount (USD)'].mean():.2f}")
col3.metric("Avg Rating", f"{filtered_df['Review Rating'].mean():.1f}")

# Visualization
fig = px.bar(filtered_df, x="Season", y="Purchase Amount (USD)", color="Gender", barmode="group")
st.plotly_chart(fig, use_container_width=True)