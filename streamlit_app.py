import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium 

def fetch_predict_data(limit, name, location, start_date, end_date):
    url = f"http://127.0.0.1:8000/predict?limit={limit}&name={name}&location={location}&start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    return response.json()

def fetch_crime_by_location_data(location_search, from_date, to_date):
    url = f"http://127.0.0.1:8000/analytics/crime_by_location?location_search={location_search}&from_date={from_date}&to_date={to_date}"
    response = requests.get(url)
    return response.json()

st.sidebar.title("Crime Prediction and Analytics")
page = st.sidebar.selectbox("Choose a page", ["Crime Prediction", "Crime Analytics"])

if page == "Crime Prediction":
    st.title("Crime Prediction for Event Locations")

    limit = st.slider("Limit", min_value=50, max_value=100, value=10, step=1)
    name = st.text_input("Event Name", "")  
    location = st.text_input("Location", "")  
    start_date = st.date_input("Start Date", pd.to_datetime("today")) 
    end_date = st.date_input("End Date", value=None)

    prediction_data = fetch_predict_data(limit, name, location, start_date, end_date)

    if isinstance(prediction_data, list) and prediction_data:
        prediction_df = pd.DataFrame(prediction_data)
    else:
        st.error("No prediction data available or data format is incorrect.")
        prediction_df = pd.DataFrame() 

    if not prediction_df.empty:
        st.subheader("Map of Predicted Crimes")
        map_center = [prediction_df["LATITUDE"].mean(), prediction_df["LONGITUDE"].mean()]
        crime_map = folium.Map(location=map_center, zoom_start=7)
        marker_cluster = MarkerCluster().add_to(crime_map)

        for _, row in prediction_df.iterrows():
            popup_info = f"""
            <div style="width: 300px; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
                <b>Event Name:</b> {row['NAME']}<br>
                <b>Event Time:</b> {row['EVENT_DATETIME']}<br>
                <b>Address:</b> {row['LOCATION']}<br>
                <b>City:</b> {row['LSOA_NAME']}<br>
                <b>Crime:</b> {row['CRIME_TYPE']}<br>
                <b>Confidence:</b> {row['CRIME_TYPE_confidence']:.2f}
            </div>
            """
            
            folium.Marker(
                [row['LATITUDE'], row['LONGITUDE']],
                popup=folium.Popup(popup_info, max_width=500)
            ).add_to(marker_cluster)
        st_folium(crime_map, width=700)

        st.subheader("Crime Prediction Data")
        prediction_df["PREDICTION"] = prediction_df["CRIME_TYPE"]
       
        grid_columns = ["NAME", "LOCATION", "LSOA_NAME", "PREDICTION", "EVENT_DATETIME"]
        st.dataframe(prediction_df[grid_columns])

        st.markdown("Data Source: [Ticket Master](https://www.ticketmaster.co.uk/)")


elif page == "Crime Analytics":
    st.title("UK Crime Analytics by Location")

    location_search = st.text_input("Location Search", "London")
    from_date = st.date_input("From Date", pd.to_datetime("2024-01-01"))
    to_date = st.date_input("To Date", pd.to_datetime("2025-02-01"))

    analytics_data = fetch_crime_by_location_data(location_search, from_date, to_date)
    analytics_df = pd.DataFrame(analytics_data)

    if not analytics_df.empty:
        st.subheader("Crime Statistics")

        crime_count = analytics_df["crime_count"].sum()
        st.write(f"Total Crimes: {crime_count}")
        top_crime = analytics_df.groupby("crime_type")["crime_count"].sum().idxmax()
        st.write(f"Top Crime Committed: {top_crime}")

        st.subheader("Total Crimes by Type")
        total_crimes = analytics_df.groupby("crime_type")["crime_count"].sum().sort_values(ascending=False)

        total_crimes_fig = px.pie(total_crimes, names=total_crimes.index, values=total_crimes.values, 
                                  title="Total Crimes by Crime Type", 
                                  color=total_crimes.index, 
                                  color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(total_crimes_fig)

        st.subheader("Crime per Month")
        monthly_crimes = analytics_df.groupby("month")["crime_count"].sum().reset_index()

        crime_per_month_fig = px.line(monthly_crimes, x="month", y="crime_count", 
                                      title="Crime Count per Month", labels={"month": "Month", "crime_count": "Total Crimes"})
        # crime_per_month_fig.update_layout(xaxis_tickangle=-45, xaxis_tickformat="%Y-%m")  
        crime_per_month_fig.update_layout(xaxis_tickangle=-45)  

        st.plotly_chart(crime_per_month_fig)

        st.subheader("Top Locations with Crime")
        top_locations = analytics_df.groupby("lsoa_name")["crime_count"].sum().sort_values(ascending=False).head(10)
        st.write(top_locations)

        st.subheader("Filtered Crime Data")
        st.dataframe(analytics_df)
        st.markdown("Data Source: [Police.uk Data](https://data.police.uk/data/)")