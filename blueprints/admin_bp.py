from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__)

# Home page (Admin)
@admin_bp.route("/admin/<string:id>")
def admin_home(id):
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@admin_bp.route("/customer_database/<string:id>")
def customer_database(id):
    return render_template("admin/customer_database.html", id=id)


# Recipe Database page (Admin)
@admin_bp.route("/recipe_database/<string:id>")
def recipe_database(id):
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@admin_bp.route("/menu_database/<string:id>")
def menu_database(id):
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@admin_bp.route("/articles_database/<string:id>")
def articles_database(id):
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@admin_bp.route("/customer_feedback/<string:id>")
def customer_feedback(id):
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@admin_bp.route("/edit_admin_profile/<string:id>")
def edit_admin_profile(id):
    return render_template("admin/edit_profile.html", id=id)