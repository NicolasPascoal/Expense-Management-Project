import { X } from "lucide-react";
import { inputStyle } from "../utils/styles";
import { fmt, parseVal, calcularValor } from "../utils/format";
import { novaLinha, linhaPreenchida } from "../utils/notaItens";

const LARGURA = { item: "minmax(0, 1fr)", quantidade: "64px", unitario: "112px", valor: "112px" };

export function ItensNota({ itens, setItens, colunasDoItem, erros, semItens }) {
  const preenchidas = itens.filter(linhaPreenchida);
  const totalNota = preenchidas.reduce((soma, linha) => soma + parseVal(linha.valor), 0);
  const colunasGrid = colunasDoItem.map(c => LARGURA[c.name]).join(" ") + " 32px";

  const alterar = (chave, campo, valor) => {
    setItens(lista => lista.map(linha => {
      if (linha.chave !== chave) return linha;
      const nova = { ...linha, [campo]: valor };
      if (campo === "quantidade" || campo === "unitario") {
        nova.valor = calcularValor(nova.quantidade, nova.unitario, nova.valor);
      }
      return nova;
    }));
  };

  const remover = chave => setItens(lista => lista.filter(linha => linha.chave !== chave));
  const adicionar = () => setItens(lista => [...lista, { ...novaLinha(), novo: true }]);

  return (
    <div className="nota-itens" style={{ "--colunas-item": colunasGrid }}>
      <div className="nota-secao">itens da nota</div>

      <div className="nota-item nota-item-cabecalho" aria-hidden="true">
        {colunasDoItem.map(col => <span key={col.name}>{col.label}</span>)}
        <span />
      </div>

      {itens.map((linha, i) => {
        const comErro = erros.has(linha.chave);
        return (
          <div key={linha.chave} className={"nota-item-linha" + (comErro ? " nota-item--erro" : "")}>
            <div className="nota-item">
              {colunasDoItem.map((col, j) => (
                <label key={col.name} className={`nota-campo nota-campo--${col.name}`}>
                  <span className="nota-campo-rotulo">{col.label}</span>
                  <input
                    type={col.type || "text"}
                    inputMode={col.name === "unitario" || col.name === "valor" ? "decimal" : undefined}
                    step={col.type === "number" ? "any" : undefined}
                    value={linha[col.name] ?? ""}
                    onChange={e => alterar(linha.chave, col.name, e.target.value)}
                    aria-label={`${col.label} do item ${i + 1}`}
                    autoFocus={linha.novo && j === 0}
                    style={{ ...inputStyle, marginTop: 0, ...(comErro && col.name === "valor" ? { borderColor: "var(--bad)" } : {}) }}
                    className={col.name === "unitario" || col.name === "valor" ? "mono" : undefined}
                  />
                </label>
              ))}
              {itens.length > 1 ? (
                <button
                  type="button"
                  onClick={() => remover(linha.chave)}
                  className="nota-remover"
                  title="Remover item"
                  aria-label={`Remover item ${i + 1}`}
                >
                  <X size={14} />
                </button>
              ) : <span />}
            </div>
            {comErro && <div className="nota-erro">Informe o valor do item</div>}
          </div>
        );
      })}

      {semItens && <div className="nota-erro">Adicione ao menos um item</div>}
      <button type="button" onClick={adicionar} className="nota-adicionar">+ Adicionar item</button>

      <div className="nota-rodape">
        <span>{preenchidas.length === 1 ? "1 item" : `${preenchidas.length} itens`}</span>
        <span className="nota-total">
          <span className="nota-total-rotulo">total da nota</span>
          <b className="mono">{fmt(totalNota)}</b>
        </span>
      </div>
    </div>
  );
}
