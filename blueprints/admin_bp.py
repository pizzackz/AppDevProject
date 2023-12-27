from flask import Blueprint, render_template, redirect, url_for, session, flash

admin_bp = Blueprint("admin", __name__)


# Home page (Admin)
@admin_bp.route("/admin/<string:id>")
def admin_home(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@admin_bp.route("/<string:id>/customer_database")
def customer_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/customer_database.html", id=id)


# Recipe Database page (Admin)
@admin_bp.route("/<string:id>/recipe_database")
def recipe_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@admin_bp.route("/<string:id>/menu_database")
def menu_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@admin_bp.route("/<string:id>/articles_database")
def articles_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@admin_bp.route("/<string:id>/customer_feedback")
def customer_feedback(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@admin_bp.route("/<string:id>/edit_admin_profile")
def edit_admin_profile(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/edit_profile.html", id=id)