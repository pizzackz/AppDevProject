from flask import Flask, render_template, request, redirect, url_for
from Forms import Login, Signup

app = Flask(__name__)


# Login page
@app.route("/login")
def login():
    login_form = Login(request.form)
    return render_template("login.html", form=login_form)


# Signup page
@app.route("/signup")
def signup():
    signup_form = Signup(request.form)
    return render_template("signup.html", form=signup_form)


# Home page (Default - Guest)
@app.route("/")
@app.route("/home")
def home():
    return render_template("guest/home.html")


# Menu page (Guest)
@app.route("/menu")
def menu():
    return render_template("guest/menu.html")


# Articles page (Guest)
@app.route("/articles")
def articles():
    return render_template("guest/articles.html")


# Home page (Customer)
@app.route("/customer/<string:id>")
def customer_home(id):
    return render_template("customer/home.html", id=id)


# Order page (Customer)
@app.route("/order/<string:id>")
def order(id):
    return render_template("customer/order.html", id=id)


# Recipe Creator page (Customer)
@app.route("/recipe_creator/<string:id>")
def recipe_creator(id):
    return render_template("customer/recipe_creator.html", id=id)


# Edit Profile page (Customer)
@app.route("/edit_customer_profile/<string:id>")
def edit_cust_profile(id):
    return render_template("customer/edit_profile.html", id=id)


# Favourites page (Customer)
@app.route("/favourites/<string:id>")
def favourites(id):
    return render_template("customer/favourites.html", id=id)


# Articles page (Customer)
@app.route("/articles/<string:id>")
def customer_articles(id):
    return render_template("customer/articles.html", id=id)


# Current Delivery page (Customer)
@app.route("/current_delivery/<string:id>")
def current_delivery(id):
    return render_template("customer/current_delivery.html", id=id)


# Feedback page (Customer)
@app.route("/feedback/<string:id>")
def feedback(id):
    return render_template("customer/feedback.html", id=id)


# Order History page (Customer)
@app.route("/order_history/<string:id>")
def order_history(id):
    return render_template("customer/order_history.html", id=id)


# Home page (Admin)
@app.route("/admin/<string:id>")
def admin_home(id):
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@app.route("/customer_database/<string:id>")
def customer_database(id):
    return render_template("admin/customer_database.html", id=id)


# Recipe Database page (Admin)
@app.route("/recipe_database/<string:id>")
def recipe_database(id):
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@app.route("/menu_database/<string:id>")
def menu_database(id):
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@app.route("/articles_database/<string:id>")
def articles_database(id):
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@app.route("/customer_feedback/<string:id>")
def customer_feedback(id):
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@app.route("/edit_admin_profile/<string:id>")
def edit_admin_profile(id):
    return render_template("admin/edit_profile.html", id=id)


if __name__ == "__main__":
    app.run(debug=True)