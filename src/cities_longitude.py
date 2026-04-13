"""
cities_longitude.py

This module provides functions to calculate the longitude of cities based on input data.
It includes support for leap years, detailed return values, error handling, and thorough documentation.
"""

def is_leap_year(year):
    """
    Check if a given year is a leap year.

    Parameters:
    year (int): The year to check.

    Returns:
    bool: True if the year is a leap year, False otherwise.
    """
    try:
        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    return True
                return False
            return True
        return False
    except Exception as e:
        return {"error": str(e)}

def calculate_longitude(city_name):
    """
    Calculate the longitude of a given city.

    Parameters:
    city_name (str): The name of the city.

    Returns:
    dict: A dictionary containing the city name and its longitude if found,
          or an error message if the city is not found or an error occurs.
    """
    city_longitudes = {
        "New York": -74.006,
        "Los Angeles": -118.2437,
        "Tokyo": 139.6917,
        # Add more cities as needed
    }

    try:
        longitude = city_longitudes.get(city_name)
        if longitude is None:
            raise ValueError("City not found")
        return {
            "city": city_name,
            "longitude": longitude,
            "message": "Longitude retrieved successfully",
        }
    except ValueError as ve:
        return {
            "error": str(ve),
            "message": "There was an issue retrieving the longitude.",
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "An unexpected error occurred.",
        }

# Example usage (for testing purposes)
if __name__ == '__main__':
    year = 2024  # Example year for leap year check
    print(f"Is {year} a leap year? {is_leap_year(year)}")
    city = "New York"
    print(calculate_longitude(city))
