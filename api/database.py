# api/database.py
import os
from peewee import *
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lindenpc.db")

if "sqlite" in DATABASE_URL:
    db = SqliteDatabase(DATABASE_URL.split(":///")[1])  # для SQLite
else:
    db = PostgresqlDatabase(DATABASE_URL)  # для PostgreSQL


class BaseModel(Model):
    class Meta:
        database = db


class Role(BaseModel):
    role_id = AutoField(primary_key=True)
    role_name = CharField(unique=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'Role'  # Явное указание имени таблицы


class User(BaseModel):
    user_id = AutoField(primary_key=True)
    login = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    # Corrected ForeignKeyField
    role = ForeignKeyField(Role, backref='users', field='role_id')

    class Meta:
        table_name = 'User'  # Явное указание имени таблицы


class Category(BaseModel):
    category_id = AutoField(primary_key=True)
    category_name = CharField(unique=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'Category'  # Явное указание имени таблицы


class Manufacturer(BaseModel):
    manufacturer_id = AutoField(primary_key=True)
    manufacturer_name = CharField(unique=True)
    contact_information = TextField(null=True)

    class Meta:
        table_name = 'Manufacturer'  # Явное указание имени таблицы


class Component(BaseModel):
    component_id = AutoField(primary_key=True)
    component_name = CharField()
    description = TextField(null=True)
    # Corrected ForeignKeyField
    category = ForeignKeyField(
        Category, backref='components', field='category_id')
    manufacturer = ForeignKeyField(
        # Corrected ForeignKeyField
        Manufacturer, backref='components', field='manufacturer_id')
    price = DecimalField()
    quantity_in_stock = IntegerField()

    class Meta:
        table_name = 'Component'  # Явное указание имени таблицы


class Delivery(BaseModel):
    delivery_id = AutoField(primary_key=True)
    delivery_date = DateField()
    supplier = CharField()
    status = CharField()

    class Meta:
        table_name = 'Delivery'  # Явное указание имени таблицы


class Order(BaseModel):
    order_id = AutoField(primary_key=True)
    order_date = DateField()
    # Corrected ForeignKeyField
    component = ForeignKeyField(
        Component, backref='orders', field='component_id')
    quantity = IntegerField()
    status = CharField()

    class Meta:
        table_name = 'Order'  # Явное указание имени таблицы


class DeliveryItem(BaseModel):
    delivery_item_id = AutoField(primary_key=True)
    # Corrected ForeignKeyField
    delivery = ForeignKeyField(
        Delivery, backref='delivery_items', field='delivery_id')
    # Corrected ForeignKeyField
    component = ForeignKeyField(
        Component, backref='delivery_items', field='component_id')
    quantity = IntegerField()
    price_per_unit = DecimalField()

    class Meta:
        table_name = 'Delivery_Item'  # Явное указание имени таблицы


class EventLog(BaseModel):
    event_id = AutoField(primary_key=True)
    user = ForeignKeyField(User, backref='event_logs',
                           field='user_id')  # Corrected ForeignKeyField
    timestamp = DateTimeField()
    event_type = CharField()
    description = TextField(null=True)
    affected_table = CharField(null=True)
    affected_record_id = IntegerField(null=True)

    class Meta:
        table_name = 'Event_Log'  # Явное указание имени таблицы


class Audit(BaseModel):
    audit_id = AutoField(primary_key=True)
    # Corrected ForeignKeyField
    user = ForeignKeyField(User, backref='audits', field='user_id')
    timestamp = DateTimeField()
    table_name = CharField()
    record_id = IntegerField()
    field_name = CharField()
    old_value = TextField(null=True)
    new_value = TextField(null=True)

    class Meta:
        table_name = 'Audit'  # Явное указание имени таблицы


def create_tables():
    with db:
        db.create_tables([Role, User, Category, Manufacturer, Component,
                          Delivery, Order, DeliveryItem, EventLog, Audit])
        print("Tables created successfully")


if __name__ == '__main__':
    create_tables()
