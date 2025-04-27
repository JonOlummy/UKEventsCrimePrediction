import os
import glob
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

snowflake_user = os.getenv('SNOWFLAKE_USER')
snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')
snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
snowflake_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
snowflake_database = os.getenv('SNOWFLAKE_DATABASE')
snowflake_schema = os.getenv('SNOWFLAKE_SCHEMA')
snowflake_table = os.getenv('SNOWFLAKE_TABLE')

base_path = '/Users/jono/Desktop/crime_data_uk'

def connect_to_snowflake():
    connection = snowflake.connector.connect(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        warehouse=snowflake_warehouse,
        database=snowflake_database,
        schema=snowflake_schema,
        insecure_mode=True
    )
    return connection

def read_files_in_folders(base_path):
    all_files = []
    folder_pattern = os.path.join(base_path, '*/')  
    folders = glob.glob(folder_pattern)  
    
    for folder in folders:
        file_pattern = os.path.join(folder, '*.csv')  
        files = glob.glob(file_pattern)  
        for file in files:
            print(f"Reading file: {file}")
            df = pd.read_csv(file)
            all_files.append(df)
            
    
    return pd.concat(all_files, ignore_index=True)

def prepare_dataframe_for_snowflake(df):
    df.columns = [col.strip().upper().replace(' ', '_') for col in df.columns]
    return df

def insert_data_into_snowflake(df):
    connection = connect_to_snowflake()
    try:
        success, num_chunks, num_rows, num_errors = write_pandas(connection, df, snowflake_table)
        if success:
            print(f"Successfully inserted {num_rows} rows into the table {snowflake_table}.")
        else:
            print(f"Error inserting data: {num_errors} errors occurred.")
    finally:
        connection.close()

def main():
    print("Loading data from all files...")
    df = read_files_in_folders(base_path)
    
    print("Preparing DataFrame for Snowflake...")
    df = prepare_dataframe_for_snowflake(df)
    
    print("Inserting data into Snowflake...")
    insert_data_into_snowflake(df)

if __name__ == "__main__":
    main()
