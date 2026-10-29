# Lançamento com vários itens (nota com mais de um produto)

- **Data:** 2026-10-29
- **Status:** implementado em 2026-10-29
- **Branch:** `feat/lancamento-varios-itens`

## 1. Problema

O cliente lança despesas a partir de notas fiscais. Uma nota costuma ter vários produtos do mesmo fornecedor, mesma data, mesma categoria e mesma forma de pagamento. Hoje o formulário "Novo Lançamento" aceita um produto por vez: para uma nota com 5 itens, o usuário abre o formulário 5 vezes e redigita os mesmos dados comuns.

**Objetivo:** no "Novo Lançamento", preencher os dados comuns da nota uma vez e adicionar quantos itens forem necessários. Cada item tem descrição, quantidade, valor unitário e total.

## 2. Decisão principal: sem alteração no banco de dados

Cada item da nota vira **um lançamento normal** na tabela `lancamentos_v2`. Os campos comuns são copiados para cada um. O JSON `dados` de cada lançamento tem exatamente o mesmo formato de um lançamento feito à mão hoje (`data`, `categoria`, `item`, `fornecedor`, `quantidade`, `unitario`, `valor`, `forma`, `conta`, `obs`).

- Sem tabela nova, sem coluna nova, sem migration.
- Tabela de lançamentos, filtros, totais, Orçamento (realizado por categoria), Fluxo de Caixa, Timeline e exportação CSV continuam funcionando sem alteração, porque todos trabalham com lançamentos individuais.
- **Consequência aceita:** depois de salvos, os itens não ficam ligados entre si. Cada um é editado e excluído individualmente, como se tivesse sido lançado à mão.

## 3. Abordagens consideradas

| # | Abordagem | Decisão |
|---|---|---|
| 1 | **Rota nova `POST /api/lancamentos/lote`**: todos os itens numa requisição e numa transação (tudo ou nada) | **Escolhida.** Muda só código do backend, não o banco. Nunca deixa uma nota salva pela metade |
| 2 | Só frontend, chamando N vezes o `POST /api/lancamentos` atual | Descartada: se a conexão cair no meio, parte da nota fica salva (mesmo problema já documentado na importação CSV, `docs/BusinessRules.md` §8) |
| 3 | Um lançamento só, com a lista de itens dentro do JSON | Descartada: tabela, filtros, Orçamento e CSV teriam de aprender a ler listas |

## 4. Experiência do usuário

### 4.1 Layout do modal "Novo Lançamento" (desktop)

```
┌ ➕ Novo Lançamento ──────────────────────────────────────── ✕ ┐
│ dados da nota                                                  │
│ Data [29/10/2026]        Fornecedor [Depósito São José      ]  │
│ Categoria [Material ▾]   Forma [Pix ▾]      Conta [▾]          │
│ Observações [NF 4521                                        ]  │
│                                                                │
│ itens da nota                                                  │
│  Item / descrição               Qtd   Unitário      Total      │
│  [Cimento CP-II 50kg        ]  [10]  [   38,90]  [  389,00]  ✕ │
│  [Areia média m³            ]  [ 2]  [  120,00]  [  240,00]  ✕ │
│  + Adicionar item                                              │
│ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ 2 itens                              total da nota  R$ 629,00  │
│                           [Cancelar]  [Salvar 2 lançamentos]   │
└────────────────────────────────────────────────────────────────┘
```

- **Dados da nota (campos comuns):** todas as colunas da obra, exceto as quatro do item. Na obra padrão: data, categoria, fornecedor, forma, conta e obs. A conta é comum por ser o mesmo pagamento.
- **Itens da nota (por item):** `item` (descrição), `quantidade` (padrão `1`), `unitario` e `valor` (total), só as que existirem nas colunas da obra.
- **Uma nota de um item só** é a mesma tela com uma linha. Não existe chave de "modo múltiplo".
- Modal mais largo nesse modo: `max-width` de 760px, contra 560px hoje.

### 4.2 Celular (largura ≤ 600px)

Cada item vira um cartão: descrição em largura total em cima; Qtd, Unitário e Total lado a lado embaixo; ✕ no canto superior direito. Os títulos das colunas somem e cada campo mostra o próprio rótulo.

### 4.3 Identidade visual

Segue o sistema de design já existente em `front/src/index.css`, sem cores ou fontes novas:

- Rótulos de seção ("dados da nota", "itens da nota") no estilo de `.filtro-label`: IBM Plex Mono, minúsculas, cor `--mut`.
- Unitário, total do item e total da nota em IBM Plex Mono.
- Botão principal com a classe `.btn-primary` (terracota `--accent`); Cancelar com `.btn-secondary`.
- **Elemento de assinatura (o único novo):** o rodapé com linha tracejada (`1px dashed var(--line)`) e o "total da nota" em mono, lembrando o fim de um cupom fiscal. Ele atualiza enquanto o usuário digita. O resto fica discreto.

