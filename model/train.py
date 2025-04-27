import mindsdb_sdk
import time
# import nltk
# nltk.download('punkt_tab')


server_local = mindsdb_sdk.connect('http://127.0.0.1:47334')

model = server_local.create_model(
    name='uk_crime_predictor',
    predict='CRIME_TYPE',  
    query=f'''
            SELECT LONGITUDE, LATITUDE, MONTH, LOCATION, CRIME_TYPE, LSOA_NAME
            FROM (
                SELECT DISTINCT CRIME_ID, LONGITUDE, MONTH, LOCATION, LATITUDE, CRIME_TYPE, LSOA_NAME
                FROM PUBLIC.UK_CRIME_DATA
                WHERE LONGITUDE IS NOT NULL
                AND LATITUDE IS NOT NULL
                AND CRIME_TYPE IS NOT NULL
                AND CRIME_ID IS NOT NULL
            ) AS unique_data;
    ''',  
    database='snowflake_data',
    engine='lightwood', 
)

print(f"Training started for model: {model.name}")

while model.get_status() not in ('complete', 'error'):
    print("Model is still training... please wait.")
    time.sleep(5)

print(f"Model training finished! Status: {model.get_status()}")