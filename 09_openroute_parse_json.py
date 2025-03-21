import requests
import json

directions_api = "https://api.openrouteservice.org/v2/directions/driving-car"
geocode_api = "https://api.openrouteservice.org/geocode/search?"
key = "5b3ce3597851110001cf62489f42b88d3ea14758a210790d600d9404"

def geocode_address(address):
    url = f"{geocode_api}api_key={key}&text={address}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if json_data["features"]:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            print(f"Geocoded coordinates for '{address}': {coords}")  # Debugging
            if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180:
                return coords
            else:
                print(f"Error: Invalid coordinates for address '{address}'")
                return None
        else:
            print(f"Error: No results found for address '{address}'")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
while True:
    orig = input("Starting Location: ")
    if orig == "quit" or orig == "q":
        break
    dest = input("Destination: ")
    if dest == "quit" or dest == "q":
        break

    # Geocode the addresses
    orig_coords = geocode_address(orig)
    dest_coords = geocode_address(dest)

    if not orig_coords or not dest_coords:
        print("Unable to geocode one or both addresses. Please try again.\n")
        continue

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
    print(json_data)  # Debugging

    if response.status_code == 200:
        if 'routes' in json_data and json_data['routes']:
            route = json_data['routes'][0]
            if 'segments' in route and route['segments']:
                segment = route['segments'][0]
                print("\nAPI Status: Successful route call.\n")
                print("=============================================")
                print(f"Directions from {orig} to {dest}")

                # Extract trip duration and distance
                duration = segment.get('duration', 'N/A')
                distance = segment.get('distance', 'N/A')

                print(f"Trip Duration: {duration} seconds")
                print(f"Distance: {distance} meters")
                print("=============================================")

                # Extract and print step-by-step directions
                if 'steps' in segment:
                    for step in segment['steps']:
                        instruction = step.get('instruction', 'N/A')
                        step_distance = step.get('distance', 'N/A')
                        print(f"{instruction} ({step_distance} meters)")
                else:
                    print("No step-by-step directions available.")

                print("=============================================\n")
            else:
                print("Error: No segments found in the route.")
        else:
            print("Error: No routes found in the response.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
