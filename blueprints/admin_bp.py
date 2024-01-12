from flask import current_app, Blueprint, render_template, request, redirect, session, flash
import hashlib
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2, CreateAdminForm, UpdateAdminForm
from functions import generate_otp, send_email
from admin_acc_functions import create_admin, retrieve_admin_details, retrieve_all_admins, update_admin_details, delete_admin

admin_bp = Blueprint("admin", __name__)


# Home page (Admin)
@admin_bp.route("/admin/<string:id>")
def admin_home(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@admin_bp.route("/admin/<string:id>/customer_database")
def customer_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/customer_database.html", id=id)


# Recipe Database page (Admin)
@admin_bp.route("/admin/<string:id>/recipe_database")
def recipe_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@admin_bp.route("/admin/<string:id>/menu_database")
def menu_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@admin_bp.route("/admin/<string:id>/articles_database")
def articles_database(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@admin_bp.route("/admin/<string:id>/customer_feedback")
def customer_feedback(id):
    print(f"short_id = {id}, data = {session.get('admin')}")
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Customer)
@admin_bp.route("/admin/<string:id>/edit_profile", methods=["GET", "POST"])
def edit_admin_profile(id):
    # session.pop("new_data", None)
    # session.pop("new_email_otp", None)

    print("session keys = " + str(session.keys()) + ", admin data = " + str(session.get("admin")) + ", new data = " + str(session.get("new_data", {})))

    # Clear new_data in session, redirect to reset password if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session.pop("new_data", None)
        return redirect(f"/admin/{id}/edit_profile/reset_password")

    # Render appropriate templates based on request methods
    if request.method == "POST":
        form = AccountDetailsForm(request.form)

        print(request.form.get("button"))
        print("admin in session = " + str(session["admin"]))

        if request.form.get("button") == "revert":
            # Clear possible session data
            session.pop("new_data", None)
            session.pop("new_email_otp", None)

            # Force reload by using redirect to clear all previously made changes
            return redirect(f"/admin/{id}/edit_profile")

        if form.validate():
            if request.form.get("button") == "save":
                admin_data = session.get("admin")

                # Store new data in temporary new data in session for when redirecting to verify email page
                session["new_data"] = {}

                # Store first name in session
                if form.first_name.data != admin_data.get("first_name"):
                    session["new_data"]["first_name"] = form.first_name.data

                # Store last name in session
                if form.last_name.data != admin_data.get("last_name"):
                    session["new_data"]["last_name"] = form.last_name.data

                # Store display name in session
                if form.display_name.data != admin_data.get("display_name"):
                    session["new_data"]["display_name"] = form.display_name.data

                # Redirect to another route when email changes
                if form.email.data != admin_data.get("email"):
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

                    return redirect(f"/admin/{id}/edit_profile/verify_new_email")
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

                    return redirect(f"/admin/{id}/edit_profile")
        else:
            print("Form data is invalidated")
            return render_template("admin/edit_profile.html", id=id, form=form)

    # Clear "new_data" in session if no actual new data is needed to be saved
    if "new_data" in session and session.get("new_data", None) == {}:
        session.pop("new_data", None)
        return redirect(f"/admin/{id}/edit_profile")

    # Save new data to db when redirected from verify_new_email
    if "new_data" in session and session.get("new_data", None) != {}:
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

        # Display admin account details from new_data in session, else from admin in session
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


# Edit Profile page - Verify Email Popup (Customer)
@admin_bp.route("/admin/<string:id>/edit_profile/verify_new_email", methods=["GET", "POST"])
def verify_new_email(id):
    print("admin data = " + str(session.get("admin")))
    print("session keys = " + str(session.keys()))

    # Retrieve admin account details from new_data in session, else from admin in session (Include profile image later)
    first_name =  session.get("admin").get("first_name")
    last_name = session.get("admin").get("last_name")
    display_name = session.get("admin").get("display_name")
    email = session.get("admin").get("email")

    if "new_data" in session:
        if "first_name" in session.get("new_data"):
            first_name = session.get("new_data").get("first_name")
        if "last_name" in session.get("new_data"):
            last_name = session.get("new_data").get("last_name")
        if "display_name" in session.get("new_data"):
            display_name = session.get("new_data").get("display_name")
        if "email" in session.get("new_data"):
            email = session.get("new_data").get("email")
    
    # Pass admin details as tuple then manually display each of them as though they are form fields & labels
    admin_details = (first_name, last_name, display_name, email)

    # Clear new_email_otp in session, clear email in new_data in session if user closed the popup
    if request.form.get("button") == "close":
        session.pop("new_email_otp", None)
        if "new_data" in session:
            session.get("new_data").pop("email")

        return redirect(f"/admin/{id}/edit_profile")
    
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

        return redirect(f"/admin/{id}/edit_profile/verify_new_email")

    if request.method == "POST":
        otp_form = OTPForm2(request.form)

        if otp_form.validate():
            # Check correct otp
            if otp_form.otp.data != session.get("new_email_otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return redirect(f"/admin/{id}/edit_profile/verify_new_email")
            else:
                # Display email verified msg
                flash("Email Verified!")

                # Clear new_email_otp in session
                session.pop("new_email_otp")

                return redirect(f"/admin/{id}/edit_profile")
        else:
            return render_template("admin/edit_profile_otp.html", admin_details=admin_details, otp_form=otp_form)

    if request.method == "GET":
        otp_form = OTPForm2()
        return render_template("admin/edit_profile_otp.html", id=id, admin_details=admin_details, otp_form=otp_form)


# Edit Profile page - Reset Password popup (Customer)
@admin_bp.route("/admin/<string:id>/edit_profile/reset_password", methods=["GET", "POST"])
def reset_password(id):
    print("session keys = " + str(session.keys()))
    print("admin data = " + str(session.get("admin")))

    # Retrieve admin account details from admin in session
    first_name =  session.get("admin").get("first_name")
    last_name = session.get("admin").get("last_name")
    display_name = session.get("admin").get("display_name")
    email = session.get("admin").get("email")

    # Pass admin details as tuple then manually display each of them as though they are form fields & labels
    admin_details = (first_name, last_name, display_name, email)

    # Redirect user to edit_admin_profile if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(f"/admin/{id}/edit_profile")

    # Handle POST request
    if request.method == "POST":
        password_form = ResetPasswordForm2(request.form)

        if password_form.validate():
            # Hash password
            password = password_form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Check whether password is the same as existing password for admin
            if session.get("admin").get("password") == hashed_password:
                flash("Cannot set new password to be the same as current password", "error")
                return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)

            # Check whether passwords match
            if password_form.password.data != password_form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)

            # Update user password data in shelve db, Update admin in session
            user_id = session.get("admin").get("user_id")
            update_admin_details(user_id, password=hashed_password)

            # Display successful password reset msg
            flash("Password has been reset!", "success")

            return redirect(f"/admin/{id}/edit_profile")
        else:
            print("Form invalidated!")
            return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)

    # Handle GET request
    if request.method == "GET":
        password_form = ResetPasswordForm2()
        return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)


