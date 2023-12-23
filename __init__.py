# IMPLEMENT LOGOUTS FOR CUSTOMERS & ADMINS!!!

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import hashlib
import shelve
import random

from config import Config
from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from Forms import BaseSignUpForm, OTPForm, PasswordForm, LoginForm
from Customer import Customer

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(guest_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)


# Functions
# Generate otp
def generate_otp(length):
    digits = "0123456789"
    otp = ""

    for i in range(length):
        otp += random.choice(digits)

    return otp


# Verifying otp after validated form
def is_valid_otp(otp):
    entered_otp = otp
    stored_otp = session.get("create_customer", None).get("otp")

    if entered_otp == stored_otp:
        return True
    else:
        flash("Invalid OTP! Please try again")
        return False


# Login page
@app.route("/login")
def login():
    form = LoginForm(request.form)
    return render_template("login.html", form=form)


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # session.clear()
    stage = session.get("signup_stage", "base")
    print("signup stage = " + stage)

    # Clear/ Reset sessions if user clicked 'Back to Signup'
    if request.args.get("back"):
        session.pop("create_customer", None)
        session["signup_stage"] = "base"
        return redirect(url_for("signup"))

    # Redirect to appropriate template based on current stage for POST requests
    if request.method == "POST":
        if stage == "base" or request.form.get("resend_otp"):
            form = BaseSignUpForm(request.form)
            if form.validate():
                # Generate and send OTP
                otp = generate_otp(6)
                print("otp = " + otp)
                mail = Mail(app)

                msg = Message(
                    "Your Verification Code",
                    sender="itastefully@gmail.com",
                    recipients=[form.email.data],
                )
                # Can try to style the body later on
                msg.body = f"Your verification code is: {otp}"
                mail.send(msg)

                # Display otp sent msg
                flash("An OTP has been sent to your email!", "info")

                # Store temporary data in session, update signup stage in session
                session["create_customer"] = {
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "username": form.username.data,
                    "email": form.email.data,
                    "otp": otp,
                }
                session["signup_stage"] = "verify_email"

                return redirect(url_for("signup"))
            else:
                return render_template("signup_base.html", form=form)
        elif stage == "verify_email":
            form = OTPForm(request.form)
            if form.validate():
                # Check correct otp
                if not is_valid_otp(form.otp.data):
                    # Display invalid otp msg
                    flash("Invalid OTP!", "error")
                    return render_template("signup_otp.html", form=form)

                # Update signup stage in session
                session["signup_stage"] = "set_password"
                return redirect(url_for("signup"))
            else:
                return render_template("signup_otp.html", form=form)
        elif stage == "set_password":
            form = PasswordForm(request.form)
            # Handle password checking
            if form.validate():
                if form.password.data != form.confirm_password.data:
                    flash("Passwords do not match!", "error")
                    return render_template("signup_password.html", form=form)

                # Hash password
                password = form.password.data
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

                # Store ALL customer data in shelve db
                customers_dict = {}

                try:
                    db = shelve.open("customer.db", "c")

                    if "Customers" in db:
                        customers_dict = db["Customers"]
                    else:
                        db["Customers"] = customers_dict
                except:
                    # Display database error message
                    flash("Error in connecting to database", "error")
                    return render_template("signup_password.html", form=form)
                else:
                    customer = Customer(
                        # Change how user_id is set when we have thought of a way to do so
                        session["create_customer"]["username"],
                        session["create_customer"]["first_name"],
                        session["create_customer"]["last_name"],
                        session["create_customer"]["username"],
                        session["create_customer"]["email"],
                        hashed_password
                    )

                    customers_dict[customer.get_user_id()] = customer
                    db["Customers"] = customers_dict
                finally:
                    if db:
                        db.close()

                # Display successful account creation msg
                flash("Account created, login now!", "success")

                # Clear signup stage, create_customer in session
                session.pop("signup_stage", None)
                session.pop("create_customer", None)

                return redirect(url_for("login"))
            else:
                print("Password not validated")
                return render_template("signup_password.html", form=form)

    # Render appropriate template based on current stage for GET requests
    if request.method == "GET":
        if stage == "base":
            form = BaseSignUpForm()
            return render_template("signup_base.html", form=form)
        elif stage == "verify_email":
            form = OTPForm()
            return render_template("signup_otp.html", form=form)
        elif stage == "set_password":
            form = PasswordForm()
            return render_template("signup_password.html", form=form)


# Error page (code 404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404


# Error page (code 500) - Complete html page for this
# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template("error_500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
