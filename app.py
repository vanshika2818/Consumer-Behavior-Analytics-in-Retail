import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Load your pre-processed dataset
df = pd.read_csv('customer_shopping_behavior.csv')

# 2. Add Sidebar Interactivity
st.sidebar.header("Filter Results")
selected_season = st.sidebar.multiselect("Select Season", options=df['Season'].unique(), default=df['Season'].unique())
selected_category = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())

# 3. Filter data based on user input
filtered_df = df[(df['Season'].isin(selected_season)) & (df['Category'].isin(selected_category))]

# 4. Display Live Metrics
st.title("Consumer Behavior Analytics")
col1, col2 = st.columns(2)
col1.metric("Average Purchase Amount", f"${filtered_df['Purchase Amount (USD)'].mean():.2f}")
col2.metric("Avg Review Rating", f"{filtered_df['Review Rating'].mean():.1f} / 5.0")

# 5. Interactive Visuals
fig = px.sunburst(filtered_df, path=['Category', 'Item Purchased'], values='Purchase Amount (USD)')
st.plotly_chart(fig)