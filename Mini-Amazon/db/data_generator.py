import csv
import random
from random_word import RandomWords
r = RandomWords()
categories = []
products = []
passwords = []
import names
from faker import Faker
from werkzeug.security import generate_password_hash
from randomtimestamp import randomtimestamp, random_date, random_time

# Categories
with open("data/Categories.csv", 'w') as output:
    csvwriter = csv.writer(output)
    
    for i in range(50):
        category = r.get_random_word()
        while category == None:
            category = r.get_random_word()
        categories.append(category)
        csvwriter.writerow([category])
print("Categories done")

# Users
with open("data/Users.csv", 'w') as output:
    csvwriter = csv.writer(output)

    r = RandomWords()
    fake = Faker()

    rows = []
    for i in range(0, 100):
        f_name = names.get_first_name()
        l_name = names.get_last_name()
        password = r.get_random_word()
        while password == None:
            password = r.get_random_word()
        email = f_name + password + "@gmail.com"
        row = [email, f_name, l_name, generate_password_hash(password), fake.address().replace('\n', ' '), random.randrange(0, 10000)]
        rows.append(row)
        passwords.append([email, password])

    csvwriter.writerows(rows)

with open("data/Passwords.csv", 'w') as output:
    csvwriter = csv.writer(output)
    csvwriter.writerows(passwords)
print("Users done")

# Orders
rows = []
with open("data/Orders.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(0, 100):
        row = [random.randrange(1, 101), randomtimestamp(start_year=2000, end_year=2022, text=True, pattern="%Y-%m-%d %H:%M:%S")]
        rows.append(row)

    csvwriter.writerows(rows)
print("Orders done")

# Products
with open("data/Products.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(200):
        id = i+1 ##make this random 
        seller_id = random.randint(1,100)
        name = " ".join(r.get_random_words()[:2])
        details = " ".join(r.get_random_words()[:4])
        price = random.randint(500,100000) / 100.00
        image = "0"
        type_index = random.randint(0,49)
        type = categories[type_index]
        quantity = random.randint(5,50)
        row = [id,seller_id,name,details,price,image,type,quantity]
        products.append(row)
        csvwriter.writerow(row)
print("Products done")

# Order_Contains
rows = []
with open("data/Order_Contains.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(1, 101):
        product_id1 = random.randint(1,200)
        seller_id1 = products[product_id1-1][1]
        product_id2 = random.randint(1,200)
        seller_id2 = products[product_id2-1][1]
        product_id3 = random.randint(1,200)
        seller_id3 = products[product_id3-1][1]
        row = [i,random.randrange(0, 1), random.randrange(1, 4), random.randrange(0, 10000) / 100.00, product_id1, seller_id1]
        row2 = [i,random.randrange(0, 1), random.randrange(1, 4), random.randrange(0, 10000) / 100.00, product_id2, seller_id2]
        row3 = [i,random.randrange(0, 1), random.randrange(1, 4), random.randrange(0, 10000) / 100.00, product_id3, seller_id3]

        rows.append(row)

    csvwriter.writerows(rows)
print("Order_Contains done")

# Seller_Reviews
rows = []
with open("data/Seller_Reviews.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(1, 101):
        row = [i,random.randrange(1, 101), random.randrange(1, 6), randomtimestamp(start_year=2000, end_year=2022, text=True, pattern="%Y-%m-%d %H:%M:%S")]
        rows.append(row)

    csvwriter.writerows(rows)
print("Seller_Reviews done")

# Product_Reviews
with open("data/Product_Reviews.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(1, 101):
        product_id = random.randint(1,200)
        seller_id = products[product_id-1][1]
        rating = random.randint(0,5)
        row = [i,product_id,seller_id,rating,randomtimestamp(start_year=2000, end_year=2022, text=True, pattern="%Y-%m-%d %H:%M:%S")]
        csvwriter.writerow(row)
print("Product_Reviews done")

# Carts
with open("data/Carts.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for i in range(200):
        user_id = random.randint(1,100)
        product_id = random.randint(1,200)
        seller_id = products[product_id-1][1]
        quantity = random.randint(0,10)
        row = [user_id,product_id,seller_id,quantity]
        csvwriter.writerow(row)

