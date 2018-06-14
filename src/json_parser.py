import requests
import json

container_conn = 'http://localhost:12345'
sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=10)
sess.mount('http://', adapter)

def parse_json(resource='/cfg'):
    return sess.get(container_conn + resource).json()

def put_dict(list, resource='/cfg'):
    """
    Returns True if the POST action has been executed successfully.
    """
    copy = list.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    r = sess.put(container_conn + resource, data=copy)
    return r.raise_for_status()

def put_str(data, resource='/cfg'):
    json_data = json.load(data)

    r = sess.put(container_conn + resource, data=json_data)

def resp_to_dict(resp):
    return resp.copy().to_dict()

if __name__ == '__main__':
    print(parse_json())
