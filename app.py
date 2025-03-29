from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/"


@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        
        if not file:
            error = "No file selected. Please upload a .csv file"
            return render_template('index.html', error = error)
        
        filename = secure_filename(file.filename)
        if not file.filename.endswith('.csv'):
            error = "Invalid file format! Please upload a .csv file"
            return render_template('index.html', error = error)

        return redirect(url_for('visualize', name = filename))
    return render_template('index.html')


@app.route('/visualize', methods = ['GET', 'POST'])
def visualize():
    return render_template('visuals.html') 

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)