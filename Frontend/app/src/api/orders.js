import client from "./client";

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