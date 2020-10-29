# src/models/LayoutModel.py
from . import db
import datetime
from marshmallow import fields, Schema

class LayoutModel(db.Model):
    """
    Layout Model
    """

    __tablename__ = 'layout'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.user_id = data.get('user_id')
        self.title = data.get('title')
        self.contents = data.get('contents')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
  
    @staticmethod
    def get_all_layouts():
        return LayoutModel.query.all()
  
    @staticmethod
    def get_one_layout(id):
        return LayoutModel.query.get(id)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class LayoutSchema(Schema):
    """
    Layout Schema
    """
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    contents = fields.Str(required=True)
    user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)