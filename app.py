from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd

app = Flask(__name__)

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = "579b464db66ec23bdd000001eca496d3a4724af148b12338926e92c3"

def fetch_all_states():
    params = {'api-key': API_KEY, 'format': 'json', 'limit': 12000}
    response = requests.get(API_URL, params=params)

    states = []
    if response.status_code == 200:
        records = response.json().get('records', [])
        states = sorted(set(record.get('state', '') for record in records if record.get('state')))
    return states

@app.route('/')
def index():
    states = fetch_all_states()
    return render_template('api.html', states=states, districts=[], data=[])

@app.route('/get_districts', methods=['POST'])
def get_districts():
    state = request.json.get('state')

    params = {'api-key': API_KEY, 'format': 'json', 'limit': 12000, 'filters[state.keyword]': state}
    response = requests.get(API_URL, params=params)

    districts = []
    if response.status_code == 200:
        records = response.json().get('records', [])
        districts = sorted(set(record.get('district', '') for record in records if record.get('district')))

    return jsonify(districts)

@app.route('/get_data', methods=['POST'])
def get_data():
    state = request.form.get('state')
    district = request.form.get('district')

    params = {
        'api-key': API_KEY,
        'format': 'json',
        'limit': 12000,
        'filters[state.keyword]': state,
        'filters[district]': district
    }
    response = requests.get(API_URL, params=params)

    data = []
    if response.status_code == 200:
        data = response.json().get('records', [])
        df = pd.DataFrame(data)
        df.to_excel("filtered_data.xlsx", index=False)

    states = fetch_all_states()
    return render_template('api.html', states=states, selected_state=state, data=data)

if __name__ == '__main__':
    app.run(debug=True)
