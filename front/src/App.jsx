import { useEffect } from "react";
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
import { RequisicoesTab } from "./components/RequisicoesTab";
import { btnStyle } from "./utils/styles";
import {
  LayoutDashboard,
  ClipboardList,
  ClipboardCheck,
  Wallet,
  Wrench,
  ShieldCheck,
  Plus,
  FileDown,
  FileUp,
  LogOut,
  Construction
} from "lucide-react";

export default function App() {
  const expenses = useExpenses();

  // Garantir que o prestador caia na aba correta se estiver em uma aba proibida
  useEffect(() => {
    if (expenses.user?.role === "prestador" && !expenses.user?.is_admin && expenses.tab !== "requisicoes") {
      expenses.setTab("requisicoes");
    }
  }, [expenses.user?.role, expenses.user?.is_admin, expenses.tab]);

  if (!expenses.token) {
    return <Login onLogin={(data) => {
      expenses.setToken(data.token);
      expenses.setUser(data.user);
    }} />;
  }

  const allTabs = [
    ["dashboard", "Dashboard", LayoutDashboard],
    ["lancamentos", "Lançamentos", ClipboardList],
    ["requisicoes", "Materiais", ClipboardCheck],
    ["contas", "Por Conta", Wallet],
    ["servicos", "Serviços", Wrench]
  ];

  // Filtra as abas baseado no papel do usuário
  let tabs = allTabs;
  if (expenses.user?.role === "prestador" && !expenses.user?.is_admin) {
    tabs = [["requisicoes", "Materiais", ClipboardCheck]];
  }

  if (expenses.user?.is_admin) {
    tabs.push(["admin", "Admin", ShieldCheck]);
  }

  return (
    <div style={{ fontFamily: "system-ui,sans-serif", background: "#f1f5f9", minHeight: "100vh", paddingBottom: 40 }}>
      {/* Header */}
      <div className="app-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div className="app-header-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Construction size={24} /> Gestão de Despesas
            </div>
            <button onClick={expenses.logout} style={{ ...btnStyle("#ef4444"), padding: "4px 10px", fontSize: 11, display: "flex", alignItems: "center", gap: 4 }}>
              <LogOut size={12} /> Sair
            </button>
          </div>
          <div className="app-header-sub">{expenses.projetoAtivo?.nome || "Selecione um projeto"}</div>
        </div>
        <div className="app-header-actions">
          <ProjectSelector {...expenses} />
        </div>
      </div>

      <div className="app-content">
        {/* Barra de Ações (Oculta para Prestadores) */}
        {(!expenses.user?.role || expenses.user?.role !== "prestador" || expenses.user?.is_admin) && (
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
            <button onClick={() => { expenses.setShowForm(true); expenses.setEditId(null); expenses.setForm({}); expenses.setTab("lancamentos"); }} style={{ ...btnStyle("#2563eb"), display: "flex", alignItems: "center", gap: 6 }}>
              <Plus size={18} /> Novo Lançamento
            </button>
            <button onClick={expenses.exportCSV} style={{ ...btnStyle("#16a34a"), display: "flex", alignItems: "center", gap: 6 }}>
              <FileDown size={18} /> Exportar CSV
            </button>
            <input ref={expenses.receiptRef} type="file" accept="image/*,application/pdf" onChange={expenses.scanReceipt} style={{ display: "none" }} capture="environment" />
            <button onClick={() => expenses.fileRef.current.click()} style={{ ...btnStyle("#7c3aed"), display: "flex", alignItems: "center", gap: 6 }}>
              <FileUp size={18} /> Importar CSV
            </button>
            <input ref={expenses.fileRef} type="file" accept=".csv" onChange={expenses.importCSV} style={{ display: "none" }} />
          </div>
        )}

        {/* Tabs */}
        <div className="app-tabs" style={{ marginBottom: 20 }}>
          {tabs.map(([k, l, Icon]) => (
            <button key={k} onClick={() => expenses.setTab(k)} className={`app-tab-btn${expenses.tab === k ? " active" : ""}`} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Icon size={16} /> {l}
            </button>
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
        {expenses.tab === "dashboard" && <DashboardTab {...expenses} />}
        {expenses.tab === "lancamentos" && <LancamentosTab {...expenses} />}
        {expenses.tab === "requisicoes" && <RequisicoesTab {...expenses} />}
        {expenses.tab === "contas" && <ContasTab {...expenses} />}
        {expenses.tab === "servicos" && <ServicosTab {...expenses} />}
        {expenses.tab === "admin" && <AdminTab {...expenses} />}
      </div>
    </div>
  );
}
