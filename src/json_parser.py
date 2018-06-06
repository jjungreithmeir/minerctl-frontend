import requests

container_conn = 'http://localhost:3000/info'

def parse_json():
    resp = requests.get(container_conn)
    return resp.json()

def post():
    userdata = {"rpm": 3000}
    requests.post(container_conn, data=userdata)

if __name__ == '__main__':
    print(parse_json())
