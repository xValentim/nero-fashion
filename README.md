# 🍌 **NanoBanana Fashion AI** - Enhanced Online Boutique

![Continuous Integration](https://github.com/GoogleCloudPlatform/microservices-demo/workflows/Continuous%20Integration%20-%20Main/Release/badge.svg)

**NanoBanana Fashion AI** is an enhanced version of Google's **Online Boutique** demo application, featuring a revolutionary **AI-powered fashion assistant** built with Google's Gemini AI. This project demonstrates how to modernize e-commerce applications with cutting-edge artificial intelligence capabilities.

## 🎯 **Competition Project Overview**

This project enhances the original Google Cloud microservices demo by adding:
- 🤖 **AI Fashion Assistant** powered by Google Gemini
- 📷 **Intelligent Image Analysis** for personalized recommendations  
- 🛍️ **Smart Product Recommendations** based on user style
- 🎨 **AI-Generated Product Visualizations** 
- 📧 **Personalized Email Marketing** with AI insights
- 🛒 **Enhanced Shopping Cart** with AI suggestions

## 🏗️ **Enhanced Architecture**

**NanoBanana Fashion AI** extends the original 11-microservice architecture with our innovative **NanoBanana Service**, creating a comprehensive AI-driven e-commerce platform.

[![Enhanced Architecture](/docs/img/new-architecture-diagram.png)](/docs/img/new-architecture-diagram.png)

Find **Protocol Buffers Descriptions** at the [`./protos` directory](/protos).

| Service | Language | Description |
|---------|----------|-------------|
| [frontend](/src/frontend) | Go | Exposes HTTP server for the web interface. Generates session IDs automatically. |
| [cartservice](/src/cartservice) | C# | Stores shopping cart items in Redis and retrieves them. |
| [productcatalogservice](/src/productcatalogservice) | Go | Provides product catalog from JSON with search capabilities. |
| [currencyservice](/src/currencyservice) | Node.js | Converts currencies using real European Central Bank data. |
| [paymentservice](/src/paymentservice) | Node.js | Processes credit card payments (mock implementation). |
| [shippingservice](/src/shippingservice) | Go | Calculates shipping costs and handles delivery (mock). |
| [emailservice](/src/emailservice) | Python | Sends order confirmation emails to customers. |
| [checkoutservice](/src/checkoutservice) | Go | Orchestrates cart, payment, shipping, and email processes. |
| [recommendationservice](/src/recommendationservice) | Python | Recommends products based on cart contents. |
| [adservice](/src/adservice) | Java | Provides contextual text advertisements. |
| **[🍌 nanobananaservice](/src/nanobananaservice)** | **Python/FastAPI** | **🚀 AI Fashion Assistant with Gemini AI for intelligent recommendations, image analysis, and personalized shopping experiences.** |
| [loadgenerator](/src/loadgenerator) | Python/Locust | Simulates realistic user shopping behavior for testing. |

## ✨ **AI Features - NanoBanana Service**

### 🤖 **AI Fashion Assistant**
- **Personalized Style Analysis**: Upload your photo and get AI-powered fashion advice
- **Smart Product Recommendations**: AI suggests items based on your style and preferences
- **Fashion Tips & Trends**: Get real-time fashion advice from Gemini AI

### 📷 **Advanced Image Processing**
- **Product Visualization**: AI-generated images showing how products look on you
- **Style Matching**: Intelligent matching between user photos and product catalog
- **Image Enhancement**: AI-powered product photography and styling

### 🛍️ **Enhanced Shopping Experience**
- **Smart Cart Integration**: AI suggestions added directly to shopping cart
- **Personalized Emails**: AI-generated fashion newsletters and recommendations
- **Real-time Analysis**: Instant fashion feedback and styling suggestions

### 🔌 **API Endpoints**
- `GET /` - Service root endpoint and status check
- `GET /health` - Service health check
- `GET /products` - Enhanced product catalog with AI insights
- `GET /products/{product_id}` - Get specific product details
- `GET /products-name/{name}` - Search products by exact name
- `POST /assistant-fashion` - AI fashion advice from user images
- `POST /describe-image` - AI image analysis (product/person)
- `POST /remix-images` - AI-generated product combinations
- `POST /sell-product-from-query` - AI sales content generation
- `POST /cart/add-item` - Smart cart management
- `GET /cart/{user_id}` - Retrieve user shopping cart contents
- `DELETE /cart/{user_id}` - Empty user shopping cart
- `POST /email/send-confirmation` - Personalized email campaigns


![Continuous Integration](https://github.com/GoogleCloudPlatform/microservices-demo/workflows/Continuous%20Integration%20-%20Main/Release/badge.svg)

**Online Boutique** is a cloud-first microservices demo application.  The application is a
web-based e-commerce app where users can browse items, add them to the cart, and purchase them.

Google uses this application to demonstrate how developers can modernize enterprise applications using Google Cloud products, including: [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine), [Cloud Service Mesh (CSM)](https://cloud.google.com/service-mesh), [gRPC](https://grpc.io/), [Cloud Operations](https://cloud.google.com/products/operations), [Spanner](https://cloud.google.com/spanner), [Memorystore](https://cloud.google.com/memorystore), [AlloyDB](https://cloud.google.com/alloydb), and [Gemini](https://ai.google.dev/). This application works on any Kubernetes cluster.

If you’re using this demo, please **★Star** this repository to show your interest!

**Note to Googlers:** Please fill out the form at [go/microservices-demo](http://go/microservices-demo).

## Architecture

**Online Boutique** is composed of 12 microservices written in different
languages that talk to each other over gRPC. This includes an AI-powered fashion assistant service (nanobananaservice) that uses Google's Gemini AI for intelligent product recommendations and image analysis.

[![Architecture of
microservices](/docs/img/architecture-diagram.png)](/docs/img/architecture-diagram.png)

Find **Protocol Buffers Descriptions** at the [`./protos` directory](/protos).

| Service                                              | Language      | Description                                                                                                                       |
| ---------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [frontend](/src/frontend)                           | Go            | Exposes an HTTP server to serve the website. Does not require signup/login and generates session IDs for all users automatically. |
| [cartservice](/src/cartservice)                     | C#            | Stores the items in the user's shopping cart in Redis and retrieves it.                                                           |
| [productcatalogservice](/src/productcatalogservice) | Go            | Provides the list of products from a JSON file and ability to search products and get individual products.                        |
| [currencyservice](/src/currencyservice)             | Node.js       | Converts one money amount to another currency. Uses real values fetched from European Central Bank. It's the highest QPS service. |
| [paymentservice](/src/paymentservice)               | Node.js       | Charges the given credit card info (mock) with the given amount and returns a transaction ID.                                     |
| [shippingservice](/src/shippingservice)             | Go            | Gives shipping cost estimates based on the shopping cart. Ships items to the given address (mock)                                 |
| [emailservice](/src/emailservice)                   | Python        | Sends users an order confirmation email (mock).                                                                                   |
| [checkoutservice](/src/checkoutservice)             | Go            | Retrieves user cart, prepares order and orchestrates the payment, shipping and the email notification.                            |
| [recommendationservice](/src/recommendationservice) | Python        | Recommends other products based on what's given in the cart.                                                                      |
| [adservice](/src/adservice)                         | Java          | Provides text ads based on given context words.                                                                                   |
| [nanobananaservice](/src/nanobananaservice)         | Python/FastAPI| AI-powered fashion assistant using Gemini. Provides product recommendations, image analysis, and fashion advice via REST API.     |
| [loadgenerator](/src/loadgenerator)                 | Python/Locust | Continuously sends requests imitating realistic user shopping flows to the frontend.                                              |

## 📱 **Screenshots**

| Enhanced Home Page with AI | AI Fashion Assistant Demo |
|----------------------------|---------------------------|
| [![Screenshot of enhanced store homepage](/docs/img/online-boutique-frontend-1.png)](/docs/img/online-boutique-frontend-1.png) | [![Screenshot of AI fashion assistant](/docs/img/online-boutique-frontend-2.png)](/docs/img/online-boutique-frontend-2.png) |

## 🚀 **Quick Start - Deploy NanoBanana Fashion AI**

### Prerequisites
- [Google Cloud Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated
- [Docker Desktop](https://www.docker.com/get-started) running locally
- [Gemini AI API Key](https://ai.google.dev/) for AI features
- Kubernetes cluster (GKE recommended)

### 🎯 **Option A: Automated Deployment (Recommended)**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xValentim/nero-fashion.git
   cd hackaton-gke
   ```

2. **Configure environment variables**:
   ```powershell
   $PROJECT_ID = "your-gcp-project-id"
   $REGION = "us-central1"  
   $GEMINI_API_KEY = "your-gemini-api-key"
   ```

3. **Run automated deployment**:
   ```powershell
   # Edit deploy-simple.ps1 with your configuration
   .\deploy-simple.ps1
   ```

### 🎯 **Option B: Manual Step-by-Step Deployment**

1. **Set up Google Cloud environment**:
   ```bash
   # Authenticate and set project
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   
   # Create GKE cluster
   gcloud container clusters create nanobanana-cluster \
     --region=us-central1 \
     --machine-type=e2-standard-4 \
     --num-nodes=2
   
   # Get credentials
   gcloud container clusters get-credentials nanobanana-cluster --region=us-central1
   ```

2. **Set up Artifact Registry**:
   ```bash
   # Enable API and create repository
   gcloud services enable artifactregistry.googleapis.com
   gcloud artifacts repositories create images \
     --repository-format=docker \
     --location=us-central1
   
   # Configure Docker authentication
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

3. **Create Gemini API Secret**:
   ```bash
   kubectl create secret generic gemini-api \
     --from-literal=GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```

4. **Build and deploy NanoBanana Service**:
   ```bash
   # Build and push the AI service
   cd src/nanobananaservice
   docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/images/nanobananaservice:latest .
   docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/images/nanobananaservice:latest
   cd ../..
   
   # Deploy all services
   kubectl apply -f release/kubernetes-manifests.yaml
   kubectl apply -f kustomize/components/nanobananaservice/nanobananaservice.yaml
   ```

5. **Wait for deployment and get external IPs**:
   ```bash
   # Wait for pods to be ready
   kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
   kubectl wait --for=condition=ready pod -l app=nanobananaservice --timeout=300s
   
   # Get external IPs
   kubectl get service frontend-external
   kubectl get service nanobananaservice-external
   ```

## 🧪 **Testing the AI Features**

### Access the Application
- **Frontend**: `http://FRONTEND_EXTERNAL_IP`
- **AI API**: `http://NANOBANANA_EXTERNAL_IP:8080`
- **API Documentation**: `http://NANOBANANA_EXTERNAL_IP:8080/docs`

### Test AI Endpoints
```bash
# Health check
curl http://NANOBANANA_IP:8080/health

# Get products with AI insights
curl http://NANOBANANA_IP:8080/products

# Test AI fashion assistant (requires image upload)
curl -X POST http://NANOBANANA_IP:8080/assistant-fashion \
  -F "image=@path/to/user-photo.jpg"

# Test smart cart features
curl -X POST http://NANOBANANA_IP:8080/cart/add-item \
  -F "user_id=test123" \
  -F "product_id=OLJCESPC7Z" \
  -F "quantity=1"
```

### 📊 **Monitor and Debug**
```bash
# Monitor NanoBanana Service logs
kubectl logs -f deployment/nanobananaservice

# Check all pods status
kubectl get pods

# Describe any failing pods
kubectl describe pod POD_NAME
```

## 🛠 **Development Features**

### NanoBanana AI Service Features
The AI-powered fashion assistant includes:

- **🎯 Smart Product Recommendations**: Context-aware suggestions based on user preferences and browsing history
- **🖼️ Image Analysis**: Upload a photo and get instant fashion advice and matching product recommendations
- **🛒 Intelligent Cart Management**: AI-enhanced cart functionality with smart quantity and preference suggestions
- **📧 Personalized Email Notifications**: Smart email confirmations with styling tips and related products
- **🔗 Seamless gRPC Integration**: Real-time communication with all microservices for instant updates

### API Endpoints Available

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root service endpoint with status message |
| `/health` | GET | Service health check |
| `/products` | GET | Get all products with AI insights |
| `/products/{product_id}` | GET | Get specific product details |
| `/products-name/{name}` | GET | Search products by name |
| `/products-name/{name}` | GET | Search products by exact name match |
| `/assistant-fashion` | POST | Upload image for fashion analysis |
| `/describe-image` | POST | AI image analysis for products or persons |
| `/remix-images` | POST | AI-powered image remixing with two input images |
| `/sell-product-from-query` | POST | Generate personalized sales content from user image and text |
| `/cart/add-item` | POST | Add item to cart with AI suggestions |
| `/cart/{user_id}` | GET | Get user cart with recommendations |
| `/cart/{user_id}` | DELETE | Clear user cart |
| `/email/send-confirmation` | POST | Send confirmation email with styling tips |

## 📋 **Local Development Setup**

### Requirements
- **Python 3.8+** with pip
- **Docker Desktop** running
- **Google Cloud SDK** configured
- **Jupyter Notebook** (optional, for testing)

### Setting up the Environment

1. **Clone and configure environment**:
   ```bash
   git clone https://github.com/xValentim/nero-fashion.git
   cd hackaton-gke
   
   # Create virtual environment
   python -m venv env
   source env/bin/activate  # Linux/Mac
   # or
   env\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r src/nanobananaservice/requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   export PRODUCT_CATALOG_SERVICE_ADDR="localhost:3550"
   export CART_SERVICE_ADDR="localhost:7070"
   export EMAIL_SERVICE_ADDR="localhost:5000"
   ```

3. **Run services locally for development**:
   ```bash
   # Terminal 1: Start the FastAPI server
   cd src/nanobananaservice
   uvicorn app:app --reload --host 0.0.0.0 --port 8080
   
   # Terminal 2: Port-forward GKE services (if using cloud deployment)
   kubectl port-forward service/productcatalogservice 3550:3550
   kubectl port-forward service/cartservice 7070:7070
   kubectl port-forward service/emailservice 5000:5000
   ```

4. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Interactive API documentation
   open http://localhost:8080/docs
   ```

## 🏗 **Architecture & Technology Stack**

### Core Technologies
- **Google Kubernetes Engine (GKE)**: Container orchestration and scalable deployment
- **Artifact Registry**: Docker image storage and management  
- **Gemini AI**: Advanced fashion analysis and recommendation engine
- **FastAPI** (Python): High-performance async API framework for the AI service
- **gRPC**: High-performance inter-service communication
- **Go, Node.js, C#, Java, Python**: Multi-language microservices architecture

### AI/ML Integration
- **Gemini Pro Vision**: Image analysis and fashion recommendations
- **Gemini Pro**: Text generation for product descriptions and styling advice
- **Custom AI Workflows**: Intelligent product matching and personalized recommendations

## 🏆 **Competition Highlights**

### Innovation & Technical Excellence
- **🎯 AI-Powered Fashion Assistant**: Google's Gemini AI for personalized recommendations and image analysis
- **🔗 Microservices Integration**: Seamless gRPC communication between 12 specialized services
- **☁️ Cloud-Native Architecture**: GKE deployment with auto-scaling and load balancing
- **📱 Enhanced User Experience**: Interactive FastAPI interface with real-time AI recommendations
- **🛠 Production-Ready**: Complete CI/CD pipeline with automated deployment scripts
- **🔒 Security**: Google Cloud IAM integration with secure API key management

## 📈 **Future Roadmap**

### Planned Enhancements
- **Advanced AI Features**: Style preference learning and trend prediction
- **Mobile Integration**: React Native app with AR try-on features
- **Analytics Dashboard**: Admin panel with AI-driven business insights
- **Global Scale**: Multi-language support and edge computing optimization

## 🤝 **Contributing & Support**

### How to Contribute
1. Fork the repository and create your feature branch
2. Add new AI features or enhance existing microservices  
3. Submit pull requests with detailed descriptions
4. Follow Python PEP 8 standards and add comprehensive tests

### Resources & Contact
- **Repository**: [https://github.com/xValentim/nero-fashion](https://github.com/xValentim/nero-fashion)
- **Documentation**: [GKE](https://cloud.google.com/kubernetes-engine/docs) | [Gemini AI](https://ai.google.dev/) | [FastAPI](https://fastapi.tiangolo.com/)
- **API Reference**: Interactive docs at `/docs` endpoint when deployed

## 📄 **License**

Licensed under Apache License 2.0 - see [LICENSE](LICENSE) file for details.

Built with ❤️ by Team NanoBanana using Google Cloud Platform and Gemini AI.

---

**🍌 Ready to revolutionize fashion with AI? Deploy NanoBanana Fashion AI today!**
