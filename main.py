from flask import Flask, render_template_string, request, send_file
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import os
import zipfile

app = Flask(__name__)

def fetch_prtg_data(prtg_url, username, password):
    response = requests.get(f"{prtg_url}/api/table.json",
                            params={"content": "channels", "output": "json", "username": username, "password": password})
    response.raise_for_status()
    return response.json()

def analyze_data(data):
    df = pd.DataFrame(data['channels'])
    return df.describe()

def save_text_results(df, filename):
    df.to_excel(filename, index=False)

def save_csv(df, filename):
    df.to_csv(filename, index=False)

def save_graph(df, filename):
    plt.figure(figsize=(10, 6))
    df.plot(title='PRTG Monitoring Data', kind='bar')
    plt.xlabel('Sensors')
    plt.ylabel('Values')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def create_zip(files, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files:
            zipf.write(file)
    return zip_filename

# Integrated HTML and CSS
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PRTG Data Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
        h1 { color: #333; }
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }
        input[type="text"], input[type="submit"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { background-color: #5cb85c; color: white; border: none; cursor: pointer; }
        input[type="submit"]:hover { background-color: #4cae4c; }
    </style>
</head>
<body>
    <h1>PRTG Data Analyzer</h1>
    <form method="POST">
        <label for="url">PRTG URL:</label>
        <input type="text" name="url" required>
        <label for="username">Username:</label>
        <input type="text" name="username" required>
        <label for="password">Password:</label>
        <input type="text" name="password" required>
        <input type="submit" value="Analyze Data">
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prtg_url = request.form['url']
        username = request.form['username']
        password = request.form['password']

        try:
            data = fetch_prtg_data(prtg_url, username, password)
            analysis_results = analyze_data(data)

            text_file = 'prtg_analysis.xlsx'
            csv_file = 'prtg_analysis.csv'
            graph_file = 'graph.png'
            zip_file = 'prtg_analysis.zip'

            save_text_results(analysis_results, text_file)
            save_csv(analysis_results, csv_file)
            save_graph(pd.DataFrame(data['channels']), graph_file)

            # Create a zip file containing all results
            create_zip([text_file, csv_file, graph_file], zip_file)

            return send_file(zip_file, as_attachment=True)

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template_string(html_content)

if __name__ == "__main__":
    print("Access the web interface at: http://127.0.0.1:5000")
    app.run(debug=True)


#Project by Dillah Captain (Abdallah Mohammed/2025)