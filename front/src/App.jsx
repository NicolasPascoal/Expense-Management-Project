import { useExpenses } from "./hooks/useExpenses";
import { FormModal } from "./components/FormModal";
import { DeleteModal } from "./components/DeleteModal";
import { LancamentosTab } from "./components/LancamentosTab";
import { DashboardTab } from "./components/DashboardTab";
import { ContasTab } from "./components/ContasTab";
import { EMPTY_FORM } from "./data/constants";
import { btnStyle } from "./utils/styles";

export default function App() {
  const expenses = useExpenses();

  return (
    <div style={{fontFamily:"system-ui,sans-serif",background:"#f1f5f9",minHeight:"100vh",paddingBottom:40}}>
      {/* Header */}
      <div className="app-header">
        <div>
          <div className="app-header-title">🏗️ Construtora Itanhaém</div>
          <div className="app-header-sub">Sistema de Gestão de Despesas</div>
        </div>
        <div className="app-header-actions">
          <button onClick={()=>{expenses.setShowForm(true);expenses.setEditId(null);expenses.setForm(EMPTY_FORM);expenses.setTab("lancamentos");}} style={btnStyle("#2563eb")}>+ Novo Lançamento</button>
          <button onClick={expenses.exportCSV} style={btnStyle("#16a34a")}>⬇ Exportar CSV</button>
          <button onClick={()=>expenses.receiptRef.current.click()} style={btnStyle("#ea580c")}>📷 Ler Recibo</button>
          <input ref={expenses.receiptRef} type="file" accept="image/*,application/pdf" onChange={expenses.scanReceipt} style={{display:"none"}} capture="environment"/>
          <button onClick={()=>expenses.fileRef.current.click()} style={btnStyle("#7c3aed")}>⬆ Importar CSV</button>
          <input ref={expenses.fileRef} type="file" accept=".csv" onChange={expenses.importCSV} style={{display:"none"}}/>
        </div>
      </div>

      {/* Tabs */}
      <div className="app-tabs">
        {[["lancamentos","📋 Lançamentos"],["dashboard","📊 Dashboard"],["contas","👤 Por Conta"]].map(([k,l])=>(
          <button key={k} onClick={()=>expenses.setTab(k)} className={`app-tab-btn${expenses.tab===k?" active":""}`}>{l}</button>
        ))}
      </div>

      <div className="app-content">
        {expenses.showForm && <FormModal {...expenses} />}
        {expenses.deleteId && <DeleteModal {...expenses} />}

        {expenses.tab === "lancamentos" && <LancamentosTab {...expenses} />}
        {expenses.tab === "dashboard" && <DashboardTab {...expenses} />}
        {expenses.tab === "contas" && <ContasTab {...expenses} />}
      </div>
    </div>
  );
}
