export const fmt = v => v.toLocaleString("pt-BR",{style:"currency",currency:"BRL"});

// Total do item: quantidade × unitário quando os dois são > 0; senão mantém
// o valor atual (que o usuário pode ter digitado à mão).
export const calcularValor = (quantidade, unitario, valorAtual) => {
  const q = parseFloat(quantidade) || 0;
  const u = parseVal(unitario) || 0;
  return q && u ? (q * u).toFixed(2) : valorAtual;
};

export const parseVal = s => {
  if(typeof s === "number") return s;
  const str = String(s).replace(/R\$\s*/g, "").trim();
  // Se tem vírgula, é formato pt-BR: 1.234,56 → remove pontos de milhar, troca vírgula por ponto
  if(str.includes(",")) {
    return parseFloat(str.replace(/\./g, "").replace(",", ".")) || 0;
  }
  // Senão já está em formato numérico com ponto decimal americano: 45.00, 1234.50
  return parseFloat(str) || 0;
};
