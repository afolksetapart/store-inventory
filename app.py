from collections import OrderedDict
import csv
from datetime import datetime
import os
import re

from peewee import *

inventory = SqliteDatabase('inventory.db')


class Product(Model):

    product_id = AutoField()
    product_name = TextField()
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


def clean_inventory(inventory_data):
    for item in inventory_data:
        try:
            item['product_quantity'] = int(item['product_quantity'])
            item['product_price'] = int(
                re.sub('\D', '', item['product_price']))
            item['date_updated'] = datetime.strptime(
                item['date_updated'], '%m/%d/%Y')
        except ValueError:
            print(
                f"{item['product_name']} contains unkown value(s) and must be manually reformatted")
    return inventory_data


def add_item(item):
    try:
        Product.create(product_name=item['product_name'], product_quantity=item['product_quantity'],
                       product_price=item['product_price'], date_updated=item['date_updated'])
    except IntegrityError:
        product_record = Product.get(product_name=item['product_name'])
        product_record.product_quantity = item['product_quantity']
        product_record.product_price = item['product_price']
        product_record.date_updated = datetime.now()
        product_record.save()


def import_inventory(csv_data):
    for item in csv_data:
        add_item(item)


def clear():
    os.system('clear')


def menu_loop():
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

        selection = input(
            "Please make a selection from the menu above =>  ").lower().strip()

        while selection not in menu and selection != 'q':
            selection = input(
                f"Sorry, '{selection}' is not a valid selection, please try again =>  ")

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
            print(f"Price: ${(product.product_price / 100)}\n")
            print(f"Date Updated: {product.date_updated}\n")

        except ValueError:
            if not ID:
                break
            else:
                clear()
                print(f"'{ID}' is not a valid ID\n")
                print("[press ENTER to return to the MAIN MENU, or...]\n")


def create_item():
    """Add New Item"""
    pass


def backup_db():
    """Back-up Curent Inventory"""
    pass


menu = OrderedDict([
    ('v', view_item),
    ('a', create_item),
    ('b', backup_db)
])

# read through CSV file and create list of dicts
if __name__ == "__main__":
    initialize()
    data = read_inventory()
    clean_data = clean_inventory(data)
    import_inventory(clean_data)
    menu_loop()
