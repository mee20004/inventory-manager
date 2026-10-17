# Overview

Inventory Manager is a Python console program that uses SQL to manage product records in a SQLite database. It can add, display, search, update, and delete products. It also shows the number of products and total inventory value using the SQL aggregate functions COUNT and SUM.

My purpose for this project is to practice connecting a program to a relational database, sending SQL commands, and using the returned results. I also want to understand how saved database records differ from data stored only in a running program.

Run the program from this folder:

```sh
python3 inventory.py
```

Choose an option from the numbered menu. Each product has an ID shown when it is added or displayed. Use this ID to update or delete a product. Updates ask for all three fields again. Deletion asks for confirmation. Searches match part of a product name; a blank search displays all products. Quantities must be whole numbers from 0 to 1,000,000. Prices must be between $0 and $1,000,000 and have no more than two decimal places. Each completed change is saved automatically. Choose option 7 to quit. Restarting the program loads the same database.

[Software Demo Video](https://youtu.be/SHX3fDXAh4I)

# Relational Database

The program uses SQLite, which stores its database in a local file named `inventory.db` next to `inventory.py`. The program creates this file and its table automatically when it starts. No separate database server is needed. The database file is excluded from version control so each user starts with their own inventory.

There is one table named `products`:

- `id`: An automatically assigned integer primary key that identifies each product.
- `name`: Required product name containing at least one non-space character.
- `quantity`: Required nonnegative integer quantity, limited to 1,000,000.
- `price_cents`: Required integer unit price in cents, limited to 100,000,000 cents.

Prices are stored as whole cents to avoid floating-point rounding errors. For example, $12.50 is stored as 1250. The `create_database` function contains the CREATE TABLE statement. The program uses INSERT, SELECT, UPDATE, and DELETE statements for its main operations. User values are passed as query parameters. UPDATE and DELETE use a WHERE clause with the product ID to affect only the selected record.

The summary query uses COUNT(*) for the number of product records and SUM(quantity * price_cents) for the inventory value. COALESCE returns zero when the table is empty. These two aggregate functions complete the planned stretch challenge.

# Development Environment

The program runs in the macOS terminal with Python 3. It can be opened in a text editor such as Visual Studio Code.

It uses the Python standard library: sqlite3 for SQL database access, decimal for price input and formatting, and pathlib for the database location. No external packages need to be installed.

# Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite CREATE TABLE Documentation](https://www.sqlite.org/lang_createtable.html)
- [SQLite Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)

# Future Work

- Add categories in a separate table and join them with products.
- Add a low-stock report to identify products that need restocking.
- Track dates and quantities for inventory changes.
