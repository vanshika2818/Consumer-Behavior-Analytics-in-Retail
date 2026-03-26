import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import os # Added to securely read the Environment Variable

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")
st.title("Dynamic Consumer Behavior Analytics")

# --- 5. LIVE DATABASE INTEGRATION (Read) ---
@st.cache_data
def load_data():
    # 1. Securely fetch the database URL from Render's environment variables
    db_url = os.environ.get("DATABASE_URL")
    
    # 2. Connect to the cloud database
    engine = create_engine(db_url)
    
    # 3. Read the data live from the database instead of the CSV!
    df = pd.read_sql("SELECT * FROM customer", engine)
    
    # Clean up column names in case they changed
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    if 'purchase_amount_(usd)' in df.columns:
        df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})
        
    # ✨ FIX: Handle missing values in previous_purchases column
    if 'previous_purchases' in df.columns:
        df['previous_purchases'] = df['previous_purchases'].fillna(0)
        
    if 'age_group' not in df.columns:
        labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
        df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)
        
    return df

df = load_data()

# --- 1. DYNAMIC FILTERING & QUERYING ---
st.sidebar.header("Dashboard Filters")

# Sidebar widgets
selected_season = st.sidebar.multiselect("Select Season(s)", df['season'].unique(), default=df['season'].unique())
selected_category = st.sidebar.multiselect("Select Category(s)", df['category'].unique(), default=df['category'].unique())
selected_age = st.sidebar.multiselect("Select Age Group(s)", df['age_group'].unique(), default=df['age_group'].unique())

# Apply the filters to the dataframe
filtered_df = df[
    (df['season'].isin(selected_season)) & 
    (df['category'].isin(selected_category)) &
    (df['age_group'].isin(selected_age))
]

# --- KPI METRICS ---
st.markdown("Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)

# Calculate metrics dynamically based on filters
kpi1.metric(label="Total Records", value=len(filtered_df))
kpi2.metric(label="Average Purchase", value=f"${filtered_df['purchase_amount'].mean():.2f}")
kpi3.metric(label="Total Revenue", value=f"${filtered_df['purchase_amount'].sum():,.2f}")

st.markdown("---")
# --- 3. INTERACTIVE VISUALIZATIONS ---
st.subheader("Visual Analytics")
col1, col2 = st.columns(2)

with col1:
    # Scatter plot with Hover Data and Zoom/Pan capabilities
    fig_scatter = px.scatter(
        filtered_df, x="age", y="purchase_amount", 
        color="category", size="previous_purchases",
        hover_data=["item_purchased", "location"], # Reveals details on hover
        title="Purchase Amount vs. Age"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    # Bar chart to explore categorical distributions
    fig_bar = px.histogram(
        filtered_df, x="frequency_of_purchases", color="gender",
        barmode="group", title="Purchase Frequency Distribution"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 2. REAL-TIME DATA EXPLORATION ---
st.subheader("Real-Time Data Exploration")
st.write("Click column headers to sort, or use the magnifying glass to search.")
# Renders an interactive table
st.dataframe(filtered_df, use_container_width=True, height=250)

# Generate a CSV of the filtered results for download
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_customer_data.csv',
    mime='text/csv',
)

# --- 4. PARAMETER TUNING / MODELS ---
st.subheader("Parameter Tuning / Customer Profiling")
st.write("Enter hypothetical customer details to calculate their profile segment.")

with st.form("profiling_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        input_age = st.number_input("Customer Age", min_value=18, max_value=100, value=30)
    with col_b:
        input_purchases = st.number_input("Previous Purchases", min_value=0, max_value=100, value=10)
        
    submitted = st.form_submit_button("Calculate Profile")
    if submitted:
        # Simulating the statistical model/logic
        predicted_group = "Young Adult" if input_age <= 31 else ("Adult" if input_age <= 44 else ("Middle-aged" if input_age <= 57 else "Senior"))
        loyalty = "High" if input_purchases > 25 else "Standard"
        st.success(f"**Calculated Segment:** {predicted_group} | **Loyalty Tier:** {loyalty}")

# --- 5. LIVE DATABASE INTEGRATION (Write-Back) ---
st.sidebar.markdown("---")
st.sidebar.header("Add New Transaction")

with st.sidebar.form("write_back_form"):
    new_age = st.number_input("Customer Age", 18, 100, 25)
    new_category = st.selectbox("Category", df['category'].unique())
    new_amount = st.number_input("Purchase Amount ($)", 1, 1000, 50)
    
    submit_tx = st.form_submit_button("Submit to Database")
    if submit_tx:
        # Reconnect to the database to insert the new row
        db_url = os.environ.get("DATABASE_URL")
        engine = create_engine(db_url)
        
        # Execute the SQL Insert command
        insert_query = f"INSERT INTO customer (age, category, purchase_amount) VALUES ({new_age}, '{new_category}', {new_amount})"
        
        with engine.connect() as conn:
            # Replaced st.text with sqlalchemy's text
            conn.execute(text(insert_query))
            conn.commit()
            
        st.sidebar.success(f"Transaction recorded! Added ${new_amount} for {new_category}.")
        
        load_data.clear()
        # This forces Streamlit to refresh the page and fetch the updated data!
        st.rerun()