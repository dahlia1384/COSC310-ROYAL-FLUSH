import React, { useEffect, useState } from "react";
import { getOrdersByUser } from "../api/orders";
import OrderStatusCard from "../components/orders/OrderStatusCard";

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const userId = 1; 

  const loadOrders = async () => {
    try {
      const data = await getOrdersByUser(userId);
      const activeOrders = data.filter(
        (order) => order.status !== "completed" && order.status !== "cancelled"
      );
      setOrders(activeOrders);
    } catch (error) {
      console.error("Failed to load orders:", error);
    }
  };

  useEffect(() => {
    loadOrders();
    const interval = setInterval(loadOrders, 5000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>My Current Orders</h1>
      {orders.length === 0 ? (
        <p>No active orders right now.</p>
      ) : (
        orders.map((order) => <OrderStatusCard key={order.id} order={order} />)
      )}
    </div>
  );
}