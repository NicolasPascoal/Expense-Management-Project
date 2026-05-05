import { useExpenses } from "./hooks/useExpenses";
import { FormModal } from "./components/FormModal";
import { Login } from "./components/Login";
import { ConfirmModal } from "./components/ConfirmModal";
import { ProjectModal } from "./components/ProjectModal";
import { ProjectSelector } from "./components/ProjectSelector";
import { LancamentosTab } from "./components/LancamentosTab";
import { DashboardTab } from "./components/DashboardTab";
import { ContasTab } from "./components/ContasTab";
import { ServicosTab } from "./components/ServicosTab";
import { AdminTab } from "./components/AdminTab";
import { btnStyle } from "./utils/styles";

export default function App() {
  const expenses = useExpenses();

  if (!expenses.token) {
    return <Login onLogin={(data) => {
      expenses.setToken(data.token);
      expenses.setUser(data.user);
    }} />;
  }

  const tabs = [
    ["lancamentos", "📋 Lançamentos"],
    ["dashboard", "📊 Dashboard"],
    ["contas", "👤 Por Conta"],
    ["servicos", "🛠️ Serviços"]
  ];

  if (expenses.user?.is_admin) {
    tabs.push(["admin", "🔐 Admin"]);
  }

  return (
    <div style={{ fontFamily: "system-ui,sans-serif", background: "#f1f5f9", minHeight: "100vh", paddingBottom: 40 }}>
      {/* Header */}
      <div className="app-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div className="app-header-title">🏗️ Gestão de Despesas</div>
            <button onClick={expenses.logout} style={{ ...btnStyle("#ef4444"), padding: "4px 10px", fontSize: 11 }}>Sair</button>
          </div>
          <div className="app-header-sub">{expenses.projetoAtivo?.nome || "Selecione um projeto"}</div>
        </div>
        <div className="app-header-actions">
          <ProjectSelector {...expenses} />
        </div>
      </div>

      <div className="app-content">
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          background: "#fff",
          padding: "12px 16px",
          borderRadius: 10,
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          marginBottom: 20,
          flexWrap: "wrap"
        }}>
          <button onClick={() => { expenses.setShowForm(true); expenses.setEditId(null); expenses.setForm({}); expenses.setTab("lancamentos"); }} style={btnStyle("#2563eb")}>+ Novo Lançamento</button>
          <button onClick={expenses.exportCSV} style={btnStyle("#16a34a")}>⬇ Exportar CSV</button>
          <input ref={expenses.receiptRef} type="file" accept="image/*,application/pdf" onChange={expenses.scanReceipt} style={{ display: "none" }} capture="environment" />
          <button onClick={() => expenses.fileRef.current.click()} style={btnStyle("#7c3aed")}>⬆ Importar CSV</button>
          <input ref={expenses.fileRef} type="file" accept=".csv" onChange={expenses.importCSV} style={{ display: "none" }} />
        </div>

        {/* Tabs */}
        <div className="app-tabs" style={{ marginBottom: 20 }}>
          {tabs.map(([k, l]) => (
            <button key={k} onClick={() => expenses.setTab(k)} className={`app-tab-btn${expenses.tab === k ? " active" : ""}`}>{l}</button>
          ))}
        </div>

        {expenses.showForm && <FormModal {...expenses} />}
        {expenses.showProjectModal && <ProjectModal {...expenses} />}
        {expenses.confirmConfig && (
          <ConfirmModal 
            config={expenses.confirmConfig} 
            onClose={() => expenses.setConfirmConfig(null)} 
          />
        )}

        {expenses.tab === "lancamentos" && <LancamentosTab {...expenses} />}
        {expenses.tab === "dashboard" && <DashboardTab {...expenses} />}
        {expenses.tab === "contas" && <ContasTab {...expenses} />}
        {expenses.tab === "servicos" && <ServicosTab {...expenses} />}
        {expenses.tab === "admin" && <AdminTab {...expenses} />}
      </div>
    </div>
  );
}
