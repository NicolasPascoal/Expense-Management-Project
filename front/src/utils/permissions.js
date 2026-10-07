// Papéis expandidos (Tarefa 6.1) — espelha back/app/utils/permissions.py.
// Desde a Tarefa 6.2, "acesso_financeiro" de não-admin vale só nas obras às
// quais o usuário está vinculado — o recorte é feito pelo backend.
export const PERMISSOES_POR_PAPEL = {
  financeiro: new Set(["acesso_financeiro"]),
  gestor_obra: new Set(["acesso_financeiro", "aprovar_requisicoes", "gerenciar_tarefas"]),
  prestador: new Set(),
};

export function can(user, permissao) {
  if (user?.is_admin) return true;
  return (PERMISSOES_POR_PAPEL[user?.role] || new Set()).has(permissao);
}
