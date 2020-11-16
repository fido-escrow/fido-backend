#/src/views/ContractView.py
import os
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from mifiel import Client, Document
from ..shared.Authentication import Auth
from ..models.ContractModel import ContractModel, ContractSchema

app = Flask(__name__)
contract_api = Blueprint('contract_api', __name__)
contract_schema = ContractSchema()
temp_folder = "/fido/fido-backend/temp"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
client = Client(app_id=os.getenv('MIFIEL_APP_ID'), secret_key=os.getenv('MIFIEL_APP_SECRET'))
env_name = os.getenv('FLASK_ENV')
if env_name == 'development':
    client.base_url='https://sandbox.mifiel.com'

@contract_api.route('/<int:project_id>', methods=['GET'])
@Auth.auth_required
def get_all(project_id):
    """
    Get All contracts
    """
    contracts = ContractModel.get_all_contracts(project_id)
    data = contract_schema.dump(contracts, many=True)
    return custom_response(data, 200)

@contract_api.route('/upload/<int:project_id>', methods=['POST'])
@Auth.auth_required
def upload(project_id):
    user = UserModel.get_one_user(g.user.get('id'))
    if user.docs_paid < 1:
        return custom_response({'error': 'You dont have any pad documents'}, 403)
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(temp_folder, uploaded_file.filename))
    signatories = []
    try:
        mifieldocu = Document.create(client=client, signatories=signatories, file=os.path.join(temp_folder, uploaded_file.filename))
    except Exception as error:
        return custom_response(err, 400)
    finally:
        os.remove(os.path.join(temp_folder, uploaded_file.filename))
    
    contract = ContractModel({})
    contract.name = uploaded_file.filename
    contract.project_id = project_id
    contract.content=''
    contract.mifiel_signed=False
    contract.graph_signed=False
    contract.mifiel_id=mifieldocu.id
    contract.status = '0'
    contract.typo = '1'
    contract.save()
    user.docs_paid -= 1
    user.save()
    data = contract_schema.dump(contract)
    return custom_response(data, 201)      

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )