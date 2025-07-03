import os
import pandas as pd
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Column mapping configuration
COLUMN_MAPPING = {
    'ean': ['ean', 'barcode', 'product code', 'upc', 'code'],
    'title': ['title', 'product', 'product name', 'name', 'description'],
    'cost_gbp': ['cost', 'cost (gbp)', 'price', 'unit cost', 'cost_gbp', 'cost gbp', 'cost£'],
    'family': ['family', 'category', 'main category', 'product family'],
    'subgroup': ['subgroup', 'sub category', 'sub family', 'product subgroup']
}

def normalize_column_name(col_name):
    """Normalize column names for matching."""
    return str(col_name).strip().lower().replace(' ', '').replace('_', '').replace('-', '').replace('(', '').replace(')', '')

def find_matching_column(df_columns, possible_names):
    """Find the first matching column in the DataFrame."""
    for col in df_columns:
        normalized = normalize_column_name(col)
        for name in possible_names:
            if name in normalized:
                return col
    return None

def process_excel(file_path):
    """Process Excel file and return standardized DataFrame."""
    try:
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
    except:
        try:
            df = pd.read_excel(file_path, engine='xlrd')
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    # Map columns
    column_map = {}
    for target, possible_names in COLUMN_MAPPING.items():
        matched_col = find_matching_column(df.columns, [normalize_column_name(n) for n in possible_names])
        column_map[target] = matched_col
    
    # Create new DataFrame with standardized columns
    processed_data = {}
    for target in COLUMN_MAPPING.keys():
        source_col = column_map[target]
        processed_data[target] = df[source_col] if source_col else [None] * len(df)
    
    return pd.DataFrame(processed_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        # Save uploaded file
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)
        
        try:
            # Process file
            output_df = process_excel(input_path)
            
            # Save processed CSV
            output_filename = "processed_" + os.path.splitext(file.filename)[0] + ".csv"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            output_df.to_csv(output_path, index=False)
            
            return send_file(
                output_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=output_filename
            )
        except Exception as e:
            return f"Processing error: {str(e)}", 500
        finally:
            # Cleanup files
            if os.path.exists(input_path):
                os.remove(input_path)
    
    return "Error processing file", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)