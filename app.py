from flask import Flask, request, jsonify
import json

app = Flask(__name__)

def normalize_value(value):
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value.lower().strip()
    elif isinstance(value, list):
        return [normalize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    elif value is None:
        return ""
    else:
        return str(value)

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict({str(i): item}, new_key, sep=sep).items())
        else:
            items.append((new_key, normalize_value(v)))
    return dict(items)

def compare_data(original, mapped):
    original_flat = flatten_dict(original)
    mapped_flat = flatten_dict(mapped)
    
    original_values = set(original_flat.values())
    mapped_values = set(mapped_flat.values())
    
    unmapped_values = original_values - mapped_values
    
    missing_fields = set()
    missing_fields_with_location = {}
    for key, value in original_flat.items():
        if value in unmapped_values:
            missing_fields.add(key.split('.')[-1])
            missing_fields_with_location[key] = value
    
    return list(missing_fields), missing_fields_with_location

@app.route('/api/compare', methods=['POST'])
def compare_json():
    data = request.json
    original_json = data.get('original')
    mapped_json = data.get('mapped')
    
    if not original_json or not mapped_json:
        return jsonify({"error": "Both 'original' and 'mapped' JSON objects are required"}), 400
    
    missing_fields, missing_fields_with_location = compare_data(original_json, mapped_json)
    
    return jsonify({
        "missing_fields": missing_fields,
        "missing_fields_with_location": missing_fields_with_location
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020)