// Linhas da nota com vários itens (ItensNota/FormModal).

let proximaChave = 1;
export const novaLinha = () => ({ chave: proximaChave++, item: "", quantidade: "1", unitario: "", valor: "" });

// Quantidade sozinha não conta: toda linha nova já nasce com quantidade 1.
export const linhaPreenchida = linha =>
  ["item", "unitario", "valor"].some(campo => String(linha[campo] ?? "").trim() !== "");
