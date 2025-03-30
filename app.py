from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/"

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        relational_file = request.files.get('relational')
        attribute_file = request.files.get('attribute')
        
        if not relational_file and not attribute_file:
            error = "No file selected. Please upload a .csv file"
            return render_template('index.html', error = error)
        
        for file in [relational_file, attribute_file]:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            elif file:
                error = "Invalid file format! Please upload a .csv file"
                return render_template('index.html', error = error)
        return redirect(url_for('visualize'))
    return render_template('index.html' )


@app.route('/visualize', methods = ['GET', 'POST'])
def visualize():
    network_density = 0.5
    attributes = ['a', 'b', 'c']
    ei_indices = [0.2, 0.3, 0.7]

    degree_centrality = 0.3
    closeness_centrality = 0.4
    betweenness_centrality = 0.2

    return render_template('visuals.html', network_density = network_density, ei_indices = zip(attributes, ei_indices),
                            degree_centrality = degree_centrality, closeness_centrality = closeness_centrality,
                            betweenness_centrality = betweenness_centrality) 

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)