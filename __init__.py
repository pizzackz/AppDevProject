from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return "<h1>Hi everyone</h1><p>Good to have you here</p><p>Let's get started on this project together!</p>"


if __name__ == "__main__":
    app.run(debug=True)