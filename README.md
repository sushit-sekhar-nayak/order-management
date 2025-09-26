# Order Management System (Microservices)

This project implements an **Order Management System** using **microservice architecture**, containerized with **Docker**, and deployable on **Kubernetes (Minikube / Docker Desktop)**.  

The system consists of three services:

1. **Inventory Service** – Manage products and quantities.
2. **Order Service** – Place orders, check inventory, generate invoice metadata, and send order events.
3. **Shipping Service** – Subscribe to order events, create shipping records, and track shipping status.

Each service has its own database and REST APIs documented with **Swagger/OpenAPI**.

---

## Folder Structure

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


---

## Requirements

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Swagger-UI
- RabbitMQ
- Docker
- Kubernetes / Minikube
- Requests library

---

## Running Locally

### Start Inventory Service

cd inventory
python app.py
Swagger UI: http://127.0.0.1:5001/docs

### Start Order Service
cd order
python app.py
Swagger UI: http://127.0.0.1:5002/docs

### Start Shipping Service
cd shipping
python app.py
Swagger UI: http://127.0.0.1:5003/docs
Make sure RabbitMQ is running locally on default port 5672.

Sample API Flow

1. Add product to inventory
curl -X POST http://127.0.0.1:5001/products \
-H "Content-Type: application/json" \
-d '{"sku":"A101","name":"Widget","quantity":10,"price":109.9}'

2. Place an order
curl -X POST http://127.0.0.1:5002/orders \
-H "Content-Type: application/json" \
-d '{"items":[{"sku":"A101","qty":2}]}'

3. Check order status
curl http://127.0.0.1:5002/orders/<order_id>

4. Check product inventory
curl http://127.0.0.1:5001/products/A101

5. Shipping service automatically receives order event via RabbitMQ
Check shipping status:
curl http://127.0.0.1:5003/shipping/<order_id>

### Docker
Each service has its own Dockerfile. Build and run with:
docker build -t inventory-service ./inventory
docker build -t order-service ./order
docker build -t shipping-service ./shipping

docker run -p 5001:5001 inventory-service
docker run -p 5002:5002 order-service
docker run -p 5003:5003 shipping-service

### Kubernetes Deployment
Kubernetes YAML files are in the k8s/ folder. Example:
kubectl apply -f k8s/rabbitmq-deployment.yaml
kubectl apply -f k8s/inventory-deployment.yaml
kubectl apply -f k8s/order-deployment.yaml
kubectl apply -f k8s/shipping-deployment.yaml
Verify pods:
kubectl get pods

### API Documentation
All services provide Swagger UI at /docs.
OpenAPI spec is located in each service under static/openapi.yaml.

### Notes
Each service has its own SQLite database (*.db) for simplicity.
Communication between Order → Shipping uses RabbitMQ.
Invoice generation currently returns metadata (JSON). PDF generation can be added.
UI can be implemented in React or Angular (optional).

### Bonus (Optional)
Integrate a Payment Gateway during order placement.
Add JWT-based authentication for all APIs.

### References
Flask Documentation
Flask-SQLAlchemy
Flask-Swagger-UI
RabbitMQ Tutorials
Kubernetes Official Docs




