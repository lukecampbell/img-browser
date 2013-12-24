from flask import Flask, render_template, send_from_directory, make_response, send_file
from glob import glob
from PIL import Image
from config import *
from StringIO import StringIO
from cropped_thumbnail import cropped_thumbnail
import fnmatch
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html', title="Index Title")

def get_images():
    matches = []
    for root, dirnames, filenames in os.walk(BASEDIR):
        for filename in fnmatch.filter(filenames, "*.jpg"):
            matches.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, "*.gif"):
            matches.append(os.path.join(root, filename))
    baselen = len(BASEDIR + '/')
    jpg_list  = [ s[baselen:] for s in matches ]
    return jpg_list

@app.route("/browse")
def browse():
    jpg_list = get_images()
    rows = []
    inner_row = []
    i = 0
    for jpgitem in jpg_list:
        if(i % 4) == 0 and i > 0:
            rows.append(inner_row)
            inner_row = []
        inner_row.append(jpgitem)
        i+=1
    if inner_row:
        rows.append(inner_row)
    print rows
    return render_template('browse.html', title='Browse', jpg_rows=rows)

@app.route("/<path:value>.jpg")
def send_jpg(value):
    jstr = os.path.join(BASEDIR,value + '.jpg')
    return send_from_directory(BASEDIR, value + '.jpg')

@app.route("/<path:value>.gif")
def send_gif(value):
    jstr = os.path.join(BASEDIR, value + '.gif')
    return send_from_directory(BASEDIR, value + '.gif')

@app.route("/<path:value>.mp4")
def send_mp4(value):
    jstr = os.path.join(BASEDIR, value + '.gif')
    return send_from_directory(BASEDIR, value + '.mp4')
    
@app.route("/thumb/<path:value>.jpg")
def send_thumb_jpg(value):
    jstr = os.path.join(BASEDIR, value + '.jpg')
    size= 135, 135
    im = Image.open(jstr)
    im = cropped_thumbnail(im, size)
    return serve_pil_jpg(im)

@app.route("/thumb/<path:value>.gif")
def send_thumb_gif(value):
    jstr = os.path.join(BASEDIR, value + '.gif')
    size = 135, 135
    im = Image.open(jstr)
    im = cropped_thumbnail(im, size)
    return serve_pil_gif(im)


def serve_pil_jpg(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def serve_pil_gif(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'GIF')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

