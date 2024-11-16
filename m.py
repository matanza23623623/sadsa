from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Credenciales para el inicio de sesión
USERNAME = "31188252"
PASSWORD = "VOUYOPnA"
TOKEN = None
TOKEN_EXPIRATION = 0  # Tiempo de expiración del token en epoch

def get_token():
    global TOKEN, TOKEN_EXPIRATION
    # Verificar si el token es válido o si ha expirado
    if TOKEN is None or time.time() >= TOKEN_EXPIRATION:
        url_signin = "https://colmen-api.rgn.io/auth/signin"
        headers_signin = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        data_signin = {
            "username": USERNAME,
            "password": PASSWORD
        }
        response = requests.post(url_signin, headers=headers_signin, json=data_signin)

        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get('data', {}).get('token')
            TOKEN_EXPIRATION = time.time() + 3600  # Ajusta el tiempo de validez del token si es necesario
            print("Nuevo token obtenido:", TOKEN)
        else:
            raise Exception("Error en autenticación")
    return TOKEN

# Endpoint para realizar la consulta de Renaper
@app.route('/api/renaper', methods=['GET'])
def renaper():
    try:
        token = get_token()  # Obtener el token automáticamente
        dni = request.args.get("dni")
        sexo = request.args.get("sexo")

        if not dni or sexo not in ['M', 'F']:
            return jsonify({"error": "Parámetros inválidos"}), 400

        url_renaper = "https://colmen-api.rgn.io/renaper/remote"
        headers_renaper = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        data_renaper = {
            "dni": dni,
            "sexo": sexo
        }
        response = requests.post(url_renaper, headers=headers_renaper, json=data_renaper)

        if response.status_code == 200:
            return jsonify(response.json())  # Retorna solo el JSON
        else:
            return jsonify({"error": "Error en la solicitud Renaper"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
