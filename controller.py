from flask import render_template, Flask

app = Flask(__name__)

@app.route("/")
def index():
    list_miners = []
    for index, miner in enumerate(range(120)):
        list_miners.append(index)
    return render_template('index.html', miners=list_miners)
