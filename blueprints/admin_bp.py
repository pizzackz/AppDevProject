from flask import current_app, Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2
from functions import generate_otp, send_email
from admin_acc_functions import update_admin_details, retrieve_admin_details

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
@admin_bp.route("/<string:id>/edit_admin_profile", methods=["GET", "POST"])
def edit_admin_profile(id):
    # session.pop("new_data", None)
    # session.pop("new_email_otp", None)

    print("admin data = " + str(session.get("admin")))
    print("new data = " + str(session.get("new_data", {})))

    # Clear new_data in session, redirect to reset password if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session.pop("new_data", None)
        return redirect(url_for("admin.reset_password", id=id))

    # Render appropriate templates based on request methods
    if request.method == "POST":
        form = AccountDetailsForm(request.form)

        print(request.form.get("button"))
        print("admin in session = " + str(session["admin"]))

        if form.validate():
            if request.form.get("button") == "save":
                cust_data = session.get("admin")

                # Store new data in temporary new data in session for when redirecting to verify email page
                session["new_data"] = {}

                # Store first name
                if form.first_name.data != cust_data.get("first_name"):
                    session["new_data"]["first_name"] = form.first_name.data

                # Store last name
                if form.last_name.data != cust_data.get("last_name"):
                    session["new_data"]["last_name"] = form.last_name.data

                # Store display name
                if form.display_name.data != cust_data.get("display_name"):
                    session["new_data"]["display_name"] = form.display_name.data

                # Redirect to another route when email changes
                if form.email.data != cust_data.get("email"):
                    # Generate and send OTP
                    with current_app.app_context():
                        mail = current_app.extensions.get("mail")

                        otp = generate_otp(6)
                        send_email(mail, "Your Verification Code", "itastefully@gmail.com", [form.email.data], body=f"Your verification code is {otp}")

                    # Display otp sent msg
                    flash("An OTP has been sent to your email!", "info")

                    # Store otp in session, email in new_data in session
                    session["new_email_otp"] = otp
                    session["new_data"]["email"] = form.email.data

                    return redirect(url_for("admin.verify_new_email", id=id))
                # Immediately save the changed data when no changes to email
                else:
                    print("saving new data")
                    new_data = session.get("new_data")
                    user_id = session.get("admin").get("user_id")

                    # Update admin data
                    update_admin_details(
                        user_id=user_id,
                        first_name=new_data.get("first_name", None),
                        last_name=new_data.get("last_name", None),
                        display_name=new_data.get("display_name", None)
                        )

                    # Flash details saved msg
                    flash("Details saved!", "success")

                    # Update admin in session, Clear new_data in session
                    session["admin"] = retrieve_admin_details(user_id)
                    session.pop("new_data")

                    print("new admin in session = " + str(session.get("admin")))

                    return redirect((url_for("admin.edit_cust_profile", id=id)))
            elif request.form.get("button") == "revert":
                # Clear possible session data
                session.pop("new_data", None)
                session.pop("new_email_otp", None)

                # Force reload by using redirect to clear all previously made changes
                return redirect(url_for("admin.edit_cust_profile", id=id))
            elif request.form.get("button") == "edit_profile_pic":
                print("Edit profile picture!")

                return redirect(url_for("admin.edit_cust_profile", id=id))
        else:
            print("Form data is invalidated")
            return render_template("admin/edit_profile.html", id=id, form=form)

    # Save new data to db when redirected from verify_new_email
    if "new_data" in session:
        print("saving new data 2")
        new_data = session.get("new_data")
        user_id = session.get("admin").get("user_id")

        # Update admin data
        update_admin_details(
            user_id=user_id,
            first_name=new_data.get("first_name", None),
            last_name=new_data.get("last_name", None),
            display_name=new_data.get("display_name", None),
            email=new_data.get("email", None)
            )

        # Flash details saved msg
        flash("Details saved!", "success")

        # Update admin in session, Clear new_data in session
        session["admin"] = retrieve_admin_details(user_id)
        session.pop("new_data", None)

    if request.method == "GET":
        form = AccountDetailsForm()

        # Display admin account details from new_data in session, else from admin in session (Include profile image later)
        form.first_name.data =  session.get("admin").get("first_name")
        form.last_name.data = session.get("admin").get("last_name")
        form.display_name.data = session.get("admin").get("display_name")
        form.email.data = session.get("admin").get("email")

        if "new_data" in session:
            if "first_name" in session.get("new_data"):
                form.first_name.data = session.get("new_data").get("first_name")
            if "last_name" in session.get("new_data"):
                form.last_name.data = session.get("new_data").get("last_name")
            if "display_name" in session.get("new_data"):
                form.display_name.data = session.get("new_data").get("display_name")
            if "email" in session.get("new_data"):
                form.email.data = session.get("new_data").get("email")

        return render_template("admin/edit_profile.html", id=id, form=form)


