# README.md

# Proyecto Nginx en Kubernetes

Este proyecto contiene la configuración necesaria para desplegar una aplicación Nginx en un clúster de Kubernetes utilizando un Deployment.

## Archivos del Proyecto

- **deployment.yaml**: Define un Deployment de Kubernetes para la aplicación Nginx. Especifica el número de réplicas, las etiquetas de selección, la plantilla del pod y la configuración del contenedor, incluyendo el puerto y el volumen.

- **okteto.yaml**: Manifiesto de Okteto que automatiza el proceso de desarrollo. Define la configuración del entorno de desarrollo, incluyendo el nombre del servicio, la imagen a utilizar, los puertos expuestos y cualquier volumen necesario.

## Configuración y Ejecución

1. Asegúrate de tener acceso a un clúster de Kubernetes y que `kubectl` esté configurado correctamente.
2. Aplica el archivo `deployment.yaml` para crear el Deployment:
   ```
   kubectl apply -f deployment.yaml
   ```
3. Si estás utilizando Okteto, puedes iniciar el entorno de desarrollo con:
   ```
   okteto up
   ```
4. Accede a la aplicación Nginx a través del puerto expuesto en tu clúster.

## Notas

Asegúrate de tener los permisos necesarios para crear recursos en el clúster de Kubernetes y de que los volúmenes persistentes estén configurados correctamente.