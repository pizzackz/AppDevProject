from flask import Flask, session, request, redirect, flash, url_for, render_template
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import shelve

from config import Config
from Forms import (
    BaseSignUpForm,
    OTPForm,
    PasswordForm,
    LoginForm,
    EmailForm,
    ResetPasswordForm,
)

from blueprints.guest_bp import guest_bp
from blueprints.customer_bp import customer_bp
from blueprints.admin_bp import admin_bp
from functions import (
    generate_otp,
    send_email,
    get_user_object,
    get_account_type,
    compare_passwords,
)
from cust_acc_functions import create_customer, update_cust_details
from admin_acc_functions import update_admin_details

# Modules for Recipe
from recipe import *

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
    # Clear session data from signing up if redirected to login
    session.pop("create_customer", None)

    # Flash appropriate msg when redirected from guest pages
    redirect_messages = {
        "order_page": "Please login first before ordering!",
        "recipe_creator_page": "Please login first before using our recipe creator!",
    }
    button_clicked = request.form.get("button")
    if button_clicked in redirect_messages:
        flash(redirect_messages[button_clicked], "warning")
        return redirect(url_for("login"))

    # Clear all user's logged in data if clicked on 'logout', redirect to clear url args
    if request.args.get("logout"):
        # Update last online date only for customers
        if "customer" in session:
            user_id = session.get("customer").get("user_id")
            update_cust_details(user_id, last_online=date.today())

        session.clear()
        return redirect(url_for("login"))

    # Clear login-related session data if user clicked 'Back to Login', redirect to clear url args
    if request.args.get("back"):
        for key in ("customer", "admin", "reset_pass_details"):
            session.pop(key, None)
        return redirect(url_for("login"))

    # Redirect to send email page if user clicked 'Forgot Password'
    if request.args.get("reset_password"):
        return redirect(url_for("login_send_email"))

    form = LoginForm(request.form)

    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data

        user_object = get_user_object(username=username)
        if not user_object:
            flash("Wrong Username or Password!", "error")
            return render_template("login_base.html", form=form)

        user_id = user_object.get_user_id()
        account_type = get_account_type(user_object=user_object)

        if account_type == "customer" and user_object.get_is_locked():
            return redirect(url_for("login_locked_account", user_id=user_id))

        if compare_passwords(account_type, user_id, password):
            # Update last online date only for customers
            if account_type == "customer":
                update_cust_details(user_id, last_online=date.today())
                user_object = get_user_object(user_id=user_id)

            session[account_type] = (
                user_object.get_cust_data()
                if account_type == "customer"
                else user_object.get_admin_data()
            )

            return redirect(url_for(f"{account_type}.{account_type}_home", id=user_id))
        else:
            flash("Wrong Username or Password!", "error")

    # Handle GET request
    return render_template("login_base.html", form=form)


# Login - Send email for password reset page
@app.route("/login/send_email", methods=["GET", "POST"])
def login_send_email():
    form = EmailForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Check whether account exists, Get user id
        user_object = get_user_object(email=form.email.data)

        if not user_object:
            # Display invalid username or password msg
            flash("No such account with this email exists!", "error")
            print(f"Account with email f{form.email.data} does not exist")
            return render_template("login_send_email.html", form=form)

        # Generate and send OTP
        otp = generate_otp(6)
        send_email(
            mail,
            "Your Verification Code",
            "itastefully@gmail.com",
            [form.email.data],
            body=f"Your verification code to reset your password is {otp}",
        )

        # Store user_id, otp, email data in reset_pass_details in session, Display otp sent msg
        session["reset_pass_details"] = {"email": form.email.data, "otp": otp}
        flash("An OTP has been sent to your email!", "info")

        return redirect(url_for("login_verify_email"))

    # Handle GET request
    form = EmailForm()
    return render_template("login_send_email.html", form=form)


