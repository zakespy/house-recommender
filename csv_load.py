import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load CSV
csv_file = r"D:\IIA\house-recommender\datasources\datasource1_flats\kolkata_processed.csv"
df = pd.read_csv(csv_file)

# Step 2: Connect using PyMySQL
engine = create_engine(
    "mysql+pymysql://root:Satyam%40123@localhost:3306/flats"
)

# Step 3: Write DataFrame to MySQL
df.to_sql("kolkata", con=engine, if_exists="replace", index=False)

print("✅ CSV data inserted into MySQL successfully!")
