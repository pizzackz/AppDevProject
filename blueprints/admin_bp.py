from flask import current_app, Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2, CreateAdminForm, UpdateAdminForm, SearchCustomerForm, FileForm, AccountDetailsForm2, LockCustomerAccountForm, CreateRecipeForm, createArticle, createMenu, updateMenu
from functions import generate_otp, send_email, is_unique_data, is_allowed_file, delete_file
from admin_acc_functions import create_admin, retrieve_admin_details, retrieve_all_admins, update_admin_details, delete_admin
from cust_acc_functions import retrieve_all_customers, retrieve_cust_details, update_cust_details, delete_customer
from product_functions import create_new_product, retrieve_all_products, retrieve_product_item, update_product_item, delete_product_item
from feedback_functions import retrieve_cust_feedback_dict, delete_cust_feedback
import shelve
from functools import wraps

# Modules for Recipe
from recipe import *

# Modules for Articles
from article import *

# Modules for Menu
from menu import *
from menuForm import *

admin_bp = Blueprint("admin", __name__)


# Decorator function to check admin login status
def admin_login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not (session.get("admin") and session.get("admin").get("user_id")):
            flash('Please log in as admin to access the page.', 'error')
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return decorated_function


# Home page (Admin)
@admin_bp.route("/<string:id>/admin")
@admin_login_required
def admin_home(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/home.html", id=id)


# Customer Database page (Admin)
@admin_bp.route("/<string:id>/admin/customer_database", methods=["GET", "POST"])
@admin_login_required
def customer_database(id):
    form = SearchCustomerForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Retrieve all customer data
        customers_list = retrieve_all_customers()
        wanted_cust_list = []

        # Check whether have customers
        if not customers_list:
            flash("Currently no customers' data stored", "info")
            print("no customers stored")
            return render_template("admin/cust_db_base.html", id=id, form=form)

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
            return render_template("admin/cust_db_base.html", id=id, form=form)

        return render_template("admin/cust_db_customers.html", id=id, form=form, count=len(wanted_cust_list), cust_list=wanted_cust_list)

    # Handle GET request
    return render_template("admin/cust_db_base.html", id=id, form=form)


# Customer Database page - Table of Customers (Admin)
@admin_bp.route("/<string:id>/admin/customer_database/retrieve_customer", methods=["GET", "POST"])
@admin_login_required
def retrieve_customer(id):
    cust_id = request.args.get("cust_id")
    cust_data = retrieve_cust_details(cust_id)
    print(cust_data)

    # Reset locked details when clicked on 'unlock' button
    if request.form.get("button") == "unlock_button":
        # Send email about unlocking account
        recipient = cust_data.get("email")
        with current_app.app_context():
            mail = current_app.extensions.get("mail")
            send_email(
                mail,
                "Account Unlocked",
                "itastefully@gmail.com",
                [recipient],
                body=f"Your account has been unlocked! Please feel free to login to your account anytime!"
            )

        # Update customer details, Display unlocked account message
        update_cust_details(cust_id, is_locked=False, locked_reason="", unlock_request=False, delete_request=False)
        flash(f"{cust_data.get('username')}'s account has been unlocked!", "success")

        return redirect(url_for("admin.retrieve_customer", id=id, cust_id=cust_id))

    # Redirect to lock_account when clicked on 'lock' button
    if request.form.get("button") == "lock_button":
        return redirect(url_for("admin.lock_customer_account", id=id, cust_id=cust_id))

    # Redirect to delete_customer_account when clicked on 'delete' button
    if request.form.get("button") == "delete_button":
        return redirect(url_for("admin.delete_customer_account", id=id, cust_id=cust_id))
    
    # Redirect to view_customer_feedback when clicked on 'show feedback' button
    if request.form.get("button") == "show_feedback_button":
        return redirect(url_for("admin.view_customer_feedback", id=id, cust_id=cust_id))

    # Handle getting all retrieved customer data
    form = AccountDetailsForm2(request.form)
    # Display customer account details from cust_data
    form.first_name.data = cust_data.get("first_name")
    form.last_name.data = cust_data.get("last_name")
    form.display_name.data = cust_data.get("display_name")
    form.email.data = cust_data.get("email")

    return render_template("admin/cust_db_cust_profile.html", id=id, form=form, cust_details=cust_data)


# Customer Database page - Lock Account Popup (Admin)
@admin_bp.route("/<string:id>/admin/customer_database/lock_customer", methods=["GET", "POST"])
@admin_login_required
def lock_customer_account(id):
    form = LockCustomerAccountForm(request.form)
    cust_id = request.args.get("cust_id")
    cust_data = retrieve_cust_details(cust_id)

    # Redirect to retrieve_customer when clicked on close/ cancel button
    if request.form.get("button") in ("close", "cancel"):
        return redirect(url_for("admin.retrieve_customer", id=id, cust_id=cust_id))

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Send email about locked reason
        recipient = cust_data.get("email")
        with current_app.app_context():
            mail = current_app.extensions.get("mail")
            send_email(
                mail,
                "Reason for Locking Your Account",
                "itastefully@gmail.com",
                [recipient],
                body=f"Your account has been locked because: {form.reason.data}"
            )

        # Update locked reason for customer
        update_cust_details(cust_id, is_locked=True, locked_reason=form.reason.data)

        # Display email sent message
        flash(f"Reason for locking {cust_data.get('username')}'s account has been sent!", "success")

        return redirect(url_for("admin.retrieve_customer", id=id, cust_id=cust_id))

    # Handle GET request
    return render_template("admin/cust_db_lock_account.html", id=id, cust_id=cust_id, form=form, cust_details=cust_data)


# Customer Database page - View Feedback (Admin)
@admin_bp.route("/<string:id>/admin/customer_database/feedback", methods=["GET", "POST"])
@admin_login_required
def view_customer_feedback(id):
    cust_id = request.args.get("cust_id")

    # Redirect to retrieve_customer when clicked on 'back to customer details
    if request.form.get("button") == "back":
        return redirect(url_for("admin.retrieve_customer", id=id, cust_id=cust_id))

    cust_data = retrieve_cust_details(cust_id)
    display_name = cust_data.get("display_name")
    feedback_data = retrieve_cust_feedback_dict(cust_id)
    count = 0 if not feedback_data else len(feedback_data)

    # Handle GET request
    return render_template("admin/cust_db_feedback.html", id=id, cust_id=cust_id, display_name=display_name, count=count, feedback_details=feedback_data)


# Customer Database page - Delete Account Popup (Admin)
@admin_bp.route("/<string:id>/admin/customer_database/delete_customer", methods=["GET", "POST"])
@admin_login_required
def delete_customer_account(id):
    cust_id = request.args.get("cust_id")
    cust_data = retrieve_cust_details(cust_id)

    # Redirect to retrieve_customer when clicked on close/ cancel button
    if request.form.get("button") in ("close", "cancel"):
        return redirect(url_for("admin.retrieve_customer", id=id, cust_id=cust_id))

    # Handle deleting of account
    if request.form.get("button") == "delete":
        # Send email about deleting account
        recipient = cust_data.get("email")
        with current_app.app_context():
            mail = current_app.extensions.get("mail")
            send_email(
                mail,
                "Account Deleted",
                "itastefully@gmail.com",
                [recipient],
                body=f"Your account has been deleted! We hope to see you again soon!"
            )

        # Delete customer account, Display deleted account message
        delete_customer(cust_id)
        flash(f"{cust_data.get('username')}'s account has been deleted!", "success")

        return redirect(url_for("admin.customer_database", id=id))

    return render_template("admin/cust_db_delete_account.html", id=id, cust_id=cust_id, cust_details=cust_data)


# Customer Database page - Delete Feedback (Admin)
@admin_bp.route("/<string:id>/admin/customer_database/delete_feedback", methods=["POST"])
@admin_login_required
def delete_customer_feedback(id):
    cust_id = request.args.get("cust_id")
    feedback_id = request.args.get("feedback_id")

    # Delete customer feedback, Display deleted feedback message
    delete_cust_feedback(cust_id, feedback_id)
    flash(f"Feedback has been deleted!", "success")

    return redirect(url_for("admin.view_customer_feedback", id=id, cust_id=cust_id))


# Customer Feedback page (Admin)
@admin_bp.route("/<string:id>/admin/customer_feedback")
@admin_login_required
def customer_feedback(id):
    print(f"data = {session.get('admin')}")
    return render_template("admin/customer_feedback.html", id=id)


# Edit Profile page (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile", methods=["GET", "POST"])
@admin_login_required
def edit_admin_profile(id):
    print(
        "session keys = " + str(session.keys())
        + ", admin data = " + str(session.get("admin"))
        + ", new data = " + str(session.get("new_data", {}))
    )

    # Clear new_data in session, redirect to reset password if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session.pop("new_data", None)
        return redirect(url_for("admin.reset_password", id=id))

    # Redirect to 'edit_profile_picture' if clicked on "edit profile picture"
    if request.form.get("button") == "edit_profile_pic":
        # Clear possible session data
        session.pop("new_data", None)
        session.pop("new_email_otp", None)
        return redirect(url_for("admin.edit_profile_picture", id=id))

    if request.form.get("button") == "revert":
        # Clear possible session data
        session.pop("new_data", None)
        session.pop("new_email_otp", None)
        flash("Changes made are cleared!", "success")
        return redirect(url_for("admin.edit_admin_profile", id=id))

    # Render appropriate templates based on request methods
    form = AccountDetailsForm(request.form)

    if request.method == "POST" and form.validate():
        if request.form.get("button") == "save":
            admin_data = session.get("admin")
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
                    send_email(
                        mail,
                        "Your Verification Code",
                        "itastefully@gmail.com",
                        [form.email.data],
                        body=f"Your verification code is {otp}",
                    )
                flash("An OTP has been sent to your email!", "info")

                # Store otp in session, email in new_data in session
                session["new_email_otp"] = otp
                session["new_data"]["email"] = form.email.data

                return redirect(url_for("admin.verify_new_email", id=id))

            # Immediately save the changed data when no changes to email
            new_data = session.get("new_data")
            user_id = session.get("admin").get("user_id")

            # Update admin data
            update_admin_details(
                user_id=user_id,
                first_name=new_data.get("first_name", None),
                last_name=new_data.get("last_name", None),
                display_name=new_data.get("display_name", None),
            )
            flash("Details saved!", "success")

            # Update admin in session, Clear new_data in session
            session["admin"] = retrieve_admin_details(user_id)
            session.pop("new_data")

            return redirect(url_for("admin.edit_admin_profile", id=id))

    # Clear "new_data" in session if no actual new data is needed to be saved
    if "new_data" in session and session.get("new_data", None) == {}:
        session.pop("new_data", None)
        return redirect(url_for("admin.edit_admin_profile", id=id))

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
            email=new_data.get("email", None),
        )

        # Flash details saved msg
        flash("Details saved!", "success")

        # Update admin in session, Clear new_data in session
        session["admin"] = retrieve_admin_details(user_id)
        session.pop("new_data", None)

    # Handle GET request
    if request.method == "GET":
        # Display admin account details from new_data in session, else from admin in session
        form.first_name.data = session.get("admin").get("first_name")
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
@admin_login_required
def verify_new_email(id):
    print("admin data = " + str(session.get("admin")))
    print("session keys = " + str(session.keys()))

    # Retrieve admin account details from new_data in session, else from admin in session (Include profile image later)
    first_name = session.get("admin").get("first_name")
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

        return redirect(url_for("admin.edit_admin_profile", id=id))

    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send OTP
        with current_app.app_context():
            mail = current_app.extensions.get("mail")

            otp = generate_otp(6)
            send_email(
                mail,
                "Your Verification Code",
                "itastefully@gmail.com",
                [session.get("new_data").get("email")],
                body=f"Your verification code is {otp}",
            )

        # Store otp in session
        session["new_email_otp"] = otp

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        return redirect(url_for("admin.verify_new_email", id=id))

    otp_form = OTPForm2(request.form)

    # Handle POST request
    if request.method == "POST" and otp_form.validate():
        # Check correct otp
        if otp_form.otp.data != session.get("new_email_otp"):
            # Display invalid otp msg
            flash("Invalid OTP, please try again!", "error")
            return redirect(url_for("admin.verify_new_email", id=id))
        # Clear new_email_otp in session
        session.pop("new_email_otp")
        return redirect(url_for("admin.edit_admin_profile", id=id))

    # Handle GET request
    return render_template(
        "admin/edit_profile_otp.html",
        id=id,
        admin_details=admin_details,
        otp_form=otp_form,
    )


