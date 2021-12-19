from flask import flash, current_app as app
import datetime


# Creates a product item
class Product:
    def __init__(self, id, seller_id, name, details, price, image, category, quantity):
        self.id = id
        self.seller_id = seller_id
        self.name = name
        self.details = details
        self.price = price
        self.image = image
        self.type = category
        self.quantity = quantity
        self.average_rating = ProductReview.get_avg_rating(id)

<<<<<<< HEAD
# Gets a specific product from a seller
=======
    #get a product with a certain product id
>>>>>>> 5c040609574ee03260690bd24fd32703034c38ac
    @staticmethod
    def get(id, seller_id):
        rows = app.db.execute('''
SELECT *
FROM Product
WHERE id = :id AND seller_id = :seller_id
''',
                              id=id, 
                              seller_id = seller_id)
        return Product(*(rows[0])) if rows is not None else None

# Gets a specific product from any seller
    def getNoSell(id):
        rows = app.db.execute('''
SELECT *
FROM Product
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    #get all products
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Product
'''
                              )
        return [Product(*row) for row in rows]

    #get name of seller with a specific id
    @staticmethod
    def get_seller_name(seller_id):
        rows = app.db.execute('''
SELECT Product.id, seller_id, name, details, price, image, firstname, lastname
FROM (Users JOIN Product ON Users.id = Product.seller_id)
WHERE Users.id = :seller_id
''',
                              seller_id=seller_id)
        return [Product(*row) for row in rows]

    #get all distinct product names
    @staticmethod
    def get_all_distinct():
        rows = app.db.execute('''
SELECT DISTINCT name
FROM Product
'''
                              )
        return [row[0] for row in rows]

    #return all products sorted by price in ascending order
    @staticmethod
    def sort_ascending():
        rows = app.db.execute('''
SELECT *
FROM Product
ORDER BY Product.price ASC
'''
                              )
        return [Product(*row) for row in rows]

    #return all products sorted by price in descending order
    @staticmethod
    def sort_descending():
        rows = app.db.execute('''
SELECT *
FROM Product
ORDER BY Product.price DESC
'''
                              )
        return [Product(*row) for row in rows]

    #add a product to the database
    @staticmethod
    def add(id, sellerId, name, details, price, image, type, quantity):
        try:
            rows = app.db.execute("""
SELECT name
FROM Product
"""
                                  )
            for row in rows:
                if name == row[0]:
                    flash("Product name is already being used")
                    return None
            rows = app.db.execute("""
INSERT INTO Product(id, seller_id, name, details, price, image, type, quantity)
VALUES(:id, :sellerId, :name, :details, :price, :image, :type, :quantity)
RETURNING id
""",
                                  id=id,
                                  sellerId=int(sellerId),
                                  name=name,
                                  details=details,
                                  price=float(price),
                                  image=image,
                                  type=type,
                                  quantity=int(quantity)
                                  )
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            return None

    #add an existing product to the database
    @staticmethod
    def add_existing(name, seller_id, quantity):
        try:
            rows = app.db.execute("""
SELECT *
FROM Product
WHERE name = :name
""",
                                  name=name
                                  )
            row = rows[0]
            print(row)
            id = row[0]
            details = row[3]
            price = row[4]
            image = row[5]
            type = row[6]
            rows = app.db.execute("""
INSERT INTO Product(id, seller_id, name, details, price, image, type, quantity)
VALUES(:id, :seller_id, :name, :details, :price, :image, :type, :quantity)
RETURNING id
""",
                                  id=id,
                                  seller_id=int(seller_id),
                                  name=name,
                                  details=details,
                                  price=float(price),
                                  image=image,
                                  type=type,
                                  quantity=int(quantity)
                                  )
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            print(e)
            flash("You already sell this product")
            return None

    #get a user's inventory
    @staticmethod
    def get_inventory(id):
        rows = app.db.execute('''
SELECT *
FROM Product
WHERE Product.seller_id = :id
''',
                              id=id)
        return [Product(*row) for row in rows] if rows is not None else None

    #search products based on a keyword
    @staticmethod
    def search_products(word):

        rows = app.db.execute('''
SELECT *
FROM Product 
WHERE LOWER(Product.name) LIKE LOWER(Concat('%', :word,'%'))
OR LOWER(Product.details) LIKE LOWER(Concat('%', :word,'%'))
OR LOWER(Product.type) LIKE LOWER(Concat('%', :word,'%'))
''',
                              word=word)
        return [Product(*row) for row in rows] if rows is not None else None

    #return all products in a certain category
    @staticmethod
    def search_categories(word):

        rows = app.db.execute('''
SELECT *
FROM Product 
WHERE Product.type LIKE Concat('%', :word,'%')
''',
                              word=word)
        return [Product(*row) for row in rows] if rows is not None else None

    #remove a product
    @staticmethod
    def remove(seller_id, id):
        print(seller_id, id)
        try:
            rows = app.db.execute('''
    DELETE FROM PRODUCT
    WHERE seller_id = :seller_id AND id = :id
    ''',
                                  seller_id=seller_id,
                                  id=id)

        except Exception as e:
            return None

    #update the quantity of a product sold by a specific seller
    def update(seller_id, id, quantity):
        try:
            rows = app.db.execute('''
    UPDATE PRODUCT
    SET quantity = :quantity
    WHERE seller_id = :seller_id AND id = :id
    ''',
                                  seller_id=seller_id,
                                  id=id,
                                  quantity=quantity)

        except Exception as e:
            return None

    #get a specific product -- used for determining sellers
    @staticmethod
    def get_sellers(id):
        rows = app.db.execute('''
SELECT *
FROM Product 
WHERE Product.id = :id
''',
                              id=id)
        return [Product(*row) for row in rows] if rows is not None else None


