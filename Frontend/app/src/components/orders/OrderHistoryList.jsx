import React from "react";

export default function OrderHistoryList({ orders, onReorder }) {
  if (!orders || orders.length === 0) {
    return <p>No past orders found.</p>;
  }

  return (
    <div>
      <h2>Order History</h2>
      {orders.map((order) => (
        <div
          key={order.id}
          style={{
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "12px",
          }}
        >
          <p><strong>Order #{order.id}</strong></p>
          <p>Restaurant: {order.restaurant_name}</p>
          <p>Total: ${order.total}</p>
          <p>Status: {order.status}</p>
          <button onClick={() => onReorder(order.id)}>Reorder</button>
        </div>
      ))}
    </div>
  );
}