from flask import Blueprint, render_template, redirect, url_for

customer_bp = Blueprint("customer", __name__)

# Home page (Customer)
@customer_bp.route("/customer/<string:id>")
def customer_home(id):
    return render_template("customer/home.html", id=id)


# Order page (Customer)
@customer_bp.route("/order/<string:id>")
def order(id):
    return render_template("customer/order.html", id=id)


# Recipe Creator page (Customer)
@customer_bp.route("/recipe_creator/<string:id>")
def recipe_creator(id):
    return render_template("customer/recipe_creator.html", id=id)


# Edit Profile page (Customer)
@customer_bp.route("/edit_customer_profile/<string:id>")
def edit_cust_profile(id):
    return render_template("customer/edit_profile.html", id=id)


# Favourites page (Customer)
@customer_bp.route("/favourites/<string:id>")
def favourites(id):
    return render_template("customer/favourites.html", id=id)


# Articles page (Customer)
@customer_bp.route("/articles/<string:id>")
def customer_articles(id):
    return render_template("customer/articles.html", id=id)


# Current Delivery page (Customer)
@customer_bp.route("/current_delivery/<string:id>")
def current_delivery(id):
    return render_template("customer/current_delivery.html", id=id)


# Feedback page (Customer)
@customer_bp.route("/feedback/<string:id>")
def feedback(id):
    return render_template("customer/feedback.html", id=id)


# Order History page (Customer)
@customer_bp.route("/order_history/<string:id>")
def order_history(id):
    return render_template("customer/order_history.html", id=id)