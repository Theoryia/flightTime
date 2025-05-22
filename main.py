from flask import Flask, request, jsonify
from geopy.distance import geodesic
import requests
from flask_cors import CORS
import datetime

app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app)

# Function to fetch airport coordinates from the Aviation Weather API
def fetch_airport_coordinates(icao):
    url = f"https://aviationweather.gov/api/data/airport?ids={icao}"
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response as plain text
        data = response.text

        # Debugging: Log the raw API response
        print(f"Raw API response for ICAO {icao}: {data}")

        # Extract latitude and longitude using string processing
        try:
            latitude_line = next(line for line in data.splitlines() if "Latitude:" in line)
            longitude_line = next(line for line in data.splitlines() if "Longitude:" in line)

            latitude = float(latitude_line.split(":")[-1].strip())
            longitude = float(longitude_line.split(":")[-1].strip())

            return (latitude, longitude)
        except Exception as e:
            print(f"Error parsing coordinates for ICAO {icao}: {e}")
            return None
    except Exception as e:
        print(f"Error fetching data for ICAO {icao}: {e}")
        return None

# Function to calculate flight time based on distance and additional factors
def calculate_flight_time(
    distance_km,
    cruise_speed_kmh=900,
    climb_speed_kmh=500,
    descent_speed_kmh=500,
    climb_distance_km=80,
    descent_distance_km=80,
    taxi_out_minutes=15,
    taxi_in_minutes=10,
    sid_minutes=10,
    star_minutes=10
):
    """
    Estimate total flight time including taxi, SID, climb, cruise, descent, and STAR phases.

    Parameters:
    - distance_km: total flight distance in kilometers
    - cruise_speed_kmh: average cruise speed in km/h
    - climb_speed_kmh: average climb speed in km/h
    - descent_speed_kmh: average descent speed in km/h
    - climb_distance_km: typical distance covered during climb in km
    - descent_distance_km: typical distance covered during descent in km
    - taxi_out_minutes: average taxi-out time in minutes
    - taxi_in_minutes: average taxi-in time in minutes
    - sid_minutes: average SID (Standard Instrument Departure) time in minutes
    - star_minutes: average STAR (Standard Terminal Arrival Route) time in minutes

    Returns:
    - tuple (hours, minutes) representing the estimated total flight time
    """
    # Phase durations
    taxi_out = datetime.timedelta(minutes=taxi_out_minutes)
    sid = datetime.timedelta(minutes=sid_minutes)
    taxi_in = datetime.timedelta(minutes=taxi_in_minutes)
    star = datetime.timedelta(minutes=star_minutes)

    # Climb time
    climb_time = datetime.timedelta(hours=climb_distance_km / climb_speed_kmh)
    # Descent time
    descent_time = datetime.timedelta(hours=descent_distance_km / descent_speed_kmh)

    # Calculate remaining cruise distance
    cruise_distance = max(distance_km - climb_distance_km - descent_distance_km, 0)
    cruise_time = datetime.timedelta(hours=cruise_distance / cruise_speed_kmh)

    # Sum all phases
    total_time = taxi_out + sid + climb_time + cruise_time + descent_time + star + taxi_in

    # Convert to hours and minutes
    total_hours = total_time.seconds // 3600 + total_time.days * 24
    total_minutes = (total_time.seconds % 3600) // 60
    return total_hours, total_minutes

@app.route('/flight-time', methods=['GET'])
def flight_time():
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')

    print(f"Received departure: {departure}, arrival: {arrival}")

    if not departure or not arrival:
        return jsonify({"error": "Please provide both departure and arrival ICAO codes."}), 400

    # Get coordinates for departure and arrival airports
    departure_coords = fetch_airport_coordinates(departure)
    arrival_coords = fetch_airport_coordinates(arrival)

    # Debugging: Log the fetched coordinates
    print(f"Departure coordinates: {departure_coords}, Arrival coordinates: {arrival_coords}")

    if not departure_coords or not arrival_coords:
        return jsonify({"error": "Unable to fetch coordinates for one or both ICAO codes."}), 400

    # Calculate distance in kilometers using geopy's geodesic method
    distance_km = geodesic(departure_coords, arrival_coords).kilometers

    # Calculate flight time using the new function
    flight_time_hours, flight_time_minutes = calculate_flight_time(distance_km)

    return jsonify({
        "departure": departure,
        "arrival": arrival,
        "distance_km": round(distance_km, 2),
        "flight_time": (flight_time_hours, flight_time_minutes),
        "departure_coords": departure_coords,
        "arrival_coords": arrival_coords
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
