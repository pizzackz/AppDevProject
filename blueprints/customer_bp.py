from flask import Blueprint, render_template, redirect, url_for, session, flash

customer_bp = Blueprint("customer", __name__)


# Home page (Customer)
@customer_bp.route("/<string:id>")
def customer_home(id):
    # Retrieve customer dictionary from session
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    print(f"short_id = {id}, data = {cust_dict}")
    return render_template("customer/home.html", id=id, display_name=display_name)


# Order page (Customer)
@customer_bp.route("/<string:id>/order")
def order(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/order.html", id=id, display_name=display_name)


# Recipe Creator page (Customer)
@customer_bp.route("/<string:id>/recipe_creator")
def recipe_creator(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/recipe_creator.html", id=id, display_name=display_name)


# Edit Profile page (Customer)
@customer_bp.route("/<string:id>/edit_customer_profile")
def edit_cust_profile(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/edit_profile.html", id=id, display_name=display_name)


# Favourites page (Customer)
@customer_bp.route("/<string:id>/favourites")
def favourites(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/favourites.html", id=id, display_name=display_name)


# Articles page (Customer)
@customer_bp.route("/<string:id>/articles")
def customer_articles(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/articles.html", id=id, display_name=display_name)


# Current Delivery page (Customer)
@customer_bp.route("/<string:id>/current_delivery")
def current_delivery(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/current_delivery.html", id=id, display_name=display_name)


# Feedback page (Customer)
@customer_bp.route("/<string:id>/feedback")
def feedback(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/feedback.html", id=id, display_name=display_name)


# Order History page (Customer)
@customer_bp.route("/<string:id>/order_history")
def order_history(id):
    cust_dict = session.get("customer")
    display_name = cust_dict.get("display_name")
    return render_template("customer/order_history.html", id=id, display_name=display_name)