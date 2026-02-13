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
