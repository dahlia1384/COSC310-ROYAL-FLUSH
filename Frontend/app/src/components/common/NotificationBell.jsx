import React from "react";

export default function NotificationBell({ count, onClick }) {
  return (
    <button onClick={onClick} style={{ position: "relative", fontSize: "18px" }}>
      🔔
      {count > 0 && (
        <span
          style={{
            position: "absolute",
            top: "-8px",
            right: "-8px",
            background: "red",
            color: "white",
            borderRadius: "50%",
            padding: "2px 6px",
            fontSize: "12px",
          }}
        >
          {count}
        </span>
      )}
    </button>
  );
}