### 4.4 Textos da interface

| Lugar | Texto |
|---|---|
| Rótulo da seção comum | `dados da nota` |
| Rótulo da seção de itens | `itens da nota` |
| Botão de adicionar | `+ Adicionar item` |
| Botão de remover (ícone ✕) | `title`/`aria-label`: `Remover item` (escondido quando só existe uma linha) |
| Contador no rodapé | `1 item` / `N itens` (conta só linhas preenchidas) |
| Total no rodapé | `total da nota` + valor formatado (`R$ 629,00`) |
| Botão salvar | `Salvar lançamento` (0 ou 1 item) / `Salvar N lançamentos` (2 ou mais) |
| Botão salvar, durante o envio | `Salvando…` (desabilitado) |
| Erro de linha sem total | `Informe o valor do item` (abaixo da linha, borda `--bad`) |
| Nenhuma linha preenchida | `Adicione ao menos um item` (acima do botão "+ Adicionar item") |
| Falha ao salvar | `alert`: `Nenhum item foi salvo: <mensagem do servidor>` |

## 5. Regras de comportamento

1. **Data obrigatória** (regra atual, mantida): sem data não salva, com o mesmo `alert` de hoje.
2. **Total do item:** ao mudar Qtd ou Unitário, o total vira `quantidade × unitário` quando os dois são maiores que zero. É a mesma regra do formulário atual, e o total continua editável à mão.
3. **Linha vazia é ignorada:** uma linha sem descrição, unitário e total (quantidade sozinha não conta) não vira lançamento.
4. **Linha preenchida precisa de total maior que zero.** Caso contrário, a linha fica destacada com `Informe o valor do item` e nada é enviado. É uma regra nova, só no frontend; o backend continua sem validar campos, como hoje.
5. **Ao menos um item:** se todas as linhas estiverem vazias, o formulário pede `Adicione ao menos um item`.
6. **Sem duplicidade por clique duplo:** o botão salvar fica desabilitado enquanto a requisição está em andamento.
7. **Ordem:** os lançamentos são gravados na ordem das linhas.
8. **Fluxos que não mudam** (continuam com um item só, sem "+ Adicionar item", usando as rotas atuais):
   - Editar um lançamento existente (lápis na tabela) → `PUT /api/lancamentos/:id`.
   - Gerar lançamento a partir de requisição (Tarefa 7.5) → `POST /api/lancamentos` com `requisicao_id`.
9. **Obras com colunas personalizadas** (criadas via importação CSV): o que não for `item`/`quantidade`/`unitario`/`valor` vira campo comum. Se a obra não tiver nenhuma dessas quatro colunas, o formulário fica exatamente como hoje.

## 6. Arquitetura

### 6.1 Frontend

| Arquivo | Mudança |
|---|---|
| `front/src/components/ItensNota.jsx` (novo) | Lista de linhas de item: render, adicionar, remover, cálculo do total por linha, erro por linha, rodapé com contador e total da nota. Recebe `itens`, `setItens`, `colunasDoItem` e `erros` |
| `front/src/components/FormModal.jsx` | Decide o modo: com itens quando `!editId && !form.requisicao_id` e a obra tem alguma coluna de item. Nesse modo, renderiza "dados da nota" (colunas comuns) + `<ItensNota>`. O estado `itens` (começa com uma linha) e `salvando` ficam no próprio modal, que é montado a cada abertura e por isso já começa limpo. Valida as linhas (regras 3–5) antes de chamar `saveForm(itens)` |
| `front/src/hooks/useExpenses.js` | `saveForm(itens)`: quando recebe itens, monta um lançamento por linha (`{...form, item, quantidade, unitario: parseVal(..), valor: parseVal(..)}`), chama `api.createLancamentosEmLote` e acrescenta os retornados em `dados`. Sem itens, o comportamento atual não muda |
| `front/src/services/api.js` | `createLancamentosEmLote(projetoId, lancamentos)` → `POST /api/lancamentos/lote` |
| `front/src/utils/format.js` | Extrai a regra do total (`quantidade × unitário`) para uma função pura usada pelo `handleForm` atual e pelo `ItensNota`, sem duplicar a lógica |
| `front/src/data/constants.js` | `COLUNAS_DO_ITEM = ["item", "quantidade", "unitario", "valor"]` |
| `front/src/index.css` | Classes das linhas de item, modal largo, versão celular e rodapé tracejado |

### 6.2 Backend: `POST /api/lancamentos/lote`