# Additional admin pages
# Create Admin page
@admin_bp.route("/05010999", methods=["GET", "POST"])
@admin_bp.route("/05010999/create", methods=["GET", "POST"])
def create_admin_account():
    # Handle POST request
    if request.method == "POST":
        form = CreateAdminForm(request.form)
        
        if form.validate():
            # Check whether passwords match
            if form.password.data != form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("admin/create_admin.html", form=form)

            # Hash password
            password = form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Store ALL admin data in shelve db
            create_admin(form.first_name.data, form.last_name.data, form.username.data, form.email.data, hashed_password)

            # Store admin created in session
            session["admin_created"] = form.username.data

            return redirect("/05010999/retrieve")
        else:
            print("Form was invalidated!")
            return render_template("/admin/create_admin.html", form=form)

    # Handle GET request
    if request.method == "GET":
        form = CreateAdminForm()
        return render_template("admin/create_admin.html", form=form)


# Retrieve Admin page
@admin_bp.route("/05010999/retrieve")
def retrieve_admin():
    admins_list = retrieve_all_admins()

    return render_template("admin/retrieve_admin.html", count=len(admins_list), admins_list=admins_list)


# Update Admin page
@admin_bp.route("/05010999/update/<string:id>", methods=["GET", "POST"])
def update_admin(id):
    # Redirect to reset password 2 if user clicked 'reset your password here'
    if request.args.get("reset_password"):
        return redirect(f"/05010999/reset_password/{id}")

    # Handle POST request
    if request.method == "POST":
        form = UpdateAdminForm(request.form)

        if request.form.get("button") == "revert":
            # Force reload by using redirect to clear all previously made changes
            return redirect(f"/05010999/update/{id}")

        if form.validate():
            if request.form.get("button") == "save":
                # Update admin data in db
                update_admin_details(
                    id,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    display_name=form.display_name.data,
                    email=form.email.data
                )

                # Store admin updated in session
                session["admin_updated"] = form.display_name.data
                print("admin updated = " + str(session.get("admin_updated")))

                return redirect("/05010999/retrieve")
        else:
            print("Form was invalidated!")
            return render_template("admin/update_admin.html", form=form, id=id)

    # Handle GET request
    if request.method == "GET":
        form = UpdateAdminForm()

        # Retrieve and display admin details (except passwords)
        admin_data = retrieve_admin_details(id)

        form.first_name.data = admin_data.get("first_name")
        form.last_name.data = admin_data.get("last_name")
        form.display_name.data = admin_data.get("display_name")
        form.email.data = admin_data.get("email")

        return render_template("admin/update_admin.html", form=form, id=id)


