# Infraestructura Containerizada con Balanceo de Carga y Monitoreo

Proyecto final de Administración de Sistemas Operativos (Universidad Autónoma de Occidente). Implementa una arquitectura de microservicios con balanceo de carga mediante **Nginx** como proxy inverso frente a tres instancias de aplicación en **Python/Flask**, integrada con un stack de observabilidad compuesto por **Prometheus**, **Grafana**, **Nginx Prometheus Exporter** y **cAdvisor**.

---

## Arquitectura del Sistema

```text
[Cliente / k6] ──(HTTP :8080)──► [Nginx Reverse Proxy]
                                     ├──► [backend1 (Flask/Gunicorn :5000)]
                                     ├──► [backend2 (Flask/Gunicorn :5000)]
                                     └──► [backend3 (Flask/Gunicorn :5000)]

[cAdvisor] ───────────────(Métricas Host/Contenedores)──┐
[Nginx Exporter] ◄──(:8088/stub_status)── [Nginx] ───────┤
[Backends 1, 2, 3] ──────(/metrics)──────────────────────┼──► [Prometheus (:9090)] ──► [Grafana (:3000)]
```

### Estructura del Repositorio

```text
proyecto-final-docker/
├── docker-compose.yml       # Orquestación de los 8 contenedores, red y volúmenes
├── prueba_carga.js          # Script de pruebas de estrés para k6
├── README.md                # Documentación del proyecto
├── backend/
│   ├── app.py               # API REST en Flask con exportación de métricas (/metrics)
│   ├── Dockerfile           # Construcción de imagen Python 3.11-slim + Gunicorn
│   └── requirements.txt     # Dependencias (Flask, Gunicorn, prometheus-flask-exporter)
├── nginx/
│   └── nginx.conf           # Configuración de proxy inverso, Round Robin y stub_status
└── prometheus/
    └── prometheus.yml       # Configuración de scraping y targets monitoreados
```

---

## Requisitos Previos

* **Docker Engine / Docker Desktop** (v24.0 o superior)
* **Docker Compose** (v2.20 o superior)
* **k6** (instalado en la máquina anfitriona para ejecutar las pruebas de carga)
* Puertos libres en el host: `8080`, `8081`, `9090` y `3000`.
  * *Nota para Windows:* Verificar antes del despliegue que los puertos no estén reservados por Hyper-V/WSL ejecutando:
    ```powershell
    netsh interface ipv4 show excludedportrange protocol=tcp
    ```

---

## Despliegue de la Infraestructura

1. **Clonar el repositorio e ingresar al directorio:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO_GITHUB>
   cd proyecto-final-docker
   ```

2. **Construir las imágenes y levantar todos los servicios en segundo plano:**
   ```bash
   docker compose up -d --build
   ```

3. **Verificar que los 8 contenedores estén en ejecución (`Up`):**
   ```bash
   docker compose ps
   ```

---

## URLs de Acceso a los Servicios

| Servicio | URL de Acceso | Credenciales por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| **Aplicación Web (Nginx)** | `http://localhost:8080` | N/A | Punto de entrada público balanceado |
| **Prometheus** | `http://localhost:9090` | N/A | Base de datos de series de tiempo y consola PromQL |
| **Grafana** | `http://localhost:3000` | `admin` / `admin` | Paneles visuales y dashboards de monitoreo |
| **cAdvisor** | `http://localhost:8081` | N/A | Métricas de hardware y recursos de contenedores |

---

## Verificación del Balanceo de Carga

Para comprobar que **Nginx** distribuye el tráfico secuencialmente entre las tres instancias (`Instancia-Backend-1`, `Instancia-Backend-2` e `Instancia-Backend-3`) mediante *Round Robin*:

* **En Linux / macOS / Git Bash:**
  ```bash
  for i in {1..6}; do curl -s http://localhost:8080/; echo ""; done
  ```

* **En Windows (PowerShell):**
  ```powershell
  1..6 | ForEach-Object { (Invoke-RestMethod -Uri http://localhost:8080/).servidor }
  ```

**Salida esperada:**
```text
Instancia-Backend-1
Instancia-Backend-2
Instancia-Backend-3
Instancia-Backend-1
Instancia-Backend-2
Instancia-Backend-3
```

---

## Ejecución de Pruebas de Carga (k6)

1. **Instalar k6 en el host (si aún no está instalado):**
   * **Windows:** `winget install k6 --source winget`
   * **macOS:** `brew install k6`
   * **Linux (Debian/Ubuntu):** `sudo snap install k6`

2. **Lanzar la prueba de estrés:**
   El archivo `prueba_carga.js` escala progresivamente hasta **50 usuarios virtuales (VUs)** durante 75 segundos contra el proxy inverso:
   ```bash
   k6 run prueba_carga.js
   ```

3. **Observar métricas en tiempo real:**
   * Ingresar a **Grafana** (`http://localhost:3000`), configurar Prometheus (`http://prometheus:9090`) como *Data Source* y monitorear las tasas de peticiones por segundo (`flask_http_request_total`), latencia p95 (`flask_http_request_duration_seconds_bucket`), conexiones activas (`nginx_connections_active`) y consumo de CPU/memoria (`container_cpu_usage_seconds_total`).

---

## Detener y Limpiar el Entorno

* Para detener los contenedores conservando los datos históricos de Prometheus y Grafana:
  ```bash
  docker compose stop
  ```

* Para detener y eliminar contenedores, redes y volúmenes persistentes:
  ```bash
  docker compose down -v
  ```