# Edit Profile page - Reset Password popup (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile/reset_password", methods=["GET", "POST"])
@admin_login_required
def reset_password(id):
    print("session keys = " + str(session.keys()))
    print("admin data = " + str(session.get("admin")))

    # Retrieve admin account details from admin in session
    first_name = session.get("admin").get("first_name")
    last_name = session.get("admin").get("last_name")
    display_name = session.get("admin").get("display_name")
    email = session.get("admin").get("email")

    # Pass admin details as tuple then manually display each of them as though they are form fields & labels
    admin_details = (first_name, last_name, display_name, email)

    # Redirect user to edit_admin_profile if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(url_for("admin.edit_admin_profile", id=id))

    password_form = ResetPasswordForm2(request.form)

    # Handle POST request
    if request.method == "POST" and password_form.validate():
        # Check whether password is the same as existing password for admin
        if check_password_hash(session.get("admin").get("password"), password_form.password.data):
            flash(
                "Cannot set new password to be the same as current password",
                "error"
            )
            return render_template(
                "admin/edit_profile_reset_pass.html",
                id=id,
                admin_details=admin_details,
                password_form=password_form
            )

        # Check whether passwords match
        if password_form.password.data != password_form.confirm_password.data:
            flash("Passwords do not match!", "error")
            return render_template(
                "admin/edit_profile_reset_pass.html",
                id=id,
                admin_details=admin_details,
                password_form=password_form,
            )

        # Update user password data in shelve db, Update admin in session
        user_id = session.get("admin").get("user_id")
        update_admin_details(user_id, password=generate_password_hash(password_form.password.data, salt_length=8))
        session["admin"] = retrieve_admin_details(user_id)

        # Display successful password reset msg
        flash("Password has been reset!", "success")

        return redirect(url_for("admin.edit_admin_profile", id=id))

    # Handle GET request
    return render_template(
        "admin/edit_profile_reset_pass.html",
        id=id,
        admin_details=admin_details,
        password_form=password_form,
    )


