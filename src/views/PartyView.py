#/src/views/PartyView.py
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from ..shared.Authentication import Auth
from ..shared.Mailing import Mailing
from ..models.PartyModel import PartyModel, PartySchema
from ..models.ContractModel import ContractModel, ContractSchema
from ..models.ProjectModel import ProjectModel
from ..models.UserModel import UserModel

app = Flask(__name__)
party_api = Blueprint('party_api', __name__)
party_schema = PartySchema()
contract_schema = ContractSchema()

@party_api.route('/<int:contract_id>', methods=['GET'])
@Auth.auth_required
def get_all(contract_id):
    """
    Get All parties
    """
    parties = PartyModel.get_all_parties(contract_id)
    data = party_schema.dump(parties, many=True)
    return custom_response(data, 200)
    
@party_api.route('/<int:contract_id>', methods=['POST'])
@Auth.auth_required
def create(contract_id):
    """
    Create party Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera party- create-------------#'+json.dumps(req_data))
    
    try:
        data = party_schema.load(req_data)
    except ValidationError as err:
        return custom_response(err, 400)
        
    party = PartyModel(data)
    party.contract_id=contract_id
    party.save()
    data = party_schema.dump(party)
    return custom_response(data, 201)

@party_api.route('/signers/<int:contract_id>', methods=['POST'])
@Auth.auth_required
def signers(contract_id):
    """
    Create signer party Function
    """
    user = UserModel.get_one_user(g.user.get('id'))
    signatories = request.get_json()
    app.logger.info('llega siquiera party- create-------------#'+json.dumps(signatories))
    
    contract = ContractModel.get_one_contract(contract_id)
    if not contract:
        return custom_response({'error': 'contract not found or  request data empty'}, 400)
    #contract.status  0 creado por layout, 1 enviado a fiel por layout, 2 subido por el usuario
    if contract.mifiel_id:
        try:
            #mifieldocu = Document.find(client,contract.mifiel_id)
            #actualizar firmantes 
            # mifieldocu.signers
            # for p in mifieldocu.signers:
            #     party = PartyModel({})
            #     party.name = p['name']
            #     party.email = p['email']
            #     party.rfc = p['tax_id']
            #     party.widget_id = p['widget_id']
            #     party.contract_id = contract.id
            #     party.save()
            #     try:
            #         Mailing.send_sign_invitation(user,contract,party)
            #     except Exception as e:
            #         app.logger.error(e)
            data = contract_schema.dump(contract)
            return custom_response(data, 201)        
        except Exception as error:
                return custom_response(error, 500)
    else:
        return custom_response({'error': 'Este documento fue creado con plantillas de FIDO, una vez enviado ya no se puede modificar los firmantes'}, 400)
        
@party_api.route('/signed/<string:widget_id>', methods=['GET'])
def signed(widget_id):
    party = PartyModel.get_one_party_widget(widget_id)
    if not party:
        return custom_response({'error': 'party not found or  request data empty'}, 400)
    if party.signed:
        return custom_response({'error': 'party already signed'}, 400)
    party.signed = True
    party.save()
    contract = ContractModel.get_one_contract(party.contract_id)
    project = ProjectModel.get_one_project(contract.project_id)
    user = UserModel.get_one_user(project.user_id)
    Mailing.send_sign_confirmation(user,contract,party)
    return custom_response({'success' : True}, 200)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )