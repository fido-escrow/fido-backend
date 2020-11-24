import os
from flask import Flask, render_template
from flask_mail import Message
from ..app import mail


app = Flask(__name__)
url = os.getenv('FRONT_URL')
class Mailing():
    """
    Mail Class
    """
    @staticmethod
    def send_sign_invitation(user,contract,party):
        try:
            app.logger.info('llego la funcion    '+party.email)
            msg = Message("[FIDO] Su Firma ha sido requerida",
            sender="app@fido.mx",
            recipients=[party.email])
            msg.body = 'Hola '+party.name+',\n para el contrato'+contract.name+'tu firma ha sido requerida en '+url+'/signature/'+party.widget_id
            msg.html = render_template('sign_invitation.html', name=party.name, sender=user.name, url=url,widget_id=party.widget_id,contract_name=contract.name)
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)