# Edit Profile page - Edit Profile Picture poup (Admin)
@admin_bp.route("/<string:id>/admin/edit_profile_picture", methods=["GET", "POST"])
@admin_login_required
def edit_profile_picture(id):
    print("session keys = " + str(session.keys()))
    print("admin data = " + str(session.get("admin")))

    # Retrieve admin account details from admin in session
    first_name = session.get("admin").get("first_name")
    last_name = session.get("admin").get("last_name")
    display_name = session.get("admin").get("display_name")
    email = session.get("admin").get("email")

    # Pass admin details as tuple then manually display each of them as though they are form fields & labels
    admin_details = (first_name, last_name, display_name, email)

    # Redirect user to edit_admin_profile if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(url_for("admin.edit_admin_profile", id=id))

    form = FileForm(request.form)

    # Handle POST request
    if request.method == "POST":
        # Retrieve file object, retrieve user data
        file_item = request.files["file"]
        user_data = session.get("admin")

        # Reset profile image to default when clicked on 'remove'
        if request.form.get("button") == "remove":
            filename = user_data.get("profile_pic")

            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file(
                "admin",
                "profile_pictures",
                f"{id}",
                current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"],
            )

            # Flash no profile picture set message
            if not existing_file_path:
                flash("Please set a profile picture first before removing it!", "error")
                return render_template(
                    "admin/edit_profile_picture.html",
                    id=id,
                    admin_details=admin_details,
                    form=form,
                )

            # Set 'default' to user's profile_picture, Update admin in session
            user_id = user_data.get("user_id")
            update_admin_details(user_id, profile_pic_name="default")
            session["admin"] = retrieve_admin_details(user_id)

            # Display removed profile image msg
            flash("Profile picture successfully removed!", "success")

            return redirect(url_for("admin.edit_admin_profile", id=id))

        # Save profile image when clicked on 'change'
        # Check whether file allowed
        if is_allowed_file(file_item):
            # Retrieve new file item
            filename = secure_filename(f"{id}.{file_item.filename.rsplit('.', 1)[1]}")

            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file(
                "admin",
                "profile_pictures",
                f"{id}",
                current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"],
            )

            # Save image in local storage
            file_item.save(
                os.path.join("static", "uploads", "admin", "profile_pictures", filename)
            )

            # Update user profile picture in shelve db, Update admin in session
            user_id = session.get("admin").get("user_id")
            update_admin_details(user_id, profile_pic_name=filename)
            session["admin"] = retrieve_admin_details(user_id)

            # Display successful profile picture saved msg
            flash("Your profile picture has been saved!", "success")

            return redirect(url_for("admin.edit_admin_profile", id=id))

        # Handle invalid file submission
        flash(
            f"You can only upload files with extension that are in the following list: {current_app.config['ALLOWED_IMAGE_FILE_EXTENSIONS']}",
            "error",
        )
        print("Invalid file submitted!")

    # Handle GET request
    return render_template(
        "admin/edit_profile_picture.html",
        id=id,
        admin_details=admin_details,
        form=form,
    )


