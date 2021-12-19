from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('inventory', __name__)


class RemoveForm(FlaskForm):
    submit = SubmitField(_l('Remove Item'))


class QuantityForm(FlaskForm):
    quantity = IntegerField(_l('Quantity'), validators=[DataRequired()])
    submit = SubmitField(_l('Change Quantity'))


@bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    form = RemoveForm()
    form2 = QuantityForm()

    # find the user's inventory:
    if current_user.is_authenticated:
        products = Product.get_inventory(current_user.id)
    else:
        products = None
    if(form.validate_on_submit() and 'remove_id' in request.values):
        Product.remove(current_user.id, request.values.get('remove_id'))
        return redirect(url_for('inventory.inventory'))
    if(form2.validate_on_submit() and 'product_id' in request.values and form2.quantity.data > 0):
        Product.update(current_user.id, request.values.get(
            'product_id'), form2.quantity.data)
        return redirect(url_for('inventory.inventory'))
    elif (form2.validate_on_submit() and 'product_id' in request.values and form2.quantity.data <= 0):
        flash('Cannot have a negative quantity.')
        return redirect(url_for('inventory.inventory'))
    # render the page by adding information to the index.html file
    return render_template('inventory.html',
                           avail_products=products, form=form, form2=form2)


class AddProductForm(FlaskForm):
    productName = SelectField(
        _l('Name'), choices=['hello', 'hi', 'hey'], validators=[DataRequired()])
    quantity = StringField(_l('Quantity'), validators=[DataRequired()])
    submit = SubmitField(_l('ADD'))



@bp.route('/existingproduct', methods=['GET', 'POST'])
def existingproduct():
    form = AddProductForm()
    # get distinct products
    form.productName.choices = Product.get_all_distinct()

    # add an existing product to this seller's inventory
    if form.validate_on_submit():
        if Product.add_existing(form.productName.data,
                                current_user.id,
                                form.quantity.data
                                ):
            return redirect(url_for('inventory.inventory'))
    return render_template('existingproduct.html', form=form)
