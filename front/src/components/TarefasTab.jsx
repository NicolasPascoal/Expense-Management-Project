import { useState } from "react";
import { btnStyle, inputStyle } from "../utils/styles";
import { 
  Plus, 
  Trash2, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  User, 
  StickyNote,
  Save,
  ChevronRight
} from "lucide-react";

export function TarefasTab({ user, tarefas, usuarios, createTarefa, updateTarefa, deleteTarefa, askConfirm }) {
  const [showAdd, setShowAdd] = useState(false);
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [prestadorId, setPrestadorId] = useState("");
  const [editStates, setEditStates] = useState({}); // Controla quais tarefas estão em modo edição para o prestador

  const isAdmin = user?.is_admin;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!titulo || !prestadorId) return alert("Preencha título e prestador");
    
    await createTarefa({
      titulo,
      descricao,
      prestador_id: parseInt(prestadorId),
      status: "Pendente"
    });
    
    setTitulo("");
    setDescricao("");
    setPrestadorId("");
    setShowAdd(false);
  };

  const handleUpdateStatus = async (tarefa, newStatus) => {
    await updateTarefa(tarefa.id, { status: newStatus });
  };

  const handleSaveObs = async (tarefa) => {
    const obs = editStates[tarefa.id]?.observacoes;
    await updateTarefa(tarefa.id, { observacoes: obs });
    setEditStates(prev => {
      const next = { ...prev };
      delete next[tarefa.id];
      return next;
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Concluído": return "#16a34a";
      case "Em Andamento": return "#2563eb";
      case "Pendente": return "#f59e0b";
      default: return "#64748b";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "Concluído": return <CheckCircle2 size={16} />;
      case "Em Andamento": return <Clock size={16} />;
      case "Pendente": return <AlertCircle size={16} />;
      default: return null;
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      {/* Header Admin */}
      {isAdmin && (
        <div style={{ marginBottom: 24 }}>
          {!showAdd ? (
            <button 
              onClick={() => setShowAdd(true)}
              style={{ ...btnStyle("#2563eb"), display: "flex", alignItems: "center", gap: 8 }}
            >
              <Plus size={18} /> Nova Tarefa
            </button>
          ) : (
            <div style={{ background: "#fff", padding: 24, borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
              <h3 style={{ margin: "0 0 16px 0", fontSize: 16 }}>Criar Nova Tarefa</h3>
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <div>
                    <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Título</label>
                    <input 
                      style={inputStyle}
                      value={titulo}
                      onChange={e => setTitulo(e.target.value)}
                      placeholder="Ex: Pintura da fachada"
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Responsável</label>
                    <select 
                      style={inputStyle}
                      value={prestadorId}
                      onChange={e => setPrestadorId(e.target.value)}
                    >
                      <option value="">Selecione um prestador</option>
                      {usuarios.filter(u => u.role === "prestador" || u.is_admin).map(u => (
                        <option key={u.id} value={u.id}>{u.username}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Descrição</label>
                  <textarea 
                    style={{ ...inputStyle, minHeight: 80, resize: "vertical" }}
                    value={descricao}
                    onChange={e => setDescricao(e.target.value)}
                    placeholder="Detalhes da tarefa..."
                  />
                </div>
                <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                  <button type="button" onClick={() => setShowAdd(false)} style={btnStyle("#64748b")}>Cancelar</button>
                  <button type="submit" style={btnStyle("#2563eb")}>Criar Tarefa</button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* Lista de Tarefas */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {tarefas.length === 0 && (
          <div style={{ textAlign: "center", padding: "40px 20px", color: "#64748b", background: "#fff", borderRadius: 12 }}>
            Nenhuma tarefa encontrada.
          </div>
        )}
        
        {tarefas.map(t => (
          <div key={t.id} style={{ 
            background: "#fff", 
            borderRadius: 12, 
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            overflow: "hidden",
            borderLeft: `4px solid ${getStatusColor(t.status)}`
          }}>
            <div style={{ padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: 16, color: "#1e293b", display: "flex", alignItems: "center", gap: 8 }}>
                    {t.titulo}
                    <span style={{ 
                      fontSize: 10, 
                      padding: "2px 8px", 
                      borderRadius: 10, 
                      background: `${getStatusColor(t.status)}20`, 
                      color: getStatusColor(t.status),
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 4,
                      fontWeight: 600
                    }}>
                      {getStatusIcon(t.status)} {t.status}
                    </span>
                  </h4>
                  <div style={{ fontSize: 12, color: "#64748b", marginTop: 4, display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <User size={12} /> {t.prestador_nome}
                    </span>
                    <span>{new Date(t.data_criacao).toLocaleDateString("pt-BR")}</span>
                  </div>
                </div>
                
                {isAdmin && (
                  <button 
                    onClick={() => askConfirm({
                      title: "Excluir tarefa?",
                      message: `Deseja realmente excluir "${t.titulo}"?`,
                      confirmText: "Excluir",
                      onConfirm: () => deleteTarefa(t.id)
                    })}
                    style={{ border: "none", background: "none", color: "#94a3b8", cursor: "pointer", padding: 4 }}
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>

              <p style={{ fontSize: 14, color: "#475569", margin: "0 0 16px 0", lineHeight: 1.5 }}>
                {t.descricao || <i style={{ color: "#94a3b8" }}>Sem descrição.</i>}
              </p>

              {/* Seção de Observações / Update (Foco no Prestador) */}
              <div style={{ background: "#f8fafc", borderRadius: 8, padding: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <label style={{ fontSize: 11, fontWeight: 600, color: "#64748b", textTransform: "uppercase", display: "flex", alignItems: "center", gap: 6 }}>
                    <StickyNote size={12} /> Observações do Prestador
                  </label>
                  
                  {!isAdmin && !editStates[t.id] && (
                    <button 
                      onClick={() => setEditStates(prev => ({ ...prev, [t.id]: { observacoes: t.observacoes || "" } }))}
                      style={{ border: "none", background: "none", color: "#2563eb", fontSize: 12, fontWeight: 500, cursor: "pointer" }}
                    >
                      Editar
                    </button>
                  )}
                </div>

                {editStates[t.id] ? (
                  <div>
                    <textarea 
                      style={{ ...inputStyle, minHeight: 60, fontSize: 13, marginBottom: 8 }}
                      value={editStates[t.id].observacoes}
                      onChange={e => setEditStates(prev => ({ ...prev, [t.id]: { ...prev[t.id], observacoes: e.target.value } }))}
                      placeholder="Adicione observações sobre o progresso..."
                    />
                    <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                      <button 
                        onClick={() => setEditStates(prev => {
                          const next = { ...prev };
                          delete next[t.id];
                          return next;
                        })} 
                        style={{ ...btnStyle("#64748b"), padding: "4px 12px", fontSize: 12 }}
                      >
                        Cancelar
                      </button>
                      <button 
                        onClick={() => handleSaveObs(t)}
                        style={{ ...btnStyle("#2563eb"), padding: "4px 12px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}
                      >
                        <Save size={14} /> Salvar
                      </button>
                    </div>
                  </div>
                ) : (
                  <p style={{ fontSize: 13, color: "#64748b", margin: 0 }}>
                    {t.observacoes || <i style={{ color: "#cbd5e1" }}>Nenhuma observação adicionada ainda.</i>}
                  </p>
                )}
              </div>

              {/* Ações de Status (Somente Prestador ou Admin) */}
              {(!isAdmin || (isAdmin && t.prestador_id === user.id)) && (
                <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                  {t.status !== "Pendente" && (
                    <button 
                      onClick={() => handleUpdateStatus(t, "Pendente")}
                      style={{ ...btnStyle("#f59e0b20"), color: "#f59e0b", padding: "6px 12px", fontSize: 12, border: "1px solid #f59e0b40" }}
                    >
                      Marcar como Pendente
                    </button>
                  )}
                  {t.status !== "Em Andamento" && (
                    <button 
                      onClick={() => handleUpdateStatus(t, "Em Andamento")}
                      style={{ ...btnStyle("#2563eb20"), color: "#2563eb", padding: "6px 12px", fontSize: 12, border: "1px solid #2563eb40" }}
                    >
                      Em Andamento
                    </button>
                  )}
                  {t.status !== "Concluído" && (
                    <button 
                      onClick={() => handleUpdateStatus(t, "Concluído")}
                      style={{ ...btnStyle("#16a34a20"), color: "#16a34a", padding: "6px 12px", fontSize: 12, border: "1px solid #16a34a40" }}
                    >
                      Concluído
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
