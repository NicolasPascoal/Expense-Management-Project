import { btnStyle, inputStyle } from "../utils/styles";
import { FolderOpen, Plus, Trash2, AlertTriangle } from "lucide-react";

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
      <span style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1", display: "flex", alignItems: "center", gap: 6 }}>
        <FolderOpen size={16} /> Projeto:
      </span>
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
            style={{ ...btnStyle("#2563eb"), display: "flex", alignItems: "center", gap: 6 }}
          >
            <Plus size={16} /> Novo Projeto
          </button>
          {projetoAtivo && (
            <button 
              onClick={() => {
                askConfirm({
                  title: `Excluir projeto "${projetoAtivo.nome}"?`,
                  message: "TODOS os lançamentos, categorias e contas deste projeto serão excluídos permanentemente.",
                  icon: <AlertTriangle size={40} color="#f59e0b" />,
                  confirmText: "Excluir Tudo",
                  onConfirm: () => deleteProject(projetoAtivo.id)
                });
              }} 
              style={{ ...btnStyle("#dc2626"), display: "flex", alignItems: "center", gap: 6 }}
            >
              <Trash2 size={16} /> Excluir Projeto
            </button>
          )}
        </>
      )}
    </div>
  );
}
