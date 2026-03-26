# COSC310 — Royal Flush
### Food Delivery System — Backend Implementation

---

## Team Members

| Name | Student ID |
|------|------------|
| Dahlia Mohammadi | 10915528 |
| Nandini Anaparti | 27794205 |
| Nisini Perera | 10089811 |
| Yibing Wang | 25470915 |

---

## Project Overview

This project focuses on the backend implementation of a food delivery system using a dockerized layered architecture built with FastAPI. The backend exposes RESTful API endpoints and is organized into separate layers for models, routers, schemas, services, repositories, and testing. Specialized backend features such as pricing and notifications are separated into their own service modules to improve modularity and maintainability.

---

## Architecture Overview

The project adopts a dockerized layered backend architecture using FastAPI to expose REST endpoints, with separate service and data access layers handling business logic and database interaction. Each core backend feature is implemented as a focused module, promoting modularity, separation of concerns, and testability.

This design supports the following software quality attributes:

- **Maintainability** — improved through clean layering and separation of responsibilities.
- **Testability** — supported with Pytest and service-specific test files.
- **Scalability** — supported through containerization, allowing backend components to run consistently across environments.
- **Reliability** — improved through validation of incoming requests, structured schemas, and clear organization of backend logic.


---

## Backend Structure
```text
backend/
└── app/
    ├── data/
    │   └── (JSON data files)
    ├── models/
    ├── notification_service/
    │   └── app/
    │       ├── main.py
    │       └── test_main.py
    ├── price_service/
    │   └── app/
    │       ├── main.py
    │       ├── test_main.py
    │       └── menu_items.json
    ├── repositories/
    ├── routers/
    ├── schemas/
    ├── services/
    ├── tests/
    └── main.py
```

---

## Backend Components

### Main Application
The main FastAPI application is located in `backend/app/main.py`. This file serves as the primary entry point and connects the main application logic together.

### Models
The `models/` folder contains the core backend data models used throughout the application.

### Routers
The `routers/` folder contains the API route definitions. These handle incoming HTTP requests and connect them to the appropriate backend logic.

### Schemas
The `schemas/` folder contains request and response models used for validation and structured API communication.

### Services
The `services/` folder contains the business logic of the backend. This layer is responsible for processing requests and applying application rules.

### Repositories
The `repositories/` folder handles data access and persistence-related operations, keeping storage concerns separate from business logic.

### Data
The `data/` folder stores JSON data files used by the backend.

### Notification Service
The notification service is implemented separately under `notification_service/app/`. It has its own `main.py` and `test_main.py`, making the notification feature easier to develop and test independently.

### Price Service
The price service is implemented separately under `price_service/app/`. It includes its own `main.py`, `test_main.py`, and `menu_items.json` for pricing-related backend logic.

### Tests
Testing is supported through Pytest. Tests are located both in the shared `tests/` folder and inside service-specific folders.

---

## How to Run the Backend

Before running the backend, ensure the following tools are installed:
- Docker Desktop (version 4.x or newer)
- VSCode

### Option 1 — Using VSCode Terminal

1. Open the project in VSCode.
2. Make sure you are in the folder that contains `docker-compose.yml`.
3. Run:
```bash
docker compose up -d
```

To stop the containers:
```bash
docker compose down
```

### Option 2 — Using Docker Desktop

1. Open Docker Desktop.
2. Go to the **Containers** tab.
3. Find the project name.
4. Click **Start** to run the containers. Click **Stop** when finished.

### Option 3 — From an Image Tar

Load the image into Docker:
```bash
docker load -i [backend_name_here.tar]
```

Check the image name:
```bash
docker images
```

Run the container:
```bash
docker run -d \
  --name royal-flush-backend \
  -p 8000:8000 \
  [backend_name_goes_here:tag]
```

---

## Accessing the Backend

Once running, the backend is available at:

- **API:** http://localhost:8000/

---

## Rebuilding the Backend

If you change backend code or the Dockerfile, rebuild with:
```bash
docker compose up --build
```

Then start the containers again:
```bash
docker compose up -d
```

---

## Backend Dependencies

| Category | Component / Technology | Version |
|----------|------------------------|---------|
| Backend Language | Python | 3.13.7 |
| Backend Framework | FastAPI | 0.119.1 |
| Package Manager | pip | 25.3 |
| Database | JSON storage | Included with Python |
| Containerization | Docker Engine | 28.4.0 |
| Docker Compose | Docker Compose | v2.39.4-desktop.1 |

---

## Backend Requirements

| Package | Version |
|---------|---------|
| annotated-types | 0.7.0 |
| anyio | 4.11.0 |
| bandit | 1.8.6 |
| certifi | 2025.10.5 |
| click | 8.3.0 |
| colorama | 0.4.6 |
| fastapi | 0.119.1 |
| h11 | 0.16.0 |
| httpcore | 1.0.9 |
| httpx | 0.28.1 |
| idna | 3.11 |
| iniconfig | 2.3.0 |
| markdown-it-py | 4.0.0 |
| mdurl | 0.1.2 |
| packaging | 25.0 |
| passlib | 1.7.4 |
| pip | 25.2 |
| pluggy | 1.6.0 |
| pydantic | 2.12.3 |
| pydantic_core | 2.41.4 |
| Pygments | 2.19.2 |
| pytest | 8.4.2 |
| python-multipart | 0.0.20 |
| PyYAML | 6.0.3 |
| rich | 14.2.0 |
| sniffio | 1.3.1 |
| starlette | 0.48.0 |
| stevedore | 5.5.0 |
| typing_extensions | 4.15.0 |
| typing-inspection | 0.4.2 |
| uvicorn | 0.38.0 |

---

## Summary

The backend for COSC310-ROYAL-FLUSH is designed as a modular FastAPI-based system with clear separation between routing, schemas, business logic, data access, and service-specific modules. By using Docker and Pytest alongside a layered backend design, the project supports consistent deployment, easier testing, and future scalability. This structure provides a solid foundation for the overall  system.
