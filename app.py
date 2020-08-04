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


if __name__ == "__main__":
    initialize()
