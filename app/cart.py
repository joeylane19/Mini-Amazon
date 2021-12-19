from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
import datetime

from .models.product import Product, SellerReview, Product_Seller
from .models.purchase import Purchase
from .models.user import User
from .models.cart import Cart, Order, OrderContains


from flask import Blueprint
bp = Blueprint('cart', __name__)

# Form to change quantity in the cart
class QuantityForm(FlaskForm):
    quantity = IntegerField(_l('Quantity'))
    submit = SubmitField(_l('Change Quantity'))

# Form to remove an item from the card
class RemoveForm(FlaskForm):
    submit = SubmitField(_l('Remove Item'))

# Form to submit an order
class OrderForm(FlaskForm):
    submit = SubmitField(_l('Sumbit Order'))

# Gets the items in a persons cart. Allows one to submit an order
@bp.route('/cart', methods=['GET', 'POST'])
def viewCart():
    # get all product from users' cart and calculate total price
    cart_items = Cart.get(current_user.id)
    
    form = QuantityForm()
    form2 = RemoveForm()
    form3 = OrderForm()
    total_price = 0
    error = []
    

    for item in cart_items:
        total_price += item.price*item.quantity

    total_price = round(total_price, 2)

    #  Allows on to change quantitu
    if(form.validate_on_submit() and 'product_id' in request.values and form.quantity.data > 0):
        Cart.update(current_user.id, request.values.get('product_id'), request.values.get('seller_id'), form.quantity.data)
        return redirect(url_for('cart.viewCart'))

    elif (form.validate_on_submit() and 'product_id' in request.values and form.quantity.data <= 0):
        return redirect(url_for('cart.viewCart'))
    # Removes Item from cart
    if(form2.validate_on_submit() and 'remove_id' in request.values):
        Cart.remove(current_user.id, request.values.get('remove_id'))
        return redirect(url_for('cart.viewCart'))

    # Checks to see if one can submit an order
    if(form3.validate_on_submit() and 'order_id' in request.values):
        for item in cart_items:
            if(Product.get(item.product_id, item.seller_id).quantity < item.quantity):
                error.append("Not enough inventory in stock.")

        if(current_user.balance < total_price):
            error.append("Your user balance is too low.")

        # Creates on order
        if(error == []):
            orderNum = Cart.getMax() + 1
            date = datetime.datetime.now()
            Order.add(orderNum, current_user.id, date)

            for item in cart_items:
                product = Product.get(item.product_id, item.seller_id)
                
                User.change_balance(current_user.id, round(
                    current_user.balance - item.quantity * item.price, 2))

                User.change_balance(product.seller_id, round(User.get(
                    product.seller_id).balance + item.quantity * item.price, 2))
                Product.update(product.seller_id, product.id, product.quantity - item.quantity)
                Order.add_item(orderNum, item.quantity, item.price,
                               item.product_id, item.seller_id)

            Cart.emptyCart(current_user.id)

            return redirect(url_for('cart.viewOrder', id=orderNum))

    # render the page by adding information to the cart.html file
    return render_template('cart.html',
                           cart_items = cart_items,
                           total_price = total_price,
                           form = form,
                           form2 = form2,
                           form3 = form3,
                           error = error)


# Form to review a user
class ReviewForm(FlaskForm):
    rating = IntegerField(_l('Rating'), validators=[DataRequired()])
    submit = SubmitField(_l('Sumbit Review'))

# Deletes a review from a user
class DeleteForm(FlaskForm):
    submit = SubmitField(_l('Sumbit Review'))

# Allows one to view the order of someone
@bp.route('/order', methods=['GET', 'POST'])
def viewOrder():
    form = ReviewForm()
    form2 = DeleteForm()
    orderNum = request.args.get('id')
    order = OrderContains.get_order(orderNum)
    order_items = []

    for item in order:
        order_items.append(
            (item, SellerReview.has_reviewed(current_user.id, item.seller_id)))
    date = datetime.datetime.now()
    total_price = 0
    if(form.validate_on_submit() and 'review' in request.values):
        SellerReview.add_review(current_user.id, request.values.get(
            'review'), form.rating.data, date)
        return redirect(url_for('cart.viewOrder', id=orderNum))
    if(form.validate_on_submit() and 'reviewed' in request.values):
        SellerReview.update_review(current_user.id, request.values.get(
            'review'), form.rating.data, date)
        return redirect(url_for('cart.viewOrder', id=orderNum))
    if(form2.validate_on_submit() and 'delete' in request.values):
        SellerReview.delete(current_user.id, request.values.get('delete'))
        return redirect(url_for('cart.viewOrder', id=orderNum))

    for item in order:
        total_price += item.price*item.quantity
    total_price = round(total_price, 2)
    return render_template('order.html', order_items=order_items, total_price=total_price, form=form, form2=form2)


