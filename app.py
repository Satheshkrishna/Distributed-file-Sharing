from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
import random
import string
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
PIN_LENGTH = 6  # Length of PIN

file_data = {}

def generate_pin():
    return ''.join(random.choices(string.digits, k=PIN_LENGTH))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        pin = generate_pin()
        file_data[filename] = {'path': file_path, 'pin': pin}

        download_url = url_for('download_file', filename=filename, _external=True)
        return render_template('upload_success.html', download_url=download_url, pin=pin)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    if filename not in file_data:
        flash('File not found')
        return redirect(url_for('index'))

    if request.method == 'POST':
        entered_pin = request.form.get('pin')
        stored_pin = file_data[filename]['pin']

        if entered_pin == stored_pin:
            return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
        else:
            flash('Invalid PIN')
            return redirect(request.url)
    return render_template('enter_pin.html')

@app.route('/receive_file', methods=['POST'])
def receive_file():
    entered_pin = request.form.get('pin')
    for filename, data in file_data.items():
        if data['pin'] == entered_pin:
            return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    flash('Invalid PIN or file not found')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
