from flask import current_app, Blueprint, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
import hashlib
import os
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2, CreateAdminForm, UpdateAdminForm, SearchCustomerForm, FileForm
from functions import generate_otp, send_email, get_user_object, is_unique_data, is_allowed_file, delete_file
from admin_acc_functions import create_admin, retrieve_admin_details, retrieve_all_admins, update_admin_details, delete_admin
from cust_acc_functions import retrieve_all_customers, retrieve_cust_details

admin_bp = Blueprint("admin", __name__)


# Home page (Admin)
@admin_bp.route("/<string:id>/admin")
def admin_home(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@admin_bp.route("/<string:id>/admin/customer_database", methods=["GET", "POST"])
def customer_database(id):
    # print(f"data = {session.get('admin')}")
    # Redirect to customer_database_profile if clicked on any customer shown
    if request.args.get("username"):
        username = request.args.get("username")
        user_id = get_user_object(username=username).get_user_id()
        cust_data = retrieve_cust_details(user_id)

        # Store cust_data in session
        session["cust_data"] = cust_data

        return redirect(f"/{id}/admin/customer_database_profile")


    # Handle POST request
    if request.method == "POST":
        form = SearchCustomerForm(request.form)
        if form.validate():
            # Retrieve all customer data
            customers_list = retrieve_all_customers()
            wanted_cust_list = []

            # Check whether have customers
            if not customers_list:
                flash("Currently no customers' data stored", "info")
                print("no customers stored")
                return render_template("admin/customer_database.html", id=id , form=form)

            search_term = form.username.data.lower()

            # If customer's username contains all characters in search_term w/o caring for order, add to list
            wanted_cust_list = [
                customer
                for customer in customers_list
                if all(char in customer.get_username().lower() for char in search_term.lower())
            ]

            # Display appropriate messages
            if not wanted_cust_list:
                print("no customers found")
                flash(f"No customer account with username containing '{form.username.data}'", "error")
                return render_template("admin/customer_database.html", id=id, form=form)
            else:
                return render_template("admin/customer_database.html", id=id, form=form, cust_list=wanted_cust_list)

        else:
            print("form was not validated")
            return render_template("admin/customer_database.html", id=id, form=form)

    # Handle GET request
    if request.method == "GET":
        form = SearchCustomerForm(request.form)
        return render_template("admin/customer_database.html", id=id, form=form)


# Customer Database - Profile page (Admin)
@admin_bp.route("/<string:id>/admin/customer_database_profile", methods=["GET", "POST"])
def customer_database_profile(id):    
    # Handle POST request
    if request.method == "POST":
        pass

    # Handle GET request
    if request.method == "GET":
        print(session.get("cust_data", "Piglet"))
        return render_template("admin/cust_db_profile.html", id=id)


# Recipe Database page (Admin)
@admin_bp.route("/<string:id>/admin/recipe_database")
def recipe_database(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/recipe_database.html", id=id)


# Menu Database page (Admin)
@admin_bp.route("/<string:id>/admin/menu_database")
def menu_database(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/menu_database.html", id=id)


# Articles Database page (Admin)
@admin_bp.route("/<string:id>/admin/articles_database")
def articles_database(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/articles_database.html", id=id)


# Customer Feedback page (Admin)
@admin_bp.route("/<string:id>/admin/customer_feedback")
def customer_feedback(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile", methods=["GET", "POST"])
def edit_admin_profile(id):
    # session.pop("new_data", None)
    # session.pop("new_email_otp", None)

    print("session keys = " + str(session.keys()) + ", admin data = " + str(session.get("admin")) + ", new data = " + str(session.get("new_data", {})))

    # Clear new_data in session, redirect to reset password if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session.pop("new_data", None)
        return redirect(f"/{id}/admin/edit_profile/reset_password")

    # Render appropriate templates based on request methods
    if request.method == "POST":
        form = AccountDetailsForm(request.form)

        print(request.form.get("button"))
        print("admin in session = " + str(session["admin"]))

        # Redirect to 'edit_profile_picture' if clicked on "edit profile picture"
        if request.form.get("button") == "edit_profile_pic":
            # Clear possible session data
            session.pop("new_data", None)
            session.pop("new_email_otp", None)
            print("ran")

            return redirect(f"/{id}/admin/edit_profile_picture")

        if request.form.get("button") == "revert":
            # Clear possible session data
            session.pop("new_data", None)
            session.pop("new_email_otp", None)

            flash("Changes made are cleared!", "success")

            # Force reload by using redirect to clear all previously made changes
            return redirect(f"/{id}/admin/edit_profile")

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

                    return redirect(f"/{id}/admin/edit_profile/verify_new_email")
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

                    return redirect(f"/{id}/admin/edit_profile")
        else:
            print("Form data is invalidated")
            return render_template("admin/edit_profile.html", id=id, form=form)

    # Clear "new_data" in session if no actual new data is needed to be saved
    if "new_data" in session and session.get("new_data", None) == {}:
        session.pop("new_data", None)
        return redirect(f"/{id}/admin/edit_profile")

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


# Edit Profile page - Verify Email Popup (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile/verify_new_email", methods=["GET", "POST"])
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

        return redirect(f"/{id}/admin/edit_profile")
    
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

        return redirect(f"/{id}/admin/edit_profile/verify_new_email")

    if request.method == "POST":
        otp_form = OTPForm2(request.form)

        if otp_form.validate():
            # Check correct otp
            if otp_form.otp.data != session.get("new_email_otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return redirect(f"/{id}/admin/edit_profile/verify_new_email")
            else:
                # Clear new_email_otp in session
                session.pop("new_email_otp")

                return redirect(f"/{id}/admin/edit_profile")
        else:
            return render_template("admin/edit_profile_otp.html", admin_details=admin_details, otp_form=otp_form)

    if request.method == "GET":
        otp_form = OTPForm2()
        return render_template("admin/edit_profile_otp.html", id=id, admin_details=admin_details, otp_form=otp_form)


# Edit Profile page - Reset Password popup (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile/reset_password", methods=["GET", "POST"])
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
        return redirect(f"/{id}/admin/edit_profile")

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
            session["admin"] = retrieve_admin_details(user_id)

            # Display successful password reset msg
            flash("Password has been reset!", "success")

            return redirect(f"/{id}/admin/edit_profile")
        else:
            print("Form invalidated!")
            return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)

    # Handle GET request
    if request.method == "GET":
        password_form = ResetPasswordForm2()
        return render_template("admin/edit_profile_reset_pass.html", id=id, admin_details=admin_details, password_form=password_form)


# Edit Profile page - Edit Profile Picture poup (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile_picture", methods=["GET", "POST"])
def edit_profile_picture(id):
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
        return redirect(f"/{id}/admin/edit_profile")

    # Handle POST request
    if request.method == "POST":
        form = FileForm(request.form)

        # Retrieve file object, retrieve user data
        file_item = request.files["file"]
        user_data = session.get("admin")

        # Reset profile image to default when clicked on 'remove'
        if request.form.get("button") == "remove":
            filename = user_data.get("profile_pic")

            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file("admin", "profile_pictures", f"{id}", current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"])

            # Flash no profile picture set message
            if not existing_file_path:
                flash("Please set a profile picture first before removing it!", "error")
                return render_template("admin/edit_profile_picture.html", id=id, admin_details=admin_details, form=form)

            # Set 'default' to user's profile_picture, Update admin in session
            user_id = user_data.get("user_id")
            update_admin_details(user_id, profile_pic_name="default")
            session["admin"] = retrieve_admin_details(user_id)

            # Display removed profile image msg
            flash("Profile picture successfully removed!", "success")

            return redirect(f"/{id}/admin/edit_profile")

        # Save profile image when clicked on 'change'
        # Check whether file allowed
        if is_allowed_file(file_item):
            # Retrieve new file item
            filename = secure_filename(f"{id}.{file_item.filename.rsplit('.', 1)[1]}")

            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file("admin", "profile_pictures", f"{id}", current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"])

            # Save image in local storage
            file_item.save(os.path.join("static", "uploads", "admin", "profile_pictures", filename))

            # Update user profile picture in shelve db, Update admin in session
            user_id = session.get("admin").get("user_id")
            update_admin_details(user_id, profile_pic_name=filename)
            session["admin"] = retrieve_admin_details(user_id)

            # Display successful profile picture saved msg
            flash("Your profile picture has been saved!", "success")

            return redirect(f"/{id}/admin/edit_profile")
        else:
            flash(f"You can only upload files with extension that are in the following list: {current_app.config['ALLOWED_IMAGE_FILE_EXTENSIONS']}", "error")
            print("Invalid file submitted!")
            return render_template("admin/edit_profile_picture.html", id=id, admin_details=admin_details, form=form)

    # Handle GET request
    if request.method == "GET":
        form = FileForm()
        return render_template("admin/edit_profile_picture.html", id=id, admin_details=admin_details, form=form)

# Additional admin pages
# Create Admin page
@admin_bp.route("/05010999", methods=["GET", "POST"])
@admin_bp.route("/05010999/create", methods=["GET", "POST"])
def create_admin_account():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    # Handle POST request
    if request.method == "POST":
        form = CreateAdminForm(request.form)
        
        if form.validate():
            # Check whether passwords match
            if form.password.data != form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("admin/create_admin.html", form=form)

            # Store ALL admin data in shelve db
            create_admin(form.first_name.data, form.last_name.data, form.username.data, form.email.data, form.password.data)

            # Display account created message
            flash(f"Admin {form.username.data} was created!", "success")

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
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    admins_list = retrieve_all_admins()

    return render_template("admin/retrieve_admin.html", count=len(admins_list), admins_list=admins_list)


# Update Admin page
@admin_bp.route("/05010999/update", methods=["GET", "POST"])
def update_admin():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    id = request.args.get("id")

    # Redirect to reset password 2 if user clicked 'reset your password here'
    if request.args.get("reset_password"):
        return redirect(f"/05010999/reset_password?id={id}")

    # Handle POST request
    if request.method == "POST":
        form = UpdateAdminForm(request.form)

        if request.form.get("button") == "revert":
            # Force reload by using redirect to clear all previously made changes
            return redirect(f"/05010999/update?id={id}")

        if form.validate():
            if request.form.get("button") == "save":
                user_data = retrieve_admin_details(user_id=id)

                # Check whether email changed
                if form.email.data != user_data.get("email"):
                    # Check whether email is unique
                    if not is_unique_data(email=form.email.data):
                        # Display invalid email message
                        flash("Please use another Email")

                        return render_template(f"/05010999/update?id={id}")

                # When email either not changed or (email changed & validated)
                # Update admin data in db
                update_admin_details(
                    id,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    display_name=form.display_name.data,
                    email=form.email.data
                )

                # Display account updated message
                username = user_data.get("username")
                flash(f"Admin {username} was updated!", "success")

                return redirect("/05010999/retrieve")
            else:
                return redirect()
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


# Update Admin page - Reset Password Popup
@admin_bp.route("/05010999/reset_password", methods=["GET", "POST"])
def reset_password2():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    id = request.args.get("id")

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
        return redirect(f"/05010999/update?id={id}")

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

            # Display password reset msg
            flash("Password has been reset!", "success")

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
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)
    
    # Delete current local stored image file if have existing file saved
    delete_file("admin", "profile_pictures", f"{id[0:11]}", current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"])

    # Delete admin data in db
    user_object = delete_admin(user_id=id)
    username = user_object.get_username()

    flash(f"Admin {username} was deleted!", "error")

    return redirect("/05010999/retrieve")

