#!/usr/bin/python3
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
BASE_PATH = os.getenv('BASE_PATH')

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': API_KEY
}


album_cache = {}

def do_post(url, payload):
    response = requests.post(f'{BASE_URL}/{url}', headers=HEADERS, data=json.dumps(payload))
    return response.json()

def do_get(url):
    response = requests.get(f'{BASE_URL}/{url}', headers=HEADERS)
    return response.json()

def load_albums():
    response = do_get('albums')

    for item in response:
        album_cache[item['albumName']] = item['id']

    print(album_cache)

def create_album(name):

    payload = {
        "albumName": name
    }

    print(f'Create album {name}')

    response = do_post('albums', payload)

    return response['id']

def get_or_create_album(name):

    if (name not in album_cache):
        # create
        new_id = create_album(name)
        album_cache[name] = new_id

    return album_cache.get(name)

def update_file(filename, albums):
    payload = {
        'originalFileName': filename
    }
    response = do_post('search/metadata', payload)

    if response['assets']['count'] == 0:
        return False

    for item in response['assets']['items']:
        add_payload = {
            "ids": [
                item['id']
            ]
        }
        for album in albums:
            album_id = get_or_create_album(album)
            print(f"Add {item['originalFileName']} to album {album}")
            requests.put(f'{BASE_URL}/albums/{album_id}/assets', headers=HEADERS, data=json.dumps(add_payload))

def get_album_tags(base_path, current_path):
    rel_path = os.path.relpath(current_path, base_path)
    return rel_path.split(os.sep)

def recurse_files(base_path):
    for root, paths, files in os.walk(base_path):
        if root == base_path: continue # don't add root path to albums
        albums = get_album_tags(base_path, root)
        with open(os.path.join(base_path, 'notfound.log'), 'a') as f:
            for file in files:
                if update_file(file, albums) == False:
                    try:
                        f.write(os.path.join(root, file) + '\n')
                    except:
                        print(f'error writing {file} to log')

def main():
    recurse_files(BASE_PATH)

if __name__ == "__main__":
    main()
