from flask import Flask, redirect, url_for, render_template, request, session, current_app
from werkzeug.utils import secure_filename
from flask import flash
import os
from configparser import ConfigParser
import logging
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

app = Flask(__name__)
app.secret_key = os.urandom(24)

#App config parsed from config.ini. These are the variables need to pinpoint the location the uploaded file will be placed on the server, and the allowed file extensions
file = 'config.ini'
config = ConfigParser()
config.read(file)
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
config.read(os.path.join(path, 'config.ini'))

#Global data
UPLOAD_FOLDER = (config['data']['upload_folder'])
ALLOWED_EXTENSIONS = (config['data']['allowed_extensions'])
Error_Log = (config['data']['error_logfile_name'])

#Global Variables
selected_output = (config['var']['selected_output'])
selected_input = (config['var']['selected_input'])

# Set errorlogging and tracelevel
logging.basicConfig(filename=Error_Log,level=logging.DEBUG)

# The code below is for making it possible for the front-end user to upload a photo
@app.route("/")
def home():
    return render_template("index.html")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# The code below is to format the filename of the file and path that the user has given for the photo to be uploaded
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# The code below is to GET the photo file from the base.html submit form and uploaded to the upload_folder in the config.ini
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #print(file)
        # if user does not select file submit an empty part without filename and call flash
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session["bestandsnaam"] = filename
    return render_template("upload.html", image_name=filename)

#@app.route('/processed_photo/')
@app.route('/processed_photo/', methods=['POST'])
def processed_photo():
    int_answer = int(request.form['int_answer'])
    water_text = (request.form['water_text'])
    selected_photo = session["bestandsnaam"]
    global selected_input
    global selected_output

    #Open a Photofile
    photo = Image.open(selected_input + selected_photo)

    #Store image width and height
    w, h = photo.size
    mid = w / 2
    
    #Make the image editable
    drawing = ImageDraw.Draw(photo)
    font = ImageFont.truetype("HarlowSolidItalicItalic.ttf", int_answer)
   
    #Get text width and height and center text relative to photo size
    text = water_text
    text_w, text_h = drawing.textsize(text, font)
    bottom = h - text_h - 5
    center = text_w / 2
    midden = mid - center
    midden = int(midden)
    drawing.text((midden,bottom), text, fill="#ffffff", font=font)
    photo.save(selected_output + "ShutterBalance" + selected_photo)
    session["bestandsnaam2"] = "ShutterBalance" + selected_photo
    end_photo = session["bestandsnaam2"]
    return render_template("result.html", watermark_name=end_photo)

@app.route('/download_and_remove/')
def download_and_remove():
    verwijderen_org = session["bestandsnaam2"]
    verwijderen_exp = session["bestandsnaam"]
    path2 = os.path.join(selected_output, verwijderen_org) 
    path3 = os.path.join(selected_output, verwijderen_exp) 
    os.remove(path2) 
    os.remove(path3)
    return render_template("end.html")

@app.after_request
def after_request_func(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if (__name__) == "__main__":
     app.run(debug=True)