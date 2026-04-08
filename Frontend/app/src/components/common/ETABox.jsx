import { useEffect, useState } from "react";

function ETABox({ order, restaurant, delivery }) {
  const [etaText, setEtaText] = useState("No order yet");

  useEffect(() => {
    if (!order) {
      setEtaText("No order yet");
      return;
    }

    const interval = setInterval(() => {
      const now = new Date();

      const method = (order.delivery_method || "car").toLowerCase();

      // CITY-BASED LOGIC
      const userCity = (order.customer_city || "").toLowerCase();
      const restaurantCity = (restaurant?.address || "").toLowerCase();
      const sameCity = userCity && restaurantCity && restaurantCity.includes(userCity);

      let deliveryMinutes = 15;
      if (sameCity) {
        if (method === "car") deliveryMinutes = 10;
        else if (method === "bike") deliveryMinutes = 20;
        else if (method === "walk") deliveryMinutes = 25;
      } else {
        if (method === "car") deliveryMinutes = 20;
        else if (method === "bike") deliveryMinutes = 25;
        else if (method === "walk") deliveryMinutes = 35;
      }

      if (order.order_status === "Preparing Order") {
        setEtaText("Preparing Order...");
        return;
      }

      if (order.order_status === "Order Out for Delivery") {
        if (!delivery?.delivery_time) {
          setEtaText("Calculating ETA...");
          return;
        }

        const startTime = new Date(delivery.delivery_time);
        const etaTime = new Date(startTime.getTime() + deliveryMinutes * 60000);

        const diff = Math.max(0, Math.floor((etaTime - now) / 1000));
        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;

        setEtaText(`ETA: ${minutes}m ${seconds}s`);
        return;
      }

      if (order.order_status === "Order Delivered") {
        setEtaText("Delivered");
        return;
      }

      setEtaText("Waiting for update...");
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

