Voy a hacer el proyecto con 2 apps: una para manejar los usuarios y otra para manejar los snippets

Lo primero es crear las apps

- python manage.py startapp accounts
- python manage.py startapp snippets

Voy a cambiar la base de datos para que no use SQLite que es la por defecto, sino que utilice PostgreSQL.
Hay que modificar settings.py

Claramente ha petado, asi que voy a intentar solucionarlo (con un migrate no lo hace)

Fallo mío, que no tenía instalado el servidor postgres.
He creado una database y un usuario.

- CREATE DATABASE codeatlas;
- CREATE USER codeatlas_admin WITH PASSWORD 'codeatlas';
- GRANT ALL PRIVILEGES ON DATABASE codeatlas TO codeatlas_admin;
- ALTER DATABASE codeatlas OWNER TO codeatlas_admin;

He cambiado setting.py y he puesto los parametros de forma directa, no como aparece en la documentación. Próximamente lo
cambiaré, por ahora se queda así

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'codeatlas',
        'USER': 'codeatlas_admin',
        'PASSWORD': 'codeatlas',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Como tengo claras las rutas, voy a declararlas en los urls.py

Haciendo los modelos he caído en que pueden haber campos opcionales
https://medium.com/@maruthurnavin/handling-empty-and-optional-fields-in-django-b7ef7979e83e
https://docs.djangoproject.com/en/6.0/ref/models/fields/

Si se agrega "-" a un atributo fecha del orderby se ordenan desde el mas reciente al mas antiguo

Creo que ya he agregado todas las urls, al menos las que tengo pensadas por ahora.

He encontrado una librería guapisima para hacer highlights del codigo
https://prismjs.com/#full-list-of-features

que brusco es el .reload(), lo siento por quien use la web esta aunque sea para probar

# Lista de funciones MAP

| Función                                    | Descripción                                                | Ejemplo                                                    |
|--------------------------------------------|------------------------------------------------------------|------------------------------------------------------------|
| `map.fitBounds(bounds, options)`           | Ajusta el zoom y centro para mostrar un área específica    | `map.fitBounds(geoLayer.getBounds(), {padding: [50, 50]})` |
| `map.setView([lat, lng], zoom)`            | Mueve el mapa a coordenadas y zoom específicos             | `map.setView([40.4167, -3.7037], 10)`                      |
| `map.panTo([lat, lng])`                    | Desplaza suavemente el mapa a una ubicación                | `map.panTo([41.3851, 2.1734])`                             |
| `map.getCenter()`                          | Obtiene el centro actual del mapa                          | `const center = map.getCenter()`                           |
| `map.getZoom()`                            | Obtiene el nivel de zoom actual                            | `const zoom = map.getZoom()`                               |
| `map.getBounds()`                          | Obtiene los límites visibles del mapa                      | `const bounds = map.getBounds()`                           |
| `map.locate({setView: true})`              | Solicita la ubicación del usuario (geolocalización)        | `map.locate({setView: true, maxZoom: 14})`                 |
| `map.invalidateSize()`                     | Recalcula el tamaño del mapa (útil tras cambios en el DOM) | `map.invalidateSize()`                                     |
| `map.remove()`                             | Destruye el mapa y libera recursos                         | `map.remove()`                                             |
| `map.on(event, fn)` / `map.off(event, fn)` | Añade o elimina eventos del mapa                           | `map.on('zoomend', () => console.log('Zoom cambiado'))`    |

# Lista de funciones CAPAS Y MARCADORES

| Función                                              | Descripción                                  | Ejemplo                                                  |
|------------------------------------------------------|----------------------------------------------|----------------------------------------------------------|
| `L.marker([lat, lng], options).addTo(map)`           | Crea un marcador estándar                    | `L.marker([40.4167, -3.7037]).addTo(map)`                |
| `L.circleMarker([lat, lng], options)`                | Marcador circular personalizable             | `L.circleMarker([lat, lng], {radius: 10, color: 'red'})` |
| `L.circle([lat, lng], {radius: metros})`             | Círculo con radio en metros                  | `L.circle([lat, lng], {radius: 500})`                    |
| `L.polygon(coords).addTo(map)`                       | Dibuja polígonos personalizados              | `L.polygon([[lat1,lng1], [lat2,lng2], ...])`             |
| `layer.addTo(map)` / `map.removeLayer(layer)`        | Añade o elimina una capa del mapa            | `map.removeLayer(geoLayer)`                              |
| `layerGroup.addLayer(layer)` / `.removeLayer(layer)` | Gestiona capas dentro de un grupo            | `layerGroup.addLayer(marker)`                            |
| `L.geoJSON(data, options)`                           | Renderiza datos GeoJSON con estilos y popups |                                                          |

# Lista de funciones POPUPS

| Función                               | Descripción                                  | Ejemplo                                                    |
|---------------------------------------|----------------------------------------------|------------------------------------------------------------|
| `layer.bindPopup(content)`            | Vincula un popup a una capa                  | `marker.bindPopup('<b>Hola</b>')`                          |
| `layer.openPopup()` / `.closePopup()` | Abre o cierra manualmente el popup           | `marker.openPopup()`                                       |
| `layer.bindTooltip(text, options)`    | Añade un tooltip que aparece al hover        | `marker.bindTooltip('Python snippet', {permanent: false})` |
| `popup.setContent(content)`           | Actualiza el contenido de un popup existente | `popup.setContent('<nuevo>HTML</nuevo>')`                  |

# Eventos

| Evento                            | Se dispara cuando...                | Uso práctico                        |
|-----------------------------------|-------------------------------------|-------------------------------------|
| `click`                           | Usuario hace clic en el mapa o capa | Crear snippet en coordenadas        |
| `popupopen` / `popupclose`        | Se abre/cierra un popup             | Cargar datos dinámicos al abrir     |
| `moveend`                         | El mapa deja de moverse             | Recargar datos por bbox             |
| `zoomend`                         | Cambia el nivel de zoom             | Mostrar/ocultar capas según zoom    |
| `locationfound` / `locationerror` | Resultado de `map.locate()`         | Mostrar marcador de usuario o error |
| `layeradd` / `layerremove`        | Se añade/elimina una capa           | Sincronizar UI con estado del mapa  |

Para el index de snippets a lo mejor me conviene usar Paginator
https://docs.djangoproject.com/en/6.0/topics/pagination/

Swal para hacer toasts
https://sweetalert2.github.io/#configuration

He cambiado a async y await para probar el tema asincrono en js

Me acabo de dar cuenta de que no he hecho push estos dias madre mia