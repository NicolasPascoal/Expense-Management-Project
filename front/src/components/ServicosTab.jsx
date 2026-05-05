import { useState } from "react";
import { btnStyle } from "../utils/styles";

export function ServicosTab({ categoriasDb, contasDb, addCategoria, removeCategoria, addConta, removeConta, askConfirm }) {
  const [newCat, setNewCat] = useState("");
  const [newConta, setNewConta] = useState("");

  const handleAddCat = async () => {
    if (!newCat.trim()) return;
    await addCategoria(newCat.trim());
    setNewCat("");
  };

  const handleAddConta = async () => {
    if (!newConta.trim()) return;
    await addConta(newConta.trim());
    setNewConta("");
  };

  const sectionStyle = {
    background: "#fff",
    borderRadius: 12,
    padding: 24,
    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    display: "flex",
    flexDirection: "column",
    gap: 16
  };

  const listStyle = {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    maxHeight: 400,
    overflowY: "auto",
    paddingRight: 8
  };

  const itemStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 16px",
    background: "#f8fafc",
    borderRadius: 8,
    border: "1px solid #e2e8f0"
  };

  const inputGroupStyle = {
    display: "flex",
    gap: 8
  };

  const inputStyle = {
    flex: 1,
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid #cbd5e1",
    fontSize: 14,
    outline: "none"
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))", gap: 24 }}>
      {/* Gestão de Categorias */}
      <div style={sectionStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <span style={{ fontSize: 24 }}>📂</span>
          <h2 style={{ margin: 0, fontSize: 18, color: "#1e293b" }}>Categorias</h2>
        </div>
        <p style={{ margin: 0, fontSize: 14, color: "#64748b" }}>Gerencie as categorias disponíveis para classificação de despesas.</p>

        <div style={inputGroupStyle}>
          <input
            style={inputStyle}
            placeholder="Nova categoria..."
            value={newCat}
            onChange={e => setNewCat(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && handleAddCat()}
          />
          <button onClick={handleAddCat} style={btnStyle("#2563eb")}>Adicionar</button>
        </div>

        <div style={listStyle} className="custom-scrollbar">
          {categoriasDb.map(cat => (
            <div key={cat.id} style={itemStyle}>
              <span style={{ fontWeight: 500, color: "#334155" }}>{cat.nome}</span>
              <button
                onClick={() => {
                  askConfirm({
                    title: `Excluir categoria "${cat.nome}"?`,
                    message: "Lançamentos já existentes com esta categoria não serão alterados.",
                    icon: "📂",
                    confirmText: "Excluir",
                    onConfirm: () => removeCategoria(cat.id)
                  });
                }}
                style={{ ...btnStyle("#ef4444"), padding: "4px 8px", fontSize: 12 }}
              >
                Excluir
              </button>
            </div>
          ))}
          {categoriasDb.length === 0 && (
            <div style={{ textAlign: "center", color: "#94a3b8", padding: 20 }}>Nenhuma categoria cadastrada.</div>
          )}
        </div>
      </div>

      {/* Gestão de Contas */}
      <div style={sectionStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <span style={{ fontSize: 24 }}>💳</span>
          <h2 style={{ margin: 0, fontSize: 18, color: "#1e293b" }}>Contas / Pagadores</h2>
        </div>
        <p style={{ margin: 0, fontSize: 14, color: "#64748b" }}>Cadastre as contas bancárias ou responsáveis pelos pagamentos.</p>

        <div style={inputGroupStyle}>
          <input
            style={inputStyle}
            placeholder="Nova conta..."
            value={newConta}
            onChange={e => setNewConta(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && handleAddConta()}
          />
          <button onClick={handleAddConta} style={btnStyle("#16a34a")}>Adicionar</button>
        </div>

        <div style={listStyle} className="custom-scrollbar">
          {contasDb.map(conta => (
            <div key={conta.id} style={itemStyle}>
              <span style={{ fontWeight: 500, color: "#334155" }}>{conta.nome}</span>
              <button
                onClick={() => {
                  askConfirm({
                    title: `Excluir conta "${conta.nome}"?`,
                    message: "Lançamentos já existentes com esta conta não serão alterados.",
                    icon: "💳",
                    confirmText: "Excluir",
                    onConfirm: () => removeConta(conta.id)
                  });
                }}
                style={{ ...btnStyle("#ef4444"), padding: "4px 8px", fontSize: 12 }}
              >
                Excluir
              </button>
            </div>
          ))}
          {contasDb.length === 0 && (
            <div style={{ textAlign: "center", color: "#94a3b8", padding: 20 }}>Nenhuma conta cadastrada.</div>
          )}
        </div>
      </div>
    </div>
  );
}
