from abc import ABC, abstractmethod
import requests

class TraktAuth:
    def __init__(self, CLIENT_ID: str, CLIENT_SECRET: str, REDIRECT_URI: str):
        self.CLIENT_ID: str = CLIENT_ID
        self.CLIENT_SECRET: str = CLIENT_SECRET
        self.REDIRECT_URI = REDIRECT_URI
        self.API_URL: str = 'https://api.trakt.tv'
        self.AUTH_URL: str = f'{self.API_URL}/oauth/authorize'
        self.TOKEN_URL: str = f'{self.API_URL}/oauth/token'

    def get_authorization_url(self) -> str:
        """Genera la URL de autorización para redirigir al usuario."""
        return f'{self.AUTH_URL}?response_type=code&client_id={self.CLIENT_ID}&redirect_uri={self.REDIRECT_URI}'

    def get_access_token(self, auth_code: str) -> str | None:
        """Intercambia el código de autorización por un token de acceso en Trakt."""
        data = {
            'code': auth_code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        response = requests.post(self.TOKEN_URL, json=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            return self.access_token
        else:
            print(f"Error al obtener el token: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None