@admin_bp.route("/05010999/reset_password/<string:id>", methods=["GET", "POST"])
def reset_password2(id):
    # Retrieve admin account details from admin in db
    admin_object = retrieve_admin_details(id)

    first_name = admin_object.get("first_name")
    last_name = admin_object.get("last_name")
    display_name = admin_object.get("display_name")
    email = admin_object.get("email")

    # Pass admin details as tuple then manually display each of them as though they are form fields & labels
    admin_details = (first_name, last_name, display_name, email)

    # Redirect user to retrieve admin if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(f"/05010999/update/{id}")

    # Handle POST request
    if request.method == "POST":
        password_form = ResetPasswordForm2(request.form)

        if password_form.validate():
            # Hash password
            password = password_form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Check whether password is the same as existing password for admin
            if admin_object.get("password") == hashed_password:
                flash("Cannot set new password to be the same as current password", "error")
                return render_template("admin/reset_password.html", id=id, admin_details=admin_details, password_form=password_form)

            # Check whether passwords match
            if password_form.password.data != password_form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("admin/reset_password.html", id=id, admin_details=admin_details, password_form=password_form)

            # Update user password data in shelve db, Update admin in session
            update_admin_details(id, password=hashed_password)

            # Display successful password reset msg
            flash("Password has been resetted!", "success")

            return redirect(f"/05010999/retrieve")
        else:
            print("Form invalidated!")
            return render_template("admin/reset_password.html", id=id, admin_details=admin_details, password_form=password_form)        

    # Handle GET request
    if request.method == "GET":
        password_form = ResetPasswordForm2()
        return render_template("admin/reset_password.html", id=id, admin_details=admin_details, password_form=password_form)


# Delete Admin page
@admin_bp.route("/05010999/delete/<string:id>", methods=["POST"])
def delete_admin_account(id):
    # Delete admin data in db
    user_data = delete_admin(user_id=id)

    session["admin_deleted"] = user_data.get_display_name()

    return redirect("/05010999/retrieve")