class Category:
    def __init__(self, name):
        self.name = name

    #get all categories
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Category
'''
                              )
        return [Category(*row) for row in rows] if rows is not None else None


class ProductReview:

    def __init__(self, aid, fname, lname, pid, sid, r, date):
        self.author_id = aid
        self.fname = fname
        self.lname = lname
        self.product_id = pid
        self.seller_id = sid
        self.rating = r
        self.date = date

    #get average rating of product
    @staticmethod
    def get_avg_rating(id):
        rows = app.db.execute('''
SELECT AVG(rating)
FROM ProductReview
WHERE product_id = :id
''',
                              id=id)
        return rows[0][0]

    #get all product reviews for a specific product
    def get_all(id):
        rows = app.db.execute('''
SELECT author_id, Users.firstname, Users.lastname, product_id, seller_id, rating, date_and_time
FROM ProductReview, Users
WHERE product_id = :id and author_id = Users.id
ORDER BY date_and_time DESC
''',
                              id=id)
        return [ProductReview(*row) for row in rows] if rows is not None else None

    #get users who authored something
    def get_authored(id):
        rows = app.db.execute('''
SELECT author_id, Users.firstname, Users.lastname, product_id, seller_id, rating, date_and_time
FROM ProductReview, Users
WHERE author_id = :id AND USERS.id = :id
ORDER BY date_and_time DESC
''',
                              id=id)
        return [ProductReview(*row) for row in rows] if rows is not None else None

    #count reviews for a specific product
    def num_reviews(product_id):
        rows = app.db.execute('''
