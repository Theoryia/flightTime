# Flight Time API

This is a small Python-based API application that calculates the flight time between two airports based on their ICAO codes.

## Features

- Accepts ICAO codes for departure and arrival airports.
- Calculates the distance between the airports using geopy.
- Estimates flight time assuming an average speed of 800 km/h.

## Requirements

- Python 3.8+
- Flask
- geopy
- requests
- Flask-Cors

## Setup

## Docker

```bash
docker build -t flighttime .
docker run -d -p 5000:5000 flighttime
```

## Standalone

1. Install the required packages:

```bash
pip install -r requirements.txt

```

2. Run the application:

```bash
python main.py

```

## Usage

Send a GET request to `/flight-time` with `departure` and `arrival` query parameters. For example:

```sh
http://127.0.0.1:5000/flight-time?departure=JFK&arrival=LAX

```

## Example Response

```json
{
	"arrival": "KLAX",
	"arrival_coords": [
		33.9425,
		-118.408
	],
	"departure": "KJFK",
	"departure_coords": [
		40.6399,
		-73.7787
	],
	"distance_km": 3982.96,
	"flight_time": [
		6,
		11
	]
}

```
