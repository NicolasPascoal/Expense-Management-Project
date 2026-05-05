import { btnStyle } from "../utils/styles";

export function ConfirmModal({ config, onClose }) {
  if (!config) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-box" style={{ maxWidth: 400, textAlign: "center" }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>{config.icon || "⚠️"}</div>
        <b style={{ fontSize: 18, display: "block", marginBottom: 8 }}>{config.title}</b>
        <p style={{ color: "#64748b", fontSize: 14, marginBottom: 24 }}>{config.message}</p>
        
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button 
            onClick={onClose} 
            style={btnStyle("#64748b")}
          >
            {config.cancelText || "Cancelar"}
          </button>
          <button 
            onClick={() => {
              config.onConfirm();
              onClose();
            }} 
            style={btnStyle(config.confirmColor || "#dc2626")}
          >
            {config.confirmText || "Confirmar"}
          </button>
        </div>
      </div>
    </div>
  );
}
