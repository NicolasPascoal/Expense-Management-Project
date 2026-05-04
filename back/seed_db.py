import json
import sqlite3
import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(BASE_DIR), 'front', 'src', 'data', 'data.json')
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def seed():
    if not os.path.exists(JSON_PATH):
        print(f"Erro: Arquivo JSON não encontrado em {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Limpa a tabela antes de importar (opcional, mas evita duplicados se rodar várias vezes)
    # cursor.execute('DELETE FROM lancamentos')
    
    print(f"Importando {len(dados)} registros...")

    for item in dados:
        # Preparar dados para inserção
        # Note: O SQLite vai gerar um novo ID se não passarmos, 
        # mas podemos tentar manter o ID original se quisermos.
        # Aqui vamos deixar o SQLite gerar novos IDs para evitar conflitos futuros.
        
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
