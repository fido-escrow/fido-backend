import os
from flask import Flask, render_template
from flask_mail import Message
from ..app import mail


app = Flask(__name__)
url = os.getenv('FRONT_URL')
urlb = os.getenv('BACK_URL')

class Mailing():
    """
    Mail Class
    """
    @staticmethod
    def send_sign_invitation(user,contract,party):
        try:
            app.logger.info('llego la funcion  invitation  '+party.email)
            msg = Message("[FIDO] "+party.name+" Su Firma ha sido requerida",
            sender="app@fido.mx",
            recipients=[party.email])
            msg.body = 'Hola '+party.name+',\n para el contrato'+contract.name+'tu firma ha sido requerida en '+url+'/signature/'+party.widget_id
            msg.html = render_template('sign_invitation.html', name=party.name, sender=user.name, url=url,widget_id=party.widget_id,contract_name=contract.name)
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)

    @staticmethod
    def send_sign_confirmation(user,contract,party):
        try:
            app.logger.info('llego la funcion  confirmation  '+user.email)
            msg = Message("[FIDO] "+party.name+" ha firmado el documento",
            sender="app@fido.mx",
            recipients=[user.email])
            msg.body = 'Hola '+user.name+',\n el contrato '+contract.name+' ha sido firmado con éxito por '+party.name
            msg.html = render_template('sign_confirmation.html', name=user.name, sender=party.name, url=url, contract_name=contract.name)
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)

    @staticmethod
    def send_delete_doc(user,contract,party):
        try:
            app.logger.info('llego la funcion  delete  '+user.email)
            msg = Message("[FIDO] "+user.name+" ha eliminado el documento",
            sender="app@fido.mx",
            recipients=[party.email])
            msg.body = 'Hola '+party.name+',\n el contrato '+contract.name+' ha sido elminado por '+party.name+'. \n  No es necesaria ninguna acción de tu parte.'
            msg.html = render_template('delete_doc.html', name=party.name, sender=user.name, contract_name=contract.name)
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)

    @staticmethod
    def send_sign_final(email,contract,pdf,xml):
        try:
            msg = Message("[FIDO] todos los participantes han firmado el documento",
            sender="app@fido.mx",
            recipients=[email])
            msg.body = 'Hola ,\n el contrato '+contract+' ha sido firmado con éxito por todos los participantes, FIDO no guarda documentos por lo que es importante que guardes los documentos adjuntos.'
            msg.html = render_template('sign_final.html', contract_name=contract)
            with app.open_resource(pdf) as fp:   
                msg.attach(contract+'_signed.pdf', "application/pdf", fp.read())
            with app.open_resource(xml) as fp:   
                msg.attach(contract+'.xml', "application/xml", fp.read())
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)

    @staticmethod
    def send_apply_escrow(user,project):
        try:
            app.logger.info('llego la funcion  escrow ')
            msg = Message("[FIDO] Solicitud de escrow",
            sender="app@fido.mx",
            recipients=['hola@fido.mx','nacho@fido.mx'])
            msg.body = 'Hola admin el usuario '+user.name+' ha solicitado escrow en el proyecto '+project.name+' contactar al mail: '+user.mail+' o altelefono: '+ user.phone
            msg.html = render_template('apply_escrow.html', user=user.name, project=project.name, mail=user.mail, phone=user.phone)
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
            raise Exception(e)
    