import requests

api_key = "AIzaSyCBTu5XWGTdPJ3C3gWffHjCV8Ea47yjvtw"
search_engine_id = "a6a1ae0d15e804e92"

import requests
import json

def google_search(search_term, api_key, cse_id, **kwargs):
    service_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_term,
        'key': api_key,
        'cx': cse_id,
        **kwargs
    }
    response = requests.get(service_url, params=params)
    return response.json()

result = google_search(
    'bosch drill machine', 
    api_key, 
    search_engine_id
)

# Print the URL of the first image result
if 'items' in result:
    print(result['items'][0]['link'])
else:
    print("No results found")
