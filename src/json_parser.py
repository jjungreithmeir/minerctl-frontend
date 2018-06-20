# TODO refactor this hot spaghetti code mess
import requests
import json
from src.config_reader import ConfigReader

cfg_rdr = ConfigReader()
container_conn = cfg_rdr.get_attr('backend_address')
sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=10)
sess.mount('http://', adapter)

def parse_json(resource='/cfg'):
    return sess.get(container_conn + resource).json()

def put_dict(list, resource='/cfg'):
    copy = list.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    r = sess.put(container_conn + resource, data=copy)
    # TODO Error handling
    return r.raise_for_status()

def patch(params, resource='/miner'):
    copy = params.copy().to_dict()
    r = sess.patch(container_conn + resource, data=copy)
    # TODO Error handling

    return r.raise_for_status()

def save_json(data, filename='config/layout.json'):
    layout = data.copy().to_dict()
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

def put_str(data, resource='/cfg'):
    json_data = json.load(data)

    r = sess.put(container_conn + resource, data=json_data)

def resp_to_dict(resp):
    return resp.copy().to_dict()

if __name__ == '__main__':
    print(parse_json())