# Login - Verify email for password reset page
@app.route("/login/verify_email", methods=["GET", "POST"])
def login_verify_email():
    form = OTPForm(request.form)

    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_email(
            mail,
            "Your Verification Code",
            "itastefully@gmail.com",
            [session.get("reset_pass_details").get("email")],
            body=f"Your verification code to reset your password is {otp}",
        )
        flash("An OTP has been resent to your email!", "info")
        session["reset_pass_details"]["otp"] = otp
        return redirect(url_for("login_verify_email"))

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Check correct otp
        if form.otp.data != session.get("reset_pass_details").get("otp"):
            # Display invalid otp msg
            flash("Invalid OTP, please try again!", "error")
            return render_template("login_otp.html", form=form)
        return redirect(url_for("login_reset_password"))

    # Handle GET request
    return render_template("login_otp.html", form=form)


# Login - Reset password page
@app.route("/login/reset_password", methods=["GET", "POST"])
def login_reset_password():
    form = ResetPasswordForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Retrive necessary user data
        user_object = get_user_object(
            email=session.get("reset_pass_details").get("email")
        )
        account_type = get_account_type(user_object=user_object)
        user_id = user_object.get_user_id()
        existing_password = user_object.get_password()

        # Hash password
        hashed_password = generate_password_hash(form.password.data, salt_length=8)

        # Check whether password match existing password
        if hashed_password == existing_password:
            flash(
                "Cannot set new password to be the same as current password",
                "error",
            )
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

        return redirect(url_for("login"))

    # Handle GET request
    return render_template("login_reset_pass.html", form=form)


# Login - Locked account popup
@app.route("/login/locked_account", methods=["GET", "POST"])
def login_locked_account():
    user_id = request.args.get("user_id")

    # Handle POST request
    if request.method == "POST":
        # No form validation since there is only submit button
        # Redirect to login page if clicked on close button
        if request.form.get("button") == "close":
            return redirect(url_for("login"))

        # Delete account if clicked on delete
        if request.form.get("button") == "delete":
            # Update customer delete request, Display request sent message
            update_cust_details(user_id, delete_request=True)
            flash("Your request to delete this account has been sent! Please wait while our admins look into it!", "info")
            return redirect(url_for("login"))

        # Handle cust request to unlock if clicked on unlock
        if request.form.get("button") == "unlock":
            # Set request unlock attribute to True
            update_cust_details(user_id, unlock_request=True)
            flash(
                "Your request to unlock this account has been sent! Please wait while our admins look into it!",
                "info",
            )
            return redirect(url_for("login"))

    # Handle GET request
    form = LoginForm()
    user_data = get_user_object(user_id).get_cust_data()
    return render_template(
        "locked_account.html", form=form, user_data=user_data, user_id=user_id
    )


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Remove session data from logging in if redirected to signup
    for key in ("customer", "admin", "reset_pass_details"):
        session.pop(key, None)

    # Clear create_customer in session if user clicked 'Back to Signup'
    if request.args.get("back"):
        session.pop("create_customer", None)
        return redirect(url_for("signup"))

    form = BaseSignUpForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Generate and send OTP
        otp = generate_otp(6)
        send_email(
            mail,
            "Your Verification Code",
            "itastefully@gmail.com",
            [form.email.data],
            body=f"Your verification code is {otp}",
        )

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

        return redirect(url_for("signup_verify_email"))

    # Handle GET request
    return render_template("signup_base.html", form=form)


# Signup - Verify email page
@app.route("/signup/verify_email", methods=["GET", "POST"])
def signup_verify_email():
    # Resend otp if user clicked 'Resend PIN'
    if request.args.get("resend_pin"):
        # Generate and send otp
        otp = generate_otp(6)
        send_email(
            mail,
            "Your Verification Code",
            "itastefully@gmail.com",
            [session.get("create_customer").get("email")],
            body=f"Your verification code is {otp}",
        )

        # Display otp sent msg
        flash("An OTP has been resent to your email!", "info")

        # Update otp in create_customer in session
        session["create_customer"]["otp"] = otp

        return redirect(url_for("signup_verify_email"))

    form = OTPForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Check correct otp
        if form.otp.data != session.get("create_customer").get("otp"):
            # Display invalid otp msg
            flash("Invalid OTP, please try again!", "error")
            return render_template("signup_otp.html", form=form)

        return redirect(url_for("signup_set_password"))

    # Handle GET request
    return render_template("signup_otp.html", form=form)


