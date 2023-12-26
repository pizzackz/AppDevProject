import string
# IMPLEMENT LOGOUTS FOR CUSTOMERS & ADMINS!!!

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import hashlib
import shelve
import random

from config import Config
from Forms import BaseSignUpForm, OTPForm, PasswordForm, LoginForm, EmailForm, ResetPasswordForm
from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from cust_acc_functions import create_customer
from validators import is_correct_otp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(guest_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)

mail = Mail(app)


# Functions
# Generate otp
def generate_otp(length):
    digits = string.digits
    otp = ''.join(random.choices(digits, k=length))

    print("otp = " + otp)

    return otp


# Send email
def send_mail(subject, sender, recipients, body):
    try:
        if not isinstance(recipients, list):
            recipients = [recipients]

        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")
        return False


# Get user (customer/ admin) object from username, returns False when no such account found
def get_user_object(username):
    customers_dict = {}
    admins_dict = {}
    db = shelve.open("user_accounts.db", "c")

    if "Customers" in db:
        customers_dict = db["Customers"]
    else:
        db["Customers"] = customers_dict

    if "Admins" in db:
        admins_dict = db["Admins"]
    else:
        db["Admins"] = admins_dict

    db.close()

    for customer in customers_dict.values():
        if username == customer.get_username():
            return customer

    for admin in admins_dict.values():
        if username == admin.get_username():
            return admin

    return False


# Compare passwords
def compare_passwords(account_type, user_id, password):
    actual_password = ""
    # Hash given password
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Retrieve stored hashed password
    db = shelve.open("user_accounts.db", "c")
    if account_type == "customer":
        actual_password = db["Customers"][user_id].get_password()
    elif account_type == "admin":
        actual_password = db["Admins"][user_id].get_password()
    
    return hashed_password == actual_password
        

# Routes
# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # session.clear()
    # Remove session data from signing up if redirected to login
    session.pop("create_customer", None)
    session.pop("signup_stage", None)

    action = session.get("action", "login")

    # Reset action in session if user clicked 'Back to Login'
    if request.args.get("back"):
        session["action"] = "login"
        return redirect(url_for("login"))

    # Update action in session if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session["action"] = "send_email"
        return redirect(url_for("login"))

    form = LoginForm(request.form)
    # Render appropriate template based on current action for POST requests
    if request.method == "POST":
        if action == "login":
            form = LoginForm(request.form)
            if form.validate():
                # Identify type of account / Check whether account exists
                user_object = get_user_object(form.username.data)
                user_id = ""
                account_type = ""

                if user_object == False:
                    # Display invalid username or password msg
                    flash("Wrong Username or Password!", "error")
                    print("Wrong Username")

                    return render_template("login_base.html", form=form)
                else:
                    user_id = user_object.get_user_id()
                    if int(user_id[0:3]) in range(100, 500):
                        account_type = "customer"
                    elif int(user_id[0:3]) in range(501, 999):
                        account_type = "admin"

                # Handle password checking
                if not compare_passwords(account_type, user_id, form.password.data):
                    # Display invalid otp msg
                    flash("Wrong Username or Password!", "error")
                    print("Wrong Password")

                    return render_template("login_base.html", form=form)
                else:
                    # Remove action in session, Create account type in session
                    session.pop("action", None)
                    if account_type == "customer":
                        session[account_type] = user_object.get_cust_data()
                    elif account_type == "admin":
                        session[account_type] = user_object.get_admin_data()

                    # Redirect users to appropriate home pages
                    print("account_type = " + account_type + ", user_id[0:11] = " + user_id[0:11])
                    display_name = user_object.get_display_name()

                    if account_type == "customer":
                        return redirect(url_for("customer.customer_home", id=user_id[0:11], display_name=display_name))
                    elif account_type == "admin":
                        return redirect(url_for("admin.admin_home", id=user_id[0:11], display_name=display_name))
            else:
                return render_template("login_base.html", form=form)
        elif action == "send_email":
            pass
        elif action == "reset_password":
            pass

    # Render appropriate template based on current action for GET requests
    if request.method == "GET":
        if action == "login":
            form = LoginForm()
            return render_template("login_base.html", form=form)
        elif action == "send_email":
            form = EmailForm()
            return render_template("login_send_email.html", form=form)
        elif action == "reset_password":
            form = ResetPasswordForm()
            return render_template("login_reset_pass.html", form=form)


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
    
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_mail("Your Verification Code", "itastefully@gmail.com", [session.get("create_customer").get("email")], f"Your verification code is {otp}")

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        # Update otp in create_customer in session
        session["create_customer"]["otp"] = otp

        return redirect(url_for("signup"))

    # Redirect to appropriate template based on current stage for POST requests
    if request.method == "POST":
        if stage == "base" or request.form.get("resend_otp"):
            form = BaseSignUpForm(request.form)
            if form.validate():
                # Generate and send OTP
                otp = generate_otp(6)
                send_mail("Your Verification Code", "itastefully@gmail.com", [form.email.data], f"Your verification code is {otp}")

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
                print(form.errors)
                return render_template("signup_base.html", form=form)
        elif stage == "verify_email":
            form = OTPForm(request.form)
            if form.validate():
                # Check correct otp
                if not is_correct_otp(form.otp.data):
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
            # Check whether passwords match
            if form.validate():
                if form.password.data != form.confirm_password.data:
                    flash("Passwords do not match!", "error")
                    return render_template("signup_password.html", form=form)

                # Hash password
                password = form.password.data
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

                # Store ALL customer data in shelve db
                create_customer(session["create_customer"], hashed_password, form)

                # Display successful account creation msg
                flash("Account created, login now!", "success")

                # Clear signup stage, create_customer in session
                session.pop("signup_stage", None)
                session.pop("create_customer", None)

                return redirect(url_for("login"))
            else:
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
