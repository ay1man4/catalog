# from app.database_setup import DBSession, Category, Item, User
from app.models import Category, Item, User
from sqlalchemy import desc
from functools import wraps
from flask import request, redirect, url_for, session as login_session
from app import db


def login_required(f):
    """
    A decorator method to check if user is logged in or not
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('logged_in') is None:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def clear_login_session():
    """
    Clears login_session parameters after user sign out
    """
    login_session.pop('access_token', None)
    login_session.pop('gplus_id', None)
    login_session.pop('username', None)
    login_session.pop('email', None)
    login_session.pop('picture', None)
    login_session.pop('provider', None)
    login_session.pop('user_id', None)
    login_session.pop('logged_in', None)


def create_user():
    """
    Creates new user if not exist in DB.
    Returns:
        User: created user instance
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Query user if exist in DB.
    Returns:
        User: instance of User if exist and None if not.
    """
    try:
        user = User.query.filter_by(id=user_id).one()
        return user
    except Exception as e:
        print(e)
        return None


def getUserID(email):
    """
    Query user id if exist in DB.
    Returns:
        integer: user id if exist and None if not.
    """
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except Exception as e:
        print(e)
        return None


def isCreator(user_id):
    """
    Checks if current user is the creator of catalog category or item.
    Returns:
        boolean: True if same user is the creator, False otherwise.
        User: the user instance of creator.
    """
    creator = getUserInfo(user_id)
    if creator.id != login_session.get('user_id'):
        return creator, False
    return creator, True


def show_catalog():
    return Category.query.all()


def get_categories():
    return Category.query.all()


def get_category(category):
    return Category.query.filter(Category.name == category).first()


def new_category(name):
    category = Category.query.filter(Category.name == name).first()
    if category is None:
        category = Category()
        category.name = name
        category.user_id = login_session['user_id']
        db.session.add(category)
        db.session.commit()

        return Category.query.filter(Category.name == name).first()
    else:

        return category


def get_category_items(category):
    return Category.items.query.filter(Category.name == category)


def get_item(category, item):
    cat = Category.query.filter(Category.name == category).first()
    return Item.query\
        .filter(Item.category == cat, Item.name == item).first()


def get_latest_items():
    return Item.query.order_by(desc('created_at')).limit(10)


def new_item(category_name, name, description):
    category = Category.query\
            .filter(Category.name == category_name).first()
    item = Item()
    item.name = name
    item.description = description
    item.category = category
    item.user_id = login_session['user_id']
    db.session.add(item)
    db.session.commit()
    return Item.query\
        .filter(Item.category == category, Item.name == name).first()


def edit_item(
                old_category_name, old_item_name,
                name, description, category_name):

    old_category = Category.query\
        .filter(Category.name == old_category_name).first()
    item = Item.query\
        .filter(Item.category == old_category, Item.name == old_item_name)\
        .first()
    item.name = name
    item.description = description
    category = Category.query\
        .filter(Category.name == category_name).first()
    item.category = category
    db.session.add(item)
    db.session.commit()
    return Item.query\
        .filter(Item.category == category, Item.name == name).first()


def del_item(category_name, item_name):
    category = Category.query\
        .filter(Category.name == category_name).first()
    item = Item.query\
        .filter(Item.category == category, Item.name == item_name).first()
    creator, editable = isCreator(item.user_id)
    if item is not None and editable:
        db.session.delete(item)
        db.session.commit()
        return True
    else:
        return False
