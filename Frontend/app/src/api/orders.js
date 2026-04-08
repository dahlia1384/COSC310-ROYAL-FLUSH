const API_BASE = 'http://localhost:8000';

export async function fetchOrder(orderId) {
  const res = await fetch(`${API_BASE}/orders/${orderId}`);

  if (!res.ok) throw new Error("Failed to fetch order");
  return res.json();
}

export async function fetchOrdersByCustomer(customerId) {
  const res = await fetch(`${API_BASE}/orders/customer/${customerId}`);
  if (!res.ok) throw new Error("Failed to fetch customer orders");
  return res.json();
}

export async function createOrder(orderData) {
  const res = await fetch(`${API_BASE}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(orderData),
  });

  if (!res.ok) throw new Error("Failed to create order");
  return res.json();
}

export async function updateOrderStatus(orderId, status) {
  const res = await fetch(`${API_BASE}/orders/${orderId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_status: status }),
  });

  if (!res.ok) throw new Error("Failed to update order status");
  return res.json();
}

export async function payForOrder(orderId, paymentData) {
  const res = await fetch(`${API_BASE}/orders/${orderId}/pay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paymentData),
  });

  if (!res.ok) throw new Error("Payment failed");
  return res.json();
}

export async function fetchDelivery(orderId) {
  const res = await fetch(`${API_BASE}/deliveries/${orderId}`);

  if (!res.ok) throw new Error("Failed to fetch delivery");
  return res.json();
}

export async function updateDeliveryStatus(orderId, deliveryStatus) {
  const res = await fetch(`${API_BASE}/deliveries/${orderId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ delivery_status: deliveryStatus }),
  });

  if (!res.ok) throw new Error("Failed to update delivery status");
  return res.json();
}

