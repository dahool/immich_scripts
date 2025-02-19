#!/usr/bin/python3
import requests
import json
import psycopg2
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = 'immich'
DB_USER = 'postgres'
DB_PASSWORD = os.getenv('DB_PASSWORD')

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': API_KEY
}

def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def do_get(url):
    response = requests.get(f'{BASE_URL}/{url}', headers=HEADERS)
    return response.json()

def do_post(url, payload):
    response = requests.post(f'{BASE_URL}/{url}', headers=HEADERS, data=json.dumps(payload))
    return response.json()

def delete_assets(asset_list):
    ids = list(map(lambda item: item[0], asset_list))

    payload = json.dumps({
        "force": True,
        "ids": ids
    })

    requests.request("DELETE", f'{BASE_URL}/assets', headers=HEADERS, data=payload)

    print(f'Removed {len(ids)} assets')

def list_assets():

    print('Retrieving assets list...')

    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute('SELECT id FROM assets')
        assets = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    print('Found %d assets' % len(assets))

    delete_assets(assets)

def main():
    list_assets()

if __name__ == "__main__":
    main()
