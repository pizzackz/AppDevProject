from flask import session, Blueprint, render_template, request, url_for

import shelve
# Modules for Articles
from article_form import *
# Home page (Default - Guest)

guest_bp = Blueprint("guest", __name__)


@guest_bp.route("/")
def home():
    return render_template("guest/home.html")


# Articles page (Guest)
@guest_bp.route("/articles")
def articles():
    return render_template("guest/articles.html")

@guest_bp.route('/recipe_database', methods=['GET', 'POST'])
def recipe_database():
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
        return render_template('guest/recipe_database.html', recipes=recipe2)

    db.close()
    return render_template('guest/recipe_database.html', recipes=recipes)

@guest_bp.route('/view_recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    print(recipe_id)
    db = shelve.open('recipes.db', 'c')
    recipe_dict = db['recipes']
    recipe = recipe_dict.get(recipe_id)
    print(recipe.get_instructions())
    db.close()
    return render_template('guest/view_recipe.html', recipe=recipe)

@guest_bp.route('/menu')
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

    return render_template('guest/guest_menu.html', menus=menus)

@guest_bp.route('/view_menu/<menu_id>')
def view_menu(menu_id):
    db = shelve.open('menu.db', 'c')
    menu_dict = db['Menu']
    menu_item = menu_dict.get(menu_id)

    db.close()

    return render_template('guest/viewMenu.html', menu_item=menu_item)

@guest_bp.route('/article')
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

    return render_template('guest/guest_articles.html', form=createArticle, articles=articles)
@guest_bp.route('/view_article/<article_id>')
def view_article(article_id):
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article_item = article_dict.get(article_id)

    db['article_item'] = article_dict
    db.close()

    return render_template('guest/view_article.html', article_item=article_item)