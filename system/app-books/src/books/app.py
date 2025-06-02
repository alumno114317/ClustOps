import os
from typing import Literal
import socket
import json
from flask import Flask, jsonify, request
from flask.wrappers import Response
import logging

app = Flask(__name__)

# Configuración del logger de Flask
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Ruta al archivo de datos persistentes dentro del contenedor (donde se monta el PVC)
DATA_FILE_PATH = "/data/books.json"

# Lista inicial de libros (solo se usa si el archivo de datos no existe)
initial_books: list[dict] = [
    {"id": 1, "title": "Harry Potter and the Philosopher's ", "author": "J.K. Rowling"},
    {"id": 2, "title": "Harry Potter and the Chamber of Secrets", "author": "J.K. Rowling"},
    {"id": 3, "title": "Harry Potter and the Prisoner of Azkaban", "author": "J.K. Rowling"},
    {"id": 4, "title": "Harry Potter and the Goblet of Fire", "author": "J.K. Rowling"},
    {"id": 5, "title": "Harry Potter and the Order of the Phoenix", "author": "J.K. Rowling"},
    {"id": 6, "title": "Harry Potter and the Half-Blood Prince", "author": "J.K. Rowling"},
    {"id": 7, "title": "Harry Potter and the Deathly Hallows", "author": "J.K. Rowling"},
]
app.logger.info(f"Definición de initial_books contiene {len(initial_books)} libros.")

books: list[dict] = [] # Se cargará desde el archivo o se inicializará

def load_books_from_file():
    """Carga los libros desde el archivo JSON. Si no existe o hay error, usa la lista inicial."""
    global books
    try:
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, 'r') as f:
                books = json.load(f)
            app.logger.info(f"Libros cargados desde {DATA_FILE_PATH}. Total: {len(books)} libros.")
        else:
            books = list(initial_books) # Copia para evitar modificar la original directamente
            app.logger.info(f"Archivo {DATA_FILE_PATH} no encontrado. Usando lista inicial. 'books' ahora tiene {len(books)} libros. 'initial_books' tiene {len(initial_books)} libros.")
            save_books_to_file() # Guarda la lista inicial si el archivo no existía
    except (IOError, json.JSONDecodeError) as e:
        app.logger.error(f"Error al cargar libros desde {DATA_FILE_PATH}: {e}. Usando lista inicial.")
        books = list(initial_books) # Copia en caso de error
        app.logger.info(f"Error al cargar, usando lista inicial. 'books' ahora tiene {len(books)} libros.")

def save_books_to_file():
    """Guarda la lista actual de libros en el archivo JSON."""
    try:
        os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(books, f, indent=4)
        app.logger.info(f"Libros guardados en {DATA_FILE_PATH}. Total actual en memoria: {len(books)} libros.")
    except IOError as e:
        app.logger.error(f"Error al guardar libros en {DATA_FILE_PATH}: {e}")

# Cargar los libros al iniciar la aplicación
load_books_from_file()

# Definición de rutas para la respuesta de la ruta raíz
routes: list[dict[str, str]] = [
    {"path": "/", "methods": ["GET"], "description": "Muestra esta información de rutas."},
    {"path": "/books", "methods": ["GET"], "description": "Obtiene todos los libros."},
    {"path": "/books/<id>", "methods": ["GET"], "description": "Obtiene un libro específico por ID."},
    {"path": "/books", "methods": ["POST"], "description": "Añade un nuevo libro."},
    {"path": "/books/<id>", "methods": ["PUT"], "description": "Actualiza un libro existente por ID."},
    {"path": "/books/<id>", "methods": ["DELETE"], "description": "Elimina un libro por ID."},
    {"path": "/app-hostname", "methods": ["GET"], "description": "Obtiene el hostname del pod de la aplicación."},
]

@app.route("/", methods=["GET"])
def index() -> Response:
    return jsonify({"message": "Welcome to the Books API!", "available_routes": routes})

