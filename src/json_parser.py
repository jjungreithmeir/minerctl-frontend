import requests
import json
from src.db_init import update_config

container_conn = 'http://localhost:3000/info'

def parse_json():
    resp = requests.get(container_conn)
    return resp.json()

def post_json(list):
    """
    Returns True if the POST action has been executed successfully.
    """
    copy = list.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    # removing values that need to be sent to the db directly
    # unfortunately there is no pop function for dicts
    db_data = {}
    db_data['number_of_miners'] = copy['number_of_miners']
    update_config(db_data)
    del copy['number_of_miners']

    r = requests.post(container_conn, data=copy)
    return r.raise_for_status()

if __name__ == '__main__':
    print(parse_json())
