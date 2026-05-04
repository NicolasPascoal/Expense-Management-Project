export function Card({ title, value, icon, color }) {
  return (
    <div style={{
      background: "#fff",
      borderRadius: 10,
      padding: 16,
      boxShadow: "0 1px 4px rgba(0,0,0,.08)",
      borderLeft: `4px solid ${color}`
    }}>
      <div style={{ fontSize: 22 }}>{icon}</div>
      <div style={{ color: "#64748b", fontSize: 12, marginTop: 4 }}>{title}</div>
      <div style={{ fontWeight: 700, fontSize: 20, color }}>{value}</div>
    </div>
  );
}
