import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load CSV
for i in ["mumbai", "gurgaon", "kolkata", "hyderabad"]:
    csv_file = f"../datasources/datasource1_flats/{i}_processed.csv"
    df = pd.read_csv(csv_file)

    # Step 2: Connect to MySQL
    # Format: mysql+mysqlconnector://<user>:<password>@<host>/<database>
    engine = create_engine("mysql+mysqlconnector://root:Satyam%40123@localhost:3306/flats")

    # Step 3: Write DataFrame to MySQL (auto-creates table)
    df.to_sql(i, con=engine, if_exists="replace", index=False)

print("✅ CSV data inserted into MySQL successfully!")
