# IMPLEMENT LOGOUTS FOR CUSTOMERS & ADMINS!!!

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_mail import Mail
import hashlib

from Config import Config
from Forms import BaseSignUpForm, OTPForm, PasswordForm, LoginForm, EmailForm, ResetPasswordForm

from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from functions import generate_otp, send_email, get_user_object, get_account_type, compare_passwords, generate_unique_token
from cust_acc_functions import create_customer, update_cust_details
from admin_acc_functions import update_admin_details

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(guest_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)

mail = Mail(app)

# Routes
# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # session.clear()
    # Remove session data from signing up if redirected to login
    session.pop("create_customer", None)
    session.pop("signup_stage", None)

    login_action = session.get("login_action", "login")

    print("login_action = " + login_action + ", session keys = " + str(session.keys()))

    # Reset login_action in session, clear other login-related session data if user clicked 'Back to Login'
    if request.args.get("back"):
        session["login_action"] = "login"
        session.pop("customer", None)
        session.pop("admin", None)
        session.pop("reset_pass_token", None)
        return redirect("/login")

    # Update login_action in session if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session["login_action"] = "send_email"
        return redirect("/login")

    # Render appropriate template based on current login_action for POST requests
    if request.method == "POST":
        if login_action == "login":
            form = LoginForm(request.form)

            if form.validate():
                # Identify type of account, Check whether account exists
                user_object = get_user_object(username=form.username.data)
                user_id = ""
                account_type = ""

                if user_object == False:
                    # Display invalid username or password msg
                    flash("Wrong Username or Password!", "error")
                    print("Wrong Username")

                    return render_template("login_base.html", form=form)
                else:
                    user_id = user_object.get_user_id()
                    account_type = get_account_type(user_object=user_object)

                # Handle password checking
                if not compare_passwords(account_type, user_id, form.password.data):
                    # Display invalid otp msg
                    flash("Wrong Username or Password!", "error")
                    print("Wrong Password")

                    return render_template("login_base.html", form=form)
                else:
                    # Remove login_action in session, Create account type in session
                    session.pop("login_action", None)
                    if account_type == "customer":
                        session[account_type] = user_object.get_cust_data()
                    elif account_type == "admin":
                        session[account_type] = user_object.get_admin_data()

                    # Redirect users to appropriate home pages
                    print("account_type = " + account_type + ", user_id[0:11] = " + user_id[0:11])

                    if account_type == "customer":
                        return redirect(f"{user_id[0:11]}/home")
                    elif account_type == "admin":
                        return redirect(f"admin/{user_id[0:11]}")
            else:
                return render_template("login_base.html", form=form)
        elif login_action == "send_email":
            form = EmailForm(request.form)

            if form.validate():
                # Check whether account exists, Get user id
                user_object = get_user_object(email=form.email.data)
                user_id = ""

                if user_object == False:
                    # Display invalid username or password msg
                    flash("No such account with this email exists!", "error")
                    print(f"Account with email f{form.email.data} does not exist")

                    return render_template("login_send_email.html", form=form)
                else:
                    user_id = user_object.get_user_id()

                # Generate unique token
                token = generate_unique_token(user_id)

                # Store token in session, Store user data in session, Update login_action in session to reset password
                session["reset_pass_token"] = token
                if get_account_type(user_object=user_object) == "customer":
                    session["customer"] = user_object.get_cust_data()
                elif get_account_type(user_object=user_object) == "admin":
                    session["admin"] = user_object.get_admin_data()
                session["login_action"] = "reset_password"

                # Create url with the and send email using it
                url = url_for("login", token=token, _external=True)
                send_email(mail, "Password Reset", "itastefully", [form.email.data], body=f"Click here to reset your password: {url}")

                # Display reset password link sent msg
                flash("The reset password link has been sent to your email!", "info")
                print("login_action = " + session["login_action"] + ", reset pass token = " + session["reset_pass_token"])

                return redirect("/login")
            else:
                return render_template("login_send_email.html", form=form)
        elif login_action == "reset_password":
            # Render appropriate template once customer is sent reset password link
            if session["reset_pass_token"] == request.args.get("token"):
                form = ResetPasswordForm(request.form)

                # Clear reset pass token in session
                session.pop("reset_pass_token", None)

                if form.validate():
                    # Hash password
                    password = form.password.data
                    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

                    # Check whether password is the same as existing password for either customer or admin
                    for user_type in ("customer", "admin"):
                        if user_type in session and hashed_password == session.get(user_type).get("password"):
                            flash("Cannot set new password to be the same as current password", "error")
                            return render_template("login_reset_pass.html", form=form)

                    # Check whether passwords match
                    if form.password.data != form.confirm_password.data:
                        flash("Passwords do not match!", "error")
                        return render_template("login_reset_pass.html", form=form)

                    # Update user password data in shelve db
                    if "customer" in session:
                        user_data = session.get("customer")
                        update_cust_details(user_data.get("user_id"), password=hashed_password)
                        session.pop("customer")
                    elif "admin" in session:
                        user_data = session.get("admin")
                        update_admin_details(user_data.get("user_id"), password=hashed_password)
                        session.pop("admin")

                    # Display successful password reset msg
                    flash("Password has been resetted!", "success")

                    # Reset login_action in session, Clear reset pass token in session
                    session["login_action"] = "login"
                    session.pop("reset_pass_token", None)

                    return redirect("/login")
                else:
                    return render_template("login_send_email.html", form=form)
            else:
                form = EmailForm(request.form)
                return render_template("login_send_email.html", form=form)

    # Render appropriate template based on current login_action for GET requests
    if request.method == "GET":
        print("login action = " + login_action)
        if login_action == "login":
            form = LoginForm()
            return render_template("login_base.html", form=form)
        elif login_action == "send_email":
            form = EmailForm()
            return render_template("login_send_email.html", form=form)
        elif login_action == "reset_password":
            if session["reset_pass_token"] == request.args.get("token"):
                form = ResetPasswordForm()
                return render_template("login_reset_pass.html", form=form)
            else:
                form = EmailForm(request.form)
                return render_template("login_send_email.html", form=form)


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # session.clear()
    # Remove session data from logging in if redirected to signup
    session.pop("login_action", None)
    session.pop("reset_pass_token", None)

    stage = session.get("signup_stage", "base")
    print("signup stage = " + stage)

    # Clear/ Reset sessions if user clicked 'Back to Signup'
    if request.args.get("back"):
        session.pop("create_customer", None)
        session["signup_stage"] = "base"
        return redirect("/signup")
    
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_email(mail, "Your Verification Code", "itastefully@gmail.com", [session.get("create_customer").get("email")], body=f"Your verification code is {otp}")

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        # Update otp in create_customer in session
        session["create_customer"]["otp"] = otp

        return redirect("/signup")

    # Redirect to appropriate template based on current stage for POST requests
    if request.method == "POST":
        if stage == "base" or request.form.get("resend_otp"):
            form = BaseSignUpForm(request.form)
            if form.validate():
                # Generate and send OTP
                otp = generate_otp(6)
                send_email(mail, "Your Verification Code", "itastefully@gmail.com", [form.email.data], body=f"Your verification code is {otp}")

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

                return redirect("/signup")
            else:
                print(form.errors)
                return render_template("signup_base.html", form=form)
        elif stage == "verify_email":
            form = OTPForm(request.form)
            if form.validate():
                # Check correct otp
                if form.otp.data != session.get("create_customer").get("otp"):
                    # Display invalid otp msg
                    flash("Invalid OTP, please try again!", "error")
                    return render_template("signup_otp.html", form=form)

                # Update signup stage in session
                session["signup_stage"] = "set_password"
                return redirect("/signup")
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
                create_customer(session["create_customer"], hashed_password)

                # Display successful account creation msg
                flash("Account created, login now!", "success")

                # Clear signup stage, create_customer in session
                session.pop("signup_stage", None)
                session.pop("create_customer", None)

                return redirect("/login")
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
