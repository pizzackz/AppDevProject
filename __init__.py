# IMPLEMENT LOGOUTS FOR CUSTOMERS & ADMINS!!!

from flask import Flask, render_template, request, redirect, url_for
from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from Forms import BaseSignUpForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "idkwhattoputhere"
app.config["SESSION_TYPE"] = "filesystem"

app.register_blueprint(guest_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)

# Login page
@app.route("/login")
def login():
    return render_template("login.html", form="Hello")


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup(stage="base"):
    form = BaseSignUpForm(request.form)

    if request.method == "POST":
        if stage == "base":
            # Handle base stage form data
            form = BaseSignUpForm(request.form)
            if form.validate_on_submit():
                # Generate and send OTP, store temporary data, update stage
                stage = "verify_email"
            else:
                return render_template("signup.html", stage=stage, form=form)

    return render_template("signup.html", stage=stage, form=form)



# Error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
