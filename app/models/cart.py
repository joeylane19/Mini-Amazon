from flask import current_app as app


# Creates a cart object

class Cart:
    def __init__(self, user_id, product_id, seller_id, quantity, name, price):
        self.user_id = user_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.quantity = quantity
        self.name = name
        self.price = price

# Gets the cart items for a user
    @staticmethod
    def get(user_id):
        rows = app.db.execute('''
SELECT user_id, product_id as id, Cart.seller_id, Cart.quantity, name, price
FROM Cart, Product
WHERE user_id = :user_id AND Cart.product_id = Product.id AND Cart.seller_id = Product.seller_id
''',
                              user_id=user_id)
        return [Cart(*row) for row in rows]


# Updates the quantity of a given product in someone's
    def update(user_id, product_id, seller_id, quantity):
        try:
            rows = app.db.execute('''
    UPDATE CART
    SET quantity = :quantity
    WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id 
    ''',
                                  user_id=user_id,
                                  product_id=product_id,
                                  seller_id=seller_id,
                                  quantity=quantity)

        except Exception as e:
            return None

# Removes an item from a user's cart
    def remove(user_id, product_id):
        try:
            rows = app.db.execute('''
    DELETE FROM CART
    WHERE user_id = :user_id AND product_id = :product_id
    ''',
                                  user_id=user_id,
                                  product_id=product_id)

        except Exception as e:
            return None


# Adds a product with a certain quantity to someone's cart
    def add(user_id, product_id, seller_id, quantity):
        try:
            rows = app.db.execute('''
    INSERT INTO CART
    VALUES (:user_id, :product_id, :seller_id, :quantity)
    ''',
                                  user_id=user_id,
                                  seller_id=seller_id,
                                  quantity=quantity,
                                  product_id=product_id)

        except Exception as e:
            return None

# Gets the maximum order_id from the set of orders. Used to see if the user has an order
    @staticmethod
    def getMax():
        row = app.db.execute('''
SELECT MAX(order_id)
FROM ORDERS
''',)
        return row[0][0]


# Empties a users cart
    def emptyCart(user_id):
        try:
            rows = app.db.execute('''
    DELETE FROM CART
    WHERE user_id = :user_id
    ''',
                                  user_id=user_id)

        except Exception as e:
            return None

# Creates an order object
class Order:
    def __init__(self, order_id, user_id, date):
        self.order_id = order_id
        self.user_id = user_id
        self.date = date

# Adds an order to the databes
    def add(order_id, user_id, date):
        try:
            rows = app.db.execute('''
    INSERT INTO ORDERS
    VALUES (:order_id, :user_id, :date)
    ''',
                                  order_id=order_id,
                                  user_id=user_id,
                                  date=date)

        except Exception as e:
            return None

# Adds an items to an order
    def add_item(order_id, quantity, price, product_id, seller_id):
        try:
            rows = app.db.execute('''
    INSERT INTO ORDERCONTAINS
    VALUES (:order_id, 0, :quantity, :price, :product_id, :seller_id)
    ''',
                                  order_id=order_id,
                                  quantity=quantity,
                                  price=price,
                                  product_id=product_id,
                                  seller_id=seller_id)

        except Exception as e:
            return None

# Creates an ordercontains object. This represents an item in a given order
class OrderContains:
    def __init__(self, product_id, name, price, seller_id, quantity, fullfilled):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.seller_id = seller_id
        self.quantity = quantity
        self.fullfilled = fullfilled
        self.date = None

# Gets all the items in a given order
    def get_order(order_id):
        rows = app.db.execute('''
    SELECT PRODUCT.id, PRODUCT.name, PRODUCT.price, PRODUCT.seller_id, ORDERCONTAINS.quantity, fullfilled
    FROM ORDERCONTAINS, PRODUCT
    WHERE order_id = :order_id AND ORDERCONTAINS.product_id = PRODUCT.id AND ORDERCONTAINS.seller_id = PRODUCT.seller_id
    ''',
                              order_id=order_id)
        return [OrderContains(*row) for row in rows]

# Checks if a user has bought an item from a given seller
    def has_bought(seller_id, user_id):
        rows = app.db.execute('''
    SELECT *
    FROM ORDERCONTAINS, ORDERS
    WHERE Ordercontains.seller_id = :seller_id AND Orders.user_id = :user_id AND Orders.order_id = ORDERCONTAINS.order_id
    ''',
                              seller_id=seller_id,
                              user_id=user_id)
        return rows
