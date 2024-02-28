from enum import Enum

import mongoengine
from django.db import models
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import *


class AdditionalExport(EmbeddedDocument):
    first = StringField(required=True)
    second = StringField(required=True)
    db_column_name = StringField(required=True)


class DegField(EmbeddedDocument):
    name = StringField(required=True)
    russian_name = StringField(db_field='russianName')
    show = BooleanField(required=True)
    order = IntField(required=True)


class DegTypes(Enum):
    EXPORT = 'EXPORT'
    BOARD = 'BOARD'


class DegWidget(Document):
    meta = {'collection': 'deg_widget'}
    class_name = StringField(db_field='_class', default='tech.ppr.stats.back.model.deg.DegWidget')

    alias = StringField(required=True)
    deg = StringField(required=True)
    order = IntField(required=True)
    russian_name = StringField(db_field='russianName')
    show = BooleanField(required=True)
    table_name = StringField(required=True)
    img = StringField()
    type = EnumField(DegTypes, default=DegTypes.EXPORT)
    fields_list = EmbeddedDocumentListField(DegField, required=True)
    additional_export = EmbeddedDocumentField(AdditionalExport)
