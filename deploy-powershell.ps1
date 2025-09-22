# Deploy Online Boutique with Nano Banana Service - PowerShell Version
# Execute este script linha por linha ou bloco por bloco

Write-Host "🚀 Online Boutique + Nano Banana Service Deployment" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# =====================================================
# VARIÁVEIS - CONFIGURE ESTAS ANTES DE EXECUTAR
# =====================================================
$PROJECT_ID = "gke-app-hacka"
$REGION = "us-central1"
$GEMINI_API_KEY = ""  # SUBSTITUA PELA SUA API KEY

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Region: $REGION"
Write-Host "  Gemini API Key: $($GEMINI_API_KEY.Substring(0,10))..."
Write-Host ""

# =====================================================
# PASSO 1: SETUP ARTIFACT REGISTRY
# =====================================================
Write-Host "🔧 Step 1: Setting up Artifact Registry..." -ForegroundColor Yellow

# Habilitar Artifact Registry API
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID

# Criar repositório (se não existir)
gcloud artifacts repositories create images --repository-format=docker --location=$REGION --project=$PROJECT_ID

# Configurar autenticação Docker
gcloud auth configure-docker "$REGION-docker.pkg.dev"

# =====================================================
# PASSO 2: CRIAR SECRET DA GEMINI API
# =====================================================
Write-Host "🔑 Step 2: Creating Gemini API Secret..." -ForegroundColor Yellow

# Deletar secret existente (se houver)
kubectl delete secret gemini-api --ignore-not-found

# Criar novo secret
kubectl create secret generic gemini-api --from-literal=GEMINI_API_KEY=$GEMINI_API_KEY

# =====================================================
# PASSO 3: BUILD E PUSH DO NANOBANANASERVICE
# =====================================================
Write-Host "🏗️  Step 3: Building and pushing Nano Banana Service..." -ForegroundColor Yellow

# Ir para o diretório do serviço
Set-Location "src\nanobananaservice"

# Build da imagem Docker
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/images/nanobananaservice:latest" .

# Push para Artifact Registry
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/images/nanobananaservice:latest"

# Voltar para raiz do projeto
Set-Location "..\..\"

# =====================================================
# PASSO 4: ATUALIZAR MANIFESTS
# =====================================================
Write-Host "📝 Step 4: Updating manifest with correct image..." -ForegroundColor Yellow

# Ler o arquivo atual
$manifestContent = Get-Content "kustomize\components\nanobananaservice\nanobananaservice.yaml" -Raw

# Substituir a imagem
$newImage = "$REGION-docker.pkg.dev/$PROJECT_ID/images/nanobananaservice:latest"
$manifestContent = $manifestContent -replace "image: us-central1-docker\.pkg\.dev/gke-app-hacka/images/nanobananaservice:latest", "image: $newImage"

# Salvar o arquivo atualizado
$manifestContent | Set-Content "kustomize\components\nanobananaservice\nanobananaservice.yaml"

# =====================================================
# PASSO 5: DEPLOY DOS SERVIÇOS
# =====================================================
Write-Host "🚀 Step 5: Deploying services..." -ForegroundColor Yellow

# Deploy Online Boutique
Write-Host "Deploying Online Boutique..."
kubectl apply -f ".\release\kubernetes-manifests.yaml"

# Deploy Nano Banana Service
Write-Host "Deploying Nano Banana Service..."
kubectl apply -f ".\kustomize\components\nanobananaservice\nanobananaservice.yaml"

# =====================================================
# PASSO 6: AGUARDAR PODS
# =====================================================
Write-Host "⏳ Step 6: Waiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..."

# Aguardar frontend
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s

# Aguardar nanobananaservice
kubectl wait --for=condition=ready pod -l app=nanobananaservice --timeout=300s

# =====================================================
# PASSO 7: MOSTRAR STATUS
# =====================================================
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Current pod status:" -ForegroundColor Yellow
kubectl get pods

Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Yellow
$EXTERNAL_IP = kubectl get service frontend-external -o jsonpath="{.status.loadBalancer.ingress[0].ip}" 2>$null
if (-not $EXTERNAL_IP) { $EXTERNAL_IP = "Pending..." }
Write-Host "  Frontend: http://$EXTERNAL_IP"

Write-Host ""
Write-Host "🔍 Testing commands:" -ForegroundColor Yellow
Write-Host "  # Test Nano Banana Service health:"
Write-Host "  kubectl port-forward service/nanobananaservice 8080:8080"
Write-Host "  curl http://localhost:8080/health"
Write-Host ""
Write-Host "  # Monitor logs:"
Write-Host "  kubectl logs -f deployment/nanobananaservice"
Write-Host ""
Write-Host "🎉 Online Boutique with AI Fashion Assistant is ready!" -ForegroundColor Green

# =====================================================
# COMANDOS DE VERIFICAÇÃO EXTRAS
# =====================================================
Write-Host ""
Write-Host "📋 Quick verification commands:" -ForegroundColor Cyan
Write-Host "kubectl get all"
Write-Host "kubectl get pods -l app=nanobananaservice"
Write-Host "kubectl logs -f deployment/nanobananaservice"