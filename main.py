from flask import Flask, request, jsonify
from geopy.distance import geodesic
import requests
from flask_cors import CORS

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
def calculate_flight_time(distance_km):
    # Assume an average flight speed of 900 km/h for long-haul flights
    average_speed_kmh = 900 if distance_km > 1500 else 800

    # Calculate flight time in hours and minutes with refined speed
    flight_time_hours = int(distance_km // average_speed_kmh)
    flight_time_minutes = int((distance_km % average_speed_kmh) / average_speed_kmh * 60)

    # Add 30 minutes for taxiing and departure
    total_minutes = flight_time_hours * 60 + flight_time_minutes + 30

    # Add extra time for departure, arrival, and non-direct routes
    extra_time_minutes = 45 + int(distance_km * 0.008)  # 1% of distance as extra time
    total_minutes += extra_time_minutes

    flight_time_hours = total_minutes // 60
    flight_time_minutes = total_minutes % 60

    return flight_time_hours, flight_time_minutes

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
