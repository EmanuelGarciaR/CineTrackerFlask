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
        
    def get_movie_details(self, movie_id):
        headers = self.get_headers()
        url = f"https://api.trakt.tv/movies/{movie_id}"
        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            movie_data = response.json()
            return movie_data
        else:
            raise PostersError("Error al obtener las portadas de las películas", "error")

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
        url = f"{self.API_URL}/sync/watchlist/movies"
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

class ImageTMDB:
    def __init__(self):
        self.api_key = os.getenv('TMDB_ID')
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

    def get_movie_images(self, movie_id):
        """Obtiene las imágenes (posters y backdrops) de una película por su ID"""
        url = f"{self.base_url}/movie/{movie_id}/images"
        params = {"api_key": self.api_key}
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            images_data = response.json()
            # Obtener la lista de backdrops
            backdrops = images_data.get('backdrops', [])

            # Crear una lista con las URLs completas de las imágenes
            backdrop_urls = [f"{self.image_base_url}{backdrop['file_path']}" for backdrop in backdrops]

            return backdrop_urls

        else:
            raise ErrorFetchImage("No se pudo obtener las imagenes", "error")

class User(TraktApi):
    def __init__(self, CLIENT_ID, access_token = None):
        super().__init__(CLIENT_ID, access_token)
        self.lists: dict[str, list] = {}
        self.image_tmdb = ImageTMDB()

    def get_watch_list(self):
        """Obtiene y almacena las películas por ver del usuario en una lista."""
        watch_movies = self.get_watchlist_movies()
        if watch_movies:
            list_movies_watch = MovieList("Películas por ver")
            
            for item in watch_movies:
                movie_title = item['movie']['title']
                movie_year = item['movie']['year']
                movie_id = item['movie']['ids']['trakt']

                movie_details = self.get_movie_details(movie_id)
                if movie_details:
                    movie_images = self.image_tmdb.get_movie_images(movie_id)
                    if movie_images:
                        poster_image = movie_images[0]  # Decir si es la primera imagen
                    else:
                        raise ErrorFetchImage("No se pudo obtener las imagenes", "error") #Si no hay imagenes
                    movie = Movie(movie_title, movie_year, poster_image)
                    list_movies_watch.add_movie(movie)
            self.add_list("Películas por ver", list_movies_watch)


    def get_watched_list(self):
        """Obtiene y almacena las películas vistas del usuario en una lista."""
        watched_movies = self.get_watched_movies()
        if watched_movies:
            list_movies_viewed = MovieList("Películas vistas")
            
            for item in watched_movies:
                movie_title = item['movie']['title']
                movie_year = item['movie']['year']
                movie_id = item['movie']['ids']['trakt']

                movie_details = self.get_movie_details(movie_id)
                if movie_details:
                    movie_images = self.image_tmdb.get_movie_images(movie_id)
                    list_movies_viewed.add_movie(movie)
                    
                    if movie_images:
                        poster_image = movie_images[0]  # Decir si es la primera imagen
                    else:
                        raise ErrorFetchImage("No se pudo obtener las imagenes", "error") #Si no hay imagenes
                    
                    movie = Movie(movie_title, movie_year, poster_image)
                    list_movies_viewed.add_movie(movie)
            self.add_list("Películas vistas", list_movies_viewed)

    def get_trend_list(self):
        #Obtiene las películas en tendencia
        trend_movies = self.get_trend_movies()
        if trend_movies:
            list_movies_trend = MovieList("Películas en tendencia")
            
            for item in list_movies_trend:
                movie_title = item['movie']['title']
                movie_year = item['movie']['year']
                movie_id = item['movie']['ids']['trakt']
                print(movie_id)

                movie_details = self.get_movie_details(movie_id)
                if movie_details:
                    movie_images = self.image_tmdb.get_movie_images(movie_id)
                    if movie_images:
                        poster_image = movie_images[0]  # Decir si es la primera imagen
                    else:
                        raise ErrorFetchImage("No se pudo obtener las imagenes", "error") #Si no hay imagenes
                    
                    movie = Movie(movie_title, movie_year, poster_image)
                    list_movies_trend.add_movie(movie)
            self.add_list("Películas en tendencia", list_movies_trend)

    
    def get_name(self):
        info_user = self.get_profile()
        if info_user["name"]:
            return info_user["name"]
        else:
            return None

    def add_list(self, list_name: str, movie_list: list[str]):
        """Agrega una lista de películas al usuario."""
        #dict[str,list[str]]
        self.lists[list_name] = movie_list

    def show_list(self, list_name: str):
        """Muestra una lista específica del usuario."""
        movie_list = self.lists.get(list_name)
        if movie_list:
            movie_list.show_movies()
        else:
            return None
            #Hacer error de no se encontró la lista

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
        return f"{self.title} ({self.year})"


class MovieList:
    """Representa una lista de películas."""
    def __init__(self, name: str):
        self.name: str = name
        self.movies: list[Movie] = []

    def add_movie(self, movie: Movie):
        """Agrega una película a la lista."""
        self.movies.append(movie)

    def show_movies(self):
        """Muestra las películas almacenadas en la lista."""
        if not self.movies:
            #Hacer error de que no hay películas
            raise EmptyList("No hay películas almacenadas en la lista")
        return [movie for movie in self.movies]