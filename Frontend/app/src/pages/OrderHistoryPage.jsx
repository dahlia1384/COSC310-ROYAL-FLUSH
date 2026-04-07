import React, { useEffect, useState } from "react";
import { getOrderHistory, reorderPastOrder } from "../api/orders";
import OrderHistoryList from "../components/orders/OrderHistoryList";

export default function OrderHistoryPage() {
  const [orders, setOrders] = useState([]);
  const userId = 1; 

  const loadHistory = async () => {
    try {
      const data = await getOrderHistory(userId);
      setOrders(data);
    } catch (error) {
      console.error("Failed to load order history:", error);
    }
  };

  const handleReorder = async (orderId) => {
    try {
      await reorderPastOrder(orderId);
      alert("Order placed again successfully!");
    } catch (error) {
      console.error("Failed to reorder:", error);
      alert("Reorder failed.");
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <div>
      <h1>Order History</h1>
      <OrderHistoryList orders={orders} onReorder={handleReorder} />
    </div>
  );
}