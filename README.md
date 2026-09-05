# Bank Marketing MLOps

End-to-end machine learning deployment project using the UCI Bank Marketing dataset.

The project trains an XGBoost classification model, exposes it through a FastAPI REST API, packages it as a multi-architecture Docker image, builds and publishes the image automatically with GitHub Actions, and deploys it on a Raspberry Pi running k3s Kubernetes.

## Quick reference

### GitHub repository

https://github.com/peppescavo/bank-marketing-mlops

### Docker image

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

The image supports:

```text
linux/amd64
linux/arm64
```

### Raspberry Pi

Hostname:

```text
raspberrypi.local
```

Current LAN IP:

```text
192.168.178.29
```

SSH:

```bash
ssh peppe@raspberrypi.local
```

or:

```bash
ssh peppe@192.168.178.29
```

Note: the IP address can change if the router assigns a different DHCP address.

### Deployed API

Base address:

```text
http://192.168.178.29:30080
```

Health endpoint:

```text
http://192.168.178.29:30080/health
```

Swagger UI:

```text
http://192.168.178.29:30080/docs
```

OpenAPI specification:

```text
http://192.168.178.29:30080/openapi.json
```

Prediction endpoint:

```text
POST http://192.168.178.29:30080/predict
```

The root endpoint `/` is not defined, so opening:

```text
http://192.168.178.29:30080/
```

returns `404 Not Found`. This is expected.

### Kubernetes manifests

Deployment:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml
```

Service:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

Apply them directly on the Raspberry Pi:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml

sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

## Goal

Predict whether a bank customer will subscribe to a term deposit using information available before the end of the marketing call.

The main objective is not model optimization, but demonstrating an end-to-end machine learning deployment workflow.

## Architecture

```text
UCI Bank Marketing Dataset
          |
          v
    scikit-learn Pipeline
          |
          v
       XGBoost
          |
          v
     model.joblib
          |
          v
       FastAPI
          |
          v
        Docker
          |
          v
   GitHub Actions
          |
          v
GitHub Container Registry
          |
          v
 Raspberry Pi + k3s
          |
          v
 Kubernetes Deployment
          |
          v
       NodePort
          |
          v
      REST API
```

## Dataset

The project uses the UCI Bank Marketing dataset.

Target:

- `1`: customer subscribes to a term deposit
- `0`: customer does not subscribe

The `duration` feature is excluded because call duration is only known after the call and would therefore introduce information leakage for a pre-call prediction use case.

## Model

The model is an XGBoost classifier.

Preprocessing and prediction are stored together in a scikit-learn `Pipeline` containing:

- `OneHotEncoder` for categorical variables
- `StandardScaler` for numerical variables
- `XGBClassifier`

This allows the API to receive raw customer data without duplicating preprocessing logic.

## Model performance

Current test-set metrics:

| Metric | Value |
|---|---:|
| Accuracy | 0.9021 |
| Precision | 0.7116 |
| Recall | 0.2198 |
| F1 | 0.3359 |
| ROC AUC | 0.8151 |
| PR AUC | 0.4911 |

Because the target is imbalanced, ROC AUC and PR AUC are more informative than accuracy alone.

## API

The trained pipeline is exposed through FastAPI.

Endpoints:

```text
GET  /health
POST /predict
GET  /docs
GET  /openapi.json
```

Run locally without Docker:

```bash
uvicorn src.api:app --reload
```

Local Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Local health endpoint:

```text
http://127.0.0.1:8000/health
```

## Docker

Build locally:

```bash
docker build -t bank-marketing-api .
```

Run:

```bash
docker run -p 8000:8000 bank-marketing-api
```

Then open:

```text
http://localhost:8000/docs
```

## Continuous Integration

Every push to the `master` branch triggers GitHub Actions.

The workflow:

```text
git push
   |
   v
GitHub Actions
   |
   +--> checkout repository
   |
   +--> configure QEMU
   |
   +--> configure Docker Buildx
   |
   +--> build AMD64 + ARM64 images
   |
   +--> push image to GHCR
```

Docker image:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

The multi-architecture build allows the same image to run both on standard x86 cloud/server machines and on the ARM64 Raspberry Pi.

## Kubernetes deployment

The Raspberry Pi runs k3s, a lightweight Kubernetes distribution.

Check cluster:

```bash
sudo k3s kubectl get nodes
```

Expected state:

```text
raspberrypi   Ready
```

Check deployment:

```bash
sudo k3s kubectl get deployments
```

Check pods:

```bash
sudo k3s kubectl get pods
```

Expected state:

```text
1/1   Running
```

Check service:

```bash
sudo k3s kubectl get svc bank-marketing-api
```

The API is exposed using a Kubernetes `NodePort`:

```text
30080
```

Therefore the API is reachable on the local network at:

```text
http://192.168.178.29:30080
```

## Useful Kubernetes commands

```bash
# Node status
sudo k3s kubectl get nodes

# Pods
sudo k3s kubectl get pods

# Deployments
sudo k3s kubectl get deployments

# Services
sudo k3s kubectl get services

# Detailed pod information
sudo k3s kubectl describe pod -l app=bank-marketing-api

# Recent Kubernetes events
sudo k3s kubectl get events --sort-by=.lastTimestamp

# Application logs
sudo k3s kubectl logs -l app=bank-marketing-api

# Restart deployment
sudo k3s kubectl rollout restart deployment bank-marketing-api
```

## k3s configuration

The Raspberry Pi uses Wi-Fi interface:

```text
wlan0
```

Current node IP:

```text
192.168.178.29
```

k3s configuration file:

```text
/etc/rancher/k3s/config.yaml
```

Current configuration:

```yaml
node-ip: 192.168.178.29
flannel-iface: wlan0
disable-network-policy: true
```

Check k3s:

```bash
sudo systemctl status k3s
```

Restart k3s:

```bash
sudo systemctl restart k3s
```

View k3s logs:

```bash
sudo journalctl -u k3s -n 100 --no-pager
```

## Project structure

```text
bank-marketing-mlops/
├── .github/
│   └── workflows/
│       └── docker-build.yml
├── data/
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── metrics/
│   └── final_metrics.json
├── models/
│   └── model.joblib
├── notebooks/
├── src/
│   ├── api.py
│   ├── predict.py
│   └── train.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## End-to-end workflow

Training:

```text
dataset
→ train.py
→ preprocessing
→ XGBoost
→ model.joblib
```

Deployment:

```text
git push
→ GitHub Actions
→ multi-architecture Docker build
→ GitHub Container Registry
→ k3s
→ Kubernetes Pod
→ FastAPI
```

## Current status

Working:

- model training
- preprocessing pipeline
- model serialization
- FastAPI inference service
- Swagger documentation
- Docker containerization
- AMD64 and ARM64 Docker images
- GitHub Actions CI
- GitHub Container Registry
- Raspberry Pi k3s cluster
- Kubernetes Deployment
- Kubernetes NodePort Service
- API accessible from the local network

## Possible next steps

- automatic deployment to k3s after a successful GitHub Actions build
- automated API tests
- health/readiness probes in Kubernetes
- resource requests and limits
- model monitoring
- MLflow model tracking
- deployment to a managed cloud Kubernetes service such as Azure Kubernetes Service
- Terraform infrastructure as code