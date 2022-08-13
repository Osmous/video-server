from flask import Flask, render_template, jsonify, request

import urllib

import argparse
import sys
import os
import subprocess

import logging

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

import warnings
warnings.filterwarnings("ignore")

gevent.monkey.patch_all()

app = Flask(__name__,static_folder='static')

#Logging Filter for thumbnails to prevent spam in console.
class thumbnailFilter(logging.Filter):
    def filter(self, record):
        return "/static/thumbnails" not in record.getMessage()

#BASIC RENDERS
@app.route("/")
def index():
    genThumbnails()
    links=[]
    for count, filename in enumerate(os.listdir("static/videos")): 
        if ".gitignore" in filename:
            continue
        filenamesafe = urllib.parse.quote(filename,safe='')
        finenameNoExt= os.path.splitext(filename)[0]
        row = [filename,filenamesafe,finenameNoExt]
        links.append(row)
    return render_template("index.html",links = links)

@app.route("/videolocation", methods=['GET','POST'])
def location():
    videoname = request.args.get('name')
    location = "../static/videos/"+videoname

    return render_template("video.html",link = location)

@app.route("/livestream", methods=['GET','POST'])
def livestreamlist():
    return render_template("livestream.html")
        
# Startup methods
def genThumbnails():
    videos = []
    thumbnails = []
    for i in os.listdir("static/videos"):
        if ".gitignore" in i:
            continue
        base=os.path.splitext(i)[0]
        videos.append(base)
        if os.path.exists("static/thumbnails/"+base+".jpg"):
            continue
        else:
            #get thumbnail from video
            cmd = 'ffmpeg -loglevel 4 -ss 00:00:25.000 -i "static/videos/'+i+'" -vframes 1 -s 149x84 "static/thumbnails/'+base+'.jpg"'

            try:
                subprocess.call(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                print(e)
    for i in os.listdir("static/thumbnails"):
        base=os.path.splitext(i)[0]
        thumbnails.append(base)
    
    for i in list(set(thumbnails)-set(videos)):
        os.remove("static/thumbnails/"+i+".jpg")

if __name__ == '__main__':
    genThumbnails()
    try:
        host = '0.0.0.0'
        port = 5000
        parser = argparse.ArgumentParser()
        parser.add_argument('port', type=int)

        args = parser.parse_args()
        if args.port:
            port = args.port

        logger = logging.getLogger()
        flask_ch = logging.StreamHandler()
        logger.setLevel(logging.INFO)
        logger.addHandler(flask_ch)
        logger.addFilter(thumbnailFilter())

        http_server = WSGIServer((host, port), app,log =logger)
        app.debug = True
        print('Web server waiting for requests')
        http_server.serve_forever()


    except:
        print("Exception while running web server")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])