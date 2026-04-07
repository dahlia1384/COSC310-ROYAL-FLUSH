import client from "./client";

export const getUserNotifications = async (userId) => {
  const response = await client.get(`/users/${userId}/notifications`);
  return response.data;
};

export const markNotificationAsRead = async (notificationId) => {
  const response = await client.patch(`/notifications/${notificationId}/read`);
  return response.data;
};