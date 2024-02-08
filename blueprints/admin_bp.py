from flask import current_app, Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename
import hashlib
import os
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2, CreateAdminForm, UpdateAdminForm, SearchCustomerForm, FileForm
from functions import generate_otp, send_email, get_user_object, is_unique_data, is_allowed_file, delete_file
from admin_acc_functions import create_admin, retrieve_admin_details, retrieve_all_admins, update_admin_details, delete_admin
from cust_acc_functions import retrieve_all_customers, retrieve_cust_details
import shelve

# Modules for Recipe
from form_recipe import *
from recipe import *

# Modules for Articles
from article_form import *
from article import *

# Modules for Menu
from menu import *

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


# Recipe Pages

@admin_bp.route('/<string:id>/admin/recipe_database', methods=['GET', 'POST'])
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


@admin_bp.route('/create_recipe', methods=['GET', 'POST'])
def create_recipe():
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
                                   form=create_recipe_form)

        picture_filename = name + '.' + picture_filename[1]
        picture.save(os.path.join('static/images_recipe', picture_filename))

        name = create_recipe_form.name.data

        ingredients = create_recipe_form.ingredients.data
        ingredients = ingredients.split(',')
        print(ingredients)
        if ingredients == ['']:
            return render_template('admin/create_recipe.html', alert_error='Please add ingredients.',
                                   form=create_recipe_form)

        new_recipe = Recipe(create_recipe_form.name.data, ingredients, create_recipe_form.instructions.data,
                            picture_filename)

        print(new_recipe.get_instructions())

        for key in recipe_dict:
            recipe = recipe_dict.get(key)
            if name == recipe.get_name():
                return render_template('admin/create_recipe.html', alert_error='Recipe exists in Database.',
                                       form=create_recipe_form)

        recipe_dict[new_recipe.get_id()] = new_recipe
        db['recipes'] = recipe_dict

        db.close()

        flash(f'{name} has been created', 'success')

        return redirect(url_for('recipe_database'), id=id)

    return render_template('admin/create_recipe.html', form=create_recipe_form)


