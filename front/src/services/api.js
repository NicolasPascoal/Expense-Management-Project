const API_URL = '/api';
const AUTH_TOKEN = 'token-de-teste';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': AUTH_TOKEN
};

export const api = {
  async getLancamentos() {
    const response = await fetch(`${API_URL}/lancamentos`, { headers });
    if (!response.ok) throw new Error('Erro ao buscar lançamentos');
    return response.json();
  },

  async createLancamento(dados) {
    const response = await fetch(`${API_URL}/lancamentos`, {
      method: 'POST',
      headers,
      body: JSON.stringify(dados)
    });
    if (!response.ok) throw new Error('Erro ao criar lançamento');
    return response.json();
  },

  async updateLancamento(id, dados) {
    const response = await fetch(`${API_URL}/lancamentos/${id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(dados)
    });
    if (!response.ok) throw new Error('Erro ao atualizar lançamento');
    return response.json();
  },

  async deleteLancamento(id) {
    const response = await fetch(`${API_URL}/lancamentos/${id}`, {
      method: 'DELETE',
      headers
    });
    if (!response.ok) throw new Error('Erro ao deletar lançamento');
    return response.json();
  }
};