SELECT Count(*)
FROM ProductReview
WHERE product_id = :product_id
''',
                              product_id=product_id)
        return rows[0][0]

    #add a review
    def add_review(author_id, product_id, seller_id, rating, date):
        try:
            rows = app.db.execute('''
    INSERT INTO ProductReview
    Values (:author_id, :product_id, :seller_id, :rating, :date)
    ''',
                                  author_id=author_id,
                                  product_id=product_id,
                                  seller_id=seller_id,
                                  rating=rating,
                                  date=date)
        except Exception as e:
            return None

    #edit a review
    def edit_review(author_id, product_id, rating, date):
        try:
            rows = app.db.execute('''
    UPDATE PRODUCTREVIEW
        SET rating = :rating, date_and_time = :date
        WHERE author_id = :author_id AND product_id = :product_id
    ''',
                                  author_id=author_id,
                                  product_id=product_id,
                                  rating=rating,
                                  date=date)
        except Exception as e:
            return None

    #delete a review
    def delete_review(author_id, product_id):
        try:
            rows = app.db.execute('''
    DELETE FROM PRODUCTREVIEW
    WHERE author_id = :author_id AND product_id = :product_id
    ''',
                                  author_id=author_id,
                                  product_id=product_id)
        except Exception as e:
            return None


class SellerReview:
    def __init__(self, author_id, seller_id, rating, date_and_time):
        self.author_id = author_id
        self.seller_id = seller_id
        self.rating = rating
        self.date_and_time = date_and_time

    #add a seller review
    def add_review(author_id, seller_id, rating, date):
        try:
            rows = app.db.execute('''
    INSERT INTO SellerReview
    Values (:author_id, :seller_id, :rating, :date_and_time)
    ''',
                                  author_id=author_id,
                                  seller_id=seller_id,
                                  rating=rating,
                                  date_and_time=date)
        except Exception as e:
            return None

    #get average seller rating
    @staticmethod
    def get_avg_rating(id):
        rows = app.db.execute('''
SELECT AVG(rating)
FROM SellerReview
WHERE seller_id = :id
''',
                              id=id)
        return rows[0][0]

    #update a seller review
    def update_review(author_id, seller_id, rating, date):
        try:
            rows = app.db.execute('''
     Update Sellerreview 
     SET rating = :rating, date_and_time = :date
     where author_id = :author_id and seller_id = :seller_id;
    ''',
                                  author_id=author_id,
                                  seller_id=seller_id,
                                  rating=rating,
                                  date=date)
        except Exception as e:
            return None

    #check if a user has reviewed a seller
    def has_reviewed(user_id, seller_id):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM SellerReview
WHERE author_id = :user_id AND seller_id = :seller_id
''',            user_id=user_id,
                              seller_id=seller_id,
                              id=id)
        return rows[0][0]

    #delete a seller review
    def delete(author_id, seller_id):
        try:
            rows = app.db.execute('''
    DELETE FROM SELLERREVIEW
    WHERE author_id = :author_id AND seller_id = :seller_id
    ''',
                                  author_id=author_id,
                                  seller_id=seller_id)
        except Exception as e:
            return None

    #get all seller reviews for a seller
    def get_seller(seller_id):
        rows = app.db.execute('''
    SELECT *
    FROM SellerReview
    WHERE seller_id = :seller_id
    ORDER BY date_and_time DESC
    ''',
                              seller_id=seller_id)
        return [SellerReview(*row) for row in rows]

    #get all reviews by a specific user
    def get_authored(auhtor_id):
        rows = app.db.execute('''
    SELECT *
    FROM SellerReview
    WHERE author_id = :author_id
    ORDER BY date_and_time DESC
    ''',
                              author_id=auhtor_id)
        return [SellerReview(*row) for row in rows]


class Product_Seller:
    def __init__(self, id, seller_id, name, details, price, image, category, quantity, firstname, lastname):
        self.id = id
        self.seller_id = seller_id
        self.name = name
        self.details = details
        self.price = price
        self.image = image
        self.type = category
        self.quantity = quantity
        self.firstname = firstname
        self.lastname = lastname
        self.average_rating = ProductReview.get_avg_rating(id)

    #get the name of a seller
    @staticmethod
    def get_seller_name(id):
        rows = app.db.execute('''
SELECT Product.id, seller_id, name, details, price, image, type, quantity, firstname, lastname
FROM (Users JOIN Product ON Users.id = Product.seller_id)
WHERE Product.id = :id
''',
                              id=id)
        return [Product_Seller(*row) for row in rows] if rows is not None else None
