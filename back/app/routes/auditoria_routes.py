from flask import Blueprint, jsonify, g
from app.database.db import get_db_connection
from app.utils.auth_middleware import admin_required

auditoria_bp = Blueprint('auditoria', __name__)

LIMITE_PADRAO = 100

# Só admin (Tarefa 6.2): a auditoria não guarda a obra de cada evento, então
# não dá para filtrá-la pelos vínculos de um usuário com acesso restrito —
# liberar para financeiro/gestor_obra vazaria atividade de obras alheias.
@auditoria_bp.route('/auditoria', methods=['GET'])
@admin_required
def listar_auditoria():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.entidade, a.entidade_id, a.acao, a.detalhes, a.criado_em,
               COALESCE(u.username, 'usuário removido') AS usuario_nome
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.empresa_id = ?
        ORDER BY a.criado_em DESC
        LIMIT ?
    ''', (g.user['empresa_id'], LIMITE_PADRAO))
    eventos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(eventos), 200