- **Decorators:** `@token_required` + `@non_prestador_required`, iguais aos do `POST /api/lancamentos`.
- **Corpo:**
  ```json
  {
    "projeto_id": 3,
    "lancamentos": [
      {"data": "29/10/2026", "categoria": "Material de construção", "fornecedor": "Depósito São José",
       "item": "Cimento CP-II 50kg", "quantidade": "10", "unitario": 38.9, "valor": 389.0,
       "forma": "Pix", "conta": "", "obs": "NF 4521"}
    ]
  }
  ```
- **Validação (qualquer falha → nada é gravado):**

  | Situação | Resposta |
  |---|---|
  | `projeto_id` ausente | `400 {"erro": "projeto_id é obrigatório"}` |
  | Obra de outra empresa ou não vinculada ao usuário (`usuario_acessa_projeto`) | `400 {"erro": "projeto_id inválido"}` |
  | `lancamentos` não é lista, ou lista vazia | `400 {"erro": "Envie ao menos um lançamento"}` |
  | Mais de 100 itens | `400 {"erro": "Máximo de 100 lançamentos por vez"}` |
  | Algum item não é objeto JSON | `400 {"erro": "Lançamento inválido na posição N"}` |
  | Algum item tem `requisicao_id` | `400 {"erro": "Lançamento de requisição não pode ser criado em lote"}` |
  | Usuário `prestador` | `403` (decorator) |

- **Gravação:** chaves `id` e `projeto_id` dentro de cada item são descartadas (como já faz o `POST` atual com `projeto_id`). Toda a validação acontece antes do primeiro `INSERT`. Os `INSERT` usam uma única conexão e um único `commit` no fim. Em caso de exceção, a função chama `conn.rollback()` explicitamente antes de propagar o erro, sem depender só do pool desfazer a transação ao fechar a conexão. Isso também faz o teste de atomicidade funcionar com a fixture `db_session`, em que `close()` não faz nada.
- **Função:** `criar_lancamentos_em_lote(projeto_id, lista, empresa_id)` em `lancamentos_controller.py`, no mesmo padrão `try/finally` de `criar_lancamento_de_requisicao`.
- **Resposta:** `201` com a lista dos lançamentos criados, no mesmo formato do `GET /api/lancamentos` e na ordem enviada.
- **Auditoria:** depois do commit, um evento `criar` por lançamento. `detalhes` = `item` (ou `categoria`, como hoje), com o sufixo ` (nota com N itens)` quando N > 1.
- **Rota sem conflito:** `/lancamentos/lote` não colide com `/lancamentos/<int:id>`, que só aceita número.

## 7. Testes

**Backend** (`back/tests/test_lancamentos_lote.py`, pytest contra o Postgres de teste, conforme ADR-001):

1. Lote com 3 itens cria 3 lançamentos com os campos comuns copiados, na ordem enviada; a resposta tem 3 itens.
2. Obra de outra empresa → 400 e nenhum lançamento criado.
3. Usuário não-admin sem vínculo com a obra (Tarefa 6.2) → 400 e nada criado.
4. Usuário `prestador` → 403.
5. Lista vazia, lista acima de 100 e item que não é objeto → 400 e nada criado.
6. Item com `requisicao_id` → 400 e nada criado.
7. Atomicidade: falha no meio da gravação (por exemplo, forçando erro no N-ésimo `INSERT`) → nenhum lançamento do lote fica no banco.
8. Auditoria: um evento `criar` por lançamento criado.

**Frontend:** teste manual no navegador. O projeto ainda não tem Vitest (ADR-001 prevê introduzir junto com a divisão do `useExpenses`).

1. Nota de 1 item e de 3 itens: contador, total da nota e texto do botão corretos.
2. Total por linha recalcula ao mudar Qtd ou Unitário e aceita edição manual.
3. Linha vazia é ignorada; linha preenchida sem total bloqueia e mostra o erro.
4. Clique duplo em Salvar não duplica.
5. Editar (lápis) e "Gerar lançamento" a partir de requisição continuam iguais.
6. Celular (≤ 600px): itens em cartões, sem rolagem horizontal.
7. Lint (`npm run lint`) e build (`npm run build`) sem erros.

## 8. Fora do escopo

- Agrupar os itens salvos por nota (por exemplo, um "nº da nota"). Se for pedido depois, dá para guardar dentro do JSON `dados`, ainda sem alterar o banco.
- Categoria diferente por item: a categoria é comum à nota, conforme pedido.
- Editar a nota inteira de uma vez: a edição continua por lançamento.
- Usar a rota de lote na importação CSV. Resolveria a importação não atômica documentada, mas é outra tarefa.
- Testes automatizados de frontend.

## 9. Documentação a atualizar na implementação

- `docs/API.md` §2: nova rota `POST /api/lancamentos/lote`.
- `docs/BusinessRules.md` §4: lançamento com vários itens e as regras da seção 5.
- `STATUS.md`: entrada no log de mudanças.
