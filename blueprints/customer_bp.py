from flask import current_app, Blueprint, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
import hashlib
import os
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2, FileForm
from functions import generate_otp, send_email, is_allowed_file, delete_file
from cust_acc_functions import retrieve_cust_details, update_cust_details

customer_bp = Blueprint("customer", __name__)

# Home page (Customer)
@customer_bp.route("/<string:id>/home")
def customer_home(id):
    # Clear temp cust data in session
    session.pop("temp_cust_data", None)

    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/home.html", id=id)


# Order page (Customer)
@customer_bp.route("/<string:id>/order")
def order(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/order.html", id=id)

# Edit Profile page (Customer)
@customer_bp.route("/<string:id>/edit_profile", methods=["GET", "POST"])
def edit_cust_profile(id):
    # session.pop("new_data", None)
    # session.pop("new_email_otp", None)

    print("session keys = " + str(session.keys()))
    print("customer data = " + str(session.get("customer")))
    print("new data = " + str(session.get("new_data", {})))

    # Clear new_data in session, redirect to reset password if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        session.pop("new_data", None)
        return redirect(f"/{id}/edit_profile/reset_password")

    # Render appropriate templates based on request methods
    if request.method == "POST":
        form = AccountDetailsForm(request.form)

        print(request.form.get("button"))
        print("customer in session = " + str(session["customer"]))

        # Redirect to 'edit_profile_picture' if clicked on "edit profile picture"
        if request.form.get("button") == "edit_profile_pic":
            # Clear possible session data
            session.pop("new_data", None)
            session.pop("new_email_otp", None)
            print("ran")

            return redirect(f"/{id}/edit_profile_picture")

        if form.validate():
            if request.form.get("button") == "save":
                cust_data = session.get("customer")

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

                    return redirect(f"/{id}/edit_profile/verify_new_email")
                # Immediately save the changed data when no changes to email
                else:
                    print("saving new data")
                    new_data = session.get("new_data")
                    user_id = session.get("customer").get("user_id")

                    # Update customer data
                    update_cust_details(
                        user_id=user_id,
                        first_name=new_data.get("first_name", None),
                        last_name=new_data.get("last_name", None),
                        display_name=new_data.get("display_name", None)
                        )

                    # Flash details saved msg
                    flash("Details saved!", "success")

                    # Update customer in session, Clear new_data in session
                    session["customer"] = retrieve_cust_details(user_id)
                    session.pop("new_data")

                    print("new customer in session = " + str(session.get("customer")))

                    return redirect(f"/{id}/edit_profile")
            elif request.form.get("button") == "revert":
                # Clear possible session data
                session.pop("new_data", None)
                session.pop("new_email_otp", None)

                flash("Changes made are cleared!", "success")

                # Force reload by using redirect to clear all previously made changes
                return redirect(f"/{id}/edit_profile")
        else:
            print("Form data is invalidated")
            return render_template("customer/edit_profile.html", id=id, form=form)

    # Clear "new_data" in sessionn if no actual new data is needed to be saved
    if "new_data" in session and session.get("new_data", None) == {}:
        session.pop("new_data", None)
        return redirect(f"/{id}/edit_profile")

    # Save new data to db when redirected from verify_new_email
    if "new_data" in session and session.get("new_data", None) != {}:
        print("saving new data 2")
        new_data = session.get("new_data")
        user_id = session.get("customer").get("user_id")

        # Update customer data
        update_cust_details(
            user_id=user_id,
            first_name=new_data.get("first_name", None),
            last_name=new_data.get("last_name", None),
            display_name=new_data.get("display_name", None),
            email=new_data.get("email", None)
            )

        # Flash details saved msg
        flash("Details saved!", "success")

        # Update customer in session, Clear new_data in session
        session["customer"] = retrieve_cust_details(user_id)
        session.pop("new_data", None)

    if request.method == "GET":
        form = AccountDetailsForm()

        # Display customer account details from new_data in session, else from customer in session
        form.first_name.data =  session.get("customer").get("first_name")
        form.last_name.data = session.get("customer").get("last_name")
        form.display_name.data = session.get("customer").get("display_name")
        form.email.data = session.get("customer").get("email")

        if "new_data" in session:
            if "first_name" in session.get("new_data"):
                form.first_name.data = session.get("new_data").get("first_name")
            if "last_name" in session.get("new_data"):
                form.last_name.data = session.get("new_data").get("last_name")
            if "display_name" in session.get("new_data"):
                form.display_name.data = session.get("new_data").get("display_name")
            if "email" in session.get("new_data"):
                form.email.data = session.get("new_data").get("email")

        return render_template("customer/edit_profile.html", id=id, form=form)


# Edit Profile page - Verify Email Popup (Customer)
@customer_bp.route("/<string:id>/edit_profile/verify_new_email", methods=["GET", "POST"])
def verify_new_email(id):
    print("customer data = " + str(session.get("customer")))
    print("session keys = " + str(session.keys()))

    # Retrieve customer account details from new_data in session, else from customer in session (Include profile image later)
    first_name =  session.get("customer").get("first_name")
    last_name = session.get("customer").get("last_name")
    display_name = session.get("customer").get("display_name")
    email = session.get("customer").get("email")

    if "new_data" in session:
        if "first_name" in session.get("new_data"):
            first_name = session.get("new_data").get("first_name")
        if "last_name" in session.get("new_data"):
            last_name = session.get("new_data").get("last_name")
        if "display_name" in session.get("new_data"):
            display_name = session.get("new_data").get("display_name")
        if "email" in session.get("new_data"):
            email = session.get("new_data").get("email")
    
    # Pass cust details as tuple then manually display each of them as though they are form fields & labels
    cust_details = (first_name, last_name, display_name, email)

    # Clear new_email_otp in session, clear email in new_data in session if user closed the popup
    if request.form.get("button") == "close":
        session.pop("new_email_otp", None)
        if "new_data" in session:
            session.get("new_data").pop("email")

        return redirect(f"/{id}/edit_profile")
    
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

        return redirect(f"/{id}/edit_profile/verify_new_email")

    if request.method == "POST":
        otp_form = OTPForm2(request.form)

        if otp_form.validate():
            # Check correct otp
            if otp_form.otp.data != session.get("new_email_otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return redirect(f"/{id}/edit_profile/verify_new_email")
            else:
                # Clear new_email_otp in session
                session.pop("new_email_otp")

                return redirect(f"/{id}/edit_profile")
        else:
            return render_template("customer/edit_profile_otp.html", cust_details=cust_details, otp_form=otp_form)

    if request.method == "GET":
        otp_form = OTPForm2()
        return render_template("customer/edit_profile_otp.html", id=id, cust_details=cust_details, otp_form=otp_form)


# Edit Profile page - Reset Password popup (Customer)
@customer_bp.route("/<string:id>/edit_profile/reset_password", methods=["GET", "POST"])
def reset_password(id):
    print("session keys = " + str(session.keys()))
    print("customer data = " + str(session.get("customer")))

    # Retrieve customer account details from customer in session
    first_name =  session.get("customer").get("first_name")
    last_name = session.get("customer").get("last_name")
    display_name = session.get("customer").get("display_name")
    email = session.get("customer").get("email")

    # Pass cust details as tuple then manually display each of them as though they are form fields & labels
    cust_details = (first_name, last_name, display_name, email)

    # Redirect user to edit_customer_profile if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(f"/{id}/edit_profile")

    if request.method == "POST":
        password_form = ResetPasswordForm2(request.form)
        form = AccountDetailsForm(request.form)

        if password_form.validate():
            # Hash password
            password = password_form.password.data
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            print("hashed pass = " + hashed_password)
            print("existing pass = " + session.get("customer").get("password"))

            # Check whether password is the same as existing password for customer
            if session.get("customer").get("password") == hashed_password:
                flash("Cannot set new password to be the same as current password", "error")
                return render_template("customer/edit_profile_reset_pass.html", id=id, cust_details=cust_details, password_form=password_form)

            # Check whether passwords match
            if password_form.password.data != password_form.confirm_password.data:
                flash("Passwords do not match!", "error")
                return render_template("customer/edit_profile_reset_pass.html", id=id, cust_details=cust_details, password_form=password_form)

            # Update user password data in shelve db, Update customer in session
            user_id = session.get("customer").get("user_id")
            update_cust_details(user_id, password=hashed_password)
            session["customer"] = retrieve_cust_details(user_id)

            # Display successful password reset msg
            flash("Password has been reset!", "success")

            return redirect(f"/{id}/edit_profile")
        else:
            print("Form invalidated!")
            return render_template("customer/edit_profile_reset_pass.html", id=id, cust_details=cust_details, password_form=password_form)

    if request.method == "GET":
        password_form = ResetPasswordForm2()
        return render_template("customer/edit_profile_reset_pass.html", id=id, cust_details=cust_details, password_form=password_form)


# Edit Profile page - Edit Profile Picture poup (Customer)
@customer_bp.route("/<string:id>/edit_profile_picture", methods=["GET", "POST"])
def edit_profile_picture(id):
    print("session keys = " + str(session.keys()))
    print("customer data = " + str(session.get("customer")))

    # Retrieve customer account details from customer in session
    first_name =  session.get("customer").get("first_name")
    last_name = session.get("customer").get("last_name")
    display_name = session.get("customer").get("display_name")
    email = session.get("customer").get("email")

    # Pass customer details as tuple then manually display each of them as though they are form fields & labels
    cust_details = (first_name, last_name, display_name, email)

    # Redirect user to edit_customer_profile if user clicked on close symbol
    if request.form.get("button") == "close":
        return redirect(f"/{id}/edit_profile")

    # Handle POST request
    if request.method == "POST":
        form = FileForm(request.form)

        # Retrieve file object
        file_item = request.files["file"]

        # Reset profile image to default when clicked on 'remove'
        if request.form.get("button") == "remove":
            user_data = session.get("customer")

            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file("customer", "profile_pictures", f"{id}", current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"])

            # Flash no profile picture set message
            if not existing_file_path:
                flash("Please set a profile picture first before removing it!", "error")
                return render_template("customer/edit_profile_picture.html", id=id, cust_details=cust_details, form=form)

            # Set 'default' to user's profile_picture, Update customer in session
            user_id = user_data.get("user_id")
            update_cust_details(user_id, profile_pic_name="default")
            session["customer"] = retrieve_cust_details(user_id)

            # Display removed profile image msg
            flash("Profile picture successfully removed!", "success")

            return redirect(f"/{id}/edit_profile")

        # Save profile image when clicked on 'change'
        # Check whether file allowed
        if is_allowed_file(file_item):
            filename = secure_filename(f"{id}.{file_item.filename.rsplit('.', 1)[1]}")
            
            # Delete current local stored image file if have existing file saved
            existing_file_path = delete_file("customer", "profile_pictures", f"{id}", current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"])

            # Save image in local storage
            file_item.save(os.path.join("static", "uploads", "customer", "profile_pictures", filename))

            # Update user profile picture in shelve db, Update customer in session
            user_id = session.get("customer").get("user_id")
            update_cust_details(user_id, profile_pic_name=filename)
            session["customer"] = retrieve_cust_details(user_id)

            # Display successful profile picture saved msg
            flash("Your profile picture has been saved!", "success")

            return redirect(f"/{id}/edit_profile")
        else:
            flash(f"You can only upload files with extension that are in the following list: {current_app.config['ALLOWED_IMAGE_FILE_EXTENSIONS']}", "error")
            print("Invalid file submitted!")
            return render_template("customer/edit_profile_picture.html", id=id, cust_details=cust_details, form=form)

    # Handle GET request
    if request.method == "GET":
        form = FileForm()
        return render_template("customer/edit_profile_picture.html", id=id, cust_details=cust_details, form=form)


# Favourites page (Customer)
@customer_bp.route("/<string:id>/favourites")
def favourites(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/favourites.html", id=id)


# Articles page (Customer)
@customer_bp.route("/<string:id>/articles")
def customer_articles(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/articles.html", id=id)


# Current Delivery page (Customer)
@customer_bp.route("/<string:id>/current_delivery")
def current_delivery(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/current_delivery.html", id=id)


# Feedback page (Customer)
@customer_bp.route("/<string:id>/feedback")
def feedback(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/feedback.html", id=id)


# Order History page (Customer)
@customer_bp.route("/<string:id>/order_history")
def order_history(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/order_history.html", id=id)

@customer_bp.route()

