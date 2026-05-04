import { btnStyle } from "../utils/styles";

export function DeleteModal({ setDeleteId, confirmDelete }) {
  return (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,.4)",zIndex:100,display:"flex",alignItems:"center",justifyContent:"center"}}>
      <div style={{background:"#fff",borderRadius:12,padding:24,maxWidth:360,textAlign:"center",boxShadow:"0 20px 60px rgba(0,0,0,.3)"}}>
        <div style={{fontSize:32,marginBottom:8}}>🗑️</div>
        <b>Excluir lançamento?</b>
        <p style={{color:"#64748b",fontSize:14}}>Esta ação não pode ser desfeita.</p>
        <div style={{display:"flex",gap:8,justifyContent:"center",marginTop:12}}>
          <button onClick={()=>setDeleteId(null)} style={btnStyle("#64748b")}>Cancelar</button>
          <button onClick={confirmDelete} style={btnStyle("#dc2626")}>Excluir</button>
        </div>
      </div>
    </div>
  );
}
