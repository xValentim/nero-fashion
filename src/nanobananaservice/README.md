# Nano Banana Service

## Overview

The **Nano Banana Service** is an AI-powered fashion assistant microservice that integrates with the Online Boutique application. It uses Google's Gemini AI to provide intelligent product recommendations, image analysis, and fashion advice.

## Features

- **AI Fashion Assistant**: Provides personalized fashion advice using Gemini AI
- **Image Processing**: Analyzes user and product images for recommendations  
- **Product Integration**: Direct gRPC integration with productcatalogservice
- **RESTful API**: Easy-to-use endpoints for frontend integration
- **Image Generation**: Creates AI-generated product combinations and visualizations

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │───▶│ NanoBanana      │───▶│ ProductCatalog  │
│   (Web UI)      │    │ Service         │    │ Service (gRPC)  │
│                 │    │ (FastAPI)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │                 │
                       │  Gemini AI      │
                       │  (Google AI)    │
                       │                 │
                       └─────────────────┘
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Product Information
- `GET /products` - List all products from the catalog
- `GET /products-name/{name}` - Search products by name

### AI-Powered Features
- `POST /assistant-fashion` - Get AI fashion advice from user image
- `POST /describe-image` - Analyze and describe images (product or person)
- `POST /remix-images` - Create AI-generated product combinations
- `POST /sell-product-from-query` - Generate sales content based on user queries and images

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |
| `PRODUCT_CATALOG_SERVICE_ADDR` | gRPC address for product catalog | No (default: `productcatalogservice:3550`) |

### Kubernetes Secrets

The service requires a Kubernetes secret named `gemini-api` with the Gemini API key:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gemini-api
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-key>
```

## Deployment

### Prerequisites

1. Google Kubernetes Engine cluster
2. Artifact Registry repository
3. Gemini AI API key
4. Docker installed locally

### Manual Deployment

1. **Build and push the image**:
   ```sh
   cd src/nanobananaservice
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/images/nanobananaservice:latest .
   docker push us-central1-docker.pkg.dev/PROJECT_ID/images/nanobananaservice:latest
   ```

2. **Create the Gemini API secret**:
   ```sh
   kubectl create secret generic gemini-api --from-literal=GEMINI_API_KEY=<your-key>
   ```

3. **Deploy the service**:
   ```sh
   kubectl apply -f kustomize/components/nanobananaservice/nanobananaservice.yaml
   ```

### Automated Deployment

Use the provided deployment script:
```sh
export PROJECT_ID=<your-project>
export GEMINI_API_KEY=<your-key>
./deploy-with-nanobanana.sh
```

## Testing

### Local Testing

1. **Start port forwarding**:
   ```sh
   kubectl port-forward service/nanobananaservice 8080:8080
   ```

2. **Test the health endpoint**:
   ```sh
   curl http://localhost:8080/health
   ```

3. **Use the provided Jupyter notebook**:
   Open `src/nanobananaservice/testing_api.ipynb` for comprehensive API testing examples.

### Monitoring

Monitor service logs in real-time:
```sh
kubectl logs -f deployment/nanobananaservice
```

Check service status:
```sh
kubectl get pods -l app=nanobananaservice
```

## Development

### Local Development Setup

1. **Install dependencies**:
   ```sh
   cd src/nanobananaservice
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```sh
   export GEMINI_API_KEY=<your-key>
   export PRODUCT_CATALOG_SERVICE_ADDR=localhost:3550
   ```

3. **Start local development server**:
   ```sh
   uvicorn app:app --host 0.0.0.0 --port 8080 --reload
   ```

### Adding New Features

1. Modify the FastAPI application in `app.py`
2. Update image processing logic in `src/image_service.py`
3. Rebuild and redeploy the Docker image
4. Update API documentation as needed

## Troubleshooting

### Common Issues

1. **ImagePullBackOff errors**:
   - Ensure Artifact Registry is properly configured
   - Check that the service account has the correct permissions
   - Verify the image was pushed successfully

2. **Gemini API errors**:
   - Verify the API key is correctly set in the secret
   - Check API quotas and limits
   - Ensure the Gemini AI service is enabled in your GCP project

3. **gRPC connection errors**:
   - Verify productcatalogservice is running
   - Check network policies and service discovery
   - Ensure protobuf versions are compatible

### Debug Commands

```sh
# Check pod status
kubectl get pods -l app=nanobananaservice

# View detailed pod information
kubectl describe pod <pod-name>

# Check service configuration
kubectl get service nanobananaservice -o yaml

# Verify secrets
kubectl get secret gemini-api -o yaml
```

## Contributing

When contributing to the Nano Banana Service:

1. Follow the existing code style and structure
2. Update tests when adding new features
3. Ensure Docker builds are optimized
4. Update documentation for API changes
5. Test integration with the broader Online Boutique ecosystem

## License

This service is part of the Online Boutique demo application and follows the same licensing terms.