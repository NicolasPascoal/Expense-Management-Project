import { useState } from "react";
import { labelStyle, inputStyle, btnStyle } from "../utils/styles";

// Troca da própria senha (pedirSenhaAtual) ou redefinição pelo admin.
// onSalvar(senhaAtual, novaSenha) deve lançar erro com mensagem amigável.
export function SenhaModal({ titulo, pedirSenhaAtual, onSalvar, onClose }) {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErro("");
    if (novaSenha !== confirmacao) return setErro("As senhas não conferem.");
    setSalvando(true);
    try {
      await onSalvar(senhaAtual, novaSenha);
    } catch (err) {
      setErro(err.message);
      setSalvando(false);
    }
  };

  return (
    <div className="modal-overlay">
      <form className="modal-box" style={{ maxWidth: 400 }} onSubmit={handleSalvar}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <b style={{ fontSize: 16 }}>{titulo}</b>
          <button type="button" onClick={onClose} style={{ border: "none", background: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}>✕</button>
        </div>

        {pedirSenhaAtual && (
          <label style={labelStyle}>
            Senha atual
            <input type="password" value={senhaAtual} onChange={e => setSenhaAtual(e.target.value)} style={inputStyle} required autoFocus />
          </label>
        )}
        <label style={labelStyle}>
          Nova senha (mínimo 6 caracteres)
          <input type="password" value={novaSenha} onChange={e => setNovaSenha(e.target.value)} style={inputStyle} required minLength={6} autoFocus={!pedirSenhaAtual} />
        </label>
        <label style={labelStyle}>
          Confirme a nova senha
          <input type="password" value={confirmacao} onChange={e => setConfirmacao(e.target.value)} style={inputStyle} required minLength={6} />
        </label>

        {erro && <div style={{ color: "#ef4444", fontSize: 13, marginTop: 8 }}>{erro}</div>}

        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end" }}>
          <button type="button" onClick={onClose} style={btnStyle("#64748b")}>Cancelar</button>
          <button type="submit" disabled={salvando} style={btnStyle("#2563eb")}>{salvando ? "Salvando..." : "Salvar"}</button>
        </div>
      </form>
    </div>
  );
}
