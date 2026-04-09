import React from "react";

const statusSteps = [
  "placed",
  "confirmed",
  "preparing",
  "out_for_delivery",
  "completed",
];

export default function OrderStatusCard({ order }) {
  const currentIndex = statusSteps.indexOf(order.status);

  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "10px",
        padding: "16px",
        marginBottom: "16px",
        backgroundColor: "#fff",
      }}
    >
      <h3>Order #{order.id}</h3>
      <p>Restaurant: {order.restaurant_name || "Unknown Restaurant"}</p>
      <p>Total: ${order.total}</p>
      <p>
        Current Status: <strong>{order.status.replaceAll("_", " ")}</strong>
      </p>

      <div style={{ marginTop: "12px" }}>
        {statusSteps.map((step, index) => (
          <div key={step} style={{ marginBottom: "6px" }}>
            <span style={{ fontWeight: index <= currentIndex ? "bold" : "normal" }}>
              {index <= currentIndex ? "✓" : "○"} {step.replaceAll("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}