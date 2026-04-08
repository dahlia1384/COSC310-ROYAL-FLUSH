import client from "./client";

export const fetchOrder = async (orderId) => {
  const response = await client.get(`/orders/${orderId}`);
  return response.data;
};

export const fetchOrdersByCustomer = async (customerId) => {
  const response = await client.get(`/orders/customer/${customerId}`);
  return response.data;
};

export const createOrder = async (orderData) => {
  const response = await client.post(`/orders`, orderData);
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await client.put(`/orders/${orderId}/status`, {
    order_status: status,
  });
  return response.data;
};

export const payForOrder = async (orderId, paymentData) => {
  const response = await client.post(`/orders/${orderId}/pay`, {
    amount: paymentData.amount,
    method: paymentData.method || "card",
  });
  return response.data;
};

export const fetchDelivery = async (orderId) => {
  const response = await client.get(`/deliveries/${orderId}`);
  return response.data;
};

export const updateDeliveryStatus = async (orderId, deliveryStatus) => {
  const response = await client.put(`/deliveries/${orderId}/status`, {
    delivery_status: deliveryStatus,
  });
  return response.data;
};

export const getOrdersByUser = async (userId) => {
  const response = await client.get(`/orders/user/${userId}`);
  return response.data;
};

export const getOrderHistory = async (userId) => {
  const response = await client.get(`/orders/user/${userId}/history`);
  return response.data;
};

export const reorderPastOrder = async (orderId) => {
  const response = await client.post(`/orders/${orderId}/reorder`);
  return response.data;
};