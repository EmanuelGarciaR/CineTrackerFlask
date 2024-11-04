import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from cine_traker import TraktAuth, User
from dotenv import load_dotenv
from errors.error import *

app = Flask(__name__)
app.secret_key = os.getenv('FLASH_SECRET')

load_dotenv()
# Para crear instancia de TraktAuth
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('SECRET_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')
trakt_auth = TraktAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.route('/')
def url_auth():
    # Generar la URL de autorización
    auth_url = trakt_auth.get_authorization_url()
    return render_template('auth_template.html', auth_url=auth_url)


@app.route('/get-token', methods=['POST'])
def get_token():
    # Obtener el código ingresado por el usuario en el formulario
    auth_code = request.form.get('auth_code')

    if not auth_code:
        flash('Por favor, ingresa el código de autorización.', "error")
        return redirect(url_for('url_auth'))

    try:
        # Obtener el token de acceso usando el código de autorización
        access_token = trakt_auth.get_access_token(auth_code)
        session['access_token'] = access_token
        flash(f"Bienvenido", "success")
        return redirect(url_for('home'))
    except TokenRequestError as err:
        flash(err.args[0], err.args[1])
        return redirect(url_for('url_auth'))

@app.route("/home_page")
def home():
    if 'access_token' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('url_auth'))
    user = User(CLIENT_ID, session['access_token'])
    try:
        user.get_movies_viewed()  # Obtener las películas vistas
        viewed_movies = user.show_list("Películas vistas")  # Usar un valor por defecto vacío
    except ErrorFetchImage as err:
        flash(err.args[0], err.args[1])
        viewed_movies = []  # En caso de error, no mostrar películas

    return render_template("base_main.html", viewed_movies=viewed_movies)

@app.route("/viewed_movies")
def viewed_movies():
    if 'access_token' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('url_auth'))
    
    user = User(CLIENT_ID, session['access_token'])
    try:
        user.get_movies_viewed()  # Método para obtener las películas vistas
        viewed_movies = user.show_list("Películas vistas")
    except ErrorFetchImage as err:
        flash(err.args[0], err.args[1])
        viewed_movies = []  # En caso de error, no mostrar películas

    return render_template("movies_viewed.html", movies=viewed_movies)

if __name__ == '__main__':
    app.run(debug=True)