# Admin Database Pages
# Create Admin page
@admin_bp.route("/05010999", methods=["GET", "POST"])
@admin_bp.route("/05010999/create", methods=["GET", "POST"])
def create_admin_account():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    form = CreateAdminForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Check whether passwords match
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match!", "error")
            return render_template("admin/create_admin.html", form=form)

        # Store ALL admin data in shelve db
        create_admin(
            form.first_name.data,
            form.last_name.data,
            form.username.data,
            form.email.data,
            form.password.data,
        )

        # Display account created message
        flash(f"Admin {form.username.data} was created!", "success")
        return redirect(url_for("admin.retrieve_admin"))

    # Handle GET request
    return render_template("admin/create_admin.html", form=form)


# Retrieve Admin page
@admin_bp.route("/05010999/retrieve")
def retrieve_admin():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    admins_list = retrieve_all_admins()

    return render_template(
        "admin/retrieve_admin.html", count=len(admins_list), admins_list=admins_list
    )


# Update Admin page
@admin_bp.route("/05010999/update", methods=["GET", "POST"])
def update_admin():
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    id = request.args.get("id")

    # Redirect to reset password 2 if user clicked 'reset your password here'
    if request.args.get("reset_password"):
        return redirect(url_for("admin.reset_password2", id=id))

    # Force reload by using redirect to clear all previously made changes
    if request.form.get("button") == "revert":
        return redirect(url_for("admin.update_admin", id=id))

    form = UpdateAdminForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        if request.form.get("button") == "save":
            user_data = retrieve_admin_details(user_id=id)

            # Check whether email changed
            if form.email.data != user_data.get("email"):
                # Check whether email is unique
                if not is_unique_data(email=form.email.data):
                    # Display invalid email message
                    flash("Please use another Email")

                    return render_template(url_for("admin.update_admin", id=id))

            # When email either not changed or (email changed & validated)
            # Update admin data in db
            update_admin_details(
                id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                display_name=form.display_name.data,
                email=form.email.data,
            )

            # Display account updated message
            username = user_data.get("username")
            flash(f"Admin {username} was updated!", "success")

            return redirect(url_for("admin.retrieve_admin"))
        else:
            return redirect(url_for("admin.update_admin", id=id))

    # Handle GET request
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
        return redirect(url_for("admin.update_admin", id=id))

    password_form = ResetPasswordForm2(request.form)

    # Handle POST request
    if request.method == "POST" and password_form.validate():
        # Check whether password is the same as existing password for admin
        if check_password_hash(admin_object.get("password"), password_form.password.data):
            flash(
                "Cannot set new password to be the same as current password",
                "error",
            )
            return render_template(
                "admin/reset_password.html",
                id=id,
                admin_details=admin_details,
                password_form=password_form,
            )

        # Check whether passwords match
        if password_form.password.data != password_form.confirm_password.data:
            flash("Passwords do not match!", "error")
            return render_template(
                "admin/reset_password.html",
                id=id,
                admin_details=admin_details,
                password_form=password_form,
            )

        # Update user password data in shelve db, Update admin in session
        update_admin_details(id, password=generate_password_hash(password_form.password.data, salt_length=8))

        # Display password reset msg
        flash("Password has been reset!", "success")
        return redirect(url_for("admin.retrieve_admin"))

    # Handle GET request
    return render_template(
        "admin/reset_password.html",
        id=id,
        admin_details=admin_details,
        password_form=password_form,
    )


