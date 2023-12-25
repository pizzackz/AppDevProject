from flask import Blueprint, render_template, redirect, url_for, session, flash

admin_bp = Blueprint("admin", __name__)


# Home page (Admin)
@admin_bp.route("/admin/<string:id>")
def admin_home(id):
    # Retrieve admin dictionary from session
    admin_dict = session.get("admin")
    print(f"short_id = {id}, data = {admin_dict}")
    return render_template("admin/home.html", id=id, display_name=admin_dict.get("display_name", "Admin"))


# Customer Database page (Admin)
@admin_bp.route("/<string:id>/customer_database")
def customer_database(id):
    return render_template("admin/customer_database.html", id=id)


# Recipe Database page (Admin)
@admin_bp.route("/<string:id>/recipe_database")
def recipe_database(id):
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@admin_bp.route("/<string:id>/menu_database")
def menu_database(id):
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@admin_bp.route("/<string:id>/articles_database")
def articles_database(id):
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@admin_bp.route("/<string:id>/customer_feedback")
def customer_feedback(id):
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@admin_bp.route("/<string:id>/edit_admin_profile")
def edit_admin_profile(id):
    return render_template("admin/edit_profile.html", id=id)