from mongoengine import *

connect("temperature")


class NanChangTemperature(Document):
    date = StringField(primary_key=True)
    max_temperature = IntField()
    pass
