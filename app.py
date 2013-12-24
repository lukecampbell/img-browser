from flask import Flask, request, render_template, send_from_directory, make_response, send_file
from flask import Response, redirect, url_for
from glob import glob
from PIL import Image
from config import *
from StringIO import StringIO
from cropped_thumbnail import cropped_thumbnail
from ffvideo import VideoStream
import fnmatch
import os
import re
import mimetypes

filecache = {}

app = Flask(__name__)

@app.route("/")
def hello():
    return redirect(url_for('browse'))

def get_images():
    matches = []
    for root, dirnames, filenames in os.walk(BASEDIR):
        for filename in fnmatch.filter(filenames, "*.jpg"):
            matches.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, "*.gif"):
            matches.append(os.path.join(root, filename))
    baselen = len(BASEDIR + '/')
    jpg_list  = [ s[baselen:] for s in matches ]
    filecache.update(dict(zip(range(len(jpg_list)), jpg_list)))
    return jpg_list

def get_gifs():
    matches = []
    for root, dirnames, filenames in os.walk(BASEDIR):
        for filename in fnmatch.filter(filenames, "*.gif"):
            matches.append(os.path.join(root, filename))
    baselen = len(BASEDIR + '/')
    jpg_list  = [ s[baselen:] for s in matches ]
    filecache.update(dict(zip(range(len(jpg_list)), jpg_list)))
    return jpg_list

def get_movies():
    matches = []
    for root, dirnames, filenames in os.walk(BASEDIR):
        for filename in fnmatch.filter(filenames, "*.mp4"):
            matches.append(os.path.join(root, filename))
    baselen = len(BASEDIR + '/')
    mvlist = [ s[baselen:] for s in matches ]
    return mvlist

@app.route("/browse")
@app.route("/browse/<value>")
def browse(value=0):
    jpg_list = get_images()
    value=int(value)
    buf = StringIO()
    for i in xrange(value*20, (value+1)*20):
        if i >= len(jpg_list):
            break
        if i % 4 == 0 and i > 0:
            buf.write('</div>\n')
        if i % 4 == 0:
            buf.write('<div class="row">\n')
        buf.write('<div class="image"><a href="/view/' + str(i) + '"><img src="/thumb/' + str(i) + '"></img></a></div>\n')
    buf.write('</div>\n')
    buf.seek(0)
    return render_template('browse.html', index=value, next=value+1, prev=max(0, value-1), title='Browse', html_content=buf.read())
  
@app.route("/browse/gifs")
@app.route("/browse/gifs/<value>")
def browse_gifs(value=0):
    gif_list = get_gifs()
    value=int(value)
    buf = StringIO()
    for i in xrange(value*20, (value+1)*20):
        if i >= len(gif_list):
            break
        if i % 4 == 0 and i > 0:
            buf.write('</div>\n')
        if i % 4 == 0:
            buf.write('<div class="row">\n')
        buf.write('<div class="image"><a href="/view/' + str(i) + '"><img src="/thumb/' + str(i) + '"></img></a></div>\n')
    buf.write('</div>\n')
    buf.seek(0)
    return render_template('browse.html', next=value+1, prev=max(0, value-1), title='Browse', html_content=buf.read())


@app.route("/mbrowse")
def mbrowse():
    mlist = get_movies()
    rows = []
    inner_row = []
    i = 0
    for m in mlist:
        if(i % 4) == 0 and i > 0:
            rows.append(inner_row)
            inner_row = []
        inner_row.append(m)
        i+=1
    if inner_row:
        rows.append(inner_row)
    return render_template('mbrowse.html', title='Browse Movies', mlist=rows)

def send_video(video_file, ext='.mp4'):
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(os.path.join(BASEDIR, video_file+ext))
    path = os.path.join(BASEDIR, video_file + ext)

    size = os.path.getsize(path)
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()
    
    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1
    
    data = None
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 
        206,
        mimetype=mimetypes.guess_type(path)[0], 
        direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

    return rv

@app.after_request
def after_request(response):
    response.headers.add('Acept-Ranges', 'bytes')
    return response


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
    return send_video(value, '.mp4')

@app.route("/thumb/<value>")
def send_thumb(value):
    if not filecache:
        get_images()
    ivalue = int(value)
    img_path = filecache[ivalue]
    if img_path.endswith('.jpg'):
        return send_thumb_jpg(img_path)
    if img_path.endswith('.gif'):
        return send_thumb_gif(img_path)

def send_thumb_jpg(value):
    jstr = os.path.join(BASEDIR, value)
    size= 135, 135
    im = Image.open(jstr)
    im = cropped_thumbnail(im, size)
    return serve_pil_jpg(im)

def send_thumb_gif(value):
    jstr = os.path.join(BASEDIR, value)
    size = 135, 135
    im = Image.open(jstr)
    im = cropped_thumbnail(im, size)
    return serve_pil_gif(im)

@app.route("/thumb/<path:value>.mp4")
def send_thumb_mp4(value):
    jstr = os.path.join(BASEDIR, value + '.mp4')
    size = 135, 135
    im = VideoStream(jstr).get_frame_at_sec(5).image()
    im = cropped_thumbnail(im, size)
    return serve_pil_jpg(im)

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

@app.route("/view/<value>")
def serve_index(value):
    if not filecache:
        get_images()
    try:
        ivalue = int(value)
    except ValueError:
        raise
    img_path = filecache[ivalue]
    prev = max(ivalue - 1,0)

    return render_template('individual.html', title="View", index=value, prev=prev, next=ivalue+1,imgitem=img_path)

@app.route("/mobile/<value>")
def serve_mobile(value):
    if not filecache:
        get_images()
    try:
        ivalue = int(value)
    except ValueError:
        raise
    img_path = filecache[ivalue]
    prev = max(ivalue - 1,0)

    return render_template('mobile.html', title="Mobile View", index=value, prev=prev, next=ivalue+1,imgitem=img_path)


@app.route("/mobilebrowse")
@app.route("/mobilebrowse/<value>")
def mobilebrowse(value=0):
    jpg_list = get_images()
    value=int(value)
    buf = StringIO()
    for i in xrange(value*30, (value+1)*30):
        if i >= len(jpg_list):
            break
        buf.write('<div class="image"><a href="/view/' + str(i) + '"><img src="/thumb/' + str(i) + '"></img></a></div>\n')
    buf.write('</div>\n')
    buf.seek(0)
    return render_template('mobilebrowse.html', index=value, next=value+1, prev=max(0, value-1), title='Browse', html_content=buf.read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

