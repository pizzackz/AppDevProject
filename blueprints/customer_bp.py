from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import shelve
from Forms import AccountDetailsForm, ChangeEmailForm, OTPForm, ResetPasswordForm2


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
    # session.clear()

    action = session.get("action", "display_data")
    
    print("action = " + action + ", session keys = " + str(session.keys()))

    # Update action in session if customer clicked 'Change email...'
    if request.args.get("change_email"):
        session["action"] = "change_email"
        return redirect((url_for("customer.edit_cust_profile", id=id)))
    
    # Update action in session if customer clicked 'Reset your password...'
    if request.args.get("reset_password"):
        session["action"] = "reset_password"
        return redirect(url_for("customer.edit_cust_profile", id=id))

    # Render appropriate templates based on request methods
    if request.method == "POST":
        if action == "display_data":
            form = AccountDetailsForm(request.form)

            print(request.form.get("button"))
            print("customer in session = " + str(session["customer"]))

            if form.validate():
                if request.form.get("button") == "save":
                    # Handle saving of data into db
                    # Check whether data differ from current session data
                    cust_data = session.get("customer")
                    has_change = False

                    # Update db with newly changed data
                    db = shelve.open("user_accounts.db", "c")
                    customers_dict = db["Customers"]
                    user_id = cust_data.get("user_id")
                    customer = customers_dict.get(user_id)

                    # Update first name
                    if form.first_name.data != cust_data.get("first_name"):
                        print("first name changed to " + form.first_name.data)
                        customer.set_first_name(form.first_name.data)
                        has_change = True

                    # Update last name
                    if form.last_name.data != cust_data.get("last_name"):
                        print("last name changed to " + form.last_name.data)
                        customer.set_last_name(form.last_name.data)
                        has_change = True

                    # Update display name
                    if form.display_name.data != cust_data.get("display_name"):
                        print("display name changed to " + form.display_name.data)
                        customer.set_display_name(form.display_name.data)
                        has_change = True

                    db["Customers"] = customers_dict
                    db.close()

                    # Flash details saved msg
                    if has_change:
                        flash("Details saved!", "success")

                    # Update customer in session
                    session["customer"] = customer.get_cust_data()

                    print("new customer details in session = " + str(session["customer"]))

                elif request.form.get("button") == "revert":
                    # Force reload by using redirect to clear all previously made changes
                    return redirect(url_for("customer.edit_cust_profile", id=id))

                elif request.form.get("button") == "edit_profile_pic":
                    print("Edit profile picture!")

                return redirect(url_for("customer.edit_cust_profile", id=id))
            else:
                print("Form data is invalidated")
                return render_template("customer/edit_profile.html", id=id, form=form)
        
        elif action == "change_email":
            pass
        elif action == "verify_email":
            pass
        elif action == "reset_password":
            pass


    if request.method == "GET":
        form = AccountDetailsForm()

        # Display customer account details from customer in session (Include profile image later)
        form.first_name.data = session.get("customer").get("first_name")
        form.last_name.data = session.get("customer").get("last_name")
        form.display_name.data = session.get("customer").get("display_name")
        form.email.data = session.get("customer").get("email")

        # Display appropriate template based on action in session
        if action == "display_data":
            return render_template("customer/edit_profile.html", id=id, form=form)
        elif action == "change_email":
            pass
        elif action == "verify_email":
            pass
        elif action == "reset_password":
            pass


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