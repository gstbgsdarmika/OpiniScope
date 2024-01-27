from flask import Flask, render_template, send_from_directory


app = Flask(__name__)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/")
def index():
    active_page = 'index'
    return render_template("index.html", active_page=active_page)

@app.route("/analisis")
def analysis():
    active_page = 'analysis'
    return render_template("analysis.html", active_page=active_page)

@app.route("/analisis-file")
def analysisInputFile():
    active_page = 'analysis'
    return render_template("analysisInputFile.html", active_page=active_page)

@app.route("/analisis-teks")
def analysisInputText():
    active_page = 'analysis'
    return render_template("analysisInputText.html", active_page=active_page)

@app.route("/hasil-analisis-file")
def resultInputFile():
    active_page = 'analysis'
    return render_template("resultInputFile.html", active_page=active_page)

@app.route("/hasil-analisis-teks")
def resultInputText():
    active_page = 'analysis'
    return render_template("resultInputText.html", active_page=active_page)

@app.route("/preline.js")
def serve_preline_js():
    return send_from_directory("node_modules/preline/dist", "preline.js")

@app.route("/apexcharts.min.js")
def serve_apexcharts_js():
    return send_from_directory("node_modules/apexcharts/dist", "apexcharts.min.js")

@app.route("/lodash.min.js")
def serve_lodash_js():
    return send_from_directory("node_modules/lodash", "lodash.min.js")

@app.route("/apexcharts.min.js")
def serve_apexcharts_css():
    return send_from_directory("node_modules/apexcharts/dist", "apexcharts.css")


if __name__ == "__main__":
    app.run()