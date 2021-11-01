from flask import Flask

app = Flask(__name__)

f = open('index.html', 'r')
app_layout = f.read()
f.close()

@app.route('/')
def index():
    return app_layout  