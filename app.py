from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_buses')
def get_buses():
    with open('base.json') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=8000)
    app.run(debug=True)
