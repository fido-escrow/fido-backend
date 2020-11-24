#/src/views/ContractView.py
import os, requests
from flask import Flask, request, g, Blueprint, json, Response, send_file, jsonify
from marshmallow import ValidationError
from mifiel import Client, Document
from ..shared.Authentication import Auth
from ..models.ContractModel import ContractModel, ContractSchema
from ..models.UserModel import UserModel
from ..models.PartyModel import PartyModel, PartySchema
from ..shared.Mailing import Mailing

app = Flask(__name__)
contract_api = Blueprint('contract_api', __name__)
contract_schema = ContractSchema()
party_schema = PartySchema()
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
        return custom_response({'error': 'You dont have any paid documents'}, 400)
    uploaded_file = request.files['file']
    signatories = json.loads(request.form.get('json'))
    app.logger.info('llega siquiera --------------#'+json.dumps(signatories))
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(temp_folder, uploaded_file.filename))
    else:
        return custom_response({'error': 'No document'}, 400)
    try:
        mifieldocu = Document.create(client=client, signatories=signatories, file=os.path.join(temp_folder, uploaded_file.filename))
    except Exception as error:
        return custom_response(error, 400)
    finally:
        os.remove(os.path.join(temp_folder, uploaded_file.filename))
    signatories = mifieldocu.signers
    contract = ContractModel({})
    contract.name = uploaded_file.filename
    contract.project_id = project_id
    contract.content=''
    contract.mifiel_signed=False
    contract.graph_signed=False
    contract.mifiel_id=mifieldocu.id
    contract.widget_id=mifieldocu.widget_id
    contract.status = '0'
    contract.typo = '1'
    contract.save()
    for p in signatories:
        party = PartyModel({})
        party.name = p['name']
        party.email = p['email']
        party.rfc = p['tax_id']
        party.widget_id = p['widget_id']
        party.contract_id = contract.id
        party.save()
        try:
            app.logger.info('llego al')
            Mailing.send_sign_invitation(user,contract,party)
        except Exception as e:
            app.logger.error(e)
            
    user.docs_paid -= 1
    user.save()
    data = contract_schema.dump(contract)
    return custom_response(data, 201)

@contract_api.route('/download/<int:contract_id>', methods=['GET'])
def download(contract_id):
    """
    Download a contract  ##Si tiene id dfde mifiel se decarga sino se arma y se envíá
    """
    contract = ContractModel.get_one_contract(contract_id)
    docname=''
    if not contract:
        return custom_response({'error': 'contract not found'}, 404)
    if contract.mifiel_id :
        try:
            doc = Document.find(client,contract.mifiel_id)
            docname = doc.file_file_name
            doc.save_file(os.path.join(temp_folder,docname))
            return send_file(os.path.join(temp_folder,docname), as_attachment=True)
        except Exception as error:
            return custom_response(error, 500)
        finally:
            os.remove(os.path.join(temp_folder,docname))

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )