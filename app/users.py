from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, validators, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
import datetime
from .models.user import User

from .models.product import Product, ProductReview, SellerReview
from .models.purchase import Purchase, ItemizedPurchase, orderSummary
from .models.product import Product, Category

from flask import Blueprint
bp = Blueprint('users', __name__)

# Sign Up


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))

        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    addr = StringField(_l('Address'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.addr.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


class AddProductForm(FlaskForm):
    productName = StringField(_l('Product Name'), validators=[DataRequired()])
    price = StringField(_l('Price'), validators=[DataRequired()])
    details = StringField(_l('Details'), validators=[DataRequired()])
    image = StringField(_l('Image URL'), validators=[DataRequired()])
    type = SelectField(_l('Type'), choices=[
                       'hello', 'hi', 'hey'], validators=[DataRequired()])
    quantity = StringField(_l('Quantity'), validators=[DataRequired()])
    submit = SubmitField(_l('ADD'))


@bp.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    form = AddProductForm()
    form.type.choices = [cat.name for cat in Category.get_all()]
    products = Product.get_all()
    index = len(products) + 1

    if form.validate_on_submit():
        if Product.add(index,
                       current_user.id,
                       form.productName.data,
                       form.details.data,
                       form.price.data,
                       form.image.data,
                       form.type.data,
                       form.quantity.data
                       ):
            return redirect(url_for('inventory.inventory'))
    return render_template('addproduct.html', avail_products=products, form=form)


class fnameForm(FlaskForm):
    firstname = StringField(_l('Update First Name'),
                            validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class lnameForm(FlaskForm):
    lastname = StringField(_l('Update Last Name'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

# Does not allow user to update to same email


def checkEmail(form, field):
    if len(field.data) > 1:
        if len(field.data) > 1 and field.data == current_user.email:
            raise ValidationError("This is already your email")


class emailForm(FlaskForm):
    email = StringField(_l('Update Email'), validators=[Email(), checkEmail])
    submit = SubmitField(_l('Submit'))


class addrForm(FlaskForm):
    addr = StringField(_l('Update Address'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class pwdForm(FlaskForm):
    password = PasswordField(_l('Update Password'))
    password2 = PasswordField(
        _l('Repeat Password'), validators=[EqualTo('password')])
    submit = SubmitField(_l('Submit'))

# Ensure balance input is not negative


def checkBalance(form, field):
    if field.data:
        if (field.data) < 0:
            raise ValidationError("Value can't be negative")

# Ensure balance input is not negative and total balance does not go negative


def checkNegBalance(form, field):
    if field.data:
        if (field.data) < 0:
            raise ValidationError("Value can't be negative")
        if current_user.balance - field.data < 0:
            raise ValidationError("Balance can't be negative")


class balanceForm(FlaskForm):
    balance = FloatField(_l('Update Balance'), validators=[checkBalance])
    submit = SubmitField(_l('Submit'))


class AddReview(FlaskForm):
    rating = IntegerField(_l('Rating'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit Review'))


class DeleteReview(FlaskForm):
    submit = SubmitField(_l('Delete Review'))


class addBalanceForm(FlaskForm):
    balance = FloatField(_l('Add Funds'), validators=[checkBalance])
    submit = SubmitField(_l('Add'))


class lowerBalanceForm(FlaskForm):
    negbalance = FloatField(_l('Lower Funds'), validators=[checkNegBalance])
    submit = SubmitField(_l('Lower'))


@bp.route('/account', methods=['GET', 'POST'])
def updateAccount():
    fname_Form = fnameForm()
    ln_Form = lnameForm()
    email_Form = emailForm()
    addr_Form = addrForm()
    pwd_Form = pwdForm()
    balance_Form = balanceForm()
    addBalance = addBalanceForm()
    lowerBalance = lowerBalanceForm()
    form = AddReview()
    form2 = DeleteReview()
    date = datetime.datetime.now()

    if current_user.is_authenticated:
        original_balance = current_user.balance

    prodReviews = ProductReview.get_authored(current_user.id)
    sellReviews = SellerReview.get_authored(current_user.id)

    # Checks all updates -- if validators are true

    if (form.validate_on_submit() and "rateP" in request.values):
        ProductReview.edit_review(current_user.id, request.values.get(
            'rateP'), form.rating.data, date)
        return redirect(url_for('users.updateAccount'))
    if (form2.validate_on_submit() and "deleteP" in request.values):
        ProductReview.delete_review(
            current_user.id, request.values.get('deleteP'))
        return redirect(url_for('users.updateAccount'))

    if(form.validate_on_submit() and 'rateS' in request.values):
        SellerReview.update_review(
            current_user.id, request.values.get('rateS'), form.rating.data, date)
        return redirect(url_for('users.updateAccount'))
    if(form2.validate_on_submit() and 'deleteS' in request.values):
        SellerReview.delete(current_user.id, request.values.get('deleteS'))
        return redirect(url_for('users.updateAccount'))

    if fname_Form.validate_on_submit() and 'fname' in request.values:
        firstname = fname_Form.firstname.data
        User.change_fname(current_user.id, firstname)
        return redirect(url_for('users.updateAccount'))

    if ln_Form.validate_on_submit() and 'lname' in request.values:
        lastname = ln_Form.lastname.data
        User.change_lname(current_user.id, lastname)
        return redirect(url_for('users.updateAccount'))

    if email_Form.validate_on_submit() and 'email_1' in request.values:
        email = email_Form.email.data
        User.change_email(current_user.id, email)
        return redirect(url_for('users.updateAccount'))

    if addr_Form.validate_on_submit() and 'addr_1' in request.values:
        addr = addr_Form.addr.data
        User.change_addr(current_user.id, addr)
        return redirect(url_for('users.updateAccount'))

    if pwd_Form.validate_on_submit() and 'password_1' in request.values:
        password = pwd_Form.password.data
        User.change_password(current_user.id, password)
        return redirect(url_for('users.updateAccount'))

    if addBalance.validate_on_submit() and 'balance_1' in request.values:
        original_balance += addBalance.balance.data
        original_balance = round(original_balance, 2)
        User.change_balance(current_user.id, original_balance)
        return redirect(url_for('users.updateAccount'))

    if lowerBalance.validate_on_submit() and 'balance_2' in request.values:
        original_balance = original_balance - lowerBalance.negbalance.data
        original_balance = round(original_balance, 2)
        User.change_balance(current_user.id, original_balance)
        return redirect(url_for('users.updateAccount'))

    return render_template('account.html', fname_Form=fname_Form, ln_Form=ln_Form, email_Form=email_Form, addr_Form=addr_Form, pwd_Form=pwd_Form, balance_Form=balance_Form, prod=prodReviews, sell=sellReviews, form=form, form2=form2, addBalance=addBalance, lowerBalance=lowerBalance)


class Sort(FlaskForm):
    sortField = SelectField(_l('SortField'))
    submit = SubmitField(_l('Low to High'))


@bp.route('/buyerhistory', methods=['GET', 'POST'])
def buyerHistory():

    sortForm = Sort()
    sortForm.sortField.choices = ["Low to High", "High to Low"]

    # find the user's inventory:
    if current_user.is_authenticated:
        orders = Purchase.get_all()
        #orders = ItemizedPurchase.get_all()
    else:
        orders = None

    itemOrders = []

    for order in orders:
        ip = orderSummary.get_all_users_orders(order.order_id, current_user.id)
        if (len(ip) > 0):
            sum = 0
            total = 0
            fulfilled = 'FULFILLED'
            for each in ip:
                sum += each.quantity
                total += each.price * each.quantity
                if each.fullfilled == 0:
                    fulfilled = 'UNFULFILLED'
            ip.append(fulfilled)
            ip.append(sum)
            ip.append(total)
            itemOrders.append(ip)

    #sort orders by sum price
    if sortForm.validate_on_submit():
        if sortForm.sortField.data == "Low to High":
            itemOrders.sort(key=lambda x: x[3])
        else:
            itemOrders.sort(key=lambda x: x[3], reverse=True)
        sortForm.sortField.data = ""
        print(itemOrders)

    # render the page by adding information to the index.html file
    return render_template('buyerhistory.html', itemOrders=itemOrders, form=sortForm)
