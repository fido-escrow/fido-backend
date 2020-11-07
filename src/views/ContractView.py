#/src/views/ContractView.py
import os
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from ..shared.Authentication import Auth
from ..models.ContractModel import ContractModel, ContractSchema

app = Flask(__name__)
contract_api = Blueprint('contract_api', __name__)
contract_schema = ContractSchema()
temp_folder = "/fido/fido-backend/temp"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)



@contract_api.route('/<int:project_id>', methods=['GET'])
@Auth.auth_required
def get_all(project_id):
    """
    Get All contracts
    """
    contracts = ContractModel.get_all_contracts(project_id)
    data = contract_schema.dump(contracts, many=True)
    return custom_response(data, 200)

@contract_api.route('/<int:project_id>', methods=['POST'])
def create(project_id):
    """
    Create Contract Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera contract--------------#'+json.dumps(req_data))
    
    req_data['user_id'] = g.user.get('id')
    
    try:
        data = contract_schema.load(req_data)
    except ValidationError as err:
        return custom_response(err, 400)
        
    contract = ContractModel(data)
    contract.save()
    data = contract_schema.dump(contract)
    return custom_response(data, 201)

@contract_api.route('/upload/<int:project_id>', methods=['POST'])
@Auth.auth_required
def upload(project_id):
    uploaded_file = request.files['file']
    contract = ContractModel({})
    contract.name = uploaded_file.filename
    contract.project_id = project_id
    contract.content=''
    contract.mifiel_signed=False
    contract.graph_signed=False
    contract.mifiel_id='121283657126321356123786152'
    contract.status = '0'
    contract.typo = '1'
    
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(temp_folder, uploaded_file.filename))
#   vemos si sube a mifiel y nos regresa el id se guarda
#   guardamos eese id en contract
#   regresamos el data
    contract.save()
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