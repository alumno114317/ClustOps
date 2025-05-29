#!/bin/bash

# libros.sh - Gestiona registros de libros mediante una API.

# URL base de la API de libros
API_URL="http://localhost:5001/books"

# Función para listar todos los libros (para ayudar al usuario a elegir IDs)
list_books() {
    echo "Listando libros existentes..."
    curl -s -X GET "${API_URL}" | jq '.' # Usamos jq para formatear el JSON, instálalo si no lo tienes (sudo apt install jq)
    echo "------------------------------------"
}

# Función para añadir un libro
add_book() {
    echo "--- Añadir Nuevo Libro ---"
    read -p "Introduce el título del libro: " title
    read -p "Introduce el autor del libro: " author

    # Validar que no estén vacíos (simple validación)
    if [ -z "$title" ] || [ -z "$author" ]; then
        echo "Error: El título y el autor no pueden estar vacíos."
        return
    fi

    echo "Añadiendo libro: Título='${title}', Autor='${author}'..."
    curl -X POST -H "Content-Type: application/json" \
         -d "{\"title\":\"${title}\", \"author\":\"${author}\"}" \
         "${API_URL}"
    echo "" # Nueva línea para mejor formato de salida
}

# Función para borrar un libro
delete_book() {
    echo "--- Borrar Libro ---"
    list_books
    read -p "Introduce el ID del libro que quieres borrar: " book_id

    # Validar que el ID no esté vacío y sea un número (simple validación)
    if [ -z "$book_id" ] || ! [[ "$book_id" =~ ^[0-9]+$ ]]; then
        echo "Error: Debes introducir un ID numérico válido."
        return
    fi

    echo "Borrando libro con ID ${book_id}..."
    curl -X DELETE "${API_URL}/${book_id}"
    echo ""
}

# Función para modificar un libro
update_book() {
    echo "--- Modificar Libro ---"
    list_books
    read -p "Introduce el ID del libro que quieres modificar: " book_id

    # Validar que el ID no esté vacío y sea un número
    if [ -z "$book_id" ] || ! [[ "$book_id" =~ ^[0-9]+$ ]]; then
        echo "Error: Debes introducir un ID numérico válido."
        return
    fi

    # Obtener y mostrar el registro actual
    echo "Obteniendo datos actuales del libro ID ${book_id}..."
    current_data=$(curl -s -X GET "${API_URL}/${book_id}")

    if [ -z "$current_data" ] || [ "$current_data" == "null" ] || [[ "$current_data" == *"Not Found"* ]]; then # Ajusta la condición de "no encontrado" según tu API
        echo "Error: Libro con ID ${book_id} no encontrado."
        return
    fi

    echo "Datos actuales:"
    echo "$current_data" | jq '.'
    echo "------------------------------------"

    current_title=$(echo "$current_data" | jq -r '.title')
    current_author=$(echo "$current_data" | jq -r '.author')

    read -p "Introduce el nuevo título (deja vacío para no cambiar: '${current_title}'): " new_title
    read -p "Introduce el nuevo autor (deja vacío para no cambiar: '${current_author}'): " new_author

    # Si el usuario no introduce nada, se usa el valor actual
    if [ -z "$new_title" ]; then
        new_title="$current_title"
    fi
    if [ -z "$new_author" ]; then
        new_author="$current_author"
    fi

    echo "Actualizando libro ID ${book_id} con: Título='${new_title}', Autor='${new_author}'..."
    curl -X PUT -H "Content-Type: application/json" \
         -d "{\"title\":\"${new_title}\", \"author\":\"${new_author}\"}" \
         "${API_URL}/${book_id}"
    echo ""
}

# Menú principal interactivo
while true; do
    echo ""
    echo "Gestor Interactivo de Libros"
    echo "----------------------------"
    echo "1. Añadir un libro"
    echo "2. Borrar un libro"
    echo "3. Modificar un libro"
    echo "4. Listar todos los libros"
    echo "5. Salir"
    echo "----------------------------"
    read -p "Selecciona una opción (1-5): " choice

    case $choice in
        1)
            add_book
            ;;
        2)
            delete_book
            ;;
        3)
            update_book
            ;;
        4)
            list_books
            ;;
        5)
            echo "Saliendo..."
            break
            ;;
        *)
            echo "Opción no válida. Por favor, intenta de nuevo."
            ;;
    esac
    echo ""
    read -p "Presiona Enter para continuar..."
done

exit 0