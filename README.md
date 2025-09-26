# Order Management System (Microservices)

This project implements an **Order Management System** using **microservice architecture**, containerized with **Docker**, and deployable on **Kubernetes (Minikube / Docker Desktop)**.  

The system consists of three services:

1. **Inventory Service** – Manage products and quantities.
2. **Order Service** – Place orders, check inventory, generate invoice metadata, and send order events.
3. **Shipping Service** – Subscribe to order events, create shipping records, and track shipping status.

Each service has its own database and REST APIs documented with **Swagger/OpenAPI**.

---

## 📦 Folder Structure

order-management/
├─ inventory/
│ ├─ app.py
│ ├─ models.py
│ ├─ requirements.txt
│ ├─ Dockerfile
│ └─ static/openapi.yaml
├─ order/
│ ├─ app.py
│ ├─ models.py
│ ├─ requirements.txt
│ ├─ Dockerfile
│ └─ static/openapi.yaml
├─ shipping/
│ ├─ app.py
│ ├─ models.py
│ ├─ requirements.txt
│ ├─ Dockerfile
│ └─ static/openapi.yaml
├─ k8s/
│ ├─ rabbitmq-deployment.yaml
│ ├─ inventory-deployment.yaml
│ ├─ order-deployment.yaml
│ └─ shipping-deployment.yaml
└─ README.md

