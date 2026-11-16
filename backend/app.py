import os
import time
import random
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Identificador único de cada contenedor (ej. Backend 1, Backend 2, Backend 3)
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "Backend-Desconocido")

# Exposición automática de métricas en /metrics (latencia, tasa de peticiones, códigos HTTP)
metrics = PrometheusMetrics(
    app,
    group_by="endpoint",
    default_labels={"instance_name": INSTANCE_NAME},
    excluded_paths=["/health"]
)

@app.route("/")
def index():
    # Simula un ligero tiempo de procesamiento variable (entre 5ms y 30ms) para ver métricas realistas
    time.sleep(random.uniform(0.005, 0.03))
    return jsonify({
        "mensaje": "Respuesta exitosa desde la infraestructura containerizada",
        "servidor": INSTANCE_NAME
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "servidor": INSTANCE_NAME}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)