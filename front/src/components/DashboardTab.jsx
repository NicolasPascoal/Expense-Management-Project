import { Card } from "./Card";
import { fmt } from "../utils/format";
import { BAR_COLORS } from "../data/constants";

export function DashboardTab({ totalGeral, dados, porCategoria, porConta }) {
  return (
    <div style={{display:"grid",gap:16}}>
      <div className="cards-grid">
        <Card title="Total Geral" value={fmt(totalGeral)} icon="💰" color="#1e3a5f"/>
        <Card title="Lançamentos" value={dados.length} icon="📋" color="#2563eb"/>
        <Card title="Categorias" value={porCategoria.length} icon="🏷️" color="#16a34a"/>
        <Card title="Contas" value={porConta.length} icon="👤" color="#7c3aed"/>
      </div>

      <div style={{background:"#fff",borderRadius:10,padding:20,boxShadow:"0 1px 4px rgba(0,0,0,.08)"}}>
        <b style={{fontSize:15}}>📊 Gastos por Categoria</b>
        <div style={{marginTop:16,display:"flex",flexDirection:"column",gap:10}}>
          {porCategoria.map(([cat,val],i)=>{
            const pct = totalGeral>0?val/totalGeral*100:0;
            return (
              <div key={cat}>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:13,marginBottom:4,flexWrap:"wrap",gap:4}}>
                  <span style={{fontWeight:500}}>{cat}</span>
                  <span style={{color:"#1e3a5f",fontWeight:700}}>{fmt(val)} <span style={{color:"#94a3b8",fontWeight:400}}>({pct.toFixed(1)}%)</span></span>
                </div>
                <div style={{background:"#f1f5f9",borderRadius:999,height:10}}>
                  <div style={{background:BAR_COLORS[i%BAR_COLORS.length],width:pct+"%",height:"100%",borderRadius:999,transition:"width .4s"}}/>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
