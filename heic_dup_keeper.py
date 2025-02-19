#!/usr/bin/python3
import requests
import json
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': API_KEY
}

def do_get(url):
    response = requests.get(f'{BASE_URL}/{url}', headers=HEADERS)
    return response.json()

def delete_assets(asset_list):
    ids = list(map(lambda item: item['id'], asset_list))

    payload = json.dumps({
        "force": False,
        "ids": ids
    })

    requests.request("DELETE", f'{BASE_URL}/assets', headers=HEADERS, data=payload)

    print(f'Removed {len(ids)} assets')

def list_dups():

    print('Retrieving duplicates list...')

    response = do_get('duplicates')

    remove_assets_list = []

    for dupItem in response:
        heic_file = False
        temp_asset = []
        for asset in dupItem['assets']:
            if 'image/heic' != asset['originalMimeType']:
                temp_asset.append(asset)
            else:
                heic_file = True
        if heic_file and temp_asset: remove_assets_list.extend(temp_asset)

    if remove_assets_list:
        print('Review the following list and confirm to remove:\n')
        for item in remove_assets_list:
            print(item['originalFileName'])
        user_input = input('\nProceed? (y/n)')
        if user_input.lower() in ('y','yes'):
            delete_assets(remove_assets_list)
        else:
            print('Cancelled.')
    else:
        print('No duplicates found.')

def main():
    list_dups()

if __name__ == "__main__":
    main()
