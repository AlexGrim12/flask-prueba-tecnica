import os
from datetime import datetime

from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from functools import (
    wraps,
)  # Importar wraps para preservar el nombre de la función original
# env
from dotenv import load_dotenv

# Configuración de Flask
app = Flask(__name__)
# env
load_dotenv()
# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.getenv("DATABASE_URL")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(
    24
)  # Clave secreta para la sesión (genera una clave segura en producción)
db = SQLAlchemy(app)


# Modelo de datos para las tareas
class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.strftime("%Y-%m-%d") if self.deadline else None,
            "priority": self.priority,
            "is_completed": self.is_completed,
        }


# Modelo de usuario
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Crea las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()


# Decorador para requerir inicio de sesión
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Se requiere iniciar sesión"}), 401
        return func(*args, **kwargs)

    return wrapper


# Ruta para registrar un nuevo usuario
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Se requieren nombre de usuario y contraseña"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuario registrado correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar el usuario: {e}"}), 500


# Ruta para iniciar sesión
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Se requieren nombre de usuario y contraseña"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Inicio de sesión exitoso"}), 200


# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Cierre de sesión exitoso"}), 200


# Rutas de la API para las tareas (protegidas con @login_required)
@app.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    user_id = session["user_id"]

    try:
        new_task = Task(
            user_id=user_id,
            title=data["title"],
            description=data.get("description"),
            deadline=(
                datetime.strptime(data["deadline"], "%Y-%m-%d")
                if data.get("deadline")
                else None
            ),
            priority=data["priority"],
            is_completed=data.get("is_completed", False),
        )
        db.session.add(new_task)
        db.session.commit()
        return (
            jsonify({"message": "Tarea creada correctamente", "task_id": new_task.id}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear la tarea: {e}"}), 500


@app.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    user_id = session["user_id"]
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    user_id = session["user_id"]
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        return jsonify(task.to_dict()), 200
    else:
        return jsonify({"error": "Tarea no encontrada"}), 404


@app.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    user_id = session["user_id"]
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.deadline = (
        datetime.strptime(data["deadline"], "%Y-%m-%d")
        if data.get("deadline")
        else task.deadline
    )
    task.priority = data.get("priority", task.priority)
    task.is_completed = data.get("is_completed", task.is_completed)

    try:
        db.session.commit()
        return jsonify({"message": "Tarea actualizada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar la tarea: {e}"}), 500


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    user_id = session["user_id"]
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Tarea eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar la tarea: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=False)
