import { useState } from "react";
import { labelStyle, inputStyle } from "../utils/styles";
import { FORMAS, COLUNAS_DO_ITEM } from "../data/constants";
import { parseVal } from "../utils/format";
import { ItensNota } from "./ItensNota";
import { novaLinha, linhaPreenchida } from "../utils/notaItens";

// Ignora maiúsculas e acentos ("ébano" entre "Documentação" e "Ferramentas").
const ordemAlfabetica = new Intl.Collator("pt-BR", { sensitivity: "base" });

export function FormModal({
  form,
  editId,

  projetoAtivo,
  categoriasDb,
  contasDb,
  handleForm,
  saveForm,
  setShowForm,
  setEditId
}) {
  // Nota com vários itens: estado local — o modal é montado a cada abertura,
  // então já começa limpo.
  const [itens, setItens] = useState(() => [novaLinha()]);
  const [erros, setErros] = useState(new Set());
  const [semItens, setSemItens] = useState(false);
  const [salvando, setSalvando] = useState(false);

  if (!projetoAtivo) return null;

  const colunasDoItem = projetoAtivo.colunas.filter(c => COLUNAS_DO_ITEM.includes(c.name));
  // Editar e gerar a partir de requisição continuam com um item só.
  const modoNota = !editId && !form.requisicao_id && colunasDoItem.length > 0;
  const colunasDoForm = modoNota
    ? projetoAtivo.colunas.filter(c => !COLUNAS_DO_ITEM.includes(c.name))
    : projetoAtivo.colunas;
  const qtdItens = itens.filter(linhaPreenchida).length;

  const fechar = () => { setShowForm(false); setEditId(null); };

  const salvar = async () => {
    if (salvando) return;
    let lista;
    if (modoNota) {
      const preenchidas = itens.filter(linhaPreenchida);
      const exigeValor = colunasDoItem.some(c => c.name === "valor");
      const semValor = exigeValor ? preenchidas.filter(l => !(parseVal(l.valor) > 0)).map(l => l.chave) : [];
      setErros(new Set(semValor));
      setSemItens(preenchidas.length === 0);
      if (semValor.length || preenchidas.length === 0) return;
      lista = preenchidas.map(l => Object.fromEntries(colunasDoItem.map(c => [c.name, l[c.name]])));
    }
    setSalvando(true);
    try {
      await saveForm(lista);
    } finally {
      setSalvando(false);
    }
  };

  const textoSalvar = salvando ? "Salvando…"
    : modoNota ? (qtdItens > 1 ? `Salvar ${qtdItens} lançamentos` : "Salvar lançamento")
    : editId ? "Salvar Alterações" : "Adicionar";

  const getOptions = (col) => {
    // Só as categorias/contas cadastradas: obras antigas têm uma lista fixa
    // gravada em col.options que não existe no banco. Mostrá-la quando não
    // havia nenhuma cadastrada fazia ela "sumir" ao cadastrar a primeira.
    // Ordenado aqui, não só no ORDER BY do backend: a ordenação do Postgres
    // depende do locale do banco (no postgres:alpine é por byte — minúsculas
    // e acentos iniciais vão para o fim da lista).
    if (col.name === 'categoria') return categoriasDb.map(c => c.nome).sort(ordemAlfabetica.compare);
    if (col.name === 'conta') return contasDb.map(c => c.nome);
    if (col.name === 'forma') return (col.options && col.options.length) ? col.options : FORMAS;
    return col.options || [];
  };

  return (
    <div className="modal-overlay">
      <div className={"modal-box" + (modoNota ? " modal-box--nota" : "")}>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <b style={{ fontSize: 16 }}>{editId ? "✏️ Editar Lançamento" : "➕ Novo Lançamento"}</b>
          <button onClick={fechar} style={{ border: "none", background: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}>✕</button>
        </div>

        {form.requisicao_id && (
          <div style={{ background: "#eff6ff", color: "#1e40af", padding: "8px 12px", borderRadius: 8, fontSize: 13, marginBottom: 12 }}>
            Gerado a partir da requisição #{form.requisicao_id} — será lançado na obra <b>{projetoAtivo.nome}</b>.
          </div>
        )}

        {modoNota && <div className="nota-secao">dados da nota</div>}
        <div className="modal-form-grid">
          {colunasDoForm.map(col => (
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
                  <option value="">
                    {col.name === "conta" && contasDb.length === 0
                      ? "Nenhuma conta cadastrada — adicione na aba Serviços"
                      : col.name === "categoria" && categoriasDb.length === 0
                        ? "Nenhuma categoria cadastrada — adicione na aba Serviços"
                        : "Selecione..."}
                  </option>
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

        {modoNota && (
          <ItensNota
            itens={itens}
            setItens={setItens}
            colunasDoItem={colunasDoItem}
            erros={erros}
            semItens={semItens}
          />
        )}

        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end", flexWrap: "wrap" }}>
          <button onClick={fechar} className="btn-secondary">Cancelar</button>
          <button onClick={salvar} disabled={salvando} className="btn-primary">{textoSalvar}</button>
        </div>
      </div>
    </div>
  );
}
