from flask import Flask, request, jsonify, render_template
import re
import pandas as pd
from flasgger import Swagger
from database import init_db, insert_record
import sqlite3


app = Flask(__name__)
swagger = Swagger(app)

init_db()


def clean_text(text):
  #remove emoji
  emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002580-\U00002BEF" # chinese characters
    "]+", flags=re.UNICODE)
  text = emoji_pattern.sub(r'', text)

  #remove username (@), hastag (#), dan url (https://)
  text = re.sub(r"(@\w+|#\w+|https?://\S+)", "", text)

  #remove repeated caracter (e.g., yesss > yes)
  text = re.sub(r"([A-za-z])\1{2,}", r"\1", text)

  #remove excess spaces
  text = re.sub(r"\s+", " ", text) #space bettwen
  text = text.lstrip().rstrip()

  #lowercase
  text = text.lower()

  return text

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/csv')
def csv():
    return render_template('upload_csv.html')

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return render_template('upload_csv.html', error='No file selected.')
        if file:
            # Baca file CSV
            try:
                df = pd.read_csv(file)
                # Tampilkan data dalam bentuk tabel HTML
                table_html = df.to_html(index=False, classes='table table-striped')
                return render_template('upload_csv.html', table=table_html)
            except Exception as e:
                return render_template('upload_csv.html', error=str(e))
    return render_template('upload_csv.html')


@app.route('/clean_text', methods=['POST'])
def clean_text_endpoint():
    """
    Clean text
    ---
    parameters:
      - name: text
        in: formData
        type: string
        required: true
        description: Text to be cleaned
    responses:
      200:
        description: Cleaned text
        schema:
          type: object
          properties:
            cleaned_text:
              type: string
    """
    input_text = request.form['text']
    cleaned_text = clean_text(input_text)
    insert_record(input_text, cleaned_text)  # Simpan ke database
    return jsonify({'cleaned_text': cleaned_text})

@app.route('/clean_csv', methods=['POST'])
def clean_csv_endpoint():
    """
    Clean CSV file
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: CSV file with text column
    responses:
      200:
        description: Cleaned text from CSV
        schema:
          type: string
    """
    file = request.files['file']
    df = pd.read_csv(file)
    df['cleaned_text'] = df['content'].apply(clean_text)
    
    for _, row in df.iterrows():
        insert_record(row['content'], row['cleaned_text'])
    return df.to_json()


@app.route('/view_data', methods=['GET'])
def view_data():
    """
    View data from database
    ---
    responses:
      200:
        description: Mengambil data database
        schema:
          type: string
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM records')
    data = c.fetchall()
    conn.close()
    return render_template('view_data.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
