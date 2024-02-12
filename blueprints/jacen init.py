from flask import Flask, render_template, flash, request, redirect, url_for
from article_form import *
from article import *
import shelve, article
import os
from werkzeug.utils import secure_filename

print("hello")
app = Flask(__name__)
app.secret_key='hello_world'

@admin_bp.route('/create_article', methods=['GET', 'POST'])
def create_article(id):
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

        return redirect(url_for('article', id=id))
    return render_template('admin/article/create_article.html', form=create_article, id=id)


@admin_bp.route('/view_article/<article_id>')
def view_article(article_id, id):
    db = shelve.open('article.db', 'c')
    article_dict = db['article_item']
    article_item = article_dict.get(article_id)

    db['article_item'] = article_dict
    db.close()

    return render_template('admin/article/view_article.html', article_item=article_item, id=id)

@admin_bp.route('/article')
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

    return render_template('admin/article/admin_articles.html', form=createArticle, articles=articles, id=id)

@admin_bp.route('/update_article/<article_id>', methods=['GET', 'POST'])
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
            return render_template('admin/article/update_article.html', form=update_article, id=id)
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
        return redirect(url_for('article', id=id))
    else:
        db = shelve.open('article.db', 'c')
        article_dict = db['article_item']
        article_item = article_dict.get(article_id)
        db.close()

        update_article.title.data = article_item.get_title()
        update_article.category.data = article_item.get_category()
        update_article.description.data = article_item.get_description()
        update_article.image.data = article_item.get_image()

        return render_template('admin/article/update_article.html', form=update_article, id=id)

@admin_bp.route('/delete_article/<article_id>')
def delete_article(article_id, id):
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

    return redirect(url_for('article', id=id))

@admin_bp.route('/customer_articles')
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




if __name__ == '__main__':
    app.run(debug=True)