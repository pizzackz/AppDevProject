from flask import session, Blueprint, render_template

guest_bp = Blueprint("guest", __name__)

# Home page (Default - Guest)
@guest_bp.route("/")
def home():
    return render_template("guest/home.html")


# Menu page (Guest)
@guest_bp.route("/menu")
def menu():
    # Remove session data when redirected from signup or login
    for key in ("customer", "admin", "reset_pass_details", "create_customer"):
        session.pop(key, None)

    return render_template("guest/menu.html")


# Articles page (Guest)
@guest_bp.route("/articles")
def articles():
    return render_template("guest/articles.html")