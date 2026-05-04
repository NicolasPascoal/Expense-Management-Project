import { useState, useMemo, useRef, useEffect } from "react";
import { api } from "../services/api";
import { EMPTY_FORM, FORMAS } from "../data/constants";
import { parseVal } from "../utils/format";

export function useExpenses() {
  const [tab, setTab] = useState("lancamentos");
  const [dados, setDados] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [filtros, setFiltros] = useState({categoria:"",conta:"",forma:"",busca:""});
  const [deleteId, setDeleteId] = useState(null);
  const fileRef = useRef();
  const receiptRef = useRef();
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    fetchDados();
  }, []);

  const fetchDados = async () => {
    try {
      const res = await api.getLancamentos();
      setDados(res);
    } catch (e) {
      console.error("Erro ao buscar dados:", e);
    }
  };

  const filtered = useMemo(() => {
    return dados.filter(d => {
      if(filtros.categoria && d.categoria !== filtros.categoria) return false;
      if(filtros.conta && d.conta !== filtros.conta) return false;
      if(filtros.forma && d.forma !== filtros.forma) return false;
      if(filtros.busca) {
        const b = filtros.busca.toLowerCase();
        if(![d.item,d.fornecedor,d.obs].some(x=>(x||"").toLowerCase().includes(b))) return false;
      }
      return true;
    });
  }, [dados, filtros]);

  const totalFiltrado = filtered.reduce((a,d)=>a+parseVal(d.valor),0);

  const porCategoria = useMemo(()=>{
    const m={};
    dados.forEach(d=>{const v=parseVal(d.valor); m[d.categoria]=(m[d.categoria]||0)+v;});
    return Object.entries(m).sort((a,b)=>b[1]-a[1]);
  },[dados]);

  const porConta = useMemo(()=>{
    const m={};
    dados.forEach(d=>{const v=parseVal(d.valor); m[d.conta]=(m[d.conta]||0)+v;});
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
    if(!form.data||!form.categoria||!form.item||!form.conta) return alert("Preencha os campos obrigatórios: Data, Categoria, Item e Conta Pagadora.");
    
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
          valor: parseVal(form.valor),
          unitario: parseVal(form.unitario)
        });
        setDados([...dados, novo]);
      }
      setForm(EMPTY_FORM);
      setShowForm(false);
    } catch (e) {
      alert("Erro ao salvar lançamento");
    }
  };

  const startEdit = row => {
    setForm({...row,unitario:row.unitario,valor:row.valor});
    setEditId(row.id);
    setShowForm(true);
    setTab("lancamentos");
  };

  const confirmDelete = async () => {
    try {
      await api.deleteLancamento(deleteId);
      setDados(dados.filter(x => x.id !== deleteId));
      setDeleteId(null);
    } catch (e) {
      alert("Erro ao excluir lançamento");
    }
  };

  const exportCSV = () => {
    const fmtL = v => v.toLocaleString("pt-BR",{style:"currency",currency:"BRL"});
    const cols=["Data","Categoria","Item","Fornecedor","Quantidade","Unitário","Valor Pago (R$)","Forma Pagamento","Conta Pagadora","Observações"];
    const rows=filtered.map(d=>[d.data,d.categoria,d.item,d.fornecedor,d.quantidade,
      fmtL(parseVal(d.unitario)),fmtL(parseVal(d.valor)),d.forma,d.conta,d.obs||""].map(v=>`"${v}"`).join(";"));
    const csv="\uFEFF"+[cols.join(";"),...rows].join("\n");
    const a=document.createElement("a");
    a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    a.download="despesas_itanhaem.csv";
    a.click();
  };

  const scanReceipt = async e => {
    const file = e.target.files[0]; if(!file) return;
    setScanning(true);
    setShowForm(true); setEditId(null); setForm(EMPTY_FORM);
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
              {type:"text",text:`Você é um assistente de uma construtora. Analise este recibo/nota fiscal e extraia as informações. Retorne APENAS um JSON válido, sem texto adicional, com estes campos:
{
  "item": "descrição principal do item ou serviço",
  "fornecedor": "nome do fornecedor/empresa emissora",
  "categoria": "uma das categorias: Documentação, Terraplanagem, Fundação, Ferramentas, Material de construção, Mão de obra, Equipamentos/aluguel, Taxas e impostos, Outros",
  "valor": numero_sem_formatacao,
  "quantidade": numero,
  "unitario": numero_sem_formatacao,
  "forma": "Pix, Crédito, Débito, Boleto, Dinheiro ou Transferência",
  "data": "DD/MM/AAAA ou vazio se não encontrar",
  "obs": "informação adicional relevante se houver"
}
Classifique a categoria com base no contexto de uma construtora de condomínios residenciais.`}
            ]
          }]
        })
      });
      const data = await resp.json();
      const text = data.content.map(c=>c.text||"").join("");
      const clean = text.replace(/```json|```/g,"").trim();
      const parsed = JSON.parse(clean);
      setForm(f=>({
        ...f,
        item: parsed.item||"",
        fornecedor: parsed.fornecedor||"",
        categoria: parsed.categoria||"",
        valor: parsed.valor||"",
        quantidade: parsed.quantidade||1,
        unitario: parsed.unitario||"",
        forma: parsed.forma||"Pix",
        data: parsed.data||"",
        obs: parsed.obs||""
      }));
    } catch(err) {
      alert("Erro ao ler o recibo. Tente novamente ou preencha manualmente.");
    } finally {
      setScanning(false);
    }
  };

  const importCSV = e => {
    const file = e.target.files[0]; if(!file) return;
    const reader = new FileReader();
    reader.onload = async ev => {
      const lines = ev.target.result.split("\n").filter(Boolean);
      const headers = lines[0].split(/[,;]/).map(h=>h.trim().replace(/^"|"$/g,"").toLowerCase());
      let count = 0;
      for(let i=1;i<lines.length;i++){
        const vals = lines[i].split(/[,;]/).map(v=>v.trim().replace(/^"|"$/g,""));
        const obj={};
        headers.forEach((h,j)=>obj[h]=vals[j]||"");
        const formaRaw = vals[7]||"";
        const forma = FORMAS.includes(formaRaw) ? formaRaw : (obj["forma pagamento"]||obj["forma"]||"Pix");
        
        const payload = {
          data: vals[0]||obj["data"]||"",
          categoria: vals[1]||obj["categoria"]||"Outros",
          item: vals[2]||obj["item"]||"",
          fornecedor: vals[3]||obj["fornecedor"]||"",
          quantidade: parseFloat(vals[4]||obj["quantidade"])||1,
          unitario: parseVal(vals[5]||obj["unitário"]||obj["unitario"]||"0"),
          valor: parseVal(vals[6]||obj["valor pago (r$)"]||obj["valor"]||"0"),
          forma,
          conta: vals[8]||obj["conta pagadora"]||obj["conta"]||"",
          obs: vals[9]||obj["observações"]||obj["observacoes"]||""
        };

        try {
          await api.createLancamento(payload);
          count++;
        } catch (e) {
          console.error("Erro ao importar linha", i, e);
        }
      }
      fetchDados();
      alert(`${count} registros importados com sucesso!`);
    };
    reader.readAsText(file,"UTF-8");
    e.target.value="";
  };

  const cats = [...new Set(dados.map(d=>d.categoria))].sort();
  const contas = [...new Set(dados.map(d=>d.conta))].sort();

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
    filtered,
    totalFiltrado,
    porCategoria,
    porConta,
    totalGeral,
    cats,
    contas,
    handleForm,
    saveForm,
    startEdit,
    confirmDelete,
    exportCSV,
    scanReceipt,
    importCSV
  };
}
