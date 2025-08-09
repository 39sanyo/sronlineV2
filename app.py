from flask import Flask, render_template, url_for

app = Flask(__name__)

# landing
@app.route('/', methods = ['GET', 'POST'])
def site():
    return render_template('index.html')

# resume
@app.route('/resume', methods = ['GET', 'POST'])
def resume():
    return render_template("resume.html")

# noscam
@app.route('/noscam', methods = ['GET', 'POST'])
def noscam():
    return render_template("noscam.html")

# login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template("login.html")

# signup
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
