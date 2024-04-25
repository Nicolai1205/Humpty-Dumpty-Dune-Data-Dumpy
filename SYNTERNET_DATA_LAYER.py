#Packages to be imported
import csv
from datetime import datetime
import json
import requests
import os
import pandas as pd

def fetch_latest_kpis(url):
    """Fetch the latest KPIs from the given API endpoint."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # The API returns a JSON object with data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def process_data(data):
    """Process data to extract 'Current' fields for specified metrics and add a 'date' field."""
    if data:
        metrics = {
            'dlpublishers': data['DLPublishers']['Current'],
            'dlsubscribers': data['DLSubscribers']['Current'],
            'dlstreams': data['DLStreams']['Current']
        }
        df = pd.DataFrame([metrics])
        df['date'] = datetime.now().strftime('%Y-%m-%dT00:00:00Z')
        df = df[['date', 'dlpublishers', 'dlsubscribers', 'dlstreams']]
        return df
    else:
        print("No data to process.")
        return pd.DataFrame()

def save_to_csv(df, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"Data saved to CSV at {file_path}")

def upload_data_to_dune(file_path, api_key):
    url = 'https://api.dune.com/api/v1/table/gaard/syntropy_data_layer/insert'
    headers = {
        "X-DUNE-API-KEY": api_key,
        "Content-Type": "text/csv"
    }
    try:
        with open(file_path, "rb") as data:
            response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print("Data uploaded successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to upload data. Status Code: {response.status_code}")
            print("Response:", response.text)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Configuration
api_url = os.getenv('API_URL')
api_key = os.getenv('API_KEY')
csv_directory = os.getenv('CSV_DIRECTORY', './data')  # Defaulting to a data directory relative to the script
csv_filename = 'syntropy_latest.csv'
csv_file_path = os.path.join(csv_directory, csv_filename)


# Workflow execution
raw_data = fetch_latest_kpis(api_url)
processed_data = process_data(raw_data)
if not processed_data.empty:
    save_to_csv(processed_data, csv_file_path)
    upload_data_to_dune(csv_file_path, api_key)
else:
    print("No data available to save or upload.")
