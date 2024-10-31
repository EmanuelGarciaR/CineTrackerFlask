import os

from flask import Flask, render_template, request, redirect, url_for, flash
from cine_traker import TraktAuth
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('FLASH_SECRET')

load_dotenv()
# Para crear instancia de TraktAuth
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('SECRET_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')
trakt_auth = TraktAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.route('/')
def home():
    # Generar la URL de autorización
    auth_url = trakt_auth.get_authorization_url()
    return render_template('auth_template.html', auth_url=auth_url)


@app.route('/get-token', methods=['POST'])
def get_token():
    # Obtener el código ingresado por el usuario en el formulario
    auth_code = request.form.get('auth_code')

    if not auth_code:
        flash('Por favor, ingresa el código de autorización.', "error")
        return redirect(url_for('home'))

    # Obtener el token de acceso usando el código de autorización
    access_token = trakt_auth.get_access_token(auth_code)

    if access_token:
        flash(f"Bienvenido", "success")
        #Si se quiere mostrar el {access_token}
    else:
        flash('Error al obtener el token de acceso. Intenta nuevamente.', "error")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)