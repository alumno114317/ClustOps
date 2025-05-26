#!/bin/bash
# filepath: /home/alumno114317/ClustOps/Prueba2/scripts/balanceo.sh

# Reemplaza <IP-NODO-MICROK8S> y <NODEPORT> con los valores reales
IP_NODO="172.28.179.170"
NODEPORT="31286"

for i in {1..10}; do
  echo "Petición $i:"
  resultado=$(curl http://${IP_NODO}:${NODEPORT})
  echo "$resultado"
  sleep 0.5
done