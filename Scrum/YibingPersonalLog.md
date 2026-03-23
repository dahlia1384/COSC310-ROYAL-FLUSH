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


## March 6th
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


## March 8th
### What I did
- feat 1 (auth): add database schema for users and sessions
- feat 1 (auth): add user model and repository
### What I will do next
- continue working on feat 1


## March 9th
### What I did
- FR1
- User registration with email, hashed password, and role
- Email validation


## March 10th
### What I did
- FR2
- User login with password verification
- JWT access token generation
- Role-based access control using dependency guards


## March 11th
### What I did
- FR3
- User logout with session invalidation
- Token revocation via user_sessions table


## March 13th
### What I did
- Adding additionals:
- FastAPI auth router
- UserRepository and SessionRepository
- Security helpers for hashing and JWT


## March 15th
### What I did
- Reviewing colaborator's PRs


## March 16th
### What I did
- Completely implemented Feature 1: User Authentication and Authorization.
- Made the PR for feat 1


---

## Template (Copy for each new day)

## Date

### What I did
-

### What I will do next
-

### Blockers (optional)
-






