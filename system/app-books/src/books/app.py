import os
from typing import Literal
import socket # <--- AÑADIDO para obtener el hostname

from flask import Flask, jsonify, request
from flask.wrappers import Response

app = Flask(__name__)

books: list[dict] = [
    {
        "id": 1,
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
    },
    {
        "id": 2,
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J.K. Rowling",
    },
    {
        "id": 3,
        "title": "Harry Potter and the Prisoner of Azkaban",
        "author": "J.K. Rowling",
    },
    {"id": 4, "title": "Harry Potter and the Goblet of Fire", "author": "J.K. Rowling"},
    {
        "id": 5,
        "title": "Harry Potter and the Order of the Phoenix",
        "author": "J.K. Rowling",
    },
    {
        "id": 6,
        "title": "Harry Potter and the Half-Blood Prince",
        "author": "J.K. Rowling",
    },
    {
        "id": 7,
        "title": "Harry Potter and the Deathly Hallows",
        "author": "J.K. Rowling",
    },
]


routes: list[dict[str, str]] = [
    {
        "path": "/",
        "method": "GET",
        "description": "Welcome page with API information",
    },
    {
        "path": "/books",
        "method": "GET",
        "description": "Get all books",
    },
    {
        "path": "/books/<id>", # Añadida descripción para obtener un libro por ID
        "method": "GET",
        "description": "Get a specific book by ID",
    },
    {
        "path": "/books",
        "method": "POST",
        "description": "Add a new book",
    },
    {
        "path": "/books/<id>", # Añadida descripción para actualizar un libro
        "method": "PUT",
        "description": "Update a specific book by ID",
    },
    {
        "path": "/books/<id>", # Añadida descripción para borrar un libro
        "method": "DELETE",
        "description": "Delete a specific book by ID",
    },
    { # <--- AÑADIDO para la nueva ruta de hostname
        "path": "/app-hostname",
        "method": "GET",
        "description": "Get the hostname of the pod serving the request",
    },
]


@app.route("/", methods=["GET"])
def index() -> Response:
    return jsonify({"message": "Welcome to the Books API!", "routes": routes})


@app.route("/books", methods=["GET"])
def get_books() -> Response:
    return jsonify(books)


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int) -> Response:
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"message": "Book not found"}), 404


@app.route("/books", methods=["POST"])
def add_book() -> tuple[Response, Literal[201]]:
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        return jsonify({"message": "Missing title or author"}), 400
    
    # Encontrar el ID más alto actual para evitar colisiones si se borran libros
    next_id = max(book["id"] for book in books) + 1 if books else 1
    
    new_book: dict = {
        "id": next_id,
        "title": data["title"],
        "author": data["author"],
    }
    books.append(new_book)
    return jsonify(new_book), 201


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id: int) -> Response:
    book = next((book for book in books if book["id"] == book_id), None)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
        
    book["title"] = data.get("title", book["title"])
    book["author"] = data.get("author", book["author"])
    return jsonify(book)


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int) -> Response:
    global books # Necesario para reasignar la lista 'books'
    book_to_delete = next((book for book in books if book["id"] == book_id), None)
    if not book_to_delete:
        return jsonify({"message": "Book not found"}), 404
    
    books = [book for book in books if book["id"] != book_id]
    return jsonify({"message": "Book deleted successfully"})


# --- NUEVA RUTA AÑADIDA ---
@app.route('/app-hostname', methods=['GET'])
def app_hostname():
    hostname = socket.gethostname() # Obtiene el nombre del host (pod)
    return jsonify({"message": "app-books pod", "hostname": hostname})
# --- FIN DE LA NUEVA RUTA ---


if __name__ == "__main__":
    host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    port: int = int(os.getenv("FLASK_PORT", 5000))

    app.run(debug=True, host=host, port=port) # Añadido debug=True para desarrollo si es necesario