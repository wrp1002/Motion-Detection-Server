from flask import Flask, jsonify, render_template
import ConfigManager as config

app = Flask(__name__, static_folder="web/static", template_folder="web/templates")

@app.route('/')
def indexPage():
    return render_template("index.html")

@app.route('/cameras')
def camerasPage():
    return render_template("cameras.html")

@app.route('/config')
def configPage():
    return render_template("config.html")

def Run(debug=False):
    port = config.GetValueR("webserver", "port")
    print(port)
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__=="__main__":
    Run(True)