# Delete Admin page
@admin_bp.route("/05010999/delete/<string:id>", methods=["POST"])
def delete_admin_account(id):
    # Clear all unrelated session data
    for key in ("customer", "admin"):
        session.pop(key, None)

    # Delete current local stored image file if have existing file saved
    delete_file(
        "admin",
        "profile_pictures",
        f"{id[0:11]}",
        current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"],
    )

    # Delete admin data in db
    user_object = delete_admin(user_id=id)
    username = user_object.get_username()

    flash(f"Admin {username} was deleted!", "error")

    return redirect(url_for("admin.retrieve_admin"))


# Recipe Pages
@admin_bp.route('/<string:id>/admin/recipe_database', methods=['GET', 'POST'])
@admin_login_required
def recipe_database(id):
    db = shelve.open('recipes.db', 'c')

    try:
        recipe_dict = db['recipes']
    except:
        print('Error in retrieving recipes')
        recipe_dict = {}

    recipes = []
    for key in recipe_dict:
        recipe = recipe_dict.get(key)
        recipes.append(recipe)
        # For debugging
        print(recipe.get_name(), recipe.get_id())

    print(recipes)
    if request.method == 'POST':
        ingredients = request.form.get('ingredient')
        ingredients = ingredients.split(',')
        print(ingredients)
        recipe2 = []
        for i in range(0, len(ingredients)):
            for s in range(0, len(recipes)):
                name = (recipes[s]).get_name()
                name = name.lower()
                if ingredients[i] in (recipes[s]).get_ingredients() or ingredients[i] in name:
                    if recipes[s] not in recipe2:
                        recipe2.append(recipes[s])

        db.close()
        return render_template('admin/recipe_database.html', recipes=recipe2, id=id)

    db.close()
    return render_template('admin/recipe_database.html', recipes=recipes, id=id)


