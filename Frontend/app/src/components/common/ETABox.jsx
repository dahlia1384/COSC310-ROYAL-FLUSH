import { useEffect, useState } from "react";

function ETABox({ order, restaurant, delivery }) {
  const [etaText, setEtaText] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      if (!order) return;

      const now = new Date();

      const userCity = order.customer_city;
      const restaurantCity = restaurant.address;
      const method = order.delivery_method?.toLowerCase();

      let deliveryMinutes = 0;

      if (userCity === restaurantCity) {
        if (method === "car") deliveryMinutes = 10;
        else if (method === "bike") deliveryMinutes = 20;
        else if (method === "walk") deliveryMinutes = 25;
      }
      else {
        if (method === "car") deliveryMinutes = 20;
        else if (method === "bike") deliveryMinutes = 25;
        else if (method === "walk") deliveryMinutes = 35;
      }

      if (order.order_status === "Preparing Order") {
        setEtaText("Preparing Order...");
      }

      else if (order.order_status === "Order Out for Delivery" && delivery) {
        const eta = new Date(delivery.delivery_time);
        eta.setMinutes(eta.getMinutes() + deliveryMinutes);

        const diff = Math.max(0, Math.floor((eta - now) / 1000));

        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;

        setEtaText(`ETA: ${minutes}m ${seconds}s`);
      }

      else if (order.order_status === "Order Delivered") {
        setEtaText("Delivered");
      }

    }, 1000);

    return () => clearInterval(interval);
  }, [order, restaurant, delivery]);

  return (
    <div style={{ padding: "10px", border: "1px solid black", marginTop: "10px" }}>
      <strong>{etaText}</strong>
    </div>
  );
}

export default ETABox;