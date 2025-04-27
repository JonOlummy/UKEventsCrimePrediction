from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import mindsdb_sdk
import os
import pandas as pd
from datetime import datetime

app = FastAPI()
mdb = mindsdb_sdk.connect(os.getenv("MINDSDB_API_URL"))
db = mdb.databases.get('snowflake_data')
model = mdb.models.get('uk_crime_predictor_4')


class AnalyticsRequest(BaseModel):
    start_date: str
    end_date: str


@app.get("/predict")
def predict_events(limit: int = 100, name: str = None, location: str = None, start_date: str = None, end_date: str = None):
    today = datetime.today().strftime('%Y-%m-%d') 
    
    sql = f"""
    SELECT
      ID,
      NAME,
      CAST(JSON_EXTRACT_PATH_TEXT(TO_JSON(_EMBEDDED),'venues[0].location.longitude') AS FLOAT) AS LONGITUDE,
      CAST(JSON_EXTRACT_PATH_TEXT(TO_JSON(_EMBEDDED),'venues[0].location.latitude') AS FLOAT) AS LATITUDE,
      JSON_EXTRACT_PATH_TEXT(TO_JSON(_EMBEDDED),'venues[0].address.line1') AS LOCATION,
      JSON_EXTRACT_PATH_TEXT(TO_JSON(_EMBEDDED),'venues[0].city.name') AS LSOA_NAME,
      CONCAT(
        JSON_EXTRACT_PATH_TEXT(TO_JSON(DATES),'start.localDate'),
        ' ',
        JSON_EXTRACT_PATH_TEXT(TO_JSON(DATES),'start.localTime')
      ) AS EVENT_DATETIME
    FROM PUBLIC.EVENTS
    WHERE LONGITUDE IS NOT NULL 
      AND LATITUDE IS NOT NULL
      AND EVENT_DATETIME >= '{today}' 
    """
    
    if name:
        sql += f" AND LOWER(NAME) LIKE LOWER('%{name}%')"
    if location:
        sql += f" AND LOWER(LSOA_NAME) LIKE LOWER('%{location}%')"
    if start_date:
        sql += f" AND EVENT_DATETIME >= '{start_date}'"
    if end_date:
        sql += f" AND EVENT_DATETIME <= '{end_date}'"
    
    sql += f" LIMIT {limit};"  
    
    qr = db.query(sql)
    rows = qr.fetch()
    df = pd.DataFrame(rows)

    df.columns = [col.upper() for col in df.columns]

    df['EVENT_DATETIME'] = pd.to_datetime(df['EVENT_DATETIME'], errors='coerce')
    df['MONTH'] = df['EVENT_DATETIME'].dt.strftime('%Y-%m')

    features = df[['LONGITUDE', 'LATITUDE', 'LOCATION', 'LSOA_NAME', 'MONTH']]

    try:
        preds = model.predict(features, params={"predict_proba": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    out = pd.concat([df.reset_index(drop=True), preds.reset_index(drop=True)], axis=1)
    
    return out.to_dict(orient='records')


@app.get("/analytics/crime_by_location")
def crime_counts_by_location(
    location_search: Optional[str] = Query(default=""),
    from_date: Optional[str] = Query(default=""),
    to_date: Optional[str] = Query(default="")
):

    location_search_upper = location_search.upper()

    sql = f"""
    SELECT CRIME_TYPE,LSOA_NAME, MONTH, COUNT(*) AS crime_count
    FROM PUBLIC.UK_CRIME_DATA
    WHERE 1=1
    """

    if location_search_upper:
        sql += f" AND UPPER(LSOA_NAME) LIKE '%{location_search_upper}%'"

    if from_date and to_date:
        sql += f" AND MONTH BETWEEN '{from_date}' AND '{to_date}'"
    elif from_date:
        sql += f" AND MONTH >= '{from_date}'"
    elif to_date:
        sql += f" AND MONTH <= '{to_date}'"

    sql += """
    GROUP BY CRIME_TYPE, LSOA_NAME, MONTH
    ORDER BY crime_count DESC;
    """

    try:
        query = db.query(sql)
        df = query.fetch()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crime counts by location failed: {str(e)}")