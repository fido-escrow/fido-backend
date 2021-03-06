#/src/views/ProjectView.py
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from ..shared.Authentication import Auth
from ..models.ProjectModel import ProjectModel, ProjectSchema
from ..models.UserModel import UserModel, UserSchema
from ..models.ContractModel import ContractModel
from ..shared.Mailing import Mailing

app = Flask(__name__)
project_api = Blueprint('project_api', __name__)
project_schema = ProjectSchema()
user_schema = UserSchema()

@project_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    """
    Get All Projects
    """
    projects = ProjectModel.get_all_projects(g.user.get('id'))
    data = project_schema.dump(projects, many=True)
    return custom_response(data, 200)
    
@project_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
    """
    Create Project Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera project--------------#'+json.dumps(req_data))
    
    req_data['user_id'] = g.user.get('id')

    try:
        data = project_schema.load(req_data)
    except ValidationError as err:
        return custom_response(err, 400)
        
    project = ProjectModel(data)
    project.save()
    data = project_schema.dump(project)
    return custom_response(data, 201)    

@project_api.route('/<int:project_id>', methods=['PUT'])
@Auth.auth_required
def update(project_id):
    """
    Update A project
    """
    req_data = request.get_json()
    proy = ProjectModel.get_one_project(project_id)
    if not proy:
        return custom_response({'error': 'project not found'}, 404)

    if data.get('user_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 403)

    data = project_schema.dump(proy)

    try:
        data = project_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)

    proy.update(data)
    data = project_schema.dump(proy)
    return custom_response(data, 200)
    
@project_api.route('/apply/escrow/<int:project_id>', methods=['POST'])
@Auth.auth_required
def escrow(project_id):
    """
    Escrow A project
    """
    req_data = request.get_json()
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)
    proy = ProjectModel.get_one_project(project_id)
    if not proy:
        return custom_response({'error': 'project not found'}, 404)
    if project.user_id != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 403)
    
    user = UserModel.get_one_user(g.user.get('id'))
    user.update(data)
    proy.escrow=True
    proy.update()

    try:
        Mailing.send_apply_escrow(user,proy)
    except Exception as e:
        return custom_response({'error': 'Correo no enviado, por favor manda un correo a hola@fido.mx con tu nombre, usuario y teléfono, enseguida nosotros te contactámos ASAP. Atte. FIDO.'}, 400)

    return custom_response("success", 200)



@project_api.route('/<int:project_id>', methods=['DELETE'])
@Auth.auth_required
def delete(project_id):
    """
    Update A project
    """
    proy = ProjectModel.get_one_project(project_id)
    if not proy:
        return custom_response({'error': 'project not found'}, 404)

    if data.get('user_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 403)
    
    contracts = ContractModel.get_all_contracts(proy.id)
    if  contracts:
        return custom_response({'error': 'permission denied, you must delete every contract on your project'}, 403)
    
    proy.delete()
    return custom_response({'succes': 'Project deleted'}, 200)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )