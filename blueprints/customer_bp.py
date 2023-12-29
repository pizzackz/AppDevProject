from flask import current_app, Blueprint, render_template, request, redirect, url_for, session, flash
import shelve
from Forms import AccountDetailsForm, OTPForm2, ResetPasswordForm2
from functions import generate_otp, send_email
from cust_acc_functions import retrieve_cust_details, update_cust_details

customer_bp = Blueprint("customer", __name__)

# Home page (Customer)
@customer_bp.route("/<string:id>/home")
def customer_home(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/home.html", id=id)


# Order page (Customer)
@customer_bp.route("/<string:id>/order")
def order(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/order.html", id=id)


# Recipe Creator page (Customer)
@customer_bp.route("/<string:id>/recipe_creator")
def recipe_creator(id):
    print(f"short_id = {id}, data = {session.get('customer')}")
    return render_template("customer/recipe_creator.html", id=id)


# Edit Profile page (Customer)
@customer_bp.route("/<string:id>/edit_customer_profile", methods=["GET", "POST"])
def edit_cust_profile(id):
    # session.pop("new_data", None)
    # session.pop("new_email_otp", None)

    print("customer data = " + str(session.get("customer")))
    print("new data = " + str(session.get("new_data", {})))

    # Render appropriate templates based on request methods
    if request.method == "POST":
        form = AccountDetailsForm(request.form)

        print(request.form.get("button"))
        print("customer in session = " + str(session["customer"]))

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

                    return redirect(url_for("customer.verify_new_email", id=id))
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

                    return redirect((url_for("customer.edit_cust_profile", id=id)))
            elif request.form.get("button") == "revert":
                # Clear possible session data
                session.pop("new_data", None)
                session.pop("new_email_otp", None)

                # Force reload by using redirect to clear all previously made changes
                return redirect(url_for("customer.edit_cust_profile", id=id))
            elif request.form.get("button") == "edit_profile_pic":
                print("Edit profile picture!")

                return redirect(url_for("customer.edit_cust_profile", id=id))
        else:
            print("Form data is invalidated")
            return render_template("customer/edit_profile.html", id=id, form=form)

    # Save new data to db when redirected from verify_new_email
    if "new_data" in session:
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

        # Display customer account details from new_data in session, else from customer in session (Include profile image later)
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
@customer_bp.route("/<string:id>/edit_customer_profile/verify_email", methods=["GET", "POST"])
def verify_new_email(id):

    print("session keys = " + str(session.keys()))

    # Clear new_email_otp in session, clear email in new_data in session if user clicked on close symbol
    if request.form.get("button") == "close_otp":
        session.pop("new_email_otp", None)
        if "new_data" in session:
            session.get("new_data").pop("email")

        return redirect(url_for("customer.edit_cust_profile", id=id))
    
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

        return redirect(url_for("customer.verify_new_email", id=id))

    if request.method == "POST":
        otp_form = OTPForm2(request.form)
        form = AccountDetailsForm(request.form)

        if otp_form.validate():
            # Check correct otp
            if otp_form.otp.data != session.get("new_email_otp"):
                # Display invalid otp msg
                flash("Invalid OTP, please try again!", "error")
                return redirect(url_for("customer.verify_new_email", id=id))
            else:
                # Display email verified msg
                flash("Email Verified!")

                # Clear new_email_otp in session
                session.pop("new_email_otp")

                return redirect(url_for("customer.edit_cust_profile", id=id))
        else:
            return render_template("customer/edit_profile_otp.html", form=form, otp_form=otp_form)

    if request.method == "GET":
        form = AccountDetailsForm()
        otp_form = OTPForm2()

        # Display customer account details from new_data in session, else from customer in session (Include profile image later)
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

        return render_template("customer/edit_profile_otp.html", id=id, form=form, otp_form=otp_form)


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