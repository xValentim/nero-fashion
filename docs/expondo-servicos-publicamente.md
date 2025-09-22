# Expondo Serviços Publicamente no GKE

Este documento explica como expor seus microsserviços para acesso externo no Google Kubernetes Engine (GKE).

## Opções para Exposição Pública

### 1. LoadBalancer (Recomendado para GKE)

O tipo `LoadBalancer` é a forma mais simples de expor um serviço no GKE. O Google Cloud provisiona automaticamente um Load Balancer externo com IP público.

**Exemplo de configuração:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nanobananaservice-external
  labels:
    app: nanobananaservice
spec:
  type: LoadBalancer
  selector:
    app: nanobananaservice
  ports:
    - name: http
      port: 8080
      targetPort: 8080
```

### 2. NodePort

Expõe o serviço em uma porta específica de todos os nós do cluster. Menos seguro e não recomendado para produção.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: meu-servico-nodeport
spec:
  type: NodePort
  selector:
    app: minha-app
  ports:
    - port: 8080
      targetPort: 8080
      nodePort: 30080  # Porta entre 30000-32767
```

### 3. Ingress (Recomendado para múltiplos serviços)

Para exposição mais sofisticada com roteamento baseado em domínio/path.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: meu-ingress
spec:
  rules:
  - host: api.meudominio.com
    http:
      paths:
      - path: /nanobanana
        pathType: Prefix
        backend:
          service:
            name: nanobananaservice
            port:
              number: 8080
```

## Como Aplicar as Mudanças

### 1. Aplicar o manifesto atualizado

```powershell
kubectl apply -f .\kustomize\components\nanobananaservice\nanobananaservice.yaml
```

### 2. Verificar o status do LoadBalancer

```powershell
kubectl get service nanobananaservice-external
```

Você verá algo como:
```
NAME                        TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)          AGE
nanobananaservice-external  LoadBalancer   10.96.85.123   34.123.45.67    8080:30123/TCP   2m
```

### 3. Aguardar o IP externo ser provisionado

Pode levar alguns minutos. Use este comando para monitorar:

```powershell
kubectl get service nanobananaservice-external --watch
```

### 4. Testar o acesso externo

Uma vez que o `EXTERNAL-IP` apareça:

```powershell
curl http://EXTERNAL-IP:8080/health
```

## Comandos Úteis

### Obter IP externo programaticamente

```powershell
$EXTERNAL_IP = kubectl get service nanobananaservice-external -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
Write-Host "IP Externo: $EXTERNAL_IP"
```

### Listar todos os serviços externos

```powershell
kubectl get services --field-selector spec.type=LoadBalancer
```

### Verificar logs do serviço

```powershell
kubectl logs -f deployment/nanobananaservice
```

## Considerações de Segurança

1. **Firewall**: O GKE automaticamente configura regras de firewall para LoadBalancers
2. **HTTPS**: Para produção, considere usar Ingress com certificados TLS
3. **Authentication**: Implemente autenticação no seu serviço
4. **Rate Limiting**: Configure limitação de taxa para evitar abuso

## Custos

- LoadBalancers no GCP têm custo adicional (~$18/mês por LoadBalancer)
- Para múltiplos serviços, considere usar um Ingress compartilhado

## Exemplo Completo para o Nano Banana Service

O serviço `nanobananaservice` agora tem duas configurações:

1. **Interno** (`nanobananaservice`): Para comunicação entre pods no cluster
2. **Externo** (`nanobananaservice-external`): Para acesso público via LoadBalancer

Após o deploy, você pode acessar:
- **Internamente**: `http://nanobananaservice:8080`
- **Externamente**: `http://IP-EXTERNO:8080`

## Troubleshooting

### LoadBalancer fica "Pending"

```powershell
# Verificar quotas
gcloud compute project-info describe --project=SEU-PROJECT-ID

# Verificar logs de eventos
kubectl describe service nanobananaservice-external
```

### Não consegue acessar o IP externo

1. Verifique se o pod está rodando: `kubectl get pods -l app=nanobananaservice`
2. Verifique logs: `kubectl logs deployment/nanobananaservice`
3. Teste internamente primeiro: `kubectl port-forward service/nanobananaservice 8080:8080`