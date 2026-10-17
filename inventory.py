import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "inventory.db"


def create_database(connection):
    # Create the table the first time the program runs.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 1000000),
            price_cents INTEGER NOT NULL CHECK(price_cents BETWEEN 0 AND 100000000)
        )
    """)
    connection.commit()


def read_name():
    while True:
        name = input("Product name: ").strip()
        if name:
            return name
        print("The name cannot be blank.")


def read_integer(prompt, minimum=0, maximum=1000000):
    while True:
        try:
            number = int(input(prompt))
            if minimum <= number <= maximum:
                return number
        except ValueError:
            pass
        print(f"Enter a whole number from {minimum} to {maximum}.")


def read_price():
    while True:
        try:
            price = Decimal(input("Unit price (example: 12.50): ").strip())
            if price.is_finite() and 0 <= price <= 1000000:
                cents = price * 100
                if cents == cents.to_integral_value():
                    return int(cents)
        except InvalidOperation:
            pass
        print("Enter a price from 0 to 1000000 with no more than two decimal places.")


def money(cents):
    return f"${Decimal(cents) / 100:,.2f}"


def add_product(connection):
    name = read_name()
    quantity = read_integer("Quantity: ")
    price = read_price()
    # Question marks keep user input separate from the SQL command.
    with connection:
        cursor = connection.execute(
            "INSERT INTO products (name, quantity, price_cents) VALUES (?, ?, ?)",
            (name, quantity, price),
        )
    print(f"Added product #{cursor.lastrowid}.")


def show_rows(rows):
    if not rows:
        print("No products found.")
        return
    for product_id, name, quantity, price in rows:
        print(f"#{product_id}: {name} | Quantity: {quantity} | Unit price: {money(price)}")
        print(f"    Total value: {money(quantity * price)}")


def display_products(connection):
    rows = connection.execute(
        "SELECT id, name, quantity, price_cents FROM products ORDER BY id"
    ).fetchall()
    show_rows(rows)


def search_products(connection):
    search = input("Name contains: ").strip()
    # Escape SQL wildcard characters so the search uses the text entered.
    search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = connection.execute(
        "SELECT id, name, quantity, price_cents FROM products "
        "WHERE name LIKE ? ESCAPE '\\' ORDER BY id",
        (f"%{search}%",),
    ).fetchall()
    show_rows(rows)


def find_product(connection):
    product_id = read_integer("Product ID: ", 1, 9223372036854775807)
    product = connection.execute(
        "SELECT id, name, quantity, price_cents FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if product is None:
        print("Product not found.")
    return product


def update_product(connection):
    product = find_product(connection)
    if product is None:
        return
    show_rows([product])
    print("Enter the updated name, quantity, and price.")
    name = read_name()
    quantity = read_integer("Quantity: ")
    price = read_price()
    with connection:
        connection.execute(
            "UPDATE products SET name = ?, quantity = ?, price_cents = ? WHERE id = ?",
            (name, quantity, price, product[0]),
        )
    print("Product updated.")


def delete_product(connection):
    product = find_product(connection)
    if product is None:
        return
    show_rows([product])
    if input("Delete this product? (y/n): ").strip().lower() != "y":
        print("Deletion canceled.")
        return
    with connection:
        connection.execute("DELETE FROM products WHERE id = ?", (product[0],))
    print("Product deleted.")


def display_summary(connection):
    # Prices are stored as cents to avoid rounding errors with money.
    count, total = connection.execute(
        "SELECT COUNT(*), COALESCE(SUM(quantity * price_cents), 0) FROM products"
    ).fetchone()
    print(f"Number of products: {count}")
    print(f"Total inventory value: {money(total)}")


def main():
    connection = sqlite3.connect(DATABASE)
    try:
        create_database(connection)
        print(f"Database: {DATABASE}")
        while True:
            print("\nInventory Manager")
            print("1. Add product")
            print("2. Display products")
            print("3. Search products")
            print("4. Update product")
            print("5. Delete product")
            print("6. Inventory summary")
            print("7. Quit")
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    add_product(connection)
                elif choice == "2":
                    display_products(connection)
                elif choice == "3":
                    search_products(connection)
                elif choice == "4":
                    update_product(connection)
                elif choice == "5":
                    delete_product(connection)
                elif choice == "6":
                    display_summary(connection)
                elif choice == "7":
                    print("Goodbye. All completed changes are saved.")
                    break
                else:
                    print("Please choose an option from 1 to 7.")
            except sqlite3.Error as error:
                print(f"Database operation failed: {error}")
    finally:
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram closed. All completed changes are saved.")
    except sqlite3.Error as error:
        print(f"Could not open or initialize the database: {error}")
