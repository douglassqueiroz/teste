import base64
import cv2
import os
import threading
import logging

from datetime import datetime
from threading import Thread, Lock 
from flask import Flask, make_response, render_template, Response, request, jsonify, redirect, url_for
from queue import Queue
from crud_users import adicionar_usuario, remover_usuario, atualizar_usuario, caminho_banco_usuarios, listar_usuarios, matricula_existe
from flask_sqlalchemy import SQLAlchemy
from os import environ
from crud_users import db
from permissao import verificar_permissao_pasta

app = Flask(__name__)

#########################################################################
#CONFIGURAÇÕES DO BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id  = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = name
    
    def json(self):
        return {'name': self.name}
db.create_all()

#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'teste route'}),200)
#########################################################################




#########################################################################
# Define o caminho onde a foto será salva (altere conforme necessário)
caminho = r'C:\Users\douglas.queiroz\Documents\amanda_empilhadeira\CodWork\empilhadeiras\ProjectWork-main\ProjectWork-main\images'
###########################################################################


@app.route('/')
def index():
    return render_template('index.html')

#########################################################################
#########################################################################
#########################################################################
#########################################################################
################CRIANDO O BACKEND - SALVANDO AS FOTOS###################3

camera = cv2.VideoCapture(0)

def gen_frames():
    #global frame, lock
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
         
        
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
################CRIANDO O BACKEND - SALVANDO AS FOTOS###################



# Rota para salvar a foto
@app.route('/save_photo', methods=['POST'])
def save_photo():
    try:
        # Obtém os dados da foto da solicitação JSON
        data = request.get_json()
        photo_data = data['photoData']



        # Converte os dados base64 para bytes
        photo_bytes = photo_data.split(',')[1].encode('utf-8')

        # Gera um nome de arquivo único com carimbo de data e hora
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Adiciona microssegundos para garantir exclusividade
        photo_filename = f'photo_{timestamp}.png'
        # Salva a foto no caminho especificado
        if verificar_permissao_pasta(caminho):
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_path = os.path.join(caminho, f'photo_{current_datetime}.png')
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(photo_bytes))
 # Adicione este print para indicar que a foto foi salva com sucesso
            print("Foto salva com sucesso!", photo_filename)               
            return jsonify(success=True)
        else:
            error_message = "sem premissão para acessar a pasta."
            print(f"Erro ao salvar a foto: {error_message}")
            return jsonify(success=False, error=error_message)
    except Exception:
        error_message = str(Exception)
        print(f"Erro ao salvar a foto: {error_message}")
        return jsonify(success=False, error=error_message)
#ENCERRANDO CÓDIGO SOBRE AS FOTOS
#########################################################################
#########################################################################
#########################################################################
#########################################################################

#########################################################################
#########################################################################
#########################################################################
#########################################################################
################     INICIANDO O CRUD     ###############################
@app.route('/create_user', methods = ['POST'])
def create_user():  
  try:
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'message': 'user created'}), 201)
  except Exception:
    return make_response(jsonify({'message': 'error creating user'}), 500)

##############VERIFICANDO SE MATRICULA EXISTE PARA MOSTRAR AO USUARIO##############
@app.route('/verificar_matricula/<matricula>', methods=['GET'])


@app.route('/listar_usuarios', methods=['GET'])
def get_users():
  try:
    users = User.query.all()
    return make_response(jsonify([user.json() for user in users]), 200)
  except Exception:
    return make_response(jsonify({'message': 'error getting users'}), 500)


@app.route('/delete_user/<matricula>', methods=['DELETE'])
def delete_user(matricula):
  try:
    user = User.query.filter_by(matricula=matricula).first()
    if user:
      db.session.delete(user)
      db.session.commit()
      return make_response(jsonify({'message': 'user deleted'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except Exception:
    return make_response(jsonify({'message': 'error deleting user'}), 500)
    
@app.route('/update_user/<matricula_antiga>', methods=['PUT'])
def update_user(matricula):
  try:
    user = User.query.filter_by(matricula=matricula).first()
    if user:
      data = request.get_json()
      user.username = data['username']
      user.email = data['email']
      db.session.commit()
      return make_response(jsonify({'message': 'user updated'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except Exception:
    return make_response(jsonify({'message': 'error updating user'}), 500)

#ENCERRANDO O CRUD
#########################################################################
#########################################################################
#########################################################################
#########################################################################


if __name__ == '__main__':
    cert_path = r'C:\Users\douglas.queiroz\Documents\amanda\empilhadeiras\ProjectWork-main\certificado.pem'
    key_path = r'C:\Users\douglas.queiroz\Documents\amanda\empilhadeiras\ProjectWork-main\chave_privada.pem'
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=(cert_path, key_path) )