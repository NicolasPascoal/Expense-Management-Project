from app.database.db import get_db_connection


def usuario_restrito(user):
    """Tarefa 6.2: id do usuário cujo acesso a obras é limitado por vínculo
    (usuario_projetos), ou None para admin — que vê todas as obras da empresa.
    É o valor a passar como `usuario_id` para os controllers."""
    return None if user.get('is_admin') else user['id']


def filtro_vinculo(usuario_id, coluna_projeto='p.id'):
    """Trecho SQL (+ params) a acrescentar ao WHERE de uma query que já filtra
    por empresa, restringindo às obras vinculadas ao usuário. Sem restrição
    (admin, usuario_id=None) devolve trecho vazio."""
    if usuario_id is None:
        return '', ()
    return (
        f' AND {coluna_projeto} IN (SELECT projeto_id FROM usuario_projetos WHERE usuario_id = ?)',
        (usuario_id,),
    )


def usuario_acessa_projeto(user, projeto_id):
    """Confere se o projeto existe, pertence à empresa do usuário e — para
    não-admin — se o usuário está vinculado a ele (Tarefa 6.2)."""
    trecho, params = filtro_vinculo(usuario_restrito(user))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.id FROM projetos p WHERE p.id = ? AND p.empresa_id = ?" + trecho,
        (projeto_id, user['empresa_id']) + params
    )
    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def usuario_pertence_a_empresa(usuario_id, empresa_id):
    """Confere se o usuário existe e pertence à empresa informada."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE id = ? AND empresa_id = ?", (usuario_id, empresa_id))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe
