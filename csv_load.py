import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load CSV
csv_file = "D:\IIITD\# SEM\IIA\house-recommender\datasources\datasource1_flats\hyderabad_processed.csv"
df = pd.read_csv(csv_file)

# Step 2: Connect to MySQL
# Format: mysql+mysqlconnector://<user>:<password>@<host>/<database>
engine = create_engine("mysql+mysqlconnector://root:Avikalp2%40@localhost:3306/house_recommendation")

# Step 3: Write DataFrame to MySQL (auto-creates table)
df.to_sql("hyderabad", con=engine, if_exists="replace", index=False)

print("✅ CSV data inserted into MySQL successfully!")