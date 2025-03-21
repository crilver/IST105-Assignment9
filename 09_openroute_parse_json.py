import requests
import json
import sys

directions_api = "https://api.openrouteservice.org/v2/directions/driving-car"
geocode_api = "https://api.openrouteservice.org/geocode/search?"
key = "5b3ce3597851110001cf62489f42b88d3ea14758a210790d600d9404"

orig = sys.argv[1]
dest = sys.argv[2]

paragraph = "<p>{text}</p>"
title = "<h1>{text}</h1>"
error = "<h2>{text}</h2>"
line = "<hr>"

def geocode_address(address):
    url = f"{geocode_api}api_key={key}&text={address}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if json_data["features"]:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            print(paragraph.format(text=f"Geocoded coordinates for '{address}': {coords}"))
            if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180:
                return coords
            else:
                print(error.format(text=f"Error: Invalid coordinates for address '{address}'"))
                return None
        else:
            print(error.format(text=f"Error: No results found for address '{address}'"))
            return None
    else:
        print(error.format(text=f"Error: {response.status_code} - {response.text}"))
        return None

def parse_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds  % 60 
    return [hours, minutes, secs]

if orig == dest:
    print(error.format(text="Error: Origin and destination addresses are the same."))
    sys.exit(1)
    
# Geocode the addresses
orig_coords = geocode_address(orig)
dest_coords = geocode_address(dest)

if not orig_coords or not dest_coords:
    print(error.format(text="Error: Unable to geocode one or both addresses. Please try again.\n"))
    sys.exit(1)

# Construct the JSON body for the POST request
body = {
    "coordinates": [orig_coords, dest_coords]
}

# Make the POST request
headers = {
    "Authorization": key, 
    "Content-Type": "application/json"
}
response = requests.post(directions_api, headers=headers, json=body)
json_data = response.json()

if response.status_code == 200:
    print(title.format(text="OpenRouteService Directions"))
    print(paragraph.format(text="Origin: " + orig))
    print(paragraph.format(text="Destination: " + dest))
    print(line)
    if 'routes' in json_data and json_data['routes']:
        route = json_data['routes'][0]
        if 'segments' in route and route['segments']:
            segment = route['segments'][0]
            print(paragraph.format(text="\nAPI Status: Successful route call.\n"))
            print(paragraph.format(text="============================================="))
            print(paragraph.format(text=f"Directions from {orig} to {dest}"))

            # Extract trip duration and distance
            duration = segment.get('duration', 'N/A')
            distance = segment.get('distance', 'N/A')

            [hours, mins, secs] = parse_seconds(duration)
            print(paragraph.format(text=f"Trip Duration: {hours:.0f} hours {mins:.0f} minutes {secs:.0f} seconds"))
            print(paragraph.format(text=f"Distance: {distance/1000:.2f} kilometers"))
            print(paragraph.format(text="============================================="))

            # Extract and print step-by-step directions
            if 'steps' in segment:
                for step in segment['steps']:
                    instruction = step.get('instruction', 'N/A')
                    step_distance = step.get('distance', 'N/A')
                    print(paragraph.format(text=f"{instruction} ({step_distance} meters)"))
            else:
                print(error.format(text="Error: No step-by-step directions available."))

            print(paragraph.format(text="=============================================\n"))
        else:
            print(error.format(text="Error: No segments found in the route."))
    else:
        print(error.format(text="Error: No routes found in the response."))
else:
    print(error.format(text=f"Error: {response.status_code} - {response.text}"))