from flask import Flask, render_template

app = Flask(__name__)

# Guest home page (Default)
@app.route("/")
def home():
    return render_template("home.html")


# Customer home page
@app.route("/customer/")
def customer_home():
    return render_template("customer_home.html")


# Admin home page
@app.route("/admin/")
def admin_home():
    return render_template("admin_home.html")


if __name__ == "__main__":
    app.run(debug=True)