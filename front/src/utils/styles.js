import { CAT_COLORS } from "../data/constants";

export const btnStyle = bg => ({
  background: bg,
  color: "#fff",
  border: "none",
  borderRadius: 6,
  padding: "8px 14px",
  cursor: "pointer",
  fontSize: 13,
  fontWeight: 500,
  whiteSpace: "nowrap"
});

export const labelStyle = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
  fontSize: 13,
  color: "#475569",
  fontWeight: 500
};

export const inputStyle = {
  border: "1px solid #e2e8f0",
  borderRadius: 6,
  padding: "8px 10px",
  fontSize: 13,
  width: "100%",
  boxSizing: "border-box",
  marginTop: 2
};

export const td = {
  padding: "9px 12px",
  whiteSpace: "nowrap"
};

export const catColor = c => CAT_COLORS[c] || "#64748b";
