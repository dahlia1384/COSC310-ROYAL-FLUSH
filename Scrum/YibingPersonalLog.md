# Yibing Personal Development Log

This notebook tracks my daily work on the project.


## March 4th
### What I did
- Setting up structure of backend
- Started implementing Feature 1 (User Authentication) by setting up the SQLite database configuration.
### What I will do next
- Implement the User model and database schema.
- Develop the register and login API endpoints using FastAPI.
- Add password hashing and JWT token generation for authentication.
- Begin writing basic Pytest tests for the authentication feature.

## March 10th

### What I did

* Set up the initial **User Authentication feature structure** under the branch `Feat1-User-Authentication-and-Authorization`.
* Created the backend layers for the feature:

  * `routers/auth_router.py` for authentication API endpoints.
  * `services/auth_service.py` for authentication business logic.
  * `repositories/user_repository.py` for database access related to users.
  * `schemas/user_schema.py` for request and response validation.
* Started integrating the authentication router with the FastAPI backend structure.

### What I will do next

* Implement the **user registration endpoint**.
* Add logic for **password validation and hashing**.
* Implement the **login endpoint** and authentication flow.
* Connect the repository layer to the **user database table**.

### Blockers (optional)

* Need to ensure the **FastAPI environment and dependencies are correctly installed** so imports resolve properly.



---

## Template (Copy for each new day)

## Date

### What I did
-

### What I will do next
-

### Blockers (optional)
-
