from flask import render_template
from flask_login import current_user
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from flask import render_template, redirect, url_for, flash, request
import datetime

from .models.product import Product, Category, ProductReview, Product_Seller
from .models.purchase import Purchase
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)

# add product form


class Add(FlaskForm):
    quantity = IntegerField(_l('Quantity'), validators=[DataRequired()])
    submit = SubmitField(_l('Add'))

# search product by key word form


class SearchProductForm(FlaskForm):
    word = StringField(_l('Word'), validators=[DataRequired()])
    submit = SubmitField(_l('Search'))

# sort by price form


class SortAscending(FlaskForm):
    sortField = SelectField(_l('SortField'), validators=[DataRequired()])
    submit = SubmitField(_l('Low to High'))

# sort by category form


class CategoryForm(FlaskForm):
    cat = SelectField(_l('Cat'), validators=[DataRequired()])
    submit = SubmitField(_l('Browse Category'))


@bp.route('/', methods=['GET', 'POST'])
def index():

    # get all available products for sale:
    products = Product.get_all()
    form = Add()
    form2 = SearchProductForm()
    form4 = SortAscending()
    formC = CategoryForm()
    formC.cat.choices = [cat.name for cat in Category.get_all()]
    form4.sortField.choices = ["Low to High", "High to Low"]
    cart_prods = []

    # find the products current user has bought:
    if current_user.is_authenticated:
        cart_items = Cart.get(current_user.id)
        for cart in cart_items:
            cart_prods.append(cart.product_id)
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        if(form.validate_on_submit() and 'seller_id' in request.values):
            if request.values.get('seller_id') == str(current_user.id):
                flash("Cannot buy product that you sell")
                return redirect(url_for('index.index'))
            else:
                Cart.add(current_user.id, request.values.get('product_id'),
                         request.values.get('seller_id'), form.quantity.data)
                return redirect(url_for('index.index'))
    else:
        purchases = None

    # check sorting forms
    # searching by key word
    if form2.validate_on_submit() and "uniqueSearch" in request.values:
        products = Product.search_products(form2.word.data)
        form2.word.data = ""
    # searching by category
    elif formC.validate_on_submit() and "cSearch" in request.values:
        products = Product.search_categories(formC.cat.data)
        formC.cat.data = ""
    # sorting by price
    elif form4.submit and form4.validate_on_submit() and "ASC" in request.values:
        if form4.sortField.data == "Low to High":
            products = Product.sort_ascending()
        else:
            products = Product.sort_descending()
        form4.sortField.data = ""
    else:
        products = Product.get_all()

    # removing redundant products for products with multiple sellers
    finalProducts = []
    names = []
    for product in products:
        if not product.name in names:
            finalProducts.append(product)
        names.append(product.name)

    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=finalProducts,
                           purchase_history=purchases,
                           form=form,
                           form2=form2,
                           form4=form4,
                           categories=Category.get_all(),
                           formC=formC,
                           cart_prods=cart_prods)


class AddReview(FlaskForm):
    rating = StringField(_l('Rating'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit Review'))


class DeleteReview(FlaskForm):
    submit = SubmitField(_l('Delete Review'))


@bp.route('/product', methods=['GET', 'POST'])
def product():
    form = AddReview()
    form2 = DeleteReview()
    form3 = Add()
    product = Product.getNoSell(request.args.get('id'))
    reviews = ProductReview.get_all(request.args.get('id'))
    cart_prods = []
    if (current_user.is_authenticated):
        cart_items = Cart.get(current_user.id)
        for cart in cart_items:
            cart_prods.append([cart.product_id, cart.seller_id])

    sellers = Product.get_sellers(request.args.get('id'))
    get_info = Product_Seller.get_seller_name(request.args.get('id'))

    num = len(reviews)

    reviewed = False
    date = datetime.datetime.now()

    # Check if user can review
    for review in reviews:
        if current_user.is_authenticated and review.author_id == current_user.id:
            reviewed = True

    if("rate" in request.values and reviewed is False):
        ProductReview.add_review(
            current_user.id, product.id, product.seller_id, request.values.get('rate'), date)
        return redirect(url_for('index.product', id=request.args.get('id')))

    elif ("rate" in request.values and reviewed is True):
        ProductReview.edit_review(
            current_user.id, product.id, request.values.get('rate'), date)
        return redirect(url_for('index.product', id=request.args.get('id')))

    # Delete review
    if (form2.validate_on_submit() and "delete" in request.values):
        ProductReview.delete_review(current_user.id, product.id)
        return redirect(url_for('index.product', id=request.args.get('id')))

    if(form3.validate_on_submit()):
        if request.values.get('seller_id') == str(current_user.id):
            flash("Cannot buy product that you sell")
            return redirect(url_for('cart.viewCart'))

        # Render template -- add review changes
        else:
            Cart.add(current_user.id, request.values.get('product_id'),
                     request.values.get('seller_id'), form3.quantity.data)
            return redirect(url_for('cart.viewCart'))
            
    return render_template('productpage.html', product=product, form=form, form2=form2, form3=form3, reviews=reviews, reviewed=reviewed, num=num, sellers=sellers, get_info=get_info, cart_prods=cart_prods)
