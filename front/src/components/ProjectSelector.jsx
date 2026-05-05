import { btnStyle, inputStyle } from "../utils/styles";

export function ProjectSelector({ 
  projetos, 
  projetoAtivo, 
  setProjetoAtivo, 
  setShowProjectModal,
  deleteProject,
  user,
  askConfirm
}) {
  return (
    <div style={{
      display: "flex", 
      alignItems: "center", 
      gap: 12, 
      flexWrap: "wrap"
    }}>
      <span style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1" }}>📁 Projeto Ativo:</span>
      <select 
        value={projetoAtivo?.id || ""} 
        onChange={(e) => {
          const p = projetos.find(x => x.id === parseInt(e.target.value));
          setProjetoAtivo(p);
        }}
        style={{ 
          ...inputStyle, 
          width: "auto", 
          margin: 0, 
          minWidth: 200,
          borderColor: "#2563eb",
          fontWeight: 600,
          color: "#1e3a5f"
        }}
      >
        {projetos.map(p => (
          <option key={p.id} value={p.id}>{p.nome}</option>
        ))}
      </select>
      {user?.is_admin && (
        <>
          <button 
            onClick={() => setShowProjectModal(true)} 
            style={btnStyle("#2563eb")}
          >
            + Novo Projeto
          </button>
          {projetoAtivo && (
            <button 
              onClick={() => {
                askConfirm({
                  title: `Excluir projeto "${projetoAtivo.nome}"?`,
                  message: "TODOS os lançamentos, categorias e contas deste projeto serão excluídos permanentemente.",
                  icon: "⚠️",
                  confirmText: "Excluir Tudo",
                  onConfirm: () => deleteProject(projetoAtivo.id)
                });
              }} 
              style={btnStyle("#dc2626")}
            >
              🗑️ Excluir Projeto
            </button>
          )}
        </>
      )}
    </div>
  );
}
