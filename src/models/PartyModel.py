# src/models/PartyModel.py
from . import db
import datetime
from marshmallow import fields, Schema

class PartyModel(db.Model):
    """
    Party Model
    """

    __tablename__ = 'party'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    apaterno = db.Column(db.String(128))
    amaterno = db.Column(db.String(128))
    rfc = db.Column(db.String(128))
    moral = db.Column(db.Boolean)
    street = db.Column(db.String(250))
    int_no = db.Column(db.String(10))
    ext_no = db.Column(db.String(10)) 
    suburb = db.Column(db.String(250))
    country = db.Column(db.String(250))
    state = db.Column(db.String(250))
    city = db.Column(db.String(250))
    cp = db.Column(db.String(50))
    typo = db.Column(db.Integer)
    email = db.Column(db.String(128), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    widget_id = db.Column(db.String(250))
    signed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.name = data.get('name')
        self.apaterno = data.get('apaterno')
        self.amaterno = data.get('amaterno')
        self.rfc = data.get('rfc')
        self.moral = data.get('moral')
        self.street = data.get('street')
        self.int_no = data.get('int_no')
        self.ext_no = data.get('ext_no')
        self.suburb = data.get('suburb')
        self.country = data.get('country')
        self.state = data.get('state')
        self.city = data.get('city')
        self.cp = data.get('cp')
        self.typo = data.get('typo')
        self.email = data.get('email')
        self.contract_id = data.get('contract_id')
        self.widget_id = data.get('widget_id')
        self.signed = data.get('signed')
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
    def get_all_parties(contract_id):
        return PartyModel.query.filter_by(contract_id=contract_id).all()
    # @staticmethod
    # def get_all_blogposts():
    #     return BlogpostModel.query.all()
    @staticmethod
    def get_one_party_widget(widget_id):
        return PartyModel.query.filter_by(widget_id=widget_id).first()

    @staticmethod
    def get_one_party(id):
        return PartyModel.query.get(id)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class PartySchema(Schema):
    """
    Party Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    apaterno = fields.Str()
    amaterno = fields.Str()
    rfc = fields.Str()
    moral = fields.Bool()
    street = fields.Str()
    int_no = fields.Str()
    ext_no = fields.Str()
    suburb = fields.Str()
    country = fields.Str()
    state = fields.Str()
    city = fields.Str()
    cp = fields.Str()
    typo = fields.Int()
    email = fields.Email(required=True)
    contract_id = fields.Int(required=True)
    widget_id = fields.Str()
    signed = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)