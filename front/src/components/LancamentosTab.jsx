import { FORMAS } from "../data/constants";
import { fmt, parseVal } from "../utils/format";
import { inputStyle, btnStyle, td, catColor } from "../utils/styles";

export function LancamentosTab({
  filtered,
  filtros,
  setFiltros,
  cats,
  contas,
  totalFiltrado,
  startEdit,
  setDeleteId
}) {
  return (
    <>
      <div className="filtros-bar">
        <div className="filtro-item">
          <div className="filtro-label">🔍 Buscar</div>
          <input value={filtros.busca} onChange={e=>setFiltros(f=>({...f,busca:e.target.value}))} placeholder="Item, fornecedor..." style={{...inputStyle,margin:0}}/>
        </div>
        <div className="filtro-item">
          <div className="filtro-label">Categoria</div>
          <select value={filtros.categoria} onChange={e=>setFiltros(f=>({...f,categoria:e.target.value}))} style={{...inputStyle,margin:0}}>
            <option value="">Todas</option>
            {cats.map(c=><option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="filtro-item">
          <div className="filtro-label">Conta Pagadora</div>
          <select value={filtros.conta} onChange={e=>setFiltros(f=>({...f,conta:e.target.value}))} style={{...inputStyle,margin:0}}>
            <option value="">Todas</option>
            {contas.map(c=><option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="filtro-item">
          <div className="filtro-label">Forma Pgto</div>
          <select value={filtros.forma} onChange={e=>setFiltros(f=>({...f,forma:e.target.value}))} style={{...inputStyle,margin:0}}>
            <option value="">Todas</option>
            {FORMAS.map(f=><option key={f}>{f}</option>)}
          </select>
        </div>
        <button onClick={()=>setFiltros({categoria:"",conta:"",forma:"",busca:""})} style={{...btnStyle("#64748b"),height:38}}>Limpar</button>
      </div>

      <div style={{background:"#1e3a5f",color:"#fff",borderRadius:10,padding:"12px 16px",marginBottom:12,display:"flex",justifyContent:"space-between",alignItems:"center",flexWrap:"wrap",gap:8}}>
        <span style={{fontSize:14}}>{filtered.length} registro(s) encontrado(s)</span>
        <span style={{fontWeight:700,fontSize:18}}>{fmt(totalFiltrado)}</span>
      </div>

      <div className="table-wrap">
        <table style={{width:"100%",borderCollapse:"collapse",fontSize:13}}>
          <thead>
            <tr style={{background:"#f8fafc",borderBottom:"2px solid #e2e8f0"}}>
              {["Data","Categoria","Item","Fornecedor","Qtd","Unitário","Valor","Forma","Conta","Obs",""].map(h=>(
                <th key={h} style={{padding:"10px 12px",textAlign:"left",whiteSpace:"nowrap",color:"#475569",fontWeight:600,fontSize:12}}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length===0 && (
              <tr><td colSpan={11} style={{textAlign:"center",padding:32,color:"#94a3b8"}}>Nenhum lançamento encontrado.</td></tr>
            )}
            {filtered.map((d,i)=>(
              <tr key={d.id} style={{borderBottom:"1px solid #f1f5f9",background:i%2===0?"#fff":"#f8fafc"}}>
                <td style={td}>{d.data}</td>
                <td style={td}><span style={{background:catColor(d.categoria)+"22",color:catColor(d.categoria),borderRadius:4,padding:"2px 7px",fontSize:11,fontWeight:600}}>{d.categoria}</span></td>
                <td style={{...td,maxWidth:160}}>{d.item}</td>
                <td style={td}>{d.fornecedor}</td>
                <td style={td}>{d.quantidade}</td>
                <td style={td}>{fmt(parseVal(d.unitario))}</td>
                <td style={{...td,fontWeight:600,color:"#1e3a5f"}}>{fmt(parseVal(d.valor))}</td>
                <td style={td}>{d.forma}</td>
                <td style={td}>{d.conta}</td>
                <td style={{...td,maxWidth:120,color:"#64748b",fontSize:11}}>{d.obs}</td>
                <td style={td}>
                  <div style={{display:"flex",gap:4}}>
                    <button onClick={()=>startEdit(d)} style={{border:"none",background:"#dbeafe",color:"#2563eb",borderRadius:4,padding:"3px 8px",cursor:"pointer",fontSize:12}}>✏️</button>
                    <button onClick={()=>setDeleteId(d.id)} style={{border:"none",background:"#fee2e2",color:"#dc2626",borderRadius:4,padding:"3px 8px",cursor:"pointer",fontSize:12}}>🗑️</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
