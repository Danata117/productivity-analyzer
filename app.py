import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import json
from flask import Flask, request, jsonify
import joblib
import pandas as pd
from tensorflow.keras.models import model_from_json

app = Flask(__name__)

with open('my_model_arch.json', 'r') as f:
    model_config = json.load(f)

def remove_quantization_config(config):
    if isinstance(config, dict):
        if 'quantization_config' in config:
            del config['quantization_config']
        for key in config:
            remove_quantization_config(config[key])
    elif isinstance(config, list):
        for item in config:
            remove_quantization_config(item)

remove_quantization_config(model_config)

model = model_from_json(json.dumps(model_config))

model.load_weights('my_model_weights.weights.h5')

preprocessor = joblib.load('preprocessor.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        df = pd.DataFrame([data])
        processed_data = preprocessor.transform(df)
        prediction = model.predict(processed_data)
        return jsonify({'focus_score': float(prediction[0][0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)