@admin_bp.route('/view_recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    print(recipe_id)
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db['recipes']
    recipe = recipe_dict.get(recipe_id)
    print(recipe.get_instructions())
    db.close()
    return render_template('admin/view_recipe.html', recipe=recipe)


@admin_bp.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
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

        return redirect(url_for('recipe_database'))

    update_recipe_form.name.data = recipe.get_name()
    print(recipe.get_name())
    update_recipe_form.instructions.data = recipe.get_instructions()

    ingredients = recipe.get_ingredients()

    return render_template('admin/update_recipe.html', form=update_recipe_form, ingredients=ingredients)


@admin_bp.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
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

    return redirect(url_for('recipe_database'))

# Menu (Jairus)
@admin_bp.route('/menu')
def menu():
    db = shelve.open('menu.db', 'c')
    try:
        menu_dict = db['Menu']
    except:
        print("Error in retrieving Menu from user.db.")
        menu_dict = {}

    menus = []
    for menu_item in menu_dict.values():
        menus.append(menu_item)
        print("new image = "+str(menu_item.get_image()))

    return render_template('admin/admin_menu.html', menus=menus)

@admin_bp.route('/create_menu', methods=['GET', 'POST'])
def create_menu():
    create_menu = createMenu(request.form)
    if request.method == 'POST' and create_menu.validate():
        menu_dict = {}
        db = shelve.open('menu.db', 'c')
        try:
            menu_dict = db['Menu']
        except:
            print("Error in retrieving Menu from user.db.")

        name_to_check = create_menu.name.data
        if any(menu_item.get_name() == name_to_check for menu_item in menu_dict.values()):
            flash('Duplicate item', 'error')
            db.close()
            return redirect(url_for('menu'))

        picture = request.files['image']
        picture_filename = secure_filename(picture.filename)
        if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
            flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
            print("file is not allowed")
            return render_template('admin/createMenu.html', form=create_menu)
        file_path = os.path.join('static', 'menu_image', picture_filename)
        picture.save(file_path)

        menu = Menu_item(create_menu.name.data, create_menu.description.data, create_menu.price.data, picture_filename)
        menu_dict[menu.get_id()] = menu
        print("save image = " + str(picture_filename))

        db['Menu'] = menu_dict
        db.close()

        return redirect(url_for('menu'))
    return render_template('admin/createMenu.html', form=create_menu)

@admin_bp.route('/delete_menu/<menu_id>')
def delete_menu(menu_id):
    db = shelve.open('menu.db', 'c')
    menu_dict = db['Menu']

    menu = menu_dict.get(menu_id)
    old_picture = menu.get_image()
    if old_picture:
        os.remove(os.path.join('static', 'menu_image', old_picture))

    menu_dict.pop(menu_id)
    db['Menu'] = menu_dict
    db.close()

    return redirect(url_for('menu'))


@admin_bp.route('/update_menu/<menu_id>', methods=['GET', 'POST'])
def update_menu(menu_id):
    update_menu = createMenu(request.form)
    if request.method == 'POST' and update_menu.validate():
        db = shelve.open('menu.db', 'c')
        menu_dict = db['Menu']
        menu_item = menu_dict.get(menu_id)
        menu_item.set_name(update_menu.name.data)
        menu_item.set_description(update_menu.description.data)
        menu_item.set_price(update_menu.price.data)
        picture = request.files['image']


        # Old image retrieval works, saving new image doesn't work
        if picture.filename != '':
            old_picture_path = os.path.join('static', 'menu_image', menu_item.get_image())
            if os.path.exists(old_picture_path):
                # Remove the old image file only if it exists
                os.remove(old_picture_path)

            # Save the new image file
            picture_filename = secure_filename(picture.filename)
            if not ("." in picture_filename and picture_filename.rsplit(".", 1)[1].lower() in ("jpg", "png", "jpeg")):
                flash("File type is not allowed. Please use jpeg, jpg or png files only!", "error")
                print("file is not allowed")
                return render_template('admin/updateMenu.html', form=update_menu)
            picture_path = os.path.join('static', 'menu_image', picture_filename)
            picture.save(picture_path)
            menu_item.set_image(picture_filename)  # Update the image attribute

            print(menu_item.get_image())

        db['Menu'] = menu_dict
        db.close()
        return redirect(url_for('menu'))
    else:
        db = shelve.open('menu.db', 'c')
        menu_dict = db['Menu']
        menu_item = menu_dict.get(menu_id)
        db.close()

        update_menu.name.data = menu_item.get_name()
        update_menu.description.data = menu_item.get_description()
        update_menu.price.data = menu_item.get_price()
        update_menu.image.data = menu_item.get_image()

        return render_template('admin/updateMenu.html', form=update_menu)


@admin_bp.route('/view_menu/<menu_id>')
def view_menu(menu_id):
    db = shelve.open('menu.db', 'c')
    menu_dict = db['Menu']
    menu_item = menu_dict.get(menu_id)

    db.close()

    return render_template('admin/viewMenu.html', menu_item=menu_item)


# Articles
@admin_bp.route('/create_article', methods=['GET', 'POST'])
def create_article():
    create_article = createArticle(request.form)
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
            return render_template('admin/article/create_article.html', form=create_article)
        file_path = os.path.join('static', 'image', picture_filename)
        picture.save(file_path)

        article = article_item(picture_filename, create_article.title.data, create_article.category.data, create_article.description.data)
        article_dict[article.get_id()] = article
        print("save image = " + str(picture_filename))

        db['article_item'] = article_dict
        db.close()

        return redirect(url_for('article'))
    return render_template('admin/article/create_article.html', form=create_article)

@admin_bp.route('/view_article/<article_id>')
def view_article(article_id):
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article_item = article_dict.get(article_id)

    db['article_item'] = article_dict
    db.close()

    return render_template('admin/article/view_article.html', article_item=article_item)

@admin_bp.route('/article')
def article():
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

    return render_template('admin/article/admin_articles.html', form=createArticle, articles=articles)

@admin_bp.route('/update_article/<article_id>', methods=['GET', 'POST'])
def update_article(article_id):
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
            return render_template('admin/article/update_article.html', form=update_article)
        file_path = os.path.join('static', 'image', picture_filename)
        picture.save(file_path)

        article_item.set_image(picture_filename)
        article_dict[article.get_id()] = article
        print("save image = " + str(picture_filename))

        if picture.filename != '':
            old_picture_path = os.path.join('static', 'image', article_item.get_image())
            if os.path.exists(old_picture_path):
                os.remove(old_picture_path)

            # Save the new image file

            picture_path = os.path.join('static', 'image', picture_filename)
            picture.save(picture_path)
            article_item.set_image(picture_filename)  # Update the image attribute

            print(article_item.get_image())

        db['article_item'] = article_dict
        db.close()
        return redirect(url_for('article'))
    else:
        db = shelve.open('article.db', 'c')
        article_dict = db['article_item']
        article_item = article_dict.get(article_id)
        db.close()

        update_article.title.data = article_item.get_title()
        update_article.category.data = article_item.get_category()
        update_article.description.data = article_item.get_description()
        update_article.image.data = article_item.get_image()

        return render_template('admin/article/update_article.html', form=update_article)

@admin_bp.route('/delete_article/<article_id>')
def delete_article(article_id):
    db=shelve.open('article.db', 'c')
    article_dict=db['article_item']
    article=article_dict.get(article_id)
    print(article)
    old_picture=article.get_image()
    if old_picture:
        os.remove(os.path.join('static', 'image', old_picture))

    article_dict.pop(article_id)
    db['article_item']=article_dict
    db.close()

    return redirect(url_for('article'))

@admin_bp.route('/customer_articles')
def customer_articles():
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

    return render_template('customer/customer_articles.html', articles=articles)