import { useState } from "react";
import { labelStyle, inputStyle, btnStyle } from "../utils/styles";

export function ProjectModal({ setShowProjectModal, createProject }) {
  const [nome, setNome] = useState("");

  const handleSave = () => {
    if (!nome) return alert("Digite o nome do projeto");
    createProject(nome);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-box" style={{ maxWidth: 400 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <b style={{ fontSize: 16 }}>🆕 Novo Projeto</b>
          <button onClick={() => setShowProjectModal(false)} style={{ border: "none", background: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}>✕</button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <label style={labelStyle}>
            Nome do Projeto
            <input 
              value={nome} 
              onChange={e => setNome(e.target.value)} 
              placeholder="Ex: Obra Itanhaém" 
              style={inputStyle}
              autoFocus
            />
          </label>
          <p style={{ fontSize: 12, color: "#64748b" }}>
            * O projeto será criado com as colunas padrão de gestão de despesas. 
            Você poderá importar um CSV para criar colunas diferentes automaticamente.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end" }}>
          <button onClick={() => setShowProjectModal(false)} style={btnStyle("#64748b")}>Cancelar</button>
          <button onClick={handleSave} style={btnStyle("#2563eb")}>Criar Projeto</button>
        </div>
      </div>
    </div>
  );
}
