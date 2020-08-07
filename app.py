from collections import OrderedDict
import csv
from datetime import datetime
import os
import re

from peewee import *

inventory = SqliteDatabase('inventory.db')
errors = []


class Product(Model):

    product_id = AutoField()
    product_name = TextField(unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateField()

    class Meta:
        database = inventory


def initialize():
    inventory.connect()
    inventory.create_tables([Product], safe=True)


def read_inventory():
    with open('inventory.csv') as csv_inventory:
        inventory_reader = csv.DictReader(csv_inventory)
        dict_list = list(inventory_reader)
        return dict_list


def clean_item(item):
    try:
        item['product_quantity'] = int(item['product_quantity'])
        item['product_price'] = int(
            re.sub('\D', '', item['product_price']))
        if isinstance(item['date_updated'], str):
            item['date_updated'] = datetime.strptime(
                item['date_updated'], '%m/%d/%Y')
    except ValueError:
        errors.append(
            f"Error: {item['product_name']} contains unkown value(s) and must be manually reformatted\n")


def clean_inventory(inventory_data):
    for item in inventory_data:
        clean_item(item)
    return inventory_data


def create_row(item):
    try:
        Product.create(product_name=item['product_name'], product_quantity=item['product_quantity'],
                       product_price=item['product_price'], date_updated=item['date_updated'])
    except IntegrityError:
        product_record = Product.get(product_name=item['product_name'])
        product_record.product_quantity = item['product_quantity']
        product_record.product_price = item['product_price']
        product_record.date_updated = item['date_updated']
        product_record.save()


def import_inventory(csv_data):
    for item in csv_data:
        create_row(item)


def clear():
    os.system('clear')


def menu_loop():
    menu = OrderedDict([
        ('v', view_item),
        ('a', create_item),
        ('b', backup_db)
    ])

    selection = None
    title = "Joe's Inventory"

    while selection != 'q':
        clear()
        print("*" * len(title))
        print(title)
        print("*" * len(title))
        print('\n')

        for key, value in menu.items():
            print(f"{key} => {value.__doc__}")
        print("q => Quit\n")

        if errors:
            for error in errors:
                print(error)

        selection = input(
            "Please make a selection from the menu above =>  ").lower().strip()

        while selection not in menu and selection != 'q':
            selection = input(
                f"Sorry, '{selection}' is not a valid selection, please try again =>  ").lower().strip()

        if selection in menu:
            clear()
            menu[selection]()


def view_item():
    """Lookup Item by ID"""
    while True:

        ID = input("Please enter an item ID =>  ").strip()

        try:
            ID = int(ID)
            product = Product.get_by_id(ID)

            clear()
            print(f"Name: {product.product_name}\n")
            print(f"Quantity: {product.product_quantity}\n")
            print(
                f"Price: ${format(product.product_price / 100, '.2f')}\n")
            print(f"Date Updated: {product.date_updated}\n")
            print(f"ID: {product.product_id}\n")

        except DoesNotExist:
            clear()
            print(f"'{ID}' is out of range\n")
            print("[press ENTER to return to the MAIN MENU, or...]\n")

        except ValueError:
            if not ID:
                break
            else:
                clear()
                print(f"'{ID}' is not a valid ID\n")
                print("[press ENTER to return to the MAIN MENU, or...]\n")


def create_item():
    """Add New Item"""
    while True:
        new_item = OrderedDict()

        new_item['product_name'] = input(
            "Please Input Product Name =>  ").strip()
        if not new_item['product_name']:
            break

        new_item['product_quantity'] = input(
            "Please Input Product Quantity =>  ").strip()
        new_item['product_price'] = input(
            "Please Input Product Price (USD) =>  ").strip()
        new_item['date_updated'] = datetime.now()

        clean_item(new_item)

        if errors:
            clear()
            for error in errors:
                print(error)
                print(
                    "Please try again...\n[or press ENTER to return to the MAIN MENU]\n")
            errors.clear()
        else:
            create_row(new_item)
            input(
                "\nItem successfully added to the inventory!\n\nPress any key to return to the MAIN MENU...")
            break


def backup_db():
    """Back-up Curent Inventory"""
    with open('backup.csv', 'w') as backup:
        fieldnames = ['product_name', 'product_price',
                      'product_quantity', 'date_updated']
        bu_writer = csv.DictWriter(backup, fieldnames=fieldnames)

        bu_writer.writeheader()
        products = Product.select()

        for product in products:
            bu_writer.writerow({
                'product_name': product.product_name,
                'product_price': product.product_price,
                'product_quantity': product.product_quantity,
                'date_updated': product.date_updated
            })


# read through CSV file and create list of dicts
if __name__ == "__main__":
    initialize()
    data = read_inventory()
    clean_data = clean_inventory(data)
    if errors:
        for error in errors:
            print(f"\n{error}")
    else:
        import_inventory(clean_data)
        menu_loop()
