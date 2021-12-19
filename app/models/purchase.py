from flask import current_app as app
import datetime

# Creates a purchase item
class Purchase:
    def __init__(self, order_id, user_id, date_and_time):
        self.order_id = order_id
        self.user_id = user_id
        self.date_and_time = date_and_time

# Gets an purchase from orders
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT order_id, user_id, date_and_time
FROM Orders
WHERE order_id = :order_id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

# Gets all orders from a given user since a given date
    @staticmethod
    def get_all_by_uid_since(user_id, since):
        rows = app.db.execute('''
SELECT order_id, user_id, date_and_time
FROM Orders
WHERE user_id = :user_id
AND date_and_time >= :since
ORDER BY date_and_time DESC
''',
                              user_id=user_id,
                              since=since)
        return [Purchase(*row) for row in rows]

# Gets all the items from orders
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT order_id, user_id, date_and_time
FROM Orders
ORDER BY date_and_time DESC
''',

                              )
        return [Purchase(*row) for row in rows]


# Creates an Itemized purchased
class ItemizedPurchase:
    def __init__(self, order_id, user_id, date_and_time, fullfilled, quantity, price, product_id, seller_id, addr):
        self.order_id = order_id
        self.user_id = user_id
        self.date_and_time = date_and_time
        self.fullfilled = fullfilled
        self.quantity = quantity
        self.price = price
        self.product_id = product_id
        self.seller_id = seller_id
        self.addr = addr

# Gets all the purchases from a given seller
    @staticmethod
    def get(order_id, seller_id):
        rows = app.db.execute('''
SELECT order_id, user_id, date_and_time, fullfilled, quantity, price, product_id, seller_id, addr
FROM (Orders join Users on user_id = id) natural join OrderContains
WHERE order_id = :order_id and seller_id = :seller_id
ORDER BY date_and_time DESC
''',
                              order_id=order_id, seller_id=seller_id)
        return [ItemizedPurchase(*row) for row in rows]

# Fullfills a specific order
    def fulfill(order_id, product_id, seller_id):
        try:
            app.db.execute('''
UPDATE OrderContains
SET fullfilled = 1
WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
''',
                           order_id=order_id, product_id=product_id, seller_id=seller_id)

        except Exception as e:
            return None

# Creates an order summary object
class orderSummary:
    def __init__(self, order_id, user_id, fullfilled, quantity, price, date_and_time):
        self.order_id = order_id
        self.user_id = user_id
        self.fullfilled = fullfilled
        self.quantity = quantity
        self.price = price
        self.date_and_time = date_and_time

# Gets all the orders from a given user
    @staticmethod
    def get_all_users_orders(order_id, user_id):
        rows = app.db.execute('''
SELECT OrderContains.order_id as order_id, user_id, fullfilled, quantity, price, date_and_time
FROM (OrderContains INNER JOIN Orders on OrderContains.order_id = Orders.order_id) 
WHERE OrderContains.order_id = :order_id and user_id = :user_id
ORDER BY date_and_time DESC
''',

                              order_id=order_id,
                              user_id=user_id)

        return [orderSummary(*row) for row in rows]
