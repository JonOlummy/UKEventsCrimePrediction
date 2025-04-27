# UK Events Crime Prediction

This project provides a predictive analysis of crimes related to events across the UK. Using real-time event data and historical crime data, it predicts potential crime types at event locations based on various event attributes. The project consists of several components:


## Components & Dependencies

### 1. **FastAPI Backend**
- FastAPI serves as the backend API framework.
- It provides endpoints for predicting crime types based on event data and for fetching crime analytics based on historical data.

### 2. **MindsDB (Local)** 
- MindsDB is used for training the machine learning model that predicts crime types based on event data. The model is trained using Lightwood ML, a part of MindsDB, which integrates easily with Snowflake data.

### 3. **Snowflake** 
- Snowflake is used as the cloud-based data warehouse to store large datasets of historical crime data and event data (fetched from TicketMaster). It allows easy querying of data for model training and predictions.

### 4. **Airbyte**
- Airbyte fetches event data from TicketMaster and syncs it into Snowflake at hourly intervals.

### 5. **Streamlit Frontend**
- Streamlit is used to provide an interactive frontend where users can:
  - View crime predictions for events based on location and time.
  - Visualize crime statistics by location and date range.
  - Explore crime trends using charts, tables, and maps.

## Data Sources

### 1. **Event Data from TicketMaster**
Event data is fetched in real-time from [TicketMaster UK](https://www.ticketmaster.co.uk/), which provides information about events happening across the UK. This data includes event names, locations, dates, times, and venue information. The data is extracted via the TicketMaster API and synced into Snowflake hourly using [Airbyte](https://www.airbyte.com/).

- **API Documentation**: [TicketMaster Developer Portal](https://developer.ticketmaster.com/products-and-docs/)

### 2. **Crime Data from Police.uk**
Historical crime data for the UK is fetched from [Police.uk Data](https://data.police.uk/data/), a public dataset that contains information about crime incidents reported in the UK. The dataset includes crime types, locations, crime dates, and other relevant details. This data is used to train the predictive model for crime at event locations.

- **API Documentation**: [Police.uk API](https://data.police.uk/docs/)

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Docker** (for running MindsDB locally)
- **Snowflake account** with appropriate credentials for accessing crime data and event data.
- **Airbyte** set up for syncing event data from TicketMaster.

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/uk-events-crime-prediction.git
cd uk-events-crime-prediction
```

### 2. Install dependencies

Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the root directory and add the following variables:

```ini
MINDSDB_API_URL=http://localhost:47334 
SNOWFLAKE_USER=<your-snowflake-username>
SNOWFLAKE_PASSWORD=<your-snowflake-password>
SNOWFLAKE_ACCOUNT=<your-snowflake-account>
SNOWFLAKE_DATABASE=<your-snowflake-database>
SNOWFLAKE_WAREHOUSE=<your-snowflake-warehouse>
```

### 4. Running MindsDB locally (Optional)

If you're running MindsDB locally in Docker, use the following steps to set it up:

```bash
docker run -d -p 47334:47334 mindsdb/mindsdb
```

### 5. Running the FastAPI Backend

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

This will start the API server on `http://127.0.0.1:8000`. You can test the endpoints using tools like Postman or directly by calling the URLs in the browser.

### 6. Running the Streamlit Frontend

Start the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

This will open the dashboard in your browser at `http://localhost:8501`.

## API Endpoints

### 1. **/predict**: Predict Crime Types for Events

**GET** `http://127.0.0.1:8000/predict`

#### Parameters:
- `limit`: The number of events to return (default: 100)
- `name`: Event name (optional)
- `location`: Location (optional)
- `start_date`: Start date of the event (optional)
- `end_date`: End date of the event (optional)

Returns a list of predicted crime types for the event locations.

### 2. **/analytics/crime_by_location**: Get Crime Analytics by Location

**GET** `http://127.0.0.1:8000/analytics/crime_by_location`

#### Parameters:
- `location_search`: Location to search for (e.g., "London")
- `from_date`: Start date for the analysis (optional)
- `to_date`: End date for the analysis (optional)

Returns a list of crime counts by type for the specified location and date range.