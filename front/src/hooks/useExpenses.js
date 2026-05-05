import { useState, useMemo, useRef, useEffect } from "react";
import { api } from "../services/api";
import { FORMAS, DEFAULT_COLUMNS } from "../data/constants";
import { parseVal } from "../utils/format";

export function useExpenses() {
  const [tab, setTab] = useState("dashboard");
  const [dados, setDados] = useState([]);
  const [form, setForm] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [filtros, setFiltros] = useState({categoria:"",conta:"",forma:"",busca:""});
  const [deleteId, setDeleteId] = useState(null);
  const [confirmConfig, setConfirmConfig] = useState(null);
  const fileRef = useRef();
  const receiptRef = useRef();
  const [scanning, setScanning] = useState(false);

  // Estados de Projeto
  const [projetos, setProjetos] = useState([]);
  const [projetoAtivo, setProjetoAtivo] = useState(null);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user") || "null"));
  const [categoriasDb, setCategoriasDb] = useState([]);
  const [contasDb, setContasDb] = useState([]);
  const [requisicoes, setRequisicoes] = useState([]);

  useEffect(() => {
    if (token) {
      fetchRequisicoes();
    }
  }, [token]);

  const fetchRequisicoes = async () => {
    try {
      const res = await api.getRequisicoes();
      setRequisicoes(res);
    } catch (e) {
      console.error("Erro ao buscar requisições:", e);
    }
  };

  const createRequisicao = async (dados) => {
    try {
      await api.createRequisicao(dados);
      fetchRequisicoes();
    } catch (e) {
      alert("Erro ao criar requisição: " + e.message);
    }
  };

  const updateRequisicaoStatus = async (id, status) => {
    try {
      await api.updateRequisicaoStatus(id, status);
      fetchRequisicoes();
    } catch (e) {
      alert("Erro ao atualizar status: " + e.message);
    }
  };

  useEffect(() => {
    const handleAuthError = () => {
      setToken(null);
    };
    window.addEventListener("auth-error", handleAuthError);
    return () => window.removeEventListener("auth-error", handleAuthError);
  }, []);

  useEffect(() => {
    if (token) {
      fetchProjetos();
    }
  }, [token]);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    if (token && projetoAtivo) {
      fetchServicos();
    }
  }, [projetoAtivo, token]);

  const fetchServicos = async () => {
    if (!projetoAtivo) return;
    try {
      const [cats, ctas] = await Promise.all([
        api.getCategorias(projetoAtivo.id),
        api.getContas(projetoAtivo.id)
      ]);
      setCategoriasDb(cats);
      setContasDb(ctas);
    } catch (err) {
      console.error("Erro ao buscar serviços:", err);
    }
  };

  const addCategoria = async (nome) => {
    if (!projetoAtivo) return;
    try {
      await api.createCategoria(nome, projetoAtivo.id);
      fetchServicos();
    } catch (err) {
      alert(err.message);
    }
  };

  const removeCategoria = async (id) => {
    try {
      await api.deleteCategoria(id);
      fetchServicos();
    } catch (err) {
      alert(err.message);
    }
  };

  const addConta = async (nome) => {
    if (!projetoAtivo) return;
    try {
      await api.createConta(nome, projetoAtivo.id);
      fetchServicos();
    } catch (err) {
      alert(err.message);
    }
  };

  useEffect(() => {
    if (projetoAtivo) {
      fetchDados();
    }
  }, [projetoAtivo]);

  const fetchProjetos = async () => {
    try {
      const res = await api.getProjetos();
      setProjetos(res);
      if (res.length > 0 && !projetoAtivo) {
        setProjetoAtivo(res[0]);
      }
    } catch (e) {
      console.error("Erro ao buscar projetos:", e);
    }
  };

  const fetchDados = async () => {
    if (!projetoAtivo) return;
    try {
      const res = await api.getLancamentos(projetoAtivo.id);
      setDados(res);
    } catch (e) {
      console.error("Erro ao buscar dados:", e);
    }
  };

  const createProject = async (nome, colunas = DEFAULT_COLUMNS) => {
    try {
      const novo = await api.createProjeto({ nome, colunas });
      setProjetos([...projetos, novo]);
      setProjetoAtivo(novo);
      setShowProjectModal(false);
    } catch (e) {
      alert("Erro ao criar projeto");
    }
  };

  const deleteProject = async (id) => {
    try {
      await api.deleteProjeto(id);
      const novosProjetos = projetos.filter(p => p.id !== id);
      setProjetos(novosProjetos);
      setProjetoAtivo(novosProjetos.length > 0 ? novosProjetos[0] : null);
      if (novosProjetos.length === 0) setDados([]);
    } catch (e) {
      alert("Erro ao excluir projeto");
    }
  };

  const filtered = useMemo(() => {
    return dados.filter(d => {
      if(filtros.categoria && d.categoria !== filtros.categoria) return false;
      if(filtros.conta && d.conta !== filtros.conta) return false;
      if(filtros.forma && d.forma !== filtros.forma) return false;
      if(filtros.busca) {
        const b = filtros.busca.toLowerCase();
        // Busca em todos os campos do objeto
        return Object.values(d).some(v => (v||"").toString().toLowerCase().includes(b));
      }
      return true;
    });
  }, [dados, filtros]);

  const totalFiltrado = filtered.reduce((a,d)=>a+parseVal(d.valor),0);

  const porCategoria = useMemo(()=>{
    const m={};
    dados.forEach(d=>{
      const cat = d.categoria || "Outros";
      const v=parseVal(d.valor); 
      m[cat]=(m[cat]||0)+v;
    });
    return Object.entries(m).sort((a,b)=>b[1]-a[1]);
  },[dados]);

  const porConta = useMemo(()=>{
    const m={};
    dados.forEach(d=>{
      const conta = d.conta || "N/A";
      const v=parseVal(d.valor); 
      m[conta]=(m[conta]||0)+v;
    });
    return Object.entries(m).sort((a,b)=>b[1]-a[1]);
  },[dados]);

  const totalGeral = dados.reduce((a,d)=>a+parseVal(d.valor),0);

  const handleForm = e => {
    const {name,value} = e.target;
    setForm(f=>{
      const nf = {...f,[name]:value};
      if(name==="quantidade"||name==="unitario"){
        const q=parseFloat(nf.quantidade)||0;
        const u=parseVal(nf.unitario)||0;
        nf.valor = q&&u ? (q*u).toFixed(2) : nf.valor;
      }
      return nf;
    });
  };

  const saveForm = async () => {
    if (!projetoAtivo) return;
    
    // Validação básica se as colunas padrão existirem
    if(projetoAtivo.colunas.some(c => c.name === 'data') && !form.data) {
        return alert("O campo Data é obrigatório.");
    }
    
    try {
      if(editId) {
        const updated = await api.updateLancamento(editId, {
          ...form,
          valor: parseVal(form.valor),
          unitario: parseVal(form.unitario)
        });
        setDados(dados.map(x => x.id === editId ? updated : x));
        setEditId(null);
      } else {
        const novo = await api.createLancamento({
          ...form,
          projeto_id: projetoAtivo.id,
          valor: parseVal(form.valor),
          unitario: parseVal(form.unitario)
        });
        setDados([...dados, novo]);
      }
      setForm({});
      setShowForm(false);
    } catch (e) {
      alert("Erro ao salvar lançamento");
    }
  };

  const startEdit = row => {
    setForm({...row});
    setEditId(row.id);
    setShowForm(true);
    setTab("lancamentos");
  };

  const askConfirm = (config) => {
    setConfirmConfig(config);
  };

  const exportCSV = () => {
    if (!projetoAtivo) return;
    const cols = projetoAtivo.colunas.map(c => c.label);
    const names = projetoAtivo.colunas.map(c => c.name);
    
    const rows = filtered.map(d => names.map(n => {
        let v = d[n] || "";
        if (n === 'valor' || n === 'unitario') v = parseVal(v).toLocaleString("pt-BR",{style:"currency",currency:"BRL"});
        return `"${v}"`;
    }).join(";"));

    const csv="\uFEFF"+[cols.join(";"),...rows].join("\n");
    const a=document.createElement("a");
    a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    a.download=`despesas_${projetoAtivo.nome.toLowerCase().replace(/ /g,"_")}.csv`;
    a.click();
  };

  const scanReceipt = async e => {
    const file = e.target.files[0]; if(!file) return;
    if (!projetoAtivo) return;

    setScanning(true);
    setShowForm(true); setEditId(null); setForm({});
    e.target.value="";
    try {
      const base64 = await new Promise((res,rej)=>{
        const r=new FileReader();
        r.onload=()=>res(r.result.split(",")[1]);
        r.onerror=()=>rej(new Error("Erro ao ler arquivo"));
        r.readAsDataURL(file);
      });
      
      const mediaType = file.type||"image/jpeg";
      const isPdf = mediaType==="application/pdf";
      const contentBlock = isPdf
        ? {type:"document",source:{type:"base64",media_type:"application/pdf",data:base64}}
        : {type:"image",source:{type:"base64",media_type:mediaType,data:base64}};

      // Aqui poderíamos adaptar o prompt dinamicamente baseado nas colunas do projeto
      // Mas por enquanto mantemos o padrão que atende a maioria das obras
      const resp = await fetch("https://api.anthropic.com/v1/messages",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
          model:"claude-sonnet-4-20250514",
          max_tokens:1000,
          messages:[{
            role:"user",
            content:[
              contentBlock,
              {type:"text",text:`Analise este recibo e extraia as informações. Retorne APENAS um JSON válido.
              Tente mapear para estes campos se possível: ${projetoAtivo.colunas.map(c=>c.name).join(", ")}.`}
            ]
          }]
        })
      });
      const data = await resp.json();
      const text = data.content.map(c=>c.text||"").join("");
      const clean = text.replace(/```json|```/g,"").trim();
      const parsed = JSON.parse(clean);
      setForm(f=>({...f, ...parsed}));
    } catch(err) {
      alert("Erro ao ler o recibo. Tente preencher manualmente.");
    } finally {
      setScanning(false);
    }
  };

  const removeConta = async (id) => {
    try {
      await api.deleteConta(id);
      fetchServicos();
    } catch (err) {
      alert(err.message);
    }
  };

  const importCSV = e => {
    const file = e.target.files[0]; if(!file) return;
    const reader = new FileReader();
    reader.onload = async ev => {
      const content = ev.target.result;
      const lines = content.split(/\r?\n/).filter(line => {
        const trimmed = line.trim();
        // Ignora linhas totalmente vazias ou que contenham apenas separadores (,,,, ou ;;;;)
        return trimmed.length > 0 && trimmed.replace(/[,;]/g, "").length > 0;
      });
      if (lines.length === 0) return;

      // Detecta o separador (vírgula ou ponto-e-vírgula)
      const firstLine = lines[0];
      const separator = firstLine.includes(";") ? ";" : ",";

      // Função auxiliar para processar uma linha de CSV respeitando aspas
      const parseCSVLine = (line) => {
        const result = [];
        let current = "";
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"') {
            inQuotes = !inQuotes;
          } else if (char === separator && !inQuotes) {
            result.push(current.trim().replace(/^"|"$/g, ""));
            current = "";
          } else {
            current += char;
          }
        }
        result.push(current.trim().replace(/^"|"$/g, ""));
        return result;
      };

      const headers = parseCSVLine(lines[0]).map(h => h.toLowerCase());
      
      let targetProjeto = projetoAtivo;
      
      if (!targetProjeto) {
        // Criar projeto automático baseado nos cabeçalhos
        const colunas = headers.map(h => ({
            name: h.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, "_"),
            label: h.charAt(0).toUpperCase() + h.slice(1),
            type: "text"
        }));
        const nome = file.name.split(".")[0];
        try {
            targetProjeto = await api.createProjeto({ nome, colunas });
            setProjetos(prev => [...prev, targetProjeto]);
            setProjetoAtivo(targetProjeto);
        } catch (err) {
            return alert("Erro ao criar projeto automático");
        }
      }

      let count = 0;
      for(let i = 1; i < lines.length; i++){
        const vals = parseCSVLine(lines[i]);
        const payload = {};
        let hasData = false;
        
        // Mapeamento inteligente: tenta encontrar a coluna pelo nome ou pelo índice
        targetProjeto.colunas.forEach((col, j) => {
            // Tenta encontrar o índice da coluna no CSV pelo nome ou label
            const csvIndex = headers.findIndex(h => 
              h === col.name.toLowerCase() || 
              h === col.label.toLowerCase()
            );
            
            const indexToUse = csvIndex !== -1 ? csvIndex : j;
            const val = vals[indexToUse] || "";
            payload[col.name] = val;
            
            if (val.trim().length > 0) hasData = true;
        });

        if (!hasData) continue; // Pula se a linha não tiver nenhum dado real

        try {
          await api.createLancamento({ ...payload, projeto_id: targetProjeto.id });
          count++;
        } catch (e) {
          console.error("Erro ao importar linha", i, e);
        }
      }
      fetchDados();
      alert(`${count} registros importados com sucesso!`);
    };
    reader.readAsText(file, "UTF-8");
    e.target.value = "";
  };

  const cats = [...new Set(dados.map(d=>d.categoria || "Outros"))].sort();
  const contas = [...new Set(dados.map(d=>d.conta || "N/A"))].sort();

  return {
    tab, setTab,
    dados, setDados,
    form, setForm,
    showForm, setShowForm,
    editId, setEditId,
    filtros, setFiltros,
    deleteId, setDeleteId,
    fileRef, receiptRef,
    scanning, setScanning,
    projetos, setProjetos,
    projetoAtivo, setProjetoAtivo,
    showProjectModal, setShowProjectModal,
    createProject,
    deleteProject,
    filtered,
    totalFiltrado,
    porCategoria,
    porConta,
    totalGeral,
    cats,
    contas,
    categoriasDb,
    contasDb,
    addCategoria,
    removeCategoria,
    addConta,
    removeConta,
    fetchServicos,
    requisicoes,
    fetchRequisicoes,
    createRequisicao,
    updateRequisicaoStatus,
    token,
    setToken,
    logout,
    user,
    setUser,
    confirmConfig, setConfirmConfig,
    askConfirm,
    handleForm,
    saveForm,
    startEdit,
    exportCSV,
    scanReceipt,
    importCSV
  };
}
