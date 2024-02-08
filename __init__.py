from flask import Flask, session, request, redirect, flash, render_template
from flask_mail import Mail
from werkzeug.utils import secure_filename
import hashlib
import os

from config import Config
from Forms import BaseSignUpForm, OTPForm, PasswordForm, LoginForm, EmailForm, ResetPasswordForm, FileForm

from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from functions import generate_otp, send_email, get_user_object, get_account_type, compare_passwords
from cust_acc_functions import create_customer, update_cust_details, delete_customer
from admin_acc_functions import update_admin_details

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(guest_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)

mail = Mail(app)

# Routes
# Used for testing
# @app.route("/test", methods=["GET", "POST"])
# def test():
#     form = FileForm(request.form)

#     if request.method == "POST" and form.validate():
#         file_item = request.files["file"]
#         filename = file_item.filename
#         file_item.save(os.path.join(app.config["UPLOAD_FOLDER"], "profile_pictures", id, secure_filename(filename))) # Replace 'id' with user_id

#         return "Success!"

#     return render_template("base.html", form=form)


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # session.clear()
    # Clear session data from signing up if redirected to login
    session.pop("create_customer", None)

    # Flash appropriate msg when redirected from guest pages
    if request.form.get("button") == "order_page":
        flash("Please login first before ordering!", "warning")
        return redirect("/login")
    if request.form.get("button") == "recipe_creator_page":
        flash("Please login first before using our recipe creator!", "warning")
        return redirect("/login")

    # Clear all user's logged in data if clicked on 'logout', redirect to clear url args
    if request.args.get("logout"):
        for key in ("customer", "admin", "new_data", "new_email_otp"):
            session.pop(key, None)
        return redirect("/login")

    # Clear login-related session data if user clicked 'Back to Login', redirect to clear url args
    if request.args.get("back"):
        for key in ("customer", "admin", "reset_pass_details"):
            session.pop(key, None)
        return redirect("/login")

    # Redirect to send email page if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        return redirect("/login/send_email")

    # Handle POST request
    if request.method == "POST":
        form = LoginForm(request.form)

        if form.validate():
            # Identify type of account, Check whether account exists
            user_object = get_user_object(username=form.username.data)

            # Display invalid username or password msg
            if user_object == False:
                flash("Wrong Username or Password!", "error")
                print("Wrong Username")

                return render_template("login_base.html", form=form)
            
            user_id = user_object.get_user_id()
            account_type = get_account_type(user_object=user_object)

            # Handle locked customer accounts trying to login
            if account_type == "customer" and user_object.get_is_locked():
                # Display account temporarily locked msg
                print("Account locked")

                # Redirect to locked_account page
                return redirect(f"/login/locked_account?user_id={user_object.get_user_id()}")

            # Handle password checking
            if not compare_passwords(account_type, user_id, form.password.data):
                # Display invalid credentials msg
                flash("Wrong Username or Password!", "error")
                print("Wrong Password")

                return render_template("login_base.html", form=form)
            else:
                # Store account type in session
                if account_type == "customer":
                    session[account_type] = user_object.get_cust_data()
                elif account_type == "admin":
                    session[account_type] = user_object.get_admin_data()

                # Redirect users to appropriate home pages
                print("account_type = " + account_type + ", user_id[0:11] = " + user_id[0:11])

                if account_type == "customer":
                    return redirect(f"{user_id[0:11]}/home")
                elif account_type == "admin":
                    return redirect(f"{user_id[0:11]}/admin")
        else:
            return render_template("login_base.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = LoginForm()
        return render_template("login_base.html", form=form)


# Login - Send email for password reset page
@app.route("/login/send_email", methods=["GET", "POST"])
def login_send_email():
    # Handle POST request
    if request.method == "POST":
        form = EmailForm(request.form)
        print("form validated = " + str(form.validate()))

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
            
            # Generate and send OTP
            otp = generate_otp(6)
            send_email(mail, "Your Verification Code", "itastefully@gmail.com", [form.email.data], body=f"Your verification code to reset your password is {otp}")

            # Store user_id, otp, email data in reset_pass_details in session
            session["reset_pass_details"] = {"email": form.email.data, "otp": otp}

            # Display otp sent msg
            flash("An OTP has been sent to your email!", "info")

            return redirect("/login/verify_email")
        else:
            return render_template("login_send_email.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = EmailForm()
        return render_template("login_send_email.html", form=form)


# Login - Verify email for password reset page
@app.route("/login/verify_email", methods=["GET", "POST"])
def login_verify_email():
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_email(mail, "Your Verification Code", "itastefully@gmail.com", [session.get("reset_pass_details").get("email")], body=f"Your verification code to reset your password is {otp}")

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        # Update otp in reset_pass_details in session
        session["reset_pass_details"]["otp"] = otp

        return redirect("/login/verify_email")

    # Handle POST request
    if request.method == "POST":
        form = OTPForm(request.form)
        if form.validate():
            # Check correct otp
            if form.otp.data != session.get("reset_pass_details").get("otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return render_template("login_otp.html", form=form)

            return redirect("/login/reset_password")
        else:
            return render_template("login_otp.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = OTPForm()
        return render_template("login_otp.html", form=form)


# Login - Reset password page
@app.route("/login/reset_password", methods=["GET", "POST"])
def login_reset_password():
    # Handle POST request
    if request.method == "POST":
        form = ResetPasswordForm(request.form)
        if form.validate():
            # Retrive necessary user data
            user_object = get_user_object(email=session.get("reset_pass_details").get("email"))
            account_type = get_account_type(user_object=user_object)
            user_id = user_object.get_user_id()
            existing_password = user_object.get_password()

            # Hash password
            password = form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Check whether password match existing password
            if hashed_password == existing_password:
                flash("Cannot set new password to be the same as current password", "error")
                return render_template("login_reset_pass.html", form=form)

            # Check whether passwords match
            if form.password.data != form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("login_reset_pass.html", form=form)

            # Update user password data in shelve db
            if account_type == "customer":
                update_cust_details(user_id, password=hashed_password)
            elif account_type == "admin":
                update_admin_details(user_id, password=hashed_password)

            # Clear reset_pass_details in session
            session.pop("reset_pass_details", None)

            # Display successful password reset msg
            flash("Password has been reset!", "success")

            return redirect("/login")
        else:
            return render_template("login_reset_pass.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = ResetPasswordForm()
        return render_template("login_reset_pass.html", form=form)


# Login - locked account page
@app.route("/login/locked_account", methods=["GET", "POST"])
def login_locked_account():
    user_id = request.args.get("user_id")
    print("user id = " + user_id)

    # Handle POST request
    if request.method == "POST":
        # No form validation since there are only submit buttons
        # Redirect to login page if clicked on close button
        if request.form.get("button") == "close":
            return redirect("/login")

        # Delete account if clicked on yes on delete confirmation
        if request.form.get("button") == "delete":
            delete_customer(user_id)

            # Display account deleted msg
            flash("Your account has been successfully deleted!", "info")

            return redirect("/login")

        # Handle cust request to unlock if clicked on unlock
        if request.form.get("button") == "unlock":
            # Set request unlock attribute to True
            update_cust_details(user_id, unlock_request=True)

            # Display sent unlock request msg
            flash("Your request to unlock this account has been sent! Please wait while our admins look into it!", "info")

            return redirect("/login")

    # Handle GET request
    if request.method == "GET":
        form = LoginForm()
        user_data = get_user_object(user_id).get_cust_data()
        return render_template("locked_account.html", form=form, user_data=user_data, user_id=user_id)


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # session.clear()
    # Remove session data from logging in if redirected to signup
    for key in ("customer", "admin", "reset_pass_details"):
        session.pop(key, None)

    # Clear create_customer in session if user clicked 'Back to Signup'
    if request.args.get("back"):
        session.pop("create_customer", None)
        return redirect("/signup")

    # Handle POST request
    if request.method == "POST":
        form = BaseSignUpForm(request.form)
        if form.validate():
            # Generate and send OTP
            otp = generate_otp(6)
            send_email(mail, "Your Verification Code", "itastefully@gmail.com", [form.email.data], body=f"Your verification code is {otp}")

            # Display otp sent msg
            flash("An OTP has been sent to your email!", "info")

            # Store temporary data in session
            session["create_customer"] = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "username": form.username.data,
                "email": form.email.data,
                "otp": otp,
            }

            return redirect("/signup/verify_email")
        else:
            print("Form was invalidated!")
            return render_template("signup_base.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = BaseSignUpForm()
        return render_template("signup_base.html", form=form)


# Signup - Verify email page
@app.route("/signup/verify_email", methods=["GET", "POST"])
def signup_verify_email():
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_email(mail, "Your Verification Code", "itastefully@gmail.com", [session.get("create_customer").get("email")], body=f"Your verification code is {otp}")

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        # Update otp in create_customer in session
        session["create_customer"]["otp"] = otp

        return redirect("/signup/verify_email")

    # Handle POST request
    if request.method == "POST":
        form = OTPForm(request.form)
        if form.validate():
            # Check correct otp
            if form.otp.data != session.get("create_customer").get("otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return render_template("signup_otp.html", form=form)

            return redirect("/signup/set_password")
        else:
            return render_template("signup_otp.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = OTPForm()
        return render_template("signup_otp.html", form=form)


# Signup - Set password page
@app.route("/signup/set_password", methods=["GET", "POST"])
def signup_set_password():
    # Handle POST request
    if request.method == "POST":
        form = PasswordForm(request.form)
        if form.validate():
            # Check whether passwords match
            if form.password.data != form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("signup_password.html", form=form)

            # Hash password
            password = form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Store ALL customer data in shelve db
            create_customer(session.get("create_customer"), hashed_password)

            # Display successful account creation msg
            flash("Account created, login now!", "success")

            # Clear create_customer in session
            session.pop("create_customer", None)

            return redirect("/login")
        else:
            return render_template("signup_password.html", form=form)

    # Handle GET request
    if request.method == "GET":
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
