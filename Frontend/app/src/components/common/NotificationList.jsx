import React from "react";

export default function NotificationList({ notifications, onMarkRead }) {
  if (!notifications || notifications.length === 0) {
    return <p>No notifications yet.</p>;
  }

  return (
    <div>
      <h2>Notifications</h2>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          style={{
            border: "1px solid #ccc",
            marginBottom: "10px",
            padding: "10px",
            borderRadius: "8px",
            backgroundColor: notification.read ? "#f8f8f8" : "#eef6ff",
          }}
        >
          <p>{notification.message}</p>
          <small>Status: {notification.type}</small>
          <br />
          <small>
            {notification.read ? "Read" : "Unread"}
          </small>
          {!notification.read && (
            <div style={{ marginTop: "8px" }}>
              <button onClick={() => onMarkRead(notification.id)}>
                Mark as Read
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}