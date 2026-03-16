import pandas as pd
from sqlalchemy import create_engine

# 1. Load your local CSV file
print("Loading CSV...")
df = pd.read_csv('customer_shopping_behavior.csv')

# Clean the column names so they match what your app expects
df.columns = df.columns.str.lower().str.replace(' ', '_')
if 'purchase_amount_(usd)' in df.columns:
    df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})

# 2. Set up the connection to the Render Cloud Database
# IMPORTANT: Paste your EXTERNAL Database URL from Render here!
# It will look something like: postgresql://user:password@host.render.com/dbname
render_external_url = "postgresql://retail_analytics_db_user:3QjAleBDOHvnrLFfsSxnz1vak4wMPBjA@dpg-d6rs7bh4tr6s73aa8u20-a.oregon-postgres.render.com/retail_analytics_db"
engine = create_engine(render_external_url)

# 3. Push the data to the cloud database
print("Uploading data to Render... this might take a minute.")
df.to_sql("customer", engine, if_exists="replace", index=False)

print("✅ Data successfully uploaded! Your live app should work now.")