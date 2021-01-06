#/src/views/ContractView.py
import os
from zipfile import ZipFile
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
    project = ProjectModel.get_one_project(project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    contracts = ContractModel.get_all_contracts(project_id)
    data = contract_schema.dump(contracts, many=True)
    return custom_response(data, 200)


   
@contract_api.route('/<int:project_id>', methods=['POST'])
@Auth.auth_required
def create(project_id):
    """
    Create Contract from template Function
    """
    project = ProjectModel.get_one_project(project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    req_data = request.get_json()
    app.logger.info('llega siquiera blog--------'+str(project_id)+'------#'+json.dumps(req_data))
    
    # craer contrato y devolverlo con oparrties q son firamntes
    return custom_response(req_data, 201)

@contract_api.route('/sign/<int:contract_id>', methods=['GET'])
@Auth.auth_required
def sign(contract_id):
    """
    Send to sign mifiel Contract from template Function
    """
    contract = ContractModel.get_one_contract(contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    contract.status = 2
    contract.save()
    data = contract_schema.dump(contract)
    #mandar a firma etc
    return custom_response(data, 200)    

@contract_api.route('/upload/<int:project_id>', methods=['POST'])
@Auth.auth_required
def upload(project_id):
    user = UserModel.get_one_user(g.user.get('id'))
    project = ProjectModel.get_one_project(project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    if user.docs_paid < 1:
        return custom_response({'error': 'You dont have any paid documents'}, 400)
    uploaded_file = request.files['file']
    signatories = json.loads(request.form.get('json'))
    for p in signatories:
        p['tax_id'] = p['rfc']
        del p['rfc']
    app.logger.info('llega siquiera UPLOAD CONTRACT--------------#'+json.dumps(signatories))
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(temp_folder, uploaded_file.filename))
    else:
        return custom_response({'error': 'No document'}, 400)
    try:
        curl=burl+'/api/v1/contract/webhook'
        mifieldocu = Document.create(client=client, signatories=signatories, send_mail=0, send_invites=0, callback_url=curl, file=os.path.join(temp_folder, uploaded_file.filename))
    except Exception as error:
        return custom_response(error, 400)
    finally:
        os.remove(os.path.join(temp_folder, uploaded_file.filename))
    signers = mifieldocu.signers
    contract = ContractModel({})
    contract.name = uploaded_file.filename
    contract.project_id = project_id
    contract.content=''
    contract.mifiel_signed=False
    contract.graph_signed=False
    contract.mifiel_id=mifieldocu.id
    contract.widget_id=mifieldocu.widget_id
    contract.status = 3
    contract.typo = 1
    contract.save()
    app.logger.info('signers que llegan de MIFIEL >>>>>>>>>>>> '+str(mifieldocu.signers))
    for p in signers:
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
    if jdoc['signed_by_all']:
        doc = Document.find(client,jdoc[         'id'])
        app.logger.info('propiedad signed by all  >>>>>>>>>>>>>>>>>>>>>>>>'+str(doc.signed_by_all))
        docname = doc.file_file_name.split('.')[0]
        mpdf=os.path.join(temp_folder,docname+'_mnnbnb      1   signed.pdf')
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
            if not p.signed:
                p.signed=True
                p.save()
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
    Download a contract pdf
    """
    contract = ContractModel.get_one_contract(contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    docname=''
    if not contract:
        return custom_response({'error': 'contract not found'}, 400)
    if contract.mifiel_id:
        doc = Document.find(client,contract.mifiel_id)
        docname = doc.file_file_name
        app.logger.info('llega siquiera WEBHOOK  MIFIEL >Z>>>>'+str(doc.signed_by_all))
        if contract.mifiel_signed:
            mpdf=os.path.join(temp_folder,docname.split('.')[0]+'_signed.pdf')
            mxml=os.path.join(temp_folder,docname.split('.')[0]+'.xml')
            mzip=os.path.join(temp_folder,docname.split('.')[0]+'.zip')
            try:
                doc.save_file_signed(mpdf)
                doc.save_xml(mxml)
                ozip = ZipFile(mzip, 'w')
                ozip.write(mpdf,docname.split('.')[0]+'_signed.pdf')
                ozip.write(mxml,docname.split('.')[0]+'.xml')
                ozip.close()
                return send_file(mzip, as_attachment=True)
            except Exception as error:
                return custom_response(error, 500)
            finally:
                os.remove(mpdf)
                os.remove(mxml)
                os.remove(mzip)
        else:   
            try:
                doc.save_file(os.path.join(temp_folder,docname))
                return send_file(os.path.join(temp_folder,docname), as_attachment=True)
            except Exception as error:
                return custom_response(error, 500)
            finally:
                os.remove(os.path.join(temp_folder,docname))

@contract_api.route('/<int:contract_id>', methods=['DELETE'])
@Auth.auth_required
def delete(contract_id):
    """
    Delete A Contract
    """
    user = UserModel.get_one_user(g.user.get('id'))
    contract = ContractModel.get_one_contract(contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    
    if not contract:
        return custom_response({'error': 'contract not found'}, 404)
    #agregar esta validacion en todos los q pidan id de contrato
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    if contract.mifiel_signed :
        return custom_response({'error': 'The document is already signed by all, it is not posible to eliminate'}, 400)
    if contract.mifiel_id:
        doc = Document.delete(client,contract.mifiel_id)
        user.docs_paid += 1
        user.save()
    if contract.parties:
        for party in contract.parties:
            try:
                Mailing.send_delete_doc(user,contract,party)
            except Exception as e:
                app.logger.error(e)
    contract.delete()
    return custom_response({'succes': 'True'}, 200)

@contract_api.route('/reminder/<int:contract_id>', methods=['GET'])
@Auth.auth_required
def reminder(contract_id):
    user = UserModel.get_one_user(g.user.get('id'))
    contract = ContractModel.get_one_contract(contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
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

@contract_api.route('/signers/<int:contract_id>', methods=['POST'])
@Auth.auth_required
def signers(contract_id):
    """
    Create signer party Function
    """
    user = UserModel.get_one_user(g.user.get('id'))
    signatories = request.get_json()
    app.logger.info('llega siquiera contract SIGNERS--------------#'+json.dumps(signatories))    
    contract = ContractModel.get_one_contract(contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 300)
    if not contract:
        return custom_response({'error': 'contract not found or  request data empty'}, 400)
    if contract.status != 3:
        return custom_response({'error': 'Cant change signers in a template created document'}, 400)
    if contract.mifiel_signed:
        return custom_response({'error': 'contract already signed by all participants'}, 400)    
    #contract.status  1 creado por layout, 2 enviado a fiel por layout, 3 subido por el usuario
    if contract.mifiel_id:
        try:
            path = '{}/{}'.format(contract.mifiel_id, 'signers')
            mfdoc = Document(client)
            for p in signatories:
                p['tax_id'] = p['rfc']
                del p['rfc']
                response = mfdoc.execute_request('post', url=mfdoc.url(path), json=p)
                signer = response.json()
                app.logger.info('llega siquiera a mifiel-------MF>>> '+json.dumps(signer))
                if signer['widget_id']:
                    party = PartyModel({})
                    party.name = signer['name']
                    party.email = signer['email']
                    party.rfc = signer['tax_id']
                    party.widget_id = signer['widget_id']
                    party.contract_id = contract.id
                    party.save()
                    try:
                        Mailing.send_sign_invitation(user,contract,party)
                    except Exception as e:
                        app.logger.error(e)
            contract = ContractModel.get_one_contract(contract_id)
            data = contract_schema.dump(contract)
            return custom_response(data, 201)        
        except Exception as error:
                return custom_response(error, 500)
    else:
        return custom_response({'error': 'Docuemnt not send to sign service yet'}, 400)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )