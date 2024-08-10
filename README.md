# FinalProject-Kaleidoo

# 📦 My E-Commerce Recommendation System Application

Welcome to the **E-Commerce Recommendation System Application** repository! This guide will help you set up and run the entire application on your local Kubernetes cluster.

## 🚀 Getting Started

### Prerequisites

Before you start, make sure you have the following installed on your machine:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Kubernetes**: [Install Kubernetes](https://kubernetes.io/docs/tasks/tools/)
- **kubectl**: [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **Minikube** (or any other local Kubernetes solution): [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)

### Step 1: Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/waleed399/FinalProject-Kaleidoo.git
cd FinalProject-Kaleidoo
```

Step 2: Set Up Secrets
Before deploying your application, you need to set up the necessary Kubernetes secrets:

Create a secret.yaml file:
Ensure your secrets are properly configured in secret.yaml.
Apply the secrets:
Run the following command to apply the secrets to your Kubernetes cluster:

```bash
kubectl apply -f secret.yaml
```

Step 3: Deploy Zookeeper
Deploy the Zookeeper service, which is essential for Kafka:

```bash
kubectl apply -f zookeeper-deployment.yaml
```

Wait until the Zookeeper pod is up and running:

```bash
kubectl get pods -l app=zookeeper
```

Step 4: Deploy Kafka
Next, deploy Kafka which will use the Zookeeper service:

```bash
kubectl apply -f kafka-deployment.yaml
```

Verify that Kafka is running:

```bash
kubectl get pods -l app=kafka
```

Step 5: Deploy the Backend
Deploy your backend application:

```bash
kubectl apply -f backend-deployment.yaml
```

Ensure the backend is running smoothly:

```bash
kubectl get pods -l app=backend
```

Step 6: Deploy the Frontend
Finally, deploy your frontend application:

```bash
kubectl apply -f frontend-deployment.yaml
```

Check that the frontend is up and running:

```bash
kubectl get pods -l app=frontend
```

Step 7: Access the Application
Now that everything is deployed, you can access the frontend application. Depending on your Kubernetes setup:

```bash
minikube service frontend-service
```

kubectl port-forwarding:

```bash
kubectl port-forward service/frontend-service 8080:80
```

Visit http://localhost:8080 to view the application.
🎉 Congratulations!
Your application should now be up and running on your local Kubernetes cluster. Enjoy exploring!

## 📂 Project Structure

Here's a quick overview of the files you’ll find in this repository:

```plaintext
.
├── backend-deployment.yaml   # Backend Kubernetes deployment
├── frontend-deployment.yaml  # Frontend Kubernetes deployment
├── zookeeper-deployment.yaml # Zookeeper Kubernetes deployment
├── kafka-deployment.yaml     # Kafka Kubernetes deployment
├── secret.yaml               # Kubernetes secrets for the application
└── README.md                 # You're reading it!


Common Issues
Pods not starting: Ensure that Docker and Kubernetes are running correctly on your machine.
Access issues: Verify the Kubernetes service configurations and port-forwarding rules.
🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, please open an issue or submit a pull request.
```