@app.route("/books", methods=["GET"])
def get_books() -> Response:
    app.logger.info(f"GET /books - Devolviendo {len(books)} libros.")
    return jsonify(books)

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int) -> Response:
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        app.logger.info(f"GET /books/{book_id} - Encontrado: {book['title']}")
        return jsonify(book)
    app.logger.warning(f"GET /books/{book_id} - Libro no encontrado.")
    return jsonify({"message": "Book not found"}), 404

@app.route("/books", methods=["POST"])
def add_book() -> tuple[Response, Literal[201]]:
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        app.logger.warning("POST /books - Faltan datos (título o autor) en la solicitud.")
        return jsonify({"message": "Missing title or author"}), 400
    
    next_id = max(book["id"] for book in books) + 1 if books else 1
    
    new_book: dict = {
        "id": next_id,
        "title": data["title"],
        "author": data["author"],
    }
    books.append(new_book)
    save_books_to_file()
    app.logger.info(f"Libro añadido con ID {next_id}: {new_book['title']}")
    return jsonify(new_book), 201

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id: int) -> Response:
    app.logger.info(f"--- UPDATE /books/{book_id} ---")
    app.logger.info(f"--- UPDATE: Lista 'books' actual ({len(books)} items): {books}")
    app.logger.info(f"--- UPDATE: Buscando libro con ID (tipo {type(book_id)}): {book_id}")

    book = next((b for b in books if b["id"] == book_id), None) # Renombré 'book' a 'b' en la comprensión para evitar confusión
    
    if not book:
        app.logger.warning(f"--- UPDATE: Libro con ID {book_id} NO encontrado en la lista.")
        return jsonify({"message": "Book not found"}), 404
    
    app.logger.info(f"--- UPDATE: Libro con ID {book_id} ENCONTRADO: {book}")
    data = request.get_json()
    if not data:
        app.logger.warning(f"PUT /books/{book_id} - No se proporcionaron datos en la solicitud.")
        return jsonify({"message": "No data provided"}), 400
        
    book["title"] = data.get("title", book["title"])
    book["author"] = data.get("author", book["author"])
    save_books_to_file()
    app.logger.info(f"Libro actualizado con ID {book_id}: {book['title']}")
    return jsonify(book), 200

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int) -> Response:
    global books
    app.logger.info(f"--- DELETE /books/{book_id} ---")
    app.logger.info(f"--- DELETE: Lista 'books' actual ({len(books)} items): {books}")
    app.logger.info(f"--- DELETE: Buscando libro con ID (tipo {type(book_id)}): {book_id}")

    book_to_delete = next((b for b in books if b["id"] == book_id), None) # Renombré 'book' a 'b'
    
    if not book_to_delete:
        app.logger.warning(f"--- DELETE: Libro con ID {book_id} NO encontrado en la lista.")
        return jsonify({"message": "Book not found"}), 404
    
    app.logger.info(f"--- DELETE: Libro con ID {book_id} ENCONTRADO, procediendo a borrar: {book_to_delete}")
    books = [b for b in books if b["id"] != book_id] # Renombré 'book' a 'b'
    save_books_to_file()
    app.logger.info(f"Libro borrado con ID {book_id}")
    return jsonify({"message": "Book deleted successfully"}), 200

@app.route('/app-hostname', methods=['GET'])
def app_hostname():
    hostname = socket.gethostname()
    app.logger.info(f"GET /app-hostname - Devolviendo hostname: {hostname}")
    return jsonify({"message": "app-books pod", "hostname": hostname})

if __name__ == "__main__":
    host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    port: int = int(os.getenv("FLASK_PORT", 5000))
    # La carga inicial de libros se hace al principio del script, después de definir las funciones.
    app.logger.info(f"Iniciando servidor Flask en {host}:{port}")
    app.run(debug=False, host=host, port=port) # debug=False para producción con Gunicorn