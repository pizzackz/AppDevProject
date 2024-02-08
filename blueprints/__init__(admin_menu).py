from flask import Flask, render_template, request, redirect, url_for, flash
from menuForm import *
from menu import *
import shelve
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'yoyoyo'

@customer_bp.route('/menu')
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

@customer_bp.route('/create_menu', methods=['GET', 'POST'])
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

@customer_bp.route('/delete_menu/<menu_id>')
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


@customer_bp.route('/update_menu/<menu_id>', methods=['GET', 'POST'])
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


@customer_bp.route('/view_menu/<menu_id>')
def view_menu(menu_id):
    db = shelve.open('menu.db', 'c')
    menu_dict = db['Menu']
    menu_item = menu_dict.get(menu_id)



    db.close()



    return render_template('admin/viewMenu.html', menu_item=menu_item)

if __name__ == '__main__':
    app.run(debug=True)
