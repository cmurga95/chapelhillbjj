
from daily_update import login_and_get_csv
import asyncio
from sqlalchemy import create_engine, text, insert, MetaData, Table
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

COLUMN_MAPPING = {
    "Client": "client",
    "Member Status": "member_status",
    "Session Datetime": "session_datetime",
    "Checkin Datetime": "checkin_datetime",
    "Session Type": "session_type",
    "Coach Name": "coach_name",
    "Assistant Coach Name": "assistant_coach_name",
    "Session Category Name": "session_category_name",
    "Session Title": "session_title",
    "Plan/Package": "plan_package"
}

def connect_and_query(query: str, engine):
    try:
        with engine.connect() as connection:
            database_df = pd.read_sql(query, connection)
            print("Connection successful!")
            return database_df
    except Exception as e:
        print(f"Failed to connect: {e}")

    

def clean_and_insert_data(new_data):
    # Rename columns
    new_data = new_data.rename(columns=COLUMN_MAPPING)
    engine = create_engine(DATABASE_URL)
    query = text("SELECT MAX(session_datetime) as session_datetime FROM checkins")
    metadata = MetaData()
    table = Table('checkins', metadata, autoload_with=engine)
    # Convert datetimes
    # new_data['session_datetime'] = pd.to_datetime(new_data['session_datetime'], format='mixed')
    # new_data['checkin_datetime'] = pd.to_datetime(new_data['checkin_datetime'], format='mixed')
    
    # Get max date from DB
    max_date = connect_and_query(query, engine)

    if not max_date.empty:
        mask = pd.to_datetime(new_data['session_datetime']).dt.date > pd.to_datetime(max_date['session_datetime']).dt.date.max()

        new_data = new_data[mask]
        # print(new_data)
        if not new_data.empty:
            data_to_insert = [row.to_dict() for _, row in new_data.iterrows()]
            with engine.connect() as connection:
                connection.execute(table.insert(), data_to_insert)
                connection.commit()
                #using pandas
                # new_data.to_sql(
                # name='checkins',
                # con=engine,
                # if_exists='append',
                # index=False
                # )
                print(f"Inserted {len(new_data)} records")
        else:
            print("No new data to insert")

def main():
    # Get data (await the coroutine)
    new_data = asyncio.run(login_and_get_csv(
        os.getenv("EMAIL_PP"),
        os.getenv("PASSWORD_PP"),
        os.getenv("URL_PP")
    ))
    
    # Process data
    clean_and_insert_data(new_data)

if __name__ == "__main__":
    main()