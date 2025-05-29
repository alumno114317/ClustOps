#!/bin/bash

# restore_latest_backup.sh - Script para restaurar el único backup disponible de app-books al PV.

# --- Configuración ---
# Ruta en el HOST donde el PersistentVolume de app-books almacena sus datos.
# ¡¡ASEGÚRATE DE QUE ESTA RUTA SEA CORRECTA PARA TU PV ACTUAL!!
PV_HOSTPATH="/var/snap/microk8s/common/default-storage/mi-sistema-app-books-data-pvc-pvc-4b3741e0-99b6-407f-af65-c22c1a1ce954"

# Directorio en el HOST donde se almacena el archivo de backup.
BACKUP_SOURCE_DIR="/home/alumno114317/ClustOps/backup"
# --- Fin de Configuración ---

echo "--- Iniciando Proceso de Restauración del Último Backup ---"

# Encontrar el archivo de backup .tar.gz en el directorio de backups
# Asumimos que solo hay uno según la lógica del CronJob.
# Usamos 'find' para más robustez y para manejar casos donde no haya ninguno o haya más de uno (aunque no debería).
BACKUP_FILES_FOUND=$(find "${BACKUP_SOURCE_DIR}" -maxdepth 1 -name "app-books-backup-*.tar.gz" -type f)
NUM_BACKUP_FILES=$(echo "$BACKUP_FILES_FOUND" | wc -l)

if [ "$NUM_BACKUP_FILES" -eq 0 ]; then
  echo "Error: No se encontró ningún archivo de backup 'app-books-backup-*.tar.gz' en ${BACKUP_SOURCE_DIR}"
  exit 1
elif [ "$NUM_BACKUP_FILES" -gt 1 ]; then
  echo "Advertencia: Se encontró más de un archivo de backup en ${BACKUP_SOURCE_DIR}."
  echo "Esto no debería ocurrir si el CronJob está configurado para mantener solo el último."
  echo "Archivos encontrados:"
  echo "$BACKUP_FILES_FOUND"
  echo "Por favor, revisa el directorio de backups y la lógica del CronJob."
  echo "Para continuar, este script usará el archivo más reciente por nombre (orden lexicográfico)."
  # Toma el último por orden lexicográfico, que suele ser el más reciente si el timestamp está al principio o al final.
  # Si el formato es YYYYMMDD-HHMMSS, el orden lexicográfico es el orden cronológico.
  FULL_BACKUP_PATH=$(echo "$BACKUP_FILES_FOUND" | sort | tail -n 1)
else
  FULL_BACKUP_PATH="$BACKUP_FILES_FOUND"
fi

echo "Backup a restaurar: ${FULL_BACKUP_PATH}"
echo "Destino de restauración (PV hostPath): ${PV_HOSTPATH}"
echo ""

# Comprobar si el directorio PV_HOSTPATH existe
if [ ! -d "$PV_HOSTPATH" ]; then
  echo "Error: El directorio de destino del PV no existe: ${PV_HOSTPATH}"
  echo "Asegúrate de que el PVC 'app-books-data-pvc' esté activo y el PV correctamente configurado."
  exit 1
fi

# Limpiar el contenido actual del directorio PV_HOSTPATH antes de restaurar
echo "Paso 1: Limpiando contenido actual de ${PV_HOSTPATH}..."
if [ -d "$PV_HOSTPATH" ] && [ -n "$(ls -A "$PV_HOSTPATH")" ]; then
  echo "Directorio ${PV_HOSTPATH} no está vacío. Eliminando su contenido..."
  find "${PV_HOSTPATH}" -mindepth 1 -delete
  if [ $? -eq 0 ]; then
    echo "Contenido de ${PV_HOSTPATH} eliminado exitosamente."
  else
    echo "Error al eliminar el contenido de ${PV_HOSTPATH}. Revisa los permisos o errores."
    exit 1
  fi
else
  if [ ! -d "$PV_HOSTPATH" ]; then
      echo "El directorio ${PV_HOSTPATH} no existe. No se puede limpiar."
      exit 1
  else
      echo "Directorio ${PV_HOSTPATH} ya está vacío o no contenía nada que limpiar."
  fi
fi
echo ""

# Restaurar el backup
echo "Paso 2: Restaurando backup desde ${FULL_BACKUP_PATH} a ${PV_HOSTPATH}..."
tar -xzvf "$FULL_BACKUP_PATH" -C "$PV_HOSTPATH" -m --no-same-owner --no-same-permissions
if [ $? -eq 0 ]; then
  echo "Backup restaurado exitosamente."
else
  echo "Error durante la restauración del backup con tar."
  exit 1
fi
echo ""

echo "Paso 3: Verificando contenido restaurado en ${PV_HOSTPATH}:"
ls -lhA "${PV_HOSTPATH}"
echo ""
echo "--- Proceso de Restauración Completado ---"
echo "Recuerda reiniciar los pods de la aplicación 'app-books-deployment' para que carguen los datos restaurados:"
echo "  kubectl rollout restart deployment app-books-deployment -n mi-sistema"

exit 0