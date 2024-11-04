from errors.error import *
import requests
import os

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
            raise TokenRequestError(f"Error al obtener el token para acceder", "error")


class TraktApi:
    def __init__(self, CLIENT_ID: str, access_token: str= None):
        self.CLIENT_ID: str = CLIENT_ID
        self.access_token: str = access_token
        self.API_URL: str| None = "https://api.trakt.tv"

    def get_headers(self) -> dict[str, str]:
        """Genera los headers para las solicitudes a la API de Trakt."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "trakt-api-version": "2",
            "trakt-api-key": self.CLIENT_ID
        }

    def get_profile(self) -> dict[str, str] | None:
        """Obtiene la información del perfil del usuario autenticado."""
        headers = self.get_headers()
        url = f"{self.API_URL}/users/id"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Retorna el perfil del usuario
        else:
            raise ApiRequestError("Error al obtener el perfil de usuario", "error")
        
    def get_user_id(self):
        profile = self.get_profile()
        if profile and "ids" in profile:
            return profile["ids"].get("slug")  # Extrae el 'slug' del perfil
        else:
            raise ApiRequestError("No se pudo obtener el ID del usuario", "error")

    def get_watched_movies(self) -> list[dict[str, str]] | None:
        """Obtiene las películas YA vistas por el usuario"""
        headers = self.get_headers()
        url = f"{self.API_URL}/sync/watched/movies"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas vistas
        else:
            raise ApiRequestError("Error al obtener la lista de peliculas vistas", "error")

    def get_watchlist_movies(self) -> list[dict[str, str]] | None:
        """Obtiene la lista de seguimiento del usuario"""
        headers = self.get_headers()
        url = f"{self.API_URL}/users/EmaGarcia/watchlist/movies/rank"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas en la lista de seguimiento
        else:
            raise ApiRequestError("Error al obtener la lista de películas en seguimiento", "error")

    def get_trend_movies(self) -> list[dict[str, str]] | None:
        """Obtiene las películas en tendencia"""
        headers = self.get_headers()
        url = f"{self.API_URL}/movies/trending"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas en tendencia
        else:
            raise ApiRequestError("Error al obtener la lista de películas en tendencia", "error")

import os
import requests

class ImageTMDB:
    def __init__(self):
        self.api_key = os.getenv('TMDB_ID')  # API Key para solicitudes
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

    def get_movie_images(self, movie_id):
        """Obtiene las imágenes (posters y backdrops) de una película por su ID."""
        url = f"{self.base_url}/movie/{movie_id}/images"
        params = {
            "api_key": self.api_key,  # Solo API Key aquí
        }

        if not self.api_key:  # Verificar que la API Key no sea None
            raise ValueError("API Key de TMDB no está configurada.")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lanza una excepción si el código de estado no es 200

            images_data = response.json()
            backdrops = images_data.get('backdrops', [])

            backdrop_urls = [
                f"{self.image_base_url}{backdrop['file_path']}" 
                for backdrop in backdrops if 'file_path' in backdrop
            ]
            return backdrop_urls
        except requests.exceptions.HTTPError as e:
            # Agregar información sobre el error específico
            raise ErrorFetchImage(f"Error al realizar la solicitud: {e}", "error")
        except Exception as e:
            raise ErrorFetchImage(f"Error inesperado: {e}", "error")

class User(TraktApi):
    def __init__(self, CLIENT_ID, access_token = None):
        super().__init__(CLIENT_ID, access_token)
        self.lists: dict[str, list] = {}
        self.image_tmdb = ImageTMDB()
        
    def get_watch_list(self):
        """Obtiene y almacena las películas por ver del usuario en una lista."""
        watch_movies = self.get_watchlist_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if watch_movies:
            for item in watch_movies:
                movie_title = item['movie']['title']
                movie_year = item['movie']['year']
                movie_id = item['movie']['ids']['tmdb']

                try:
                    movie_images = self.image_tmdb.get_movie_images(movie_id)
                    poster_image = movie_images[0] if movie_images else "static/img/fondo_gris.jpg"
                    
                    # Agregar la información de la película a la lista
                    movies_data.append({
                        'title': movie_title,
                        'year': movie_year,
                        'poster_image': poster_image
                    })
                except ErrorFetchImage as e:
                    print(f"Error al obtener imágenes para {movie_title}: {e}")

        return movies_data

    # def get_watch_list(self):
    #     """Obtiene y almacena las películas por ver del usuario en una lista."""
    #     watch_movies = self.get_watchlist_movies()
    #     movies_data = []  # Lista para almacenar los datos de las películas

    #     if watch_movies:
    #         for item in watch_movies:
    #             movie_title = item['movie']['title']
    #             movie_year = item['movie']['year']
    #             movie_id = item['movie']['ids']['tmdb']

    #             movie_images = self.image_tmdb.get_movie_images(movie_id)
    #             poster_image = movie_images[0] if movie_images else "static/img/fondo_gris.jpg"
                
    #             # Agregar la información de la película a la lista
    #             movies_data.append({
    #                 'title': movie_title,
    #                 'year': movie_year,
    #                 'poster_image': poster_image
    #             })

    #     return movies_data

    
    def get_name(self):
        info_user = self.get_profile()
        return info_user.get("name")

    # def add_list(self, list_name: str, movie_list):
    #     """Agrega una lista de películas al usuario."""
    #     #dict[str,list[str]]
    #     self.lists[list_name] = movie_list

    def show_list(self, list_name: str):
        """Muestra la lista de películas solicitada."""
        if list_name in self.lists:
            return self.lists[list_name].show_movies()
        else:
            raise ListNotFoundError(f"La lista '{list_name}' no fue encontrada", "error")


    def show_all_lists(self):
        """Muestra todas las listas de películas del usuario"""
        all_lists = []  # Almacenamos las listas
        for name, movie_list in self.lists.items(): #(name, movie_list)->Tupla
            movies = movie_list.show_movies()  # Obtener las películas de la lista
            all_lists.append({'name': name, 'movies': movies})  # Agregar a la lista acumulada
        return all_lists



class Movie:
    """Representa una película con su título y año."""
    def __init__(self, title: str, year: str, poster_image: str= None):
        #Poner en el construcro poster_img
        #self.poster: str = poster
        self.title: str = title
        self.year: str = year
        self.poster_image: str = poster_image

    def __str__(self):
        if self.poster_image:
            return f"{self.title} ({self.year}) - Poster: {self.poster_image}"
        return f"{self.title} ({self.year})"

class MovieList:
    """Representa una lista de películas."""
    def __init__(self, name: str):
        self.name: str = name
        self.movies: list[Movie] = []

    # def add_movie(self, movie: Movie):
    #     """Agrega una película a la lista."""
    #     self.movies.append(movie)

    # def show_movies(self):
    #     """Muestra las películas almacenadas en la lista."""
    #     if not self.movies:
    #         #Hacer error de que no hay películas
    #         raise EmptyList("No hay películas almacenadas en la lista")
    #     return [movie for movie in self.movies]