import pandas as pd
from sqlalchemy import create_engine


for i in ["mumbai", "gurgaon", "kolkata", "hyderabad"]:
    csv_file = f"../datasources/datasource1_flats/{i}_processed.csv"
    df = pd.read_csv(csv_file)

    
    engine = create_engine("mysql+mysqlconnector://root:Satyam%40123@localhost:3306/flats")

  
    df.to_sql(i, con=engine, if_exists="replace", index=False)

print("✅ CSV data inserted into MySQL successfully!")
