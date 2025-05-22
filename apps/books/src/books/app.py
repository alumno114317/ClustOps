import os
from typing import Literal

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
        "path": "/books",
        "method": "POST",
        "description": "Add a new book",
    },
]


@app.route("/", methods=["GET"])
def index() -> Response:
    return jsonify({"message": "Welcome to the Books API!", "routes": routes})


@app.route("/books", methods=["GET"])
def get_books() -> Response:
    return jsonify(books)


@app.route("/books", methods=["POST"])
def add_book() -> tuple[Response, Literal[201]]:
    data = request.get_json()
    new_book: dict = {
        "id": len(books) + 1,
        "title": data["title"],
        "author": data["author"],
    }
    books.append(new_book)
    return jsonify(new_book), 201


if __name__ == "__main__":
    host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    port: int = int(os.getenv("FLASK_PORT", 5000))

    app.run(host, port)
