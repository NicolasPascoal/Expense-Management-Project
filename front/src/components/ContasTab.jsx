import { fmt, parseVal } from "../utils/format";

export function ContasTab({ porConta, dados }) {
  return (
    <div style={{display:"grid",gap:12}}>
      {porConta.map(([conta,total])=>{
        const itens = dados.filter(d=>d.conta===conta);
        const porCat = {};
        itens.forEach(d=>{const v=parseVal(d.valor);porCat[d.categoria]=(porCat[d.categoria]||0)+v;});
        return (
          <div key={conta} style={{background:"#fff",borderRadius:10,padding:20,boxShadow:"0 1px 4px rgba(0,0,0,.08)"}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
              <div>
                <div style={{fontWeight:700,fontSize:16}}>👤 {conta}</div>
                <div style={{color:"#64748b",fontSize:13}}>{itens.length} lançamentos</div>
              </div>
              <div style={{fontWeight:700,fontSize:20,color:"#1e3a5f"}}>{fmt(total)}</div>
            </div>
            <div style={{display:"flex",flexWrap:"wrap",gap:8}}>
              {Object.entries(porCat).sort((a,b)=>b[1]-a[1]).map(([cat,val])=>(
                <div key={cat} style={{background:"#f1f5f9",borderRadius:8,padding:"6px 12px",fontSize:12}}>
                  <span style={{color:"#64748b"}}>{cat}: </span><span style={{fontWeight:600}}>{fmt(val)}</span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
