import { useState, useEffect } from "react";
import { api } from "../services/api";
import { btnStyle, inputStyle } from "../utils/styles";
import { SenhaModal } from "./SenhaModal";

const ACOES_LINK = { border: "none", background: "none", cursor: "pointer", fontSize: 12, padding: 0 };

const PAPEIS = [
  { valor: "admin", label: "Admin" },
  { valor: "gestor_obra", label: "Gestor de Obra" },
  { valor: "financeiro", label: "Financeiro" },
  { valor: "prestador", label: "Prestador" },
];

export function AdminTab({ askConfirm, usuarios, fetchUsuarios, projetos, user }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("prestador");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [redefinindoSenhaDe, setRedefinindoSenhaDe] = useState(null);

  useEffect(() => {
    // Sincroniza usuários ao abrir a aba
    fetchUsuarios();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const isAdmin = role === "admin";
      await api.createUsuario(username, password, isAdmin, role);
      setUsername("");
      setPassword("");
      setRole("prestador");
      fetchUsuarios();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Tarefa 6.2: marca/desmarca uma obra para o usuário. Admin não aparece
  // aqui — acessa todas as obras da empresa sem precisar de vínculo.
  const handleToggleProjeto = async (usuario, projetoId) => {
    const atuais = usuario.projeto_ids || [];
    const novos = atuais.includes(projetoId)
      ? atuais.filter(id => id !== projetoId)
      : [...atuais, projetoId];
    try {
      await api.setProjetosUsuario(usuario.id, novos);
      fetchUsuarios();
    } catch (err) {
      alert(err.message);
    }
  };

  // As regras (não desativar/rebaixar a si mesmo nem o último admin) ficam no
  // backend; aqui só se esconde o que nunca faria sentido para si mesmo.
  const handleAlterarPapel = async (usuario, novoPapel) => {
    try {
      await api.updateUsuarioRole(usuario.id, novoPapel);
    } catch (err) {
      alert(err.message);
    }
    fetchUsuarios();
  };

  const handleDesativar = (usuario) => {
    askConfirm({
      title: `Desativar o acesso de "${usuario.username}"?`,
      message: "A pessoa sai do sistema na hora. O histórico dela (tarefas, requisições) é mantido e você pode reativar depois.",
      icon: "👤",
      confirmText: "Desativar",
      onConfirm: async () => {
        try {
          await api.deleteUsuario(usuario.id);
          fetchUsuarios();
        } catch (err) {
          alert(err.message);
        }
      }
    });
  };

  const handleReativar = async (usuario) => {
    try {
      await api.reativarUsuario(usuario.id);
      fetchUsuarios();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      {redefinindoSenhaDe && (
        <SenhaModal
          titulo={`Redefinir senha de "${redefinindoSenhaDe.username}"`}
          onClose={() => setRedefinindoSenhaDe(null)}
          onSalvar={async (_, novaSenha) => {
            await api.redefinirSenhaUsuario(redefinindoSenhaDe.id, novaSenha);
            setRedefinindoSenhaDe(null);
            alert("Senha redefinida. As sessões abertas dessa pessoa foram encerradas.");
          }}
        />
      )}
      <div style={{ background: "#fff", padding: 24, borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: 24 }}>
        <h2 style={{ margin: "0 0 16px 0", fontSize: 18 }}>Gestão de Acessos</h2>

        <form onSubmit={handleCreateUser} style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: 12, alignItems: "end" }}>
          <div>
            <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Usuário</label>
            <input
              style={{ ...inputStyle, margin: 0 }}
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Senha</label>
            <input
              type="password"
              style={{ ...inputStyle, margin: 0 }}
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 4 }}>Papel</label>
            <select
              style={{ ...inputStyle, margin: 0 }}
              value={role}
              onChange={e => setRole(e.target.value)}
            >
              {PAPEIS.map(p => (
                <option key={p.valor} value={p.valor}>{p.label}</option>
              ))}
            </select>
          </div>
          <button type="submit" disabled={loading} style={btnStyle("#2563eb")}>
            {loading ? "..." : "Criar Usuário"}
          </button>
        </form>
        {error && <div style={{ color: "#ef4444", fontSize: 13, marginTop: 12 }}>{error}</div>}
      </div>

      <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,0.1)", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "1px solid #e2e8f0" }}>
              <th style={{ padding: "12px 16px", textAlign: "left", fontSize: 13, color: "#64748b" }}>Usuário</th>
              <th style={{ padding: "12px 16px", textAlign: "left", fontSize: 13, color: "#64748b" }}>Permissão / Role</th>
              <th style={{ padding: "12px 16px", textAlign: "left", fontSize: 13, color: "#64748b" }}>Obras</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}></th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map(u => {
              const ehVoce = u.id === user?.id;
              return (
              <tr key={u.id} style={{ borderBottom: "1px solid #f1f5f9", opacity: u.ativo === false ? 0.55 : 1 }}>
                <td style={{ padding: "12px 16px", fontWeight: 500 }}>
                  {u.username}
                  {ehVoce && <span style={{ color: "#64748b", fontWeight: 400, fontSize: 12 }}> (você)</span>}
                  {u.ativo === false && (
                    <span style={{ display: "block", color: "#991b1b", fontSize: 11, fontWeight: 600 }}>INATIVO</span>
                  )}
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <select
                    value={u.role}
                    disabled={ehVoce}
                    title={ehVoce ? "Você não pode alterar o seu próprio papel" : undefined}
                    onChange={e => handleAlterarPapel(u, e.target.value)}
                    style={{ ...inputStyle, margin: 0, fontSize: 12, padding: "4px 8px", width: "auto", minWidth: 140 }}
                  >
                    {PAPEIS.map(p => <option key={p.valor} value={p.valor}>{p.label}</option>)}
                  </select>
                </td>
                <td style={{ padding: "12px 16px", fontSize: 13 }}>
                  {u.is_admin ? (
                    <span style={{ color: "#64748b" }}>Todas</span>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                      {projetos.map(p => (
                        // O <label> global do App.css é mono/minúsculo com !important —
                        // o nome da obra vai num <span> para manter a grafia original.
                        <label key={p.id} style={{ cursor: "pointer", margin: 0 }}>
                          <input
                            type="checkbox"
                            checked={(u.projeto_ids || []).includes(p.id)}
                            onChange={() => handleToggleProjeto(u, p.id)}
                            style={{ marginRight: 6, verticalAlign: "middle" }}
                          />
                          <span style={{ fontFamily: "'Inter', system-ui, sans-serif", fontSize: 13, color: "#334155", textTransform: "none", verticalAlign: "middle" }}>
                            {p.nome}
                          </span>
                        </label>
                      ))}
                      {(u.projeto_ids || []).length === 0 && (
                        <span style={{ color: "#ef4444", fontSize: 11 }}>Sem acesso a nenhuma obra</span>
                      )}
                    </div>
                  )}
                </td>
                <td style={{ padding: "12px 16px", textAlign: "right", whiteSpace: "nowrap" }}>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                    {!ehVoce && (
                      <button onClick={() => setRedefinindoSenhaDe(u)} style={{ ...ACOES_LINK, color: "#2563eb" }}>
                        Redefinir senha
                      </button>
                    )}
                    {!ehVoce && (u.ativo === false ? (
                      <button onClick={() => handleReativar(u)} style={{ ...ACOES_LINK, color: "#16a34a" }}>
                        Reativar
                      </button>
                    ) : (
                      <button onClick={() => handleDesativar(u)} style={{ ...ACOES_LINK, color: "#ef4444" }}>
                        Desativar
                      </button>
                    ))}
                  </div>
                </td>
              </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