@admin_bp.route('/<string:id>/admin/create_recipe', methods=['GET', 'POST'])
@admin_login_required
def create_recipe(id):
    create_recipe_form = CreateRecipeForm(request.form)
    if request.method == 'POST':
        db = shelve.open('recipes.db', 'c')
        recipe_dict = db.setdefault('recipes', {})  # Initialize if 'recipes' doesn't exist
        recipe_dict = db['recipes']

        name = create_recipe_form.name.data
        picture = request.files['picture']
        print(picture.filename)

        picture_filename = picture.filename
        picture_filename = picture_filename.split('.')
        print(picture_filename[1])

        if picture_filename[1] != 'jpg' and picture_filename[1] != 'png':
            return render_template('admin/create_recipe.html', alert_error='Images are only allowed',
                                   form=create_recipe_form, id=id)

        picture_filename = name + '.' + picture_filename[1]
        picture.save(os.path.join('static/images_recipe', picture_filename))

        name = create_recipe_form.name.data

        ingredients = create_recipe_form.ingredients.data
        ingredients = ingredients.split(',')
        print(ingredients)
        if ingredients == ['']:
            return render_template('admin/create_recipe.html', alert_error='Please add ingredients.',
                                   form=create_recipe_form, id=id)

        new_recipe = Recipe(create_recipe_form.name.data, ingredients, create_recipe_form.instructions.data,
                            picture_filename)

        print(new_recipe.get_instructions())

        for key in recipe_dict:
            recipe = recipe_dict.get(key)
            if name == recipe.get_name():
                return render_template('admin/create_recipe.html', alert_error='Recipe exists in Database.',
                                       form=create_recipe_form, id=id)

        recipe_dict[new_recipe.get_id()] = new_recipe
        db['recipes'] = recipe_dict

        db.close()

        flash(f'{name} has been created', 'success')

        return redirect(url_for('admin.recipe_database', id=id))

    return render_template('admin/create_recipe.html', form=create_recipe_form, id=id)


@admin_bp.route('/<string:id>/admin/view_recipe/<recipe_id>', methods=['GET', 'POST'])
@admin_login_required
def view_recipe(recipe_id, id):
    print(recipe_id)
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db['recipes']
    recipe = recipe_dict.get(recipe_id)
    print(recipe.get_instructions())
    db.close()
    return render_template('admin/view_recipe.html', recipe=recipe, id=id)


