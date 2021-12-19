\COPY Users(email, firstname, lastname, password, addr, balance) FROM 'data/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Category FROM 'data/Categories.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Product FROM 'data/Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellerReview FROM 'data/Seller_Reviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'data/Carts.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductReview FROM 'data/Product_Reviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Orders(user_id, date_and_time) FROM 'data/Orders.csv' WITH DELIMITER ',' NULL '' CSV
\COPY OrderContains FROM 'data/Order_Contains.csv' WITH DELIMITER ',' NULL '' CSV

