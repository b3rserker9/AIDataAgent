import requests

url = "http://localhost:5000/generate"
prompt = """
 Here is the database schema that the SQL query will run on
 CREATE TABLE aisles (aisle_id INT, aisle VARCHAR);
CREATE TABLE departments (department_id INT, department VARCHAR);
CREATE TABLE order_products_prior (order_id INT, product_id INT, add_to_cart_order INT, reordered INT);
CREATE TABLE order_products_train (order_id INT, product_id INT, add_to_cart_order INT, reordered INT);
CREATE TABLE orders (order_id INT, user_id INT, eval_set VARCHAR, order_number INT, order_dow INT, order_hour_of_day INT, days_since_prior_order DOUBLE);
CREATE TABLE products (product_id INT, product_name VARCHAR, aisle_id VARCHAR, department_id VARCHAR);
Show me the 5 most ordered products
"""

response = requests.post(url, json={"prompt": prompt})

print(response.json()['response'])