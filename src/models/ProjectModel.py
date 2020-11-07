# src/models/ProjectModel.py
from . import db
import datetime
from marshmallow import fields, Schema

from .ContractModel import ContractSchema

class ProjectModel(db.Model):
    """
    Project Model
    """

    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float())
    comision_percent = db.Column(db.Float())
    street = db.Column(db.String(250))
    int_no = db.Column(db.String(10))
    ext_no = db.Column(db.String(10))
    suburb = db.Column(db.String(250))
    district = db.Column(db.String(250))
    country = db.Column(db.String(250))
    state = db.Column(db.String(250))
    city = db.Column(db.String(250))
    cp = db.Column(db.String(250))
    typo = db.Column(db.Integer)
    due_date = db.Column(db.DateTime)
    shared_comision = db.Column(db.Float())
    escrow = db.Column(db.Boolean)
    comision_paid = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contracts = db.relationship('ContractModel', backref='project', lazy=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.price = data.get('price')
        self.comision_percent = data.get('comision_percent')
        self.street = data.get('street')
        self.int_no = data.get('int_no')
        self.ext_no = data.get('ext_no')
        self.suburb = data.get('suburb')
        self.district = data.get('district')
        self.country = data.get('country')
        self.state = data.get('state')
        self.city = data.get('city')
        self.cp = data.get('cp')
        self.typo = data.get('typo')
        self.due_date = data.get('due_date')
        self.shared_comision = data.get('shared_comision')
        self.escrow = data.get('escrow')
        self.comision_paid = data.get('comision_paid')
        self.user_id = data.get('user_id')
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
  
    # @staticmethod
    # def get_all_blogposts():
    #     return BlogpostModel.query.all()
    @staticmethod
    def get_all_projects(user_id):
        return ProjectModel.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_one_project(id):
        return ProjectModel.query.get(id)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class ProjectSchema(Schema):
    """
    Project Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    price = fields.Float()
    comision_percent = fields.Float()
    street = fields.Str()
    int_no = fields.Str()
    ext_no = fields.Str()
    suburb = fields.Str()
    district = fields.Str()
    country = fields.Str()
    state = fields.Str()
    city = fields.Str()
    cp = fields.Str()
    typo = fields.Int()
    due_date = fields.DateTime()
    shared_comision = fields.Float()
    escrow = fields.Bool()
    comision_paid = fields.Bool()
    user_id = fields.Int(required=True)
    contracts = fields.Nested(ContractSchema, many=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)