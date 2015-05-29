from subprocess import *
from flask import Flask
from flask import make_response
from flask import send_file
import os
app = Flask(__name__)

@app.route("/")
def index():
    return "RedHat Server 6 for downloading debuginfo packages!"

#TODO: add cleanup crontab 
@app.route("/download/<version_name>")
def download(version_name):
    dest="--destdir=/repos/redhat/Packages" 
    child = Popen(["yumdownloader", version_name, dest], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    log = child.communicate()[0]
    if child.wait():
        print "yumdownload run failed" 
   
    response = make_response(log)
    response.content_type = "text/plain"

    return response
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
