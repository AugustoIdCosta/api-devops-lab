import os
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_db_connection():
    # Pega a URL de conexão da variável de ambiente que definimos no Compose
    url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(url)
    return conn

@app.route('/')
def hello():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Cria uma tabela se não existir (apenas para teste)
        cur.execute('CREATE TABLE IF NOT EXISTS visitas (id serial PRIMARY KEY, num integer);')
        cur.execute('INSERT INTO visitas (num) VALUES (1);')
        conn.commit()
        
        # Conta quantas linhas tem
        cur.execute('SELECT COUNT(*) FROM visitas;')
        count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return f"Conexao com Banco: SUCESSO! <br> Visitas registradas no banco: {count}"
    except Exception as e:
        return f"Erro ao conectar no banco: {e}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)