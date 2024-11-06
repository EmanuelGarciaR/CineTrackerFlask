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

    def get_user_info(self):
        """Obtiene la información del perfil del usuario autenticado."""
        headers = self.get_headers()
        url = f"{self.API_URL}/users/settings"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            username = data["user"]["username"]
            user_id = data["user"]["ids"]["slug"]
            
            profile_info = {
                "user_name" : username, 
                "user_id" : user_id
                }
            return profile_info
        else:
            raise ApiRequestProfileError("Error al obtener el perfil de usuario", "error")

    def get_watched_movies(self) -> list[dict[str, str]] | None:
        """Obtiene las películas YA vistas por el usuario"""
        user_info = self.get_user_info()
        user_id = user_info.get("user_id")
        
        headers = self.get_headers()
        url = f"{self.API_URL}/users/{user_id}/watched/movies"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas vistas
        else:
            raise ApiRequestError("Error al obtener la lista de peliculas vistas", "error")

    def get_watchlist_movies(self) -> list[dict[str, str]] | None:
        """Obtiene la lista de seguimiento del usuario"""
        user_info = self.get_user_info()
        user_id = user_info.get("user_id")
        headers = self.get_headers()
        url = f"{self.API_URL}/users/{user_id}/watchlist/movies/rank"
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

    def get_favorited_movies(self)-> list[dict[str, str]] | None:
        """Obtiene las películas favoritas"""
        headers = self.get_headers()
        url = f"{self.API_URL}/movies/favorited/weekly"
        response = requests.get(url, headers= headers)
    
        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas favoritas
        else:
            raise ApiRequestError("Error al obtener la lista de películas favoritas", "error")

    def get_cinema_movies(self)-> list[dict[str, str]] | None:
        """Obtiene las películas favoritas"""
        headers = self.get_headers()
        url = f"{self.API_URL}/movies/boxoffice"
        response = requests.get(url, headers= headers)
    
        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas favoritas
        else:
            raise ApiRequestError("Error al obtener la lista de películas en cartelera", "error")

    def get_anticipated_movies(self)-> list[dict[str, str]] | None:
        """Obtiene las películas favoritas"""
        headers = self.get_headers()
        url = f"{self.API_URL}/movies/anticipated"
        response = requests.get(url, headers= headers)
    
        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas favoritas
        else:
            raise ApiRequestError("Error al obtener la lista de películas próximas a estrenar", "error")

    def get_recommended_movies(self)-> list[dict[str, str]] | None:
        """Obtiene las películas favoritas"""
        headers = self.get_headers()
        url = f"{self.API_URL}/recommendations/movies?ignore_collected=false&ignore_watchlisted=false"
        response = requests.get(url, headers= headers)
    
        if response.status_code == 200:
            return response.json()  # Lista de diccionarios con las películas favoritas
        else:
            raise ApiRequestError("Error al obtener la lista de películas próximas a estrenar", "error")

    def get_related_movies(self)-> list[dict[str, str]] | None:
        """Obtiene las películas relacionadas en colombia"""
        user_info = self.get_user_info()
        user_id = user_info.get("user_id")
        headers = self.get_headers()
        url = f"{self.API_URL}/movies/308/related"
        response = requests.get(url, headers= headers)
    
        if response.status_code == 200:
            return response.json()
        else:
            raise ApiRequestError("Error al obtener la lista de películas próximas a estrenar", "error")

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

    def get_watched_list(self):
        """Obtiene y almacena las películas YA VISTAS del usuario en una lista."""
        watched_movies = self.get_watched_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if watched_movies:
            for item in watched_movies:
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

    def get_trend_list(self):
        """Obtiene y almacena las películas en tendencia del usuario en una lista."""
        trend_movies = self.get_trend_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if trend_movies:
            for item in trend_movies[:10]:
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

    def get_favorited_list(self):
        """Obtiene y almacena las películas YA VISTAS del usuario en una lista."""
        fav_movies = self.get_favorited_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if fav_movies:
            for item in fav_movies:
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
    
    def get_cinema_list(self):
        """Obtiene y almacena las películas YA VISTAS del usuario en una lista."""
        cine_movies = self.get_cinema_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if cine_movies:
            for item in cine_movies[:10]:
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
    
    def get_anticipated_list(self):
        """Obtiene y almacena las películas prontas a estrenar en cine en una lista."""
        cine_movies = self.get_anticipated_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if cine_movies:
            for item in cine_movies[:10]:
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

    def get_recommended_list(self):
        """Obtiene y almacena las películas prontas a estrenar en cine en una lista."""
        cine_movies = self.get_recommended_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if cine_movies:
            for item in cine_movies[:10]:
                movie_title = item['title']
                movie_year = item['year']
                movie_id = item['ids']['tmdb']

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

    def get_related_list(self):
        """Obtiene y almacena las películas relacionadas en una lista."""
        related_movies = self.get_related_movies()
        movies_data = []  # Lista para almacenar los datos de las películas

        if related_movies:
            for item in related_movies[:10]:
                movie_title = item['title']
                movie_year = item['year']
                movie_id = item['ids']['tmdb']

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

class Movie:
    """Representa una película con su título, año y poster."""
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