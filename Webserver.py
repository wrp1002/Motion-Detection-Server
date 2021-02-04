from flask import Flask, jsonify, render_template, flash, request, Response, abort
import ConfigManager as config
import VideoManager as video
import EmailManager as email
import json
import os
import sys
import time
import threading

app = Flask(__name__, static_folder="web/static", template_folder="web/templates")
app.secret_key = b'SDFKHW$%^8wTsoigt098'

self = sys.modules[__name__]
self.targetState = 1

def Stop():
    time.sleep(1)
    raise RuntimeError("Server going down")

def Restart():
    video.Restart()
    email.Init()

#   Disable cache
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def indexPage():
    return render_template("index.html")

@app.route('/cameras')
def camerasPage():
    return render_template("cameras.html")

@app.route('/config', methods=["GET", "POST", "DELETE"])
def configPage():
    if request.method == "GET":
        config_data = config.AsString()
        return render_template("config.html", config_data=config_data)
    elif request.method == "POST":
        data = request.form.get("data")
        data = json.loads(data)
        config.SaveConfig(data)
        return Response("Config Saved!", 200)
    elif request.method == "DELETE":
        config.RestoreConfig()
        return Response("Config Restored", 200)
    else:
        abort(400)

@app.route('/api/config')
def api_config():
    configData = config.AsString()
    return Response(configData, 200)

@app.route('/api/messages')
def get_messages():
    state = config.GetValue("email", "enabled")
    response = json.dumps({
        "enabled": state
    })
    return Response(response, 200)

@app.route('/api/messages/<state>')
def set_messages(state):
    enabled = (state == "true" or state == "on")
    config.SetValue(enabled, "email", "enabled")
    response = json.dumps({
        "enabled": enabled
    })
    return Response(response, 200)

@app.route('/api/motion')
def get_motion():
    state = config.GetValue("motionEnabled")
    response = json.dumps({
        "enabled": state
    })
    return Response(response, 200)

@app.route('/api/motion/<state>')
def set_motion(state):
    enabled = (state == "true" or state == "on")
    config.SetValue(enabled, "motionEnabled")

    return Response(enabled, 200)

@app.route('/api/restart')
def restart():
    threading.Thread(target=Restart).start()
    return Response('Restarting', 200)

def Run(debug=False):
    port = config.GetValue("webserver", "port")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__=="__main__":
    Run(True)
