import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

#Create SQLite in-memory DB
conn = sqlite3.connect('product_sales.db')
cursor=conn.cursor()

#Create Tables - It defines each table with column names and data types.
cursor.execute('''
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
)
''')

cursor.execute('''
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    region TEXT
)
''')

cursor.execute('''
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    sale_date DATE,
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
)
''')


#Insert fake data
products=[
    (1, 'Laptop', 'Electronics', 1200),
    (2, 'Headphones', 'Electronics', 150),
    (3, 'Desk Chair', 'Furniture', 200),
    (4, 'Coffee Machine', 'Appliances', 300),
    (5, 'Monitor', 'Electronics', 400),
]

customers =[
    (1, 'Alice', 'Europe'),
    (2, 'Bob', 'Asia'),
    (3, 'Charlie', 'North America'),
    (4, 'Diana', 'Europe'),
    (5, 'Ethan', 'Asia')
]

cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products)
cursor.executemany('INSERT INTO customers VALUES (?, ?, ?)', customers)

#Random sales
start_date = datetime(2024, 1, 1)
sales_data = []
for i in range(1, 101):
    product_id=random.randint(1, 5)
    customer_id = random.randint(1, 5)
    quantity = random.randint(1, 5)
    sale_date = start_date + timedelta(days=random.randint(0, 300))
    sales_data.append((i, product_id, customer_id, quantity, sale_date.date()))

cursor.executemany('INSERT INTO sales VALUES (?, ?, ?, ?, ?)', sales_data)
conn.commit()

#Data Analysis with SQL
#Which is the best-selling product?

query='''
SELECT
    p.product_name,
    SUM(s.quantity) AS total_sold
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 5;
'''
top_products=pd.read_sql_query(query, conn)
print(top_products)


#Sales by Region
query2 = '''
SELECT 
    c.region,
    ROUND(SUM(s.quantity * p.price), 2) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;
'''

revenue_by_region = pd.read_sql_query(query2, conn)
print(revenue_by_region)

#Monthly Sales Trend with CTE example
query3 = '''
WITH monthly_sales AS (
    SELECT
        strftime('%Y-%m', sale_date) AS month,
        SUM(quantity * p.price) AS monthly_revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY month
)
SELECT * FROM monthly_sales ORDER BY month;
'''

monthly_sales = pd.read_sql_query(query3, conn)
print(monthly_sales)


#Visualize Amalysis Results with Pandas
import matplotlib.pyplot as plt

plt.figure(figsize=(8,4))
plt.bar(top_products['product_name'], top_products['total_sold'])
plt.title('Top 5 most Sold Products')
plt.xlabel('Product')
plt.ylabel('Total Units Sold')
plt.grid(True)
plt.show()
