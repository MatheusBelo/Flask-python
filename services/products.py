import requests
import os
from flask import Flask, jsonify, request, make_response
import jwt
from functools import wraps
import json
from jwt.exceptions import DecodeError


app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))


@app.route("/")
def home():
    return 'Olá, este é o meu microsserviço em Flask'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)


BASE_URL = "https://dummyjson.com"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'error': 'O token de autorizacao esta faltando'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except DecodeError:
            return jsonify({'error': 'O token de autorizacao e invalido'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated


@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user_id):
    headers = {'Authorization': f'Bearer {request.cookies.get("token")}'}
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code != 200:
        return jsonify({'error': response.json()['message']}), response.status_code
    products = []
    for product in response.json()['products']:
        product_data = {
            'id': product['id'],
            'title': product['title'],
            'brand': product['brand'],
            'price': product['price'],
            'description': product['description']
        }
        products.append(product_data)
    return jsonify({'data': products}), 200 if products else 204


app.config['SECRET_KEY'] = os.urandom(24)

with open('users.json', 'r') as f:
    users = json.load(f)


@app.route('/auth', methods=['POST'])
def authenticate_user():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415
    username = request.json.get('username')
    password = request.json.get('password')
    for user in users:
        if user['username'] == username and user['password'] == password:
            token = jwt.encode({'user_id' : user['id']}, app.config['SECRET_KEY'],algorithm="HS256")
            response = make_response(json({'message': 'Autenticacao ocorreu com sucesso'}))
            response.set_cookie('token',token)
            return response, 200
    return json({'error': 'Usuario ou senha invalidos'}), 401    