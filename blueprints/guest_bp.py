from flask import Blueprint, render_template

guest_bp = Blueprint("guest", __name__)

# Home page (Default - Guest)
@guest_bp.route("/")
def home():
    return render_template("guest/home.html")


# Menu page (Guest)
@guest_bp.route("/menu")
def menu():
    return render_template("guest/menu.html")


# Articles page (Guest)
@guest_bp.route("/articles")
def articles():
    return render_template("guest/articles.html")