# Signup - Set password page
@app.route("/signup/set_password", methods=["GET", "POST"])
def signup_set_password():
    form = PasswordForm(request.form)

    # Handle POST request
    if request.method == "POST" and form.validate():
        # Check whether passwords match
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match!", "error")
            return render_template("signup_password.html", form=form)

        # Hash password
        hashed_password = generate_password_hash(form.password.data, salt_length=8)

        # Store ALL customer data in shelve db
        create_customer(session.get("create_customer"), hashed_password)

        # Display successful account creation msg
        flash("Account created, login now!", "success")

        # Clear create_customer in session
        session.pop("create_customer", None)

        return redirect(url_for("login"))

    # Handle GET request
    return render_template("signup_password.html", form=form)

@app.route("/recipe_init")
def recipe_init():
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db.setdefault('recipes', {})  # Initialize if 'recipes' doesn't exist
    recipe_dict = db['recipes']

    recipes_init = [
        ["Chicken Soup",
         ["chicken", "mixed vegetables", "rice", "broth", "herbs"],
         ("1. In a large pot, heat olive oil over medium heat.\n"
          "2. Sauté the vegetables until they are softened.\n"
          "3. Add the chicken meat to the pot and cook until heated through.\n"
          "4. Pour in enough broth to cover the ingredients in the pot.\n"
          "5. Bring the soup to a simmer and let it cook for about 15-20 minutes to allow the flavors to meld.\n"
          "6. Add cooked rice or pasta to the soup.\n"
          "7. Season with salt, pepper, and herbs according to taste.\n"
          "8. Let the soup simmer for an additional 5-10 minutes.\n"
          "9. Serve hot and enjoy your comforting chicken soup!"),
         "chicken_soup.jpg"],

        ["Roasted Vegetable Frittata",
         ["roasted vegetables", "cooked meat", "eggs", "milk", "grated cheese", "olive oil"],
         ("1. Preheat your oven to 375°F (190°C).\n"
          "2. Grease a cast-iron skillet or oven-safe pan with olive oil.\n"
          "3. Spread the roasted vegetables and cooked meat (diced evenly in the skillet.\n"
          "4. In a mixing bowl, whisk together eggs, milk or cream, grated cheese, salt, and pepper.\n"
          "5. Pour the egg mixture over the vegetables and meat in the skillet.\n"
          "6. Gently stir to ensure the ingredients are evenly distributed.\n"
          "7. Place the skillet in the preheated oven and bake for 20-25 minutes, or until the frittata is set and golden brown on top.\n"
          "8. Once cooked, remove the frittata from the oven and let it cool slightly.\n"
          "9. Slice the frittata into wedges and serve warm or at room temperature.\n"
          "10. Enjoy your delicious roast vegetable frittata as a hearty meal or snack!"),
         "roasted_vegetable_frittata.jpg"],

        ["Chicken Stir Fry",
         ["cooked chicken", "mixed vegetables", "cooked rice", "soy sauce", "garlic", "ginger", "olive oil",
          "onions"],
         ("1. Heat olive oil or sesame oil in a large skillet or wok over medium-high heat.\n"
          "2. Add minced garlic and grated ginger to the skillet, sauté until fragrant.\n"
          "3. Toss in the mixed vegetables and stir-fry until they are tender yet crisp.\n"
          "4. Add the cooked chicken (shredded or sliced) to the skillet and stir-fry until heated through.\n"
          "5. Add cooked rice to the skillet and stir well to combine.\n"
          "6. Pour soy sauce over the mixture and continue to stir-fry for a few more minutes.\n"
          "7. Season with salt and pepper according to taste.\n"
          "8. Garnish with chopped green onions if desired.\n"
          "9. Serve hot and enjoy your flavorful chicken stir-fry!"),
         "chicken_stir_fry.jpg"],

        ["Ham and Cheese Casserole",
         ["cooked ham", "bread slices", "eggs", "milk", "cheddar cheese"],
         ("1. Preheat your oven to 375°F (190°C).\n"
          "2. Grease a baking dish with butter or cooking spray.\n"
          "3. Spread bread cubes and diced ham evenly in the baking dish.\n"
          "4. In a mixing bowl, whisk together eggs, milk, salt, and pepper.\n"
          "5. Pour the egg mixture over the bread cubes and ham.\n"
          "6. Sprinkle grated cheddar cheese over the top.\n"
          "7. Bake in the preheated oven for 30-35 minutes or until set and golden brown.\n"
          "8. Let it cool slightly before slicing and serving.\n"
          "9. Enjoy your hearty ham and cheese breakfast casserole!"),
         "ham_and_cheese_casserole.jpg"],

        ["Shepherd's Pie",
         ["cooked beef", "mixed vegetables", "mashed potatoes", "cheddar cheese", "worcestershire sauce"],
         ("1. Preheat your oven to 375°F (190°C).\n"
          "2. Spread cooked ground beef or lamb evenly in a baking dish.\n"
          "3. Layer mixed vegetables over the meat.\n"
          "4. Drizzle Worcestershire sauce over the vegetables.\n"
          "5. Spread mashed potatoes over the top, covering the filling completely.\n"
          "6. Sprinkle grated cheddar cheese over the mashed potatoes.\n"
          "7. Bake in the preheated oven for 25-30 minutes or until the cheese is melted and bubbly.\n"
          "8. Let it cool slightly before serving.\n"
          "9. Enjoy your comforting shepherd's pie!"),
         "shepherds_pie.jpg"],

        ["Chicken Tacos",
         ["cooked chicken", "tortilla", "onion", "tomato", "lettuce", "avocado", "cilantro", "lime wedges"],
         ("1. Warm the cooked chicken in a skillet over medium heat.\n"
          "2. Warm the tortillas in a separate skillet or microwave.\n"
          "3. Assemble tacos by filling tortillas with cooked chicken, sliced red onion, diced tomato, shredded lettuce, avocado slices, and chopped cilantro.\n"
          "4. Squeeze lime juice over the top.\n"
          "5. Serve with sour cream or Greek yogurt and hot sauce or salsa if desired. (Optional)\n"
          "6. Enjoy your flavorful chicken tacos!"),
         "chicken_tacos.jpg"],

        ["Vegetarian Pasta Primavera",
         ["mixed vegetables", "pasta", "olive oil", "garlic", "parmesan cheese", "basil leaves"],
         ("1. Cook pasta according to package instructions. Drain and set aside.\n"
          "2. In a large skillet, heat olive oil over medium heat.\n"
          "3. Add minced garlic and sauté until fragrant.\n"
          "4. Add assorted vegetables to the skillet and sauté until tender.\n"
          "5. Toss cooked pasta with the vegetables in the skillet.\n"
          "6. Season with Italian seasoning and toss to combine.\n"
          "7. Serve hot, garnished with grated Parmesan cheese and chopped fresh basil leaves if desired.\n"
          "8. Enjoy your delightful vegetarian pasta primavera!"),
         "vegetarian_pasta_primavera.jpg"],

        ["Apple Crisp",
         ["apple", "brown sugar", "all-purpose flour", "rolled oats", "ground cinnamon",
          "ground nutmeg", "butter"],
         ("1. Preheat your oven to 375°F (190°C).\n"
          "2. In a large bowl, combine sliced apples with brown sugar, cinnamon, and nutmeg.\n"
          "3. Spread the apple mixture evenly in a baking dish.\n"
          "4. In another bowl, mix together flour, rolled oats, and a bit more cinnamon.\n"
          "5. Cut in cold cubed butter until the mixture resembles coarse crumbs.\n"
          "6. Sprinkle the crumb mixture evenly over the apples.\n"
          "7. Bake in the preheated oven for about 30-35 minutes, or until the topping is golden brown and the apples are tender.\n"
          "8. Serve warm with a scoop of vanilla ice cream or a dollop of whipped cream.\n"
          "9. Enjoy your comforting apple crisp dessert!"),
         "apple_crisp.jpg"]
        ]

    for i in recipes_init:
        new_recipe = Recipe(i[0], i[1], i[2], i[3])
        recipe_dict[new_recipe.get_id()] = new_recipe

    # Create a for loop initializing the recipe object
    db['recipes'] = recipe_dict

    db.close()

    return redirect(url_for('login'))

# Error page (code 404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
