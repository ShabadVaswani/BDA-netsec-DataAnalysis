import pandas as pd
import requests
from datetime import datetime, timedelta

# File paths
ROUTERSENSE_FILE = 'data/processed/netsecfulldata/routersense_minute_processed.csv'
GARMIN_FILE = 'data/processed/garminfulldata/health data- without  network data - garmin_minute_health_activity.csv.csv'
OUTPUT_FILE = 'output/weather_data_hourly.csv'

# Location (you may need to adjust these coordinates)
# Default: New York City area
LATITUDE = 40.7128
LONGITUDE = -74.0060

def get_date_range():
    """Get the earliest start and latest end from both datasets"""
    print("📅 Determining date range from datasets...")
    
    # Read RouterSense data
    print(f"  Reading {ROUTERSENSE_FILE}...")
    rs_df = pd.read_csv(ROUTERSENSE_FILE)
    rs_df['datetime'] = pd.to_datetime(rs_df['datetime'])
    rs_start = rs_df['datetime'].min()
    rs_end = rs_df['datetime'].max()
    print(f"    RouterSense: {rs_start} to {rs_end}")
    
    # Read Garmin data
    print(f"  Reading {GARMIN_FILE}...")
    garmin_df = pd.read_csv(GARMIN_FILE)
    garmin_df['datetime'] = pd.to_datetime(garmin_df['datetime'])
    garmin_start = garmin_df['datetime'].min()
    garmin_end = garmin_df['datetime'].max()
    print(f"    Garmin: {garmin_start} to {garmin_end}")
    
    # Get earliest and latest
    start_date = min(rs_start, garmin_start)
    end_date = max(rs_end, garmin_end)
    
    print(f"\n  Combined range: {start_date} to {end_date}")
    
    return start_date, end_date

def download_weather_data(start_date, end_date):
    """Download hourly weather data from Open-Meteo API"""
    print(f"\n🌤️  Downloading weather data from Open-Meteo...")
    
    # Format dates for API (YYYY-MM-DD)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Open-Meteo API endpoint
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'start_date': start_str,
        'end_date': end_str,
        'hourly': [
            'temperature_2m',
            'relative_humidity_2m',
            'precipitation',
            'rain',
            'snowfall',
            'cloud_cover',
            'wind_speed_10m',
            'wind_direction_10m',
            'surface_pressure'
        ],
        'timezone': 'America/New_York'
    }
    
    print(f"  Location: ({LATITUDE}, {LONGITUDE})")
    print(f"  Date range: {start_str} to {end_str}")
    print(f"  Requesting data...")
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract hourly data
        hourly = data['hourly']
        
        # Create DataFrame
        df = pd.DataFrame({
            'datetime': pd.to_datetime(hourly['time']),
            'temperature_celsius': hourly['temperature_2m'],
            'humidity_percent': hourly['relative_humidity_2m'],
            'precipitation_mm': hourly['precipitation'],
            'rain_mm': hourly['rain'],
            'snowfall_cm': hourly['snowfall'],
            'cloud_cover_percent': hourly['cloud_cover'],
            'wind_speed_kmh': hourly['wind_speed_10m'],
            'wind_direction_degrees': hourly['wind_direction_10m'],
            'surface_pressure_hpa': hourly['surface_pressure']
        })
        
        # Add time components
        df['date'] = df['datetime'].dt.date
        df['time'] = df['datetime'].dt.time
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        
        # Reorder columns
        df = df[[
            'datetime', 'date', 'time', 'hour', 'day_of_week',
            'temperature_celsius', 'humidity_percent', 'precipitation_mm',
            'rain_mm', 'snowfall_cm', 'cloud_cover_percent',
            'wind_speed_kmh', 'wind_direction_degrees', 'surface_pressure_hpa'
        ]]
        
        # Save
        df.to_csv(OUTPUT_FILE, index=False)
        
        print(f"\n✅ Weather data downloaded successfully!")
        print(f"  Saved to: {OUTPUT_FILE}")
        print(f"  Total hours: {len(df):,}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Show sample
        print(f"\n📊 Sample data:")
        print(df.head(10).to_string(index=False))
        
        return df
    else:
        print(f"\n❌ Error downloading data: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

if __name__ == "__main__":
    start_date, end_date = get_date_range()
    download_weather_data(start_date, end_date)
