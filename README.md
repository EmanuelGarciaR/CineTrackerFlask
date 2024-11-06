# Movie Tracker App

## 1. Descripción

Movie Tracker App es una aplicación diseñada para ayudarte a seguir el rastro de tus películas y series favoritas utilizando la API de Trakt. Permite a los usuarios iniciar sesión con su cuenta de Trakt y gestionar sus listas de contenido, así como leer y escribir reseñas.

### 2. Gestión de Listas de Películas
- **Películas en seguimiento:** Obtiene la lista de películas por ver del usuario desde Trakt.
- **Películas vistas:** Obtiene la lista de películas ya vistas por el usuario.
- **Películas favoritas:** Obtiene las películas marcadas como favoritas.
- **Películas en tendencia:** Muestra las películas que están en tendencia en la plataforma.
- **Películas en cartelera:** Obtiene las películas actualmente en cartelera (Box Office).
- **Películas próximas a estrenar:** Muestra las películas más anticipadas por estrenar.
- **Películas relacionadas:** Muestra las películas relacionadas a Volver al futuro.

### 3. Imágenes de Películas
- Utiliza la API de TMDb para obtener imágenes (posters) de las películas.
- Si no se encuentra una imagen, se muestra una imagen predeterminada.

## Requisitos
- Python 3.11
- Una cuenta de Trakt.tv para la autenticación y acceso a los datos de películas.