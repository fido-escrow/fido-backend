# src/models/ContractModel.py
from . import db
import datetime
from marshmallow import fields, Schema

from .PartyModel import PartySchema

class ContractModel(db.Model):
    """
    Contract Model
    """

    __tablename__ = 'contract'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)
    mifiel_signed = db.Column(db.Boolean)
    mifiel_id = db.Column(db.String(250))
    graph_signed = db.Column(db.Text)
    status = db.Column(db.Integer)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    parties = db.relationship('PartyModel', backref='contract', lazy=True)
    typo = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.name = data.get('name')
        self.content = data.get('content')
        self.mifiel_signed = data.get('mifiel_signed')
        self.typo = data.get('typo')
        self.mifiel_id = data.get('mifiel_id')
        self.graph_signed = data.get('graph_signed')
        self.status = data.get('status')
        self.project_id = data.get('project_id')
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
    def get_all_contracts(project_id):
        return ContractModel.query.filter_by(project_id=project_id).all()
    
    @staticmethod
    def get_one_contract_mifiel(mifiel_id):
        return ContractModel.query.filter_by(mifiel_id=mifiel_id).first()

    @staticmethod
    def get_one_contract(id):
        return ContractModel.query.get(id)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class ContractSchema(Schema):
    """
    Contract Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    content = fields.Str()
    mifiel_signed = fields.Bool()
    mifiel_id = fields.Str()
    typo = fields.Int()
    graph_signed = fields.Str()
    status = fields.Int()
    project_id = fields.Int(required=True)
    parties = fields.Nested(PartySchema, many=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)