@admin_bp.route('/<string:id>/admin/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_recipe(recipe_id, id):
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db['recipes']
    recipe = recipe_dict.get(recipe_id)

    update_recipe_form = CreateRecipeForm(request.form)

    if request.method == 'POST':
        name = update_recipe_form.name.data
        ingredients = update_recipe_form.ingredients.data
        ingredients = ingredients.split(',')
        instructions = update_recipe_form.instructions.data
        picture = request.files['picture']

        if picture.filename != '':
            old_picture = recipe.get_picture()
            if old_picture:
                os.remove(os.path.join('static/images_recipe', old_picture))
            recipe.set_picture(picture.filename)
            picture.save(os.path.join('static/images_recipe', picture.filename))

        if name != '':
            recipe.set_name(name)
        if ingredients != []:
            recipe.set_ingredients(ingredients)
        if instructions != '':
            recipe.set_instructions(instructions)

        db['recipes'] = recipe_dict
        db.close()

        flash(f'{recipe.get_name()} has been updated', 'info')

        return redirect(url_for('admin.recipe_database', id=id))

    update_recipe_form.name.data = recipe.get_name()
    print(recipe.get_name())
    update_recipe_form.instructions.data = recipe.get_instructions()

    ingredients = recipe.get_ingredients()

    return render_template('admin/update_recipe.html', form=update_recipe_form, ingredients=ingredients, id=id)


@admin_bp.route('/<string:id>/admin/delete_recipe/<recipe_id>')
@admin_login_required
def delete_recipe(recipe_id, id):
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db['recipes']

    recipe = recipe_dict.get(recipe_id)
    old_picture = recipe.get_picture()
    if old_picture:
        os.remove(os.path.join('static/images_recipe', old_picture))

    name = recipe.get_name()

    recipe_dict.pop(recipe_id)
    db['recipes'] = recipe_dict
    db.close()

    flash(f'{name} has been deleted', 'info')

    return redirect(url_for('admin.recipe_database', id=id))


# Menu Database page (Admin)
@admin_bp.route("/<string:id>/admin/menu_database")
@admin_login_required
def menu(id):
    product_dict = retrieve_all_products()
    product_list = []

    for product in product_dict.values():
        product_list.append(product)

    return render_template('admin/admin_menu.html', id=id, product_list=product_list)


@admin_bp.route('/<string:id>/admin/create_menu', methods=['GET', 'POST'])
@admin_login_required
def create_menu(id):
    create_menu = createMenu(request.form)
    if request.method == 'POST' and create_menu.validate():
        menu_dict = retrieve_all_products()

        name_to_check = create_menu.name.data
        if any(menu_item.get_name() == name_to_check for menu_item in menu_dict.values()):
            flash('Duplicate item', 'error')
            return redirect(url_for('admin.menu', id=id))

        picture = request.files['image']
        picture_filename = secure_filename(picture.filename)
        if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
            flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
            print("file is not allowed")
            return render_template('admin/createMenu.html', form=create_menu)
        file_path = os.path.join('static', 'menu_image', picture_filename)
        picture.save(file_path)

        create_new_product(create_menu.name.data, create_menu.description.data, create_menu.price.data, create_menu.quantity.data, picture_filename)

        return redirect(url_for('admin.menu', id=id))
    return render_template('admin/createMenu.html', id=id, form=create_menu)


@admin_bp.route('/<string:id>/admin/view_menu')
@admin_login_required
def view_menu(id):
    product_id = request.args.get("menu_id")
    menu_item = retrieve_product_item(product_id)

    return render_template('admin/viewMenu.html', menu_id=product_id, menu_item=menu_item, id=id)


@admin_bp.route('/<string:id>/admin/update_menu', methods=['GET', 'POST'])
@admin_login_required
def update_menu(id):
    update_menu = createMenu(request.form)
    menu_id = request.args.get("menu_id")

    if request.method == 'POST' and update_menu.validate():
        update_product_item(
            menu_id,
            name=update_menu.name.data,
            description=update_menu.description.data,
            qty=update_menu.quantity.data,
            set_new_qty=True
        )

        picture = request.files['image']

        if picture.filename != '':
            old_picture_path = os.path.join('static', 'menu_image', menu_item.get_product_img())
            if os.path.exists(old_picture_path):
                # Remove the old image file only if it exists
                os.remove(old_picture_path)

            # Save the new image file
            picture_filename = secure_filename(picture.filename)
            if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
                flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
                print("file is not allowed")
                return render_template('admin/updateMenu.html', menu_id=menu_id, form=update_menu, id=id)
            picture_path = os.path.join('static', 'menu_image', picture_filename)
            picture.save(picture_path)
            
            update_product_item(menu_id, image=picture_filename)

        return redirect(url_for('admin.menu', id=id))

    menu_item = retrieve_product_item(menu_id)

    update_menu.name.data = menu_item.get_name()
    update_menu.description.data = menu_item.get_desc()
    update_menu.price.data = menu_item.get_price()
    update_menu.quantity.data = menu_item.get_qty()
    update_menu.image.data = menu_item.get_product_img()

    return render_template('admin/updateMenu.html', menu_id=menu_id, form=update_menu, id=id)


@admin_bp.route('/<string:id>/admin/delete_menu/')
@admin_login_required
def delete_menu(id):
    menu_id = request.args.get("menu_id")
    menu = retrieve_product_item(menu_id)

    old_picture = menu.get_product_img()
    if old_picture:
        os.remove(os.path.join('static', 'menu_image', old_picture))

    delete_product_item(menu_id)

    return redirect(url_for('admin.menu', id=id))


# Articles
@admin_bp.route('/<string:id>/admin/create_article', methods=['GET', 'POST'])
@admin_login_required
def create_article(id):
    create_article = createArticle(request.form)
    admin_data = retrieve_admin_details(id)
    if request.method == 'POST' and create_article.validate():
        article_dict = {}
        db = shelve.open('article.db', 'c')
        try:
            article_dict = db['article_item']
        except:
            print("Error in retrieving Article from user.db.")

        picture = request.files['image']
        picture_filename = secure_filename(picture.filename)
        if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
            flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
            print("file is not allowed")
            return render_template('admin/create_article.html', form=create_article, id=id)

        file_path = os.path.join('static', 'images_articles', picture_filename)
        picture.save(file_path)

        article = article_item(picture_filename, create_article.title.data, create_article.category.data, create_article.description.data, admin_data.get("display_name"))
        print(article.get_id())
        article_dict[article.get_id()] = article
        print("save image = " + str(picture_filename))

        db['article_item'] = article_dict
        db.close()

        return redirect(url_for('admin.article', id=id))
    return render_template('admin/create_article.html', form=create_article, id=id)


@admin_bp.route('/<string:id>/admin/view_article/<article_id>')
@admin_login_required
def view_article(article_id, id):
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article_item = article_dict.get(article_id)

    db['article_item'] = article_dict
    db.close()

    return render_template('admin/view_article.html', article_item=article_item, id=id)


@admin_bp.route('/<string:id>/admin/article')
@admin_login_required
def article(id):
    db = shelve.open('article.db', 'c')
    try:
        article_dict = db['article_item']
    except:
        print("Error in retrieving Article from article.db.")
        article_dict = {}
    print(article_dict)
    articles = []
    for article in article_dict.values():
        articles.append(article)
    print(articles)
    db.close()

    return render_template('admin/admin_articles.html', form=createArticle, articles=articles, id=id)


@admin_bp.route('/<string:id>/admin/update_article/<article_id>', methods=['GET', 'POST'])
@admin_login_required
def update_article(article_id, id):
    update_article = createArticle(request.form)
    if request.method == 'POST' and update_article.validate():
        db = shelve.open('article.db', 'c')
        article_dict = db['article_item']
        article_item = article_dict.get(article_id)
        article_item.set_title(update_article.title.data)
        article_item.set_category(update_article.category.data)
        article_item.set_description(update_article.description.data)
        picture = request.files.get("image")

        picture_filename = secure_filename(picture.filename)
        if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
            flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
            print("file is not allowed")
            return render_template('admin/update_article.html', form=update_article, id=id)
        file_path = os.path.join('static', 'images_articles', picture_filename)
        picture.save(file_path)

        article_item.set_image(picture_filename)
        article_dict[article_item.get_id()] = article_item

        if picture.filename != '':
            old_picture_path = os.path.join('static', 'images_articles', article_item.get_image())
            if os.path.exists(old_picture_path):
                os.remove(old_picture_path)

            # Save the new image file
            picture_path = os.path.join('static', 'images_articles', picture_filename)
            picture.save(picture_path)
            article_item.set_image(picture_filename)  # Update the image attribute

        db['article_item'] = article_dict
        db.close()
        return redirect(url_for('admin.article', id=id))
    
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article_item = article_dict.get(article_id)
    db.close()

    update_article.title.data = article_item.get_title()
    update_article.category.data = article_item.get_category()
    update_article.description.data = article_item.get_description()
    update_article.image.data = article_item.get_image()

    return render_template('admin/update_article.html', form=update_article, id=id)


@admin_bp.route('/<string:id>/admin/delete_article/<article_id>')
@admin_login_required
def delete_article(article_id, id):
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article = article_dict.get(article_id)
    old_picture = article.get_image()
    if old_picture:
        os.remove(os.path.join('static', 'images_articles', old_picture))

    article_dict.pop(article_id)
    db['article_item'] = article_dict
    db.close()

    return redirect(url_for('admin.article', id=id))


@admin_bp.route('/<string:id>/admin/customer_articles')
@admin_login_required
def customer_articles(id):
    db = shelve.open('article.db', 'c')
    try:
        article_dict = db['article_item']
    except:
        print("Error in retrieving Article from article.db.")
        article_dict = {}
    print(article_dict)
    articles = []
    for article in article_dict.values():
        articles.append(article)
    print(articles)
    db.close()

    return render_template('customer/guest_articles.html', articles=articles, id=id)


