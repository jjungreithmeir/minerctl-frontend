import requests
import json
from src.config_reader import ConfigReader

cfg_rdr = ConfigReader()
container_conn = cfg_rdr.get_attr('backend_address')
sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=10)
sess.mount('http://', adapter)

def get(resource='/cfg'):
    return sess.get(container_conn + resource).json()

def put(list, resource='/cfg'):
    copy = list.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    r = sess.put(container_conn + resource, data=copy)
    return r.raise_for_status()

def patch(data, resource='/miner', exclude=[]):
    copy = data.copy().to_dict()
    for item in exclude:
        copy.pop(item, None)
    r = sess.patch(container_conn + resource, data=copy)
    return r.raise_for_status()

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
    r = sess.patch(container_conn + resource, data=json_data)

def resp_to_dict(resp):
    return resp.copy().to_dict()

if __name__ == '__main__':
    print(get())
