## Backend de la aplicación de tareas con Flask y SQLAlchemy

Este proyecto implementa un backend para una aplicación de gestión de tareas utilizando Flask y SQLAlchemy. 

### Características

* **Autenticación de usuarios:** Registro e inicio de sesión con seguridad mediante hashing de contraseñas.
* **CRUD de tareas:** Permite crear, leer, actualizar y eliminar tareas.
* **API RESTful:** Utiliza métodos HTTP (POST, GET, PUT, DELETE) para interactuar con los recursos.
* **Base de datos PostgreSQL:** Almacena los datos de usuarios y tareas en una base de datos PostgreSQL.

### Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   ```

2. Crea un entorno virtual:

   ```bash
   python3 -m venv env
   ```

3. Activa el entorno virtual:

   * Linux/macOS: 
     ```bash
     source env/bin/activate
     ```
   * Windows:
     ```bash
     env\Scripts\activate
     ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Configura las variables de entorno:

   * Crea un archivo `.env` en la raíz del proyecto.
   * Define la variable `DATABASE_URL` con la URL de conexión a tu base de datos PostgreSQL. 
     Por ejemplo:
     ```
     DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_de_la_base_de_datos
     ```
   * Define la variable `SECRET_KEY` con una clave secreta aleatoria. 

6. Crea las tablas en la base de datos:

   ```bash
   flask db upgrade 
   ```

### Ejecución

```bash
flask run
```

### Uso

La API RESTful se encuentra disponible en la ruta base del servidor, por ejemplo: `http://127.0.0.1:5000/`. Puedes utilizar herramientas como Postman o curl para interactuar con ella.

### Rutas de la API

| Ruta           | Método | Descripción                      | Autenticación |
| -------------- | ------ | -------------------------------- | -------------- |
| `/register`    | POST   | Registra un nuevo usuario      | No             |
| `/login`       | POST   | Inicia sesión con un usuario   | No             |
| `/logout`      | GET    | Cierra la sesión del usuario  | Sí              |
| `/tasks`       | POST   | Crea una nueva tarea            | Sí              |
| `/tasks`       | GET    | Obtiene todas las tareas        | Sí              |
| `/tasks/<id>`  | GET    | Obtiene una tarea por ID       | Sí              |
| `/tasks/<id>`  | PUT    | Actualiza una tarea por ID       | Sí              |
| `/tasks/<id>`  | DELETE | Elimina una tarea por ID        | Sí              |

### Notas

* Este proyecto está en desarrollo y puede sufrir cambios.
* Se recomienda utilizar un entorno virtual para evitar conflictos de dependencias.
* Asegúrate de configurar correctamente las variables de entorno antes de ejecutar la aplicación.
* Puedes consultar la documentación de Flask y SQLAlchemy para obtener más información sobre su uso.

##### Alejandro Grimaldo