import json
import requests
from src.config_reader import ConfigReader

CFG_RDR = ConfigReader()
CONTAINER_CONN = CFG_RDR.get_attr('backend_address')
SESSION = requests.Session()
ADAPTER = requests.adapters.HTTPAdapter(max_retries=10)
SESSION.mount('http://', ADAPTER)

def get(resource='/cfg'):
    return SESSION.get(CONTAINER_CONN + resource).json()

def put(data, resource='/cfg'):
    copy = data.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    resp = SESSION.put(CONTAINER_CONN + resource, data=copy)
    return resp.raise_for_status()

def patch(data, resource='/miner', exclude=None):
    copy = data.copy().to_dict()
    for item in exclude:
        copy.pop(item, None)
    resp = SESSION.patch(CONTAINER_CONN + resource, data=copy)
    return resp.raise_for_status()

def write_json(data, filename='config/layout.json', needs_conversion=True):
    if needs_conversion:
        layout = data.copy().to_dict()
    else:
        layout = data
    with open(filename, 'w') as file:
        json.dump(layout, file)

def read_json(filename='config/layout.json', catch_exception=True):
    try:
        with open(filename) as file:
            data = json.load(file)
    except FileNotFoundError:
        if catch_exception:
            data = None
        else:
            raise FileNotFoundError
    return data

def patch_str(data, resource='/cfg'):
    json_data = json.load(data)
    resp = SESSION.patch(CONTAINER_CONN + resource, data=json_data)
    return resp.raise_for_status()

def resp_to_dict(resp):
    return resp.copy().to_dict()

if __name__ == '__main__':
    print(get())
