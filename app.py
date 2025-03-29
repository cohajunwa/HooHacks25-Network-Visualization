from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files: # check if the post request has the file
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '': # User does not select a file
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))

    return render_template('index.html')


@app.route('/display', methods = ['GET', 'POST'])
def display_file():
    
    return render_template('visuals.html', content=content) 

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True)