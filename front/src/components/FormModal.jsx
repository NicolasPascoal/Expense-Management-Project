import { CATEGORIAS, CONTAS, FORMAS } from "../data/constants";
import { labelStyle, inputStyle, btnStyle } from "../utils/styles";

export function FormModal({
  form,
  editId,
  scanning,
  handleForm,
  saveForm,
  setShowForm,
  setEditId
}) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        {scanning && (
          <div style={{background:"#eff6ff",border:"1px solid #bfdbfe",borderRadius:8,padding:"12px 16px",marginBottom:16,display:"flex",alignItems:"center",gap:10,color:"#1e40af",fontSize:14}}>
            <span style={{fontSize:20}}>🔍</span>
            <span>Lendo o recibo com IA... aguarde um instante.</span>
          </div>
        )}
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:16}}>
          <b style={{fontSize:16}}>{editId?"✏️ Editar Lançamento":"➕ Novo Lançamento"}</b>
          <button onClick={()=>{setShowForm(false);setEditId(null);}} style={{border:"none",background:"none",fontSize:20,cursor:"pointer",color:"#64748b"}}>✕</button>
        </div>
        <div className="modal-form-grid">
          <label style={labelStyle}>Data *<input type="text" name="data" placeholder="DD/MM/AAAA" value={form.data} onChange={handleForm} style={inputStyle}/></label>
          <label style={labelStyle}>Categoria *
            <select name="categoria" value={form.categoria} onChange={handleForm} style={inputStyle}>
              <option value="">Selecione...</option>
              {CATEGORIAS.map(c=><option key={c}>{c}</option>)}
            </select>
          </label>
          <label style={labelStyle} className="full-width">Item / Descrição *<input name="item" value={form.item} onChange={handleForm} style={inputStyle}/></label>
          <label style={labelStyle} className="full-width">Fornecedor<input name="fornecedor" value={form.fornecedor} onChange={handleForm} style={inputStyle}/></label>
          <label style={labelStyle}>Quantidade<input type="number" name="quantidade" value={form.quantidade} onChange={handleForm} style={inputStyle} min="0" step="any"/></label>
          <label style={labelStyle}>Valor Unitário (R$)<input name="unitario" value={form.unitario} onChange={handleForm} style={inputStyle} placeholder="0,00"/></label>
          <label style={labelStyle} className="full-width">Valor Pago (R$)<input name="valor" value={form.valor} onChange={handleForm} style={inputStyle} placeholder="0,00"/></label>
          <label style={labelStyle}>Forma Pagamento
            <select name="forma" value={form.forma} onChange={handleForm} style={inputStyle}>
              {FORMAS.map(f=><option key={f}>{f}</option>)}
            </select>
          </label>
          <label style={labelStyle}>Conta Pagadora *
            <select name="conta" value={form.conta} onChange={handleForm} style={inputStyle}>
              <option value="">Selecione...</option>
              {CONTAS.map(c=><option key={c}>{c}</option>)}
            </select>
          </label>
          <label style={labelStyle} className="full-width">Observações<textarea name="obs" value={form.obs} onChange={handleForm} style={{...inputStyle,resize:"vertical",height:60}}/></label>
        </div>
        <div style={{display:"flex",gap:8,marginTop:16,justifyContent:"flex-end",flexWrap:"wrap"}}>
          <button onClick={()=>{setShowForm(false);setEditId(null);}} style={btnStyle("#64748b")}>Cancelar</button>
          <button onClick={saveForm} style={btnStyle("#2563eb")}>{editId?"Salvar Alterações":"Adicionar"}</button>
        </div>
      </div>
    </div>
  );
}