# Edit Profile page - Verify Email Popup (Admin)
@admin_bp.route("/<string:id>/edit_admin_profile/verify_email", methods=["GET", "POST"])
def verify_new_email(id):
    print("admin data = " + str(session.get("admin")))

    # Clear new_email_otp in session, clear email in new_data in session if user clicked on close symbol
    if request.form.get("button") == "close_otp":
        session.pop("new_email_otp", None)
        if "new_data" in session:
            session.get("new_data").pop("email")

        return redirect(url_for("admin.edit_cust_profile", id=id))
    
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send OTP
        with current_app.app_context():
            mail = current_app.extensions.get("mail")

            otp = generate_otp(6)
            send_email(mail, "Your Verification Code", "itastefully@gmail.com", [session.get("new_data").get("email")], body=f"Your verification code is {otp}")

        # Store otp in session
        session["new_email_otp"] = otp

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        return redirect(url_for("admin.verify_new_email", id=id))

    if request.method == "POST":
        otp_form = OTPForm2(request.form)
        form = AccountDetailsForm(request.form)

        if otp_form.validate():
            # Check correct otp
            if otp_form.otp.data != session.get("new_email_otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return redirect(url_for("admin.verify_new_email", id=id))
            else:
                # Display email verified msg
                flash("Email Verified!")

                # Clear new_email_otp in session
                session.pop("new_email_otp")

                return redirect(url_for("admin.edit_cust_profile", id=id))
        else:
            return render_template("admin/edit_profile_otp.html", form=form, otp_form=otp_form)

    if request.method == "GET":
        form = AccountDetailsForm()
        otp_form = OTPForm2()

        # Display admin account details from new_data in session, else from admin in session (Include profile image later)
        form.first_name.data =  session.get("admin").get("first_name")
        form.last_name.data = session.get("admin").get("last_name")
        form.display_name.data = session.get("admin").get("display_name")
        form.email.data = session.get("admin").get("email")

        if "new_data" in session:
            if "first_name" in session.get("new_data"):
                form.first_name.data = session.get("new_data").get("first_name")
            if "last_name" in session.get("new_data"):
                form.last_name.data = session.get("new_data").get("last_name")
            if "display_name" in session.get("new_data"):
                form.display_name.data = session.get("new_data").get("display_name")
            if "email" in session.get("new_data"):
                form.email.data = session.get("new_data").get("email")

        return render_template("admin/edit_profile_otp.html", id=id, form=form, otp_form=otp_form)


# Edit Profile page - Reset Password popup (admin)
@admin_bp.route("/<string:id>/edit_admin_profile/reset_password", methods=["GET", "POST"])
def reset_password(id):
    print("session keys = " + str(session.keys()))
    print("admin data = " + str(session.get("admin")))

    # Redirect user to edit_admin_profile if user clicked on close symbol
    if request.form.get("button") == "close_popup":
        return redirect(url_for("admin.edit_cust_profile", id=id))

    if request.method == "POST":
        password_form = ResetPasswordForm2(request.form)
        form = AccountDetailsForm(request.form)

        if password_form.validate():
            # Hash password
            password = password_form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Check whether password is the same as existing password for admin
            if session.get("admin").get("password") == hashed_password:
                flash("Cannot set new password to be the same as current password", "error")
                return render_template("admin/edit_profile_reset_pass.html", form=form, password_form=password_form)

            # Check whether passwords match
            if password_form.password.data != password_form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("admin/edit_profile_reset_pass.html", form=form, password_form=password_form)

            # Update user password data in shelve db, Update admin in session
            user_id = session.get("admin").get("user_id")
            update_admin_details(user_id, password=hashed_password)

            # Display successful password reset msg
            flash("Password has been resetted!", "success")

            return redirect(url_for("admin.edit_cust_profile", id=id))
        else:
            print("Form invalidated!")
            return render_template("admin/edit_profile_reset_pass.html", id=id, form=form, password_form=password_form)

    if request.method == "GET":
        password_form = ResetPasswordForm2()
        form = AccountDetailsForm()

        # Display admin account details from admin in session (Include profile image later)
        form.first_name.data =  session.get("admin").get("first_name")
        form.last_name.data = session.get("admin").get("last_name")
        form.display_name.data = session.get("admin").get("display_name")
        form.email.data = session.get("admin").get("email")

        return render_template("admin/edit_profile_reset_pass.html", id=id, form=form, password_form=password_form)
