#/src/views/ContractView.py
import os, requests
from flask import Flask, request, g, Blueprint, json, Response, send_file, jsonify, url_for
from marshmallow import ValidationError
from mifiel import Client, Document
from ..shared.Authentication import Auth
from ..models.ContractModel import ContractModel, ContractSchema
from ..models.UserModel import UserModel
from ..models.ProjectModel import ProjectModel
from ..models.PartyModel import PartyModel, PartySchema
from ..shared.Mailing import Mailing

app = Flask(__name__)
burl = os.getenv('BACK_URL')
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
    app.logger.info('llega siquiera UPLOAD CONTRACT--------------#'+json.dumps(signatories))
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(temp_folder, uploaded_file.filename))
    else:
        return custom_response({'error': 'No document'}, 400)
    try:
        curl=burl+'/api/v1/contract/webhook'
        app.logger.info('llega la url: '+curl)
        mifieldocu = Document.create(client=client, callback_url=curl, signatories=signatories, file=os.path.join(temp_folder, uploaded_file.filename))
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
    contract.status = 2
    contract.typo = 1
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
            Mailing.send_sign_invitation(user,contract,party)
        except Exception as e:
            app.logger.error(e)
            
    user.docs_paid -= 1
    user.save()
    data = contract_schema.dump(contract)
    return custom_response(data, 201)

@contract_api.route('/webhook', methods=['POST'])
def webhook():
    jdoc = request.get_json()
    app.logger.info('llega siquiera WEBHOOK--------------#'+json.dumps(jdoc))
    if jdoc['signed_by_all']:
        doc = Document.find(client,jdoc['id'])
        docname = doc.file_file_name.split('.')[0]
        mpdf=os.path.join(temp_folder,docname+'_signed.pdf')
        mxml=os.path.join(temp_folder,docname+'.xml')
        doc.save_file_signed(mpdf)
        doc.save_xml(mxml)
        app.logger.info('archivos estan en: pdf----'+mpdf+'   xml---'+mxml)
        contract = ContractModel.get_one_contract_mifiel(doc.id)
        contract.mifiel_signed=True
        contract.save()
        project = ProjectModel.get_one_project(contract.project_id)
        user = UserModel.get_one_user(project.user_id)
        try:
            Mailing.send_sign_final(user.email,contract.name,mpdf,mxml)
        except Exception as e:
            app.logger.error(e)
        for p in contract.parties:
            try:
                Mailing.send_sign_final(p.email,contract.name,mpdf,mxml)
            except Exception as e:
                app.logger.error(e)
        os.remove(mpdf)
        os.remove(mxml)
    return custom_response({'success' : True}, 200)

@contract_api.route('/download/<int:contract_id>', methods=['GET'])
@Auth.auth_required
def download(contract_id):
    """
    Download a contract  ##Si tiene id dfde mifiel se decarga sino se arma y se envíá
    """
    contract = ContractModel.get_one_contract(contract_id)
    docname=''
    if not contract:
        return custom_response({'error': 'contract not found'}, 400)
    if contract.mifiel_id :
        try:
            #falta revisar si ya está firmado para decargarse con todas las firmas el xml y la representacion grafica
            doc = Document.find(client,contract.mifiel_id)
            docname = doc.file_file_name
            doc.save_file(os.path.join(temp_folder,docname))
            #zippear y descargar
            return send_file(os.path.join(temp_folder,docname), as_attachment=True)
        except Exception as error:
            return custom_response(error, 500)
        finally:
            os.remove(os.path.join(temp_folder,docname))
    #else: falta revisar si se arma y se convierte a dfecarga

@contract_api.route('/reminder/<int:contract_id>', methods=['GET'])
@Auth.auth_required
def reminder(contract_id):
    user = UserModel.get_one_user(g.user.get('id'))
    contract = ContractModel.get_one_contract(contract_id)
    if not contract: 
        return custom_response({'error': 'contract not found or  request data empty'}, 400)
    if contract.mifiel_signed :
        return custom_response({'error': 'The document is already signed by all'}, 400)
    if contract.parties:
        for party in contract.parties:
            if party.widget_id and not party.signed:
                try:
                    Mailing.send_sign_invitation(user,contract,party)
                except Exception as e:
                    app.logger.error(e)
    return custom_response({'succes': 'True'}, 200)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )