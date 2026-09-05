# Bank Marketing MLOps

End-to-end machine learning deployment project based on the UCI Bank Marketing dataset.

The project trains an XGBoost classification model, exposes it through a FastAPI REST API, packages it as a Docker image, automatically builds multi-architecture images with GitHub Actions, stores them in GitHub Container Registry, and deploys the application to a Raspberry Pi running k3s Kubernetes.

The main objective is to demonstrate a complete ML deployment workflow rather than only model development in a notebook.

---

# Quick Reference

## GitHub Repository

```text
https://github.com/peppescavo/bank-marketing-mlops
```

Repository:

```text
peppescavo/bank-marketing-mlops
```

Default branch:

```text
master
```

---

## Docker Image

GitHub Container Registry:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

Supported architectures:

```text
linux/amd64
linux/arm64
```

This allows the same image to run both on standard x86 machines and on the ARM64 Raspberry Pi.

---

## Raspberry Pi

Hostname:

```text
raspberrypi.local
```

Current LAN IP:

```text
192.168.178.29
```

SSH using hostname:

```bash
ssh peppe@raspberrypi.local
```

SSH using IP:

```bash
ssh peppe@192.168.178.29
```

Check Raspberry IP:

```bash
hostname -I
```

Important: the IP address may change if the router assigns a different address through DHCP.

The k3s configuration currently explicitly uses:

```text
192.168.178.29
```

For a permanent setup, reserving this IP in the router DHCP configuration is recommended.

---

# Deployed API

Base address:

```text
http://192.168.178.29:30080
```

Swagger UI:

```text
http://192.168.178.29:30080/docs
```

Health endpoint:

```text
http://192.168.178.29:30080/health
```

Prediction endpoint:

```text
POST http://192.168.178.29:30080/predict
```

OpenAPI specification:

```text
http://192.168.178.29:30080/openapi.json
```

The root endpoint is not implemented:

```text
http://192.168.178.29:30080/
```

Therefore a response such as:

```text
404 Not Found
```

is expected.

---

# Goal

Predict whether a bank customer will subscribe to a term deposit using information available before the end of the marketing call.

The project focuses on the engineering path from model development to a running inference service:

```text
data
→ preprocessing
→ model
→ API
→ Docker
→ container registry
→ Kubernetes
→ automated deployment
```

---

# Dataset

The project uses the UCI Bank Marketing dataset.

Target:

```text
1 = customer subscribes to a term deposit
0 = customer does not subscribe
```

The `duration` variable is deliberately excluded.

Call duration is only known after the marketing call has taken place. Using it for a model intended to make predictions before the call would introduce future information and therefore data leakage.

Categorical values such as:

```text
unknown
```

are kept as explicit categories.

---

# Machine Learning Pipeline

The model is an XGBoost classifier.

Preprocessing and prediction are stored together in a scikit-learn `Pipeline`.

The preprocessing stage contains:

- `OneHotEncoder` for categorical variables
- `StandardScaler` for numerical variables

The prediction stage contains:

- `XGBClassifier`

This means the API can receive raw customer features and the same preprocessing used during training is automatically applied during inference.

The trained pipeline is serialized as:

```text
models/model.joblib
```

---

# Model Performance

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

Metrics are stored in:

```text
metrics/final_metrics.json
```

---

# Architecture

```text
                  UCI Bank Marketing Dataset
                             |
                             v
                       src/train.py
                             |
                             v
                 scikit-learn Pipeline
                             |
                  +----------+----------+
                  |                     |
                  v                     v
          preprocessing             XGBoost
                  |                     |
                  +----------+----------+
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
                 Multi-architecture build
                  amd64             arm64
                             |
                             v
              GitHub Container Registry
                             |
                             v
           ghcr.io/peppescavo/bank-marketing-mlops
                             |
                             v
                 Self-hosted GitHub Runner
                     on Raspberry Pi
                             |
                             v
                           k3s
                             |
                             v
                 Kubernetes Deployment
                             |
                             v
                            Pod
                             |
                             v
                    Kubernetes Service
                             |
                             v
                    NodePort :30080
                             |
                             v
                        FastAPI API
```

---

# FastAPI

The trained model is exposed using FastAPI.

Available endpoints:

```text
GET  /health
POST /predict
GET  /docs
GET  /openapi.json
```

Run the API locally:

```bash
uvicorn src.api:app --reload
```

Local base address:

```text
http://127.0.0.1:8000
```

Local Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Local health endpoint:

```text
http://127.0.0.1:8000/health
```

---

# Docker

Build the Docker image locally:

```bash
docker build -t bank-marketing-api .
```

Run it:

```bash
docker run -p 8000:8000 bank-marketing-api
```

Then open:

```text
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/health
```

---

# GitHub Container Registry

Production image:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

The image is automatically built by GitHub Actions.

The workflow creates images for:

```text
linux/amd64
linux/arm64
```

The ARM64 image is used by the Raspberry Pi.

---

# CI/CD

Every push to:

```text
master
```

starts the GitHub Actions pipeline.

The complete pipeline is:

```text
git push
    |
    v
GitHub Actions
GitHub-hosted runner
    |
    v
Checkout repository
    |
    v
Set up QEMU
    |
    v
Set up Docker Buildx
    |
    v
Build Docker image
    |
    +-------------------+
    |                   |
    v                   v
linux/amd64         linux/arm64
    |                   |
    +---------+---------+
              |
              v
       Push image to GHCR
              |
              v
     Build job completes
              |
              v
      Deploy job starts
              |
              v
GitHub self-hosted runner
      on Raspberry Pi
              |
              v
kubectl rollout restart
              |
              v
k3s creates a new Pod
              |
              v
Pod pulls :latest from GHCR
              |
              v
New FastAPI version running
```

The build is executed on a GitHub-hosted runner.

The deployment is executed on the Raspberry Pi using a GitHub Actions self-hosted runner.

---

# GitHub Actions Self-Hosted Runner

The Raspberry Pi is registered as a GitHub Actions runner.

Runner labels:

```text
self-hosted
Linux
ARM64
```

Runner directory:

```text
~/actions-runner
```

The runner is installed as a system service so it continues running after SSH logout and automatically starts after a Raspberry Pi reboot.

Check runner status:

```bash
cd ~/actions-runner
sudo ./svc.sh status
```

Start runner:

```bash
cd ~/actions-runner
sudo ./svc.sh start
```

Stop runner:

```bash
cd ~/actions-runner
sudo ./svc.sh stop
```

Restart runner:

```bash
cd ~/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

For manual foreground execution:

```bash
cd ~/actions-runner
./run.sh
```

Note: `./run.sh` only keeps the runner active while that terminal session is running. The system service should normally be used instead.

---

# Automated Kubernetes Deployment

After the Docker build succeeds, GitHub assigns the deployment job to the Raspberry Pi runner.

The deployment runs:

```bash
sudo k3s kubectl rollout restart deployment/bank-marketing-api
```

Then waits for the new deployment to become available:

```bash
sudo k3s kubectl rollout status deployment/bank-marketing-api --timeout=300s
```

Because the Kubernetes Deployment uses:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

the newly created Pod pulls the current `latest` image.

The result is:

```text
edit code
→ git commit
→ git push
→ build
→ publish image
→ deploy
→ new version running on Raspberry Pi
```

No manual SSH deployment is required during the normal workflow.

---

# Kubernetes

The Raspberry Pi runs:

```text
k3s
```

k3s is a lightweight Kubernetes distribution suitable for small machines and edge devices.

Check Kubernetes node:

```bash
sudo k3s kubectl get nodes
```

Expected state:

```text
raspberrypi   Ready
```

Check deployments:

```bash
sudo k3s kubectl get deployments
```

Check pods:

```bash
sudo k3s kubectl get pods
```

Expected application Pod state:

```text
1/1   Running
```

Check services:

```bash
sudo k3s kubectl get services
```

Check the application service:

```bash
sudo k3s kubectl get svc bank-marketing-api
```

---

# Kubernetes Deployment

Manifest:

```text
k8s/deployment.yaml
```

Remote raw file:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml
```

The Deployment runs one replica of:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

Application container port:

```text
8000
```

Apply manually if necessary:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml
```

---

# Kubernetes Service

Manifest:

```text
k8s/service.yaml
```

Remote raw file:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

Service type:

```text
NodePort
```

Service port:

```text
80
```

Container target port:

```text
8000
```

NodePort:

```text
30080
```

Therefore:

```text
Raspberry Pi IP : NodePort
192.168.178.29 : 30080
```

produces:

```text
http://192.168.178.29:30080
```

Apply manually if necessary:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

---

# First Manual Kubernetes Deployment

If the Kubernetes objects do not exist yet:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml

sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

Then verify:

```bash
sudo k3s kubectl get pods
sudo k3s kubectl get services
```

After the initial deployment, normal application updates are handled automatically through GitHub Actions.

---

# Useful Kubernetes Commands

Node status:

```bash
sudo k3s kubectl get nodes
```

Pods:

```bash
sudo k3s kubectl get pods
```

More pod information:

```bash
sudo k3s kubectl get pods -o wide
```

Deployments:

```bash
sudo k3s kubectl get deployments
```

Services:

```bash
sudo k3s kubectl get services
```

Application service:

```bash
sudo k3s kubectl get svc bank-marketing-api
```

Detailed Pod information:

```bash
sudo k3s kubectl describe pod -l app=bank-marketing-api
```

Application logs:

```bash
sudo k3s kubectl logs -l app=bank-marketing-api
```

Follow application logs:

```bash
sudo k3s kubectl logs -f -l app=bank-marketing-api
```

Kubernetes events:

```bash
sudo k3s kubectl get events --sort-by=.lastTimestamp
```

Restart application manually:

```bash
sudo k3s kubectl rollout restart deployment/bank-marketing-api
```

Wait for deployment:

```bash
sudo k3s kubectl rollout status deployment/bank-marketing-api --timeout=300s
```

---

# k3s Configuration

Configuration file:

```text
/etc/rancher/k3s/config.yaml
```

Current configuration:

```yaml
node-ip: 192.168.178.29
flannel-iface: wlan0
disable-network-policy: true
```

Network interface used by Kubernetes:

```text
wlan0
```

Current node IP:

```text
192.168.178.29
```

`disable-network-policy: true` is currently used as a workaround for the networking issue encountered on this Raspberry Pi setup.

---

# k3s Administration

Check service:

```bash
sudo systemctl status k3s
```

Restart k3s:

```bash
sudo systemctl restart k3s
```

Stop k3s:

```bash
sudo systemctl stop k3s
```

Start k3s:

```bash
sudo systemctl start k3s
```

Recent logs:

```bash
sudo journalctl -u k3s -n 100 --no-pager
```

Follow logs:

```bash
sudo journalctl -u k3s -f
```

---

# Network Information

Show interfaces:

```bash
ip -br addr
```

Current primary interface:

```text
wlan0
```

Current Raspberry Pi address:

```text
192.168.178.29
```

Test Raspberry connectivity:

```bash
ping 192.168.178.29
```

Test the API:

```bash
curl http://192.168.178.29:30080/health
```

Expected response:

```json
{"status":"ok"}
```

---

# Project Structure

```text
bank-marketing-mlops/
├── .github/
│   └── workflows/
│       └── docker-build.yml
│
├── data/
│
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
│
├── metrics/
│   └── final_metrics.json
│
├── models/
│   └── model.joblib
│
├── notebooks/
│
├── src/
│   ├── api.py
│   ├── predict.py
│   └── train.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

# Training Workflow

```text
bank-additional-full.csv
        |
        v
    load_data()
        |
        v
   split_data()
        |
        v
  build_pipeline()
        |
        v
 categorical preprocessing
 numerical preprocessing
        |
        v
      XGBoost
        |
        v
   model.joblib
        |
        v
 final_metrics.json
```

Run training:

```bash
python src/train.py
```

---

# Inference Workflow

```text
Client
  |
  v
POST /predict
  |
  v
FastAPI
  |
  v
Pydantic validation
  |
  v
pandas DataFrame
  |
  v
scikit-learn Pipeline
  |
  +--> OneHotEncoder
  |
  +--> StandardScaler
  |
  +--> XGBoost
  |
  v
Prediction + probability
```

---

# Development Workflow

Normal development process:

```bash
git status
git add .
git commit -m "Describe the change"
git push
```

After:

```bash
git push
```

GitHub Actions automatically performs the remaining deployment steps.

```text
push
→ build
→ GHCR
→ Raspberry runner
→ Kubernetes rollout
→ updated API
```

---

# Troubleshooting

## API not reachable

Check Pod:

```bash
sudo k3s kubectl get pods
```

Check service:

```bash
sudo k3s kubectl get svc bank-marketing-api
```

Test:

```bash
curl http://192.168.178.29:30080/health
```

---

## Pod stuck in ContainerCreating

```bash
sudo k3s kubectl describe pod -l app=bank-marketing-api
```

Then:

```bash
sudo k3s kubectl get events --sort-by=.lastTimestamp
```

---

## Pod crashes

```bash
sudo k3s kubectl logs -l app=bank-marketing-api
```

---

## k3s not working

```bash
sudo systemctl status k3s
```

Then:

```bash
sudo journalctl -u k3s -n 100 --no-pager
```

---

## GitHub deployment does not start

Check the self-hosted runner:

```bash
cd ~/actions-runner
sudo ./svc.sh status
```

Check that the runner appears online in:

```text
GitHub repository
→ Settings
→ Actions
→ Runners
```

Runner labels must match the workflow:

```text
self-hosted
Linux
ARM64
```

---

# Current Status

Implemented:

- UCI Bank Marketing dataset
- data preprocessing
- leakage-aware feature selection
- XGBoost classification model
- scikit-learn preprocessing pipeline
- model serialization
- evaluation metrics
- FastAPI REST API
- Pydantic request validation
- Swagger UI
- Docker container
- multi-architecture Docker build
- `linux/amd64` support
- `linux/arm64` support
- GitHub Actions
- GitHub Container Registry
- Raspberry Pi deployment
- k3s Kubernetes cluster
- Kubernetes Deployment
- Kubernetes NodePort Service
- local network API access
- GitHub Actions self-hosted ARM64 runner
- automatic Kubernetes rollout after successful image build

---

# Possible Future Improvements

Possible extensions:

- automated unit and API tests
- Kubernetes liveness probe
- Kubernetes readiness probe
- CPU and memory requests
- CPU and memory limits
- model monitoring
- prediction monitoring
- MLflow experiment tracking
- model versioning
- structured application logging
- Prometheus metrics
- Grafana dashboard
- Kubernetes Ingress
- HTTPS
- domain name
- GitOps using Argo CD or Flux
- Terraform
- deployment to Azure Kubernetes Service or another managed Kubernetes platform

---

# Summary

This project demonstrates the complete path from a machine learning experiment to a running production-style service:

```text
Machine Learning
      +
FastAPI
      +
Docker
      +
GitHub Actions
      +
Container Registry
      +
Kubernetes
      +
Raspberry Pi
      +
CI/CD
```

A source-code change pushed to GitHub can automatically become a new version of the machine learning API running inside Kubernetes on the Raspberry Pi.