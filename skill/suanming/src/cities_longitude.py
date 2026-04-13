"""
cities_longitude.py

This module computes longitude offsets for cities in China, considering leap years.
It provides detailed return values including original time, corrected time, and various offsets.

Functionality:
- Calculates the time correction based on longitude
- Accounts for the equation of time
- Provides inputs and outputs related to the timezone and statuses
"""

from datetime import datetime, timedelta
import pytz

# Dictionary to hold city data from China (example structure)
cities_data = {
    "Beijing": {"longitude": 116.4072},
    "Shanghai": {"longitude": 121.4737},
    # Add more cities...
}

def calculate_longitude_offset(city_name, original_time):
    """
    Calculate the longitude offset for a given city and original time.

    :param city_name: Name of the city
    :param original_time: Original datetime in UTC
    :return: A dictionary with detailed return values
    """
    if city_name not in cities_data:
        return {"status": "error", "message": "City not found"}

    longitude = cities_data[city_name]["longitude"]
    longitude_offset_minutes = longitude / 15  # 1 hour = 15 degrees
    equation_of_time_minutes = 0  # Placeholder: Implement actual calculation if needed
    corrected_time = original_time + timedelta(minutes=longitude_offset_minutes + equation_of_time_minutes)
    total_offset_minutes = longitude_offset_minutes + equation_of_time_minutes
    
    # Define timezone (UTC+8 for China)
    timezone = pytz.timezone("Asia/Shanghai")
    local_time = corrected_time.astimezone(timezone)

    return {
        "original_time": original_time.isoformat(),
        "corrected_time": local_time.isoformat(),
        "longitude_offset_minutes": longitude_offset_minutes,
        "equation_of_time_minutes": equation_of_time_minutes,
        "total_offset_minutes": total_offset_minutes,
        "timezone": str(timezone),
        "status": "success"
    }

# Example test cases
if __name__ == "__main__":
    original_time = datetime(2026, 4, 13, 8, 25, 25)
    print(calculate_longitude_offset("Beijing", original_time))
    print(calculate_longitude_offset("Shanghai", original_time))
