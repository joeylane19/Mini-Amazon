from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
import datetime

from .models.product import Product, SellerReview
from .models.purchase import Purchase
from .models.user import User
from .models.cart import Cart, Order, OrderContains

from flask import Blueprint
bp = Blueprint('public', __name__)


class ReviewForm(FlaskForm):
    rating = IntegerField(_l('Rating'), validators=[DataRequired()])
    submit = SubmitField(_l('Sumbit Review'))


class DeleteForm(FlaskForm):
    submit = SubmitField(_l('Sumbit Review'))


@bp.route('/view', methods=['GET', 'POST'])
def view():
    form = ReviewForm()
    form2 = DeleteForm()

    user = User.get(request.args.get('id'))

    seller = False
    check_seller = ""
    for product in Product.get_all():
        if(product.seller_id == user.id):
            seller = True
            check_seller = product.seller_id
    reviews = []
    if(seller):
        reviews = SellerReview.get_seller(user.id)

    num = len(reviews)
    rating = SellerReview.get_avg_rating(user.id)
    if rating:
        rating = round(rating, 1)

    # Checking to see if the current user has purchased from this seller
    canReview = False
    if(len(OrderContains.has_bought(user.id, current_user.id)) > 0):
        canReview = True

    # Checking to see if the user has reviewed this seller
    notReviewed = True
    if(SellerReview.has_reviewed(current_user.id, user.id) > 0):
        notReviewed = False

    date = datetime.datetime.now()

    # Check review capabilities
    if('rate' in request.values and canReview and notReviewed):
        SellerReview.add_review(
            current_user.id, check_seller, request.values.get('rate'), date)
        return redirect(url_for('public.view', id=check_seller))
    elif ('rate' in request.values and notReviewed is False):
        SellerReview.update_review(
            current_user.id, check_seller, request.values.get('rate'), date)
        return redirect(url_for('public.view', id=check_seller))
    if(form2.validate_on_submit() and 'delete' in request.values):
        SellerReview.delete(current_user.id, check_seller)
        return redirect(url_for('public.view', id=check_seller))

    return render_template('public.html', user=user, seller=seller, reviews=reviews, notReviewed=notReviewed, canReview=canReview, form=form, form2=form2, num=num, rating=rating)
