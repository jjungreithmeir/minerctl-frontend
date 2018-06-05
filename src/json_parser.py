import urllib.request, json

def parse_json():
    with urllib.request.urlopen("http://localhost:3000/info") as url:
        data = json.loads(url.read().decode())
        return data

if __name__ == '__main__':
    print(parse_json())
