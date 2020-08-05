import csv
from datetime import datetime
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


def import_inventory(csv_data):
    for item in csv_data:
        add_item(item)

        # read through CSV file and create list of dicts
if __name__ == "__main__":
    initialize()
    data = read_inventory()
    clean_data = clean_inventory(data)
    import_inventory(clean_data)
