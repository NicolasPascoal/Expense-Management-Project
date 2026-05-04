export const fmt = v => v.toLocaleString("pt-BR",{style:"currency",currency:"BRL"});

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
