
import googlemaps
import requests
import os

class Maps:
    def __init__(self):
        self.api_key = os.environ["GOOGLE_API_KEY"]
        self.gmaps = googlemaps.Client(key=self.api_key)

    def get_zip_code_from_lat_lng(self, lat, long):
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{long}&key={self.api_key}'
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            for result in data['results']:
                for component in result['address_components']:
                    if 'postal_code' in component['types']:
                        return component['short_name']
        return None
    
    def get_info_from_address(self, address):
        address = address.replace(" ", "%20")
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}'
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            result = data['results'][0]

            # Extract zip code
            zip_code = None
            for component in result['address_components']:
                if 'postal_code' in component['types']:
                    zip_code = component['short_name']
                    break

            # Extract place type
                place_type = None
                if 'types' in result:
                    place_type = result['types'][0]

            # Extract latitude and longitude
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']

            # Extract formatted address
            formatted_address = result["formatted_address"]

            return {
                "formatted_address": formatted_address,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lng,
                "place_type": place_type
            }

        return {}

    def get_time_to_destination(self, origin, destination):

        '''
        Input:
            origin: Address string or lat long (separated with space)
            destination: Address string or lat long (separated with space)
        Output:
            Dictionary: {
                "text": how long it takes in english
                "value": Int of number of seconds it takes to go from org to dest
            }
        '''
        result = self.gmaps.distance_matrix(origin, destination, mode="driving")
        return result["rows"][0]["elements"][0]["duration"]