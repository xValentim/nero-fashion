#!/bin/bash

# Deploy Online Boutique with Nano Banana Service
# This script automates the enhanced deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Online Boutique + Nano Banana Service Deployment${NC}"
echo "=================================================="

# Check if required variables are set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: PROJECT_ID environment variable is not set${NC}"
    echo "Please run: export PROJECT_ID=<your-project-id>"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ Error: GEMINI_API_KEY environment variable is not set${NC}"
    echo "Please run: export GEMINI_API_KEY=<your-gemini-api-key>"
    exit 1
fi

REGION=${REGION:-us-central1}

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Gemini API Key: ${GEMINI_API_KEY:0:10}..."
echo

# Step 1: Setup Artifact Registry
echo -e "${YELLOW}🔧 Step 1: Setting up Artifact Registry...${NC}"
gcloud services enable artifactregistry.googleapis.com --project=${PROJECT_ID}

if ! gcloud artifacts repositories describe images --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create images \
        --repository-format=docker \
        --location=${REGION} \
        --project=${PROJECT_ID}
else
    echo "Artifact Registry repository already exists."
fi

echo "Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Step 2: Create Gemini API Secret
echo -e "${YELLOW}🔑 Step 2: Creating Gemini API Secret...${NC}"
if kubectl get secret gemini-api &>/dev/null; then
    echo "Gemini API secret already exists."
else
    kubectl create secret generic gemini-api \
        --from-literal=GEMINI_API_KEY=${GEMINI_API_KEY}
    echo "Gemini API secret created."
fi

# Step 3: Build and push Nano Banana Service
echo -e "${YELLOW}🏗️  Step 3: Building and pushing Nano Banana Service...${NC}"
cd src/nanobananaservice

echo "Building Docker image..."
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/images/nanobananaservice:latest .

echo "Pushing to Artifact Registry..."
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/images/nanobananaservice:latest

cd ../..

# Step 4: Update image reference in manifests
echo -e "${YELLOW}📝 Step 4: Updating manifest with correct image...${NC}"
sed -i.bak "s|image: us-central1-docker.pkg.dev/gke-app-hacka/images/nanobananaservice:latest|image: ${REGION}-docker.pkg.dev/${PROJECT_ID}/images/nanobananaservice:latest|g" \
    kustomize/components/nanobananaservice/nanobananaservice.yaml

# Step 5: Deploy services
echo -e "${YELLOW}🚀 Step 5: Deploying services...${NC}"
echo "Deploying Online Boutique..."
kubectl apply -f ./release/kubernetes-manifests.yaml

echo "Deploying Nano Banana Service..."
kubectl apply -f ./kustomize/components/nanobananaservice/nanobananaservice.yaml

# Step 6: Wait for pods to be ready
echo -e "${YELLOW}⏳ Step 6: Waiting for pods to be ready...${NC}"
echo "This may take a few minutes..."

kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=nanobananaservice --timeout=300s

# Step 7: Show status
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo
echo -e "${YELLOW}📊 Current pod status:${NC}"
kubectl get pods

echo
echo -e "${YELLOW}🌐 Access URLs:${NC}"
EXTERNAL_IP=$(kubectl get service frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")
echo "  Frontend: http://${EXTERNAL_IP}"

echo
echo -e "${YELLOW}🔍 Testing commands:${NC}"
echo "  # Test Nano Banana Service health:"
echo "  kubectl port-forward service/nanobananaservice 8080:8080"
echo "  curl http://localhost:8080/health"
echo
echo "  # Monitor logs:"
echo "  kubectl logs -f deployment/nanobananaservice"
echo
echo -e "${GREEN}🎉 Online Boutique with AI Fashion Assistant is ready!${NC}"