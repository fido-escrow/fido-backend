#/src/views/ProjectView.py
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from ..shared.Authentication import Auth
from ..models.ProjectModel import ProjectModel, ProjectSchema

app = Flask(__name__)
project_api = Blueprint('project_api', __name__)
project_schema = ProjectSchema()


@project_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    """
    Get All Projects
    """
    projects = ProjectModel.get_all_projects(g.user.get('id'))
    data = project_schema.dump(projects, many=True)
    return custom_response(data, 200)

# @blogpost_api.route('/<int:blogpost_id>', methods=['GET'])
# def get_one(blogpost_id):
#     """
#     Get A Blogpost
#     """
#     post = BlogpostModel.get_one_blogpost(blogpost_id)
#     if not post:
#         return custom_response({'error': 'post not found'}, 404)
#     data = blogpost_schema.dump(post)
#     return custom_response(data, 200)
    
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
    data = project_schema.dump(proy)
    if data.get('user_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    try:
        data = project_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)

    proy.update(data)
    data = project_schema.dump(proy)
    return custom_response(data, 200)

# @blogpost_api.route('/<int:blogpost_id>', methods=['DELETE'])
# @Auth.auth_required
# def delete(blogpost_id):
#     """
#     Delete A Blogpost
#     """
#     post = BlogpostModel.get_one_blogpost(blogpost_id)
#     if not post:
#         return custom_response({'error': 'post not found'}, 404)
#     data = blogpost_schema.dump(post)
#     if data.get('user_id') != g.user.get('id'):
#         return custom_response({'error': 'permission denied'}, 400)

#     post.delete()
#     return custom_response({'message': 'deleted'}, 204)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )