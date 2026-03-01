
import json
import os
from datetime import datetime
DATA_FILE = "purchases.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_purchase(data):
    item_name = input("Enter item name: ")
    category = input("Enter category: ")
    price = float(input("Enter price: "))
    quantity = int(input("Enter quantity: "))
    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ")

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    purchase = {
        "id": len(data) + 1,
        "item_name": item_name,
        "category": category,
        "price": price,
        "quantity": quantity,
        "date": date
    }

    data.append(purchase)
    save_data(data)
    print(" Purchase added successfully!")

def update_purchase(data):
    view_purchases(data)
    try:
        pid = int(input("Enter ID of purchase to update: "))
    except ValueError:
        print(" Invalid ID.")
        return

    for p in data:
        if p["id"] == pid:
            print("Leave blank to keep current value.")
            p["item_name"] = input(f"Item name ({p['item_name']}): ") or p["item_name"]
            p["category"] = input(f"Category ({p['category']}): ") or p["category"]
            price = input(f"Price ({p['price']}): ")
            if price:
                p["price"] = float(price)
            quantity = input(f"Quantity ({p['quantity']}): ")
            if quantity:
                p["quantity"] = int(quantity)
            date = input(f"Date ({p['date']}): ")
            if date:
                p["date"] = date

            save_data(data)
            print(" Purchase updated successfully!")
            return
    print(" Purchase not found.")

def delete_purchase(data):
    view_purchases(data)
    try:
        pid = int(input("Enter ID to delete: "))
    except ValueError:
        print(" Invalid ID.")
        return

    new_data = [p for p in data if p["id"] != pid]
    if len(new_data) == len(data):
        print(" ID not found.")
    else:
        for i, p in enumerate(new_data, start=1):
            p["id"] = i
        save_data(new_data)
        print(" Purchase deleted successfully!")
    return new_data

def view_purchases(data):
    if not data:
        print("No purchases found.")
        return
    print("\n=== All Purchases ===")
    print("{:<5} {:<15} {:<15} {:<10} {:<10} {:<12}".format("ID", "Item", "Category", "Price", "Qty", "Date"))
    print("-" * 70)
    for p in data:
        print("{:<5} {:<15} {:<15} {:<10.2f} {:<10} {:<12}".format(
            p["id"], p["item_name"], p["category"], p["price"], p["quantity"], p["date"]
        ))
    print()

def summary_report(data):
    if not data:
        print("No data available for summary.")
        return

    total_spent = 0
    category_wise = {}

    for p in data:
        total = p["price"] * p["quantity"]
        total_spent += total
        category_wise[p["category"]] = category_wise.get(p["category"], 0) + total

    print("\n=== Spending Summary ===")
    print(f"Total Spent: ₹{total_spent:.2f}\n")
    print("{:<20} {:<10}".format("Category", "Amount (₹)"))
    print("-" * 35)
    for cat, amt in category_wise.items():
        print("{:<20} {:<10.2f}".format(cat, amt))
    print()

def main_menu():
    data = load_data()

    while True:
        print("\n==== ShopSmart – Smart Purchase Optimizer ====")
        print("1. Add Purchase")
        print("2. Update Purchase")
        print("3. Delete Purchase")
        print("4. View All Purchases")
        print("5. View Summary Report")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_purchase(data)
        elif choice == "2":
            update_purchase(data)
        elif choice == "3":
            data = delete_purchase(data)
        elif choice == "4":
            view_purchases(data)
        elif choice == "5":
            summary_report(data)
        elif choice == "6":
            print(" Exiting... Thank you for using ShopSmart!")
            break
        else:
            print(" Invalid choice! Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main_menu()