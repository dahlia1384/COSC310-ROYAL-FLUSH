import React, { useEffect, useState } from "react";
import { getUserNotifications, markNotificationAsRead } from "../api/notifications";
import NotificationList from "../components/common/NotificationList";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const userId = 1; 

  const loadNotifications = async () => {
    try {
      const data = await getUserNotifications(userId);
      setNotifications(data);
    } catch (error) {
      console.error("Failed to load notifications:", error);
    }
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      loadNotifications();
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  return (
    <div>
      <h1>My Notifications</h1>
      <NotificationList
        notifications={notifications}
        onMarkRead={handleMarkRead}
      />
    </div>
  );
}