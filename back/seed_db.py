import json
import os
from app.database.db import get_db_connection

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(BASE_DIR), 'front', 'src', 'data', 'data.json')

def seed():
    if not os.path.exists(JSON_PATH):
        print(f"Erro: Arquivo JSON não encontrado em {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Importando {len(dados)} registros para a tabela 'lancamentos'...")

    for item in dados:
        cursor.execute('''
            INSERT INTO lancamentos (data, categoria, item, fornecedor, quantidade, unitario, valor, forma, conta, obs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('data', ''),
            item.get('categoria', ''),
            item.get('item', ''),
            item.get('fornecedor', ''),
            float(item.get('quantidade', 0) or 0),
            float(item.get('unitario', 0) or 0),
            float(item.get('valor', 0) or 0),
            item.get('forma', ''),
            item.get('conta', ''),
            item.get('obs', '')
        ))

    conn.commit()
    conn.close()
    print("Importação concluída com sucesso!")

if __name__ == '__main__':
    seed()
