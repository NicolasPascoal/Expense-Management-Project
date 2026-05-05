import { labelStyle, inputStyle, btnStyle } from "../utils/styles";
import { FORMAS } from "../data/constants";

export function FormModal({
  form,
  editId,
  scanning,
  projetoAtivo,
  categoriasDb,
  contasDb,
  handleForm,
  saveForm,
  setShowForm,
  setEditId
}) {
  if (!projetoAtivo) return null;

  const getOptions = (col) => {
    if (col.name === 'categoria') return categoriasDb.length ? categoriasDb.map(c => c.nome) : (col.options || []);
    if (col.name === 'conta') return contasDb.length ? contasDb.map(c => c.nome) : (col.options || []);
    if (col.name === 'forma') return (col.options && col.options.length) ? col.options : FORMAS;
    return col.options || [];
  };

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        {scanning && (
          <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 8, padding: "12px 16px", marginBottom: 16, display: "flex", alignItems: "center", gap: 10, color: "#1e40af", fontSize: 14 }}>
            <span style={{ fontSize: 20 }}>🔍</span>
            <span>Lendo o recibo com IA... aguarde um instante.</span>
          </div>
        )}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <b style={{ fontSize: 16 }}>{editId ? "✏️ Editar Lançamento" : "➕ Novo Lançamento"}</b>
          <button onClick={() => { setShowForm(false); setEditId(null); }} style={{ border: "none", background: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}>✕</button>
        </div>

        <div className="modal-form-grid">
          {projetoAtivo.colunas.map(col => (
            <label
              key={col.name}
              style={labelStyle}
              className={col.fullWidth ? "full-width" : ""}
            >
              {col.label} {col.required ? "*" : ""}

              {col.type === "select" ? (
                <select
                  name={col.name}
                  value={form[col.name] || ""}
                  onChange={handleForm}
                  style={inputStyle}
                >
                  <option value="">Selecione...</option>
                  {getOptions(col).map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : col.type === "textarea" ? (
                <textarea
                  name={col.name}
                  value={form[col.name] || ""}
                  onChange={handleForm}
                  style={{ ...inputStyle, resize: "vertical", height: 60 }}
                />
              ) : (
                <input
                  type={col.type || "text"}
                  name={col.name}
                  value={form[col.name] || ""}
                  onChange={handleForm}
                  style={inputStyle}
                  placeholder={col.placeholder || ""}
                  step={col.type === "number" ? "any" : undefined}
                />
              )}
            </label>
          ))}
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end", flexWrap: "wrap" }}>
          <button onClick={() => { setShowForm(false); setEditId(null); }} style={btnStyle("#64748b")}>Cancelar</button>
          <button onClick={saveForm} style={btnStyle("#2563eb")}>{editId ? "Salvar Alterações" : "Adicionar"}</button>
        </div>
      </div>
    </div>
  );
}
