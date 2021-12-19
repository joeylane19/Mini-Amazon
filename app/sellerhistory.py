from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.purchase import Purchase, ItemizedPurchase

from flask import Blueprint
bp = Blueprint('sellerhistory', __name__)


class FulfillForm(FlaskForm):
    submit = SubmitField(_l('Change Quantity'))

# load the seller's history
@bp.route('/sellerhistory', methods=['GET', 'POST'])
def sellerhistory():
    form = FulfillForm()
    # fulfill an order line
    if(form.validate_on_submit()):
        ItemizedPurchase.fulfill(request.values.get('order_id'), request.values.get(
            'product_id'), request.values.get('seller_id'))
        return redirect(url_for('sellerhistory.sellerhistory'))
    # find the user's inventory:
    if current_user.is_authenticated:
        orders = Purchase.get_all()
    else:
        orders = None

    # prepare the frontend to display aggregated information
    itemOrders = []
    for order in orders:
        ip = ItemizedPurchase.get(order.order_id, current_user.id)
        if (len(ip) > 0):
            sum = 0
            total = 0
            fulfilled = 'FULFILLED'
            for p in ip:
                sum += p.quantity
                total += p.price * p.quantity
                if p.fullfilled == 0:
                    fulfilled = 'UNFULFILLED'
            ip.append(total)
            ip.append(fulfilled)
            ip.append(sum)
            itemOrders.append(ip)
    # render the page by adding information to the index.html file
    return render_template('sellerhistory.html',
                           itemOrders=itemOrders, form=form)
