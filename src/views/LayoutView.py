#/src/views/LayoutView.py
from flask import Flask, request, g, Blueprint, json, Response
from marshmallow import ValidationError
from ..shared.Authentication import Auth
from ..models.LayoutModel import LayoutModel, LayoutSchema

app = Flask(__name__)
layout_api = Blueprint('layout_api', __name__)
layout_schema = LayoutSchema()
    
@layout_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
    """
    Create layout Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera layout--------------#'+json.dumps(req_data))
    
    if g.user.get('id')!=0:
        return custom_response(err, 403)

    req_data['user_id'] = g.user.get('id')
    
    try:
        data = layout_schema.load(req_data)
    except ValidationError as err:
        return custom_response(err, 400)
        
    layout = LayoutModel(data)
    layout.save()
    data = layout_schema.dump(layout)
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