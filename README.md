# COSC310-ROYAL-FLUSH

Team Members:
* Dahlia Mohammadi (10915528)
* Nandini Anaparti (27794205)
* Nisini Perera (10089811)  
* Yibing Wang (25470915)


Architecture Overview: 
  For this project, we adopt a dockerized layered backend architecture using FastAPI to 
expose REST endpoints, with separate service and data access layers handling business logic 
and database interaction. Each core feature (authentication, restaurant/menu management, 
search, orders, pricing, payment, delivery tracking, and notifications) is implemented as a 
focused service module, promoting modularity, separation of concerns, and testability. 
This design supports key quality attributes. Security is enforced through 
authentication, role-based access control, and protected handling of sensitive data such as 
password hashing. Reliability and consistency are ensured by validating domain rules in the 
service layer (e.g., preventing modification of completed orders and enforcing valid 
menu–restaurant relationships). Scalability and performance are supported by stateless 
containerized APIs, load balancing capability, and query pagination to reduce heavy database 
operations. Maintainability and quality are improved through clean layering, SOLID-style 
design, automated testing with Pytest, and CI via GitHub Actions. 
A trade-off of this layered, containerized approach is additional architectural 
complexity and inter-layer communication overhead compared to a simpler monolithic 
design. However, the benefits in security, scalability, maintainability, and long-term 
extensibility make this architecture appropriate for the food delivery system.
