from flask import Flask, request, jsonify
import os
import psycopg2
from datetime import datetime


app = Flask(__name__)

def get_db_connection():
    # Pega a URL de conexão da variável de ambiente que definimos no Compose
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError("DATABASE_URL não definida")
    conn = psycopg2.connect(url)
    return conn


def ensure_schema():
    """Garante que a tabela existe."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS server_metrics (
            id serial PRIMARY KEY,
            hostname varchar(50) NOT NULL,
            cpu_usage integer,
            ram_usage integer,
            status varchar(50),
            created_at timestamp DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.route('/metrics', methods=['POST'])
def receive_metrics():
    data = request.get_json(silent=True)

    if not data or 'hostname' not in data:
        return jsonify({"erro": "Dados inválidos"}) , 400
    
    hostname = data['hostname']
    cpu = data.get('cpu', 0)
    ram = data.get('ram', 0)

    status = "NORMAL"
    if cpu > 80:
        status = "CRITICAL"
    elif cpu > 50:
        status = "WARNING"

    try:
         ensure_schema()
         conn = get_db_connection()
         cur = conn.cursor()
         cur.execute(
             'INSERT INTO server_metrics (hostname , cpu_usage, ram_usage, status) VALUES (%s,%s,%s,%s)',
             (hostname,cpu,ram,status)
         )
         conn.commit()
         cur.close()
         conn.close()
         return jsonify({"message": "Metrica recebida","Status_detectado": status}), 201
    except Exception as e:
        return jsonify({"error": str(e)}) , 500
    
@app.route('/alerts', methods=['GET'])
def get_alerts():
    try: 
        ensure_schema()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT hostname, cpu_usage, ram_usage, status, created_at FROM server_metrics WHERE status != 'NORMAL' ORDER BY created_at DESC LIMIT 10")
        alerts = cur.fetchall()
        result = []
        for row in alerts:
            result.append({
                "hostname": row[0],
                "cpu": f"{row[1]}%",
                "ram": f"{row[2]}%",
                "status": row[3],
                "hora": row[4].isoformat() if row[4] else None
            })
        cur.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify ({"error":str(e)}),500


@app.route('/')
def hello():
    try:
        ensure_schema()
        return jsonify({"message": "Sentinel Monitor v1.0"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"system": "Sentinel Monitor v1.0", "online": True})
    


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)