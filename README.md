# Bank Marketing MLOps

End-to-end machine learning deployment project based on the UCI Bank Marketing dataset.

The project covers the complete path from model development to automated deployment:

```text
data
→ preprocessing
→ model training
→ automated tests
→ FastAPI
→ Docker
→ GitHub Actions
→ GitHub Container Registry
→ Kubernetes / k3s
→ Raspberry Pi
```

The objective is not only to train a machine learning model, but to build and deploy a small production-style ML service.

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

GitHub Actions workflow:

```text
.github/workflows/docker-build.yml
```

---

## Docker Image

Production image:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

Supported architectures:

```text
linux/amd64
linux/arm64
```

The ARM64 image is used by the Raspberry Pi.

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

SSH:

```bash
ssh peppe@raspberrypi.local
```

or:

```bash
ssh peppe@192.168.178.29
```

Check current IP:

```bash
hostname -I
```

The IP is currently referenced by the k3s configuration. A DHCP reservation on the router is recommended so that it does not change.

---

## FastAPI

Base URL:

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

The `/` endpoint is not implemented.

Therefore:

```text
http://192.168.178.29:30080/
```

returns:

```text
404 Not Found
```

This is expected.

---

## Headlamp Kubernetes UI

Headlamp:

```text
http://192.168.178.29:30081
```

Headlamp is used to inspect the Kubernetes cluster graphically.

Useful sections:

```text
Workloads → Deployments
Workloads → Pods
Network → Services
```

The application appears as:

```text
bank-marketing-api
```

Generate a Headlamp login token:

```bash
sudo k3s kubectl create token headlamp-admin -n kube-system
```

The Headlamp admin account currently has cluster-admin privileges. The Headlamp NodePort should not be exposed directly to the public Internet.

---

# Goal

Predict whether a bank customer will subscribe to a term deposit using information available before the marketing call has completed.

The project emphasizes deployment engineering and MLOps concepts rather than maximizing predictive performance.

---

# Dataset

The project uses the UCI Bank Marketing dataset.

Target:

```text
1 = customer subscribes to a term deposit
0 = customer does not subscribe
```

The original dataset contains information about bank marketing campaigns.

The feature:

```text
duration
```

is deliberately excluded.

Call duration is only known after the call has taken place. Using it in a model intended to make a prediction before the call would introduce future information and therefore data leakage.

Values such as:

```text
unknown
```

are retained as explicit categorical values.

---

# Machine Learning Pipeline

The model is an XGBoost classifier.

Preprocessing and prediction are combined into a scikit-learn `Pipeline`.

Categorical variables use:

```text
OneHotEncoder(handle_unknown="ignore")
```

Numerical variables use:

```text
StandardScaler
```

The classifier is:

```text
XGBClassifier
```

The complete preprocessing + model pipeline is serialized as:

```text
models/model.joblib
```

This ensures that the exact same preprocessing is used during both training and inference.

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

Because the dataset is imbalanced, ROC AUC and PR AUC are more informative than accuracy alone.

Metrics are stored in:

```text
metrics/final_metrics.json
```

---

# Training

Training code:

```text
src/train.py
```

Run:

```bash
python src/train.py
```

Training workflow:

```text
UCI dataset
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
OneHotEncoder + StandardScaler
    |
    v
XGBoost
    |
    +----------------------+
    |                      |
    v                      v
model.joblib       final_metrics.json
```

---

# Prediction Smoke Test

A simple standalone prediction script is available at:

```text
src/predict.py
```

It loads:

```text
models/model.joblib
```

and performs one test prediction.

Run:

```bash
python src/predict.py
```

This is a simple smoke test and is separate from the production FastAPI service.

---

# FastAPI

API code:

```text
src/api.py
```

Available endpoints:

```text
GET  /health
POST /predict
GET  /docs
GET  /openapi.json
```

Run locally:

```bash
uvicorn src.api:app --reload
```

Local base URL:

```text
http://127.0.0.1:8000
```

Local Swagger:

```text
http://127.0.0.1:8000/docs
```

Local health endpoint:

```text
http://127.0.0.1:8000/health
```

Example:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

---

# Automated Tests

Minimal automated API tests are stored in:

```text
tests/test_api.py
```

The test suite currently verifies three things.

## Health test

Checks:

```text
GET /health
```

Expected:

```text
HTTP 200
{"status":"ok"}
```

## Prediction test

Sends a valid customer to:

```text
POST /predict
```

and verifies:

```text
HTTP 200
prediction is 0 or 1
probability is between 0 and 1
```

This acts as a small integration test because it exercises:

```text
FastAPI
→ Pydantic
→ pandas
→ preprocessing pipeline
→ XGBoost
```

## Validation test

Sends an incomplete request to:

```text
POST /predict
```

and verifies:

```text
HTTP 422
```

Run tests locally from the repository root:

```bash
python -m pytest -v
```

Expected:

```text
3 passed
```

`python -m pytest` is used instead of invoking `pytest` directly so that the project root is correctly available on the Python import path.

---

# Docker

Dockerfile:

```text
Dockerfile
```

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

Health test:

```bash
curl http://localhost:8000/health
```

---

# Multi-Architecture Docker Build

The GitHub Actions workflow builds the image for:

```text
linux/amd64
linux/arm64
```

This allows the same repository to produce an image that works both on conventional x86 machines and on the ARM64 Raspberry Pi.

GitHub Actions uses:

```text
QEMU
Docker Buildx
```

for the multi-platform build.

The resulting image is pushed to:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

---

# CI/CD Pipeline

Every push to:

```text
master
```

starts the CI/CD pipeline.

The complete workflow is:

```text
git push
    |
    v
+----------------------+
|       TEST JOB       |
+----------------------+
    |
    v
Checkout repository
    |
    v
Set up Python 3.12
    |
    v
Install dependencies
    |
    v
python -m pytest -v
    |
    v
3 tests pass
    |
    v
+----------------------+
|      BUILD JOB       |
+----------------------+
    |
    v
Set up QEMU
    |
    v
Set up Docker Buildx
    |
    v
Build linux/amd64
Build linux/arm64
    |
    v
Push image to GHCR
    |
    v
+----------------------+
|      DEPLOY JOB      |
+----------------------+
    |
    v
Self-hosted GitHub runner
on Raspberry Pi
    |
    v
kubectl rollout restart
    |
    v
k3s creates new Pod
    |
    v
Pod pulls latest image
    |
    v
Old Pod removed
    |
    v
New FastAPI version running
```

The jobs depend on each other:

```text
test
 ↓
build
 ↓
deploy
```

Therefore, if the tests fail:

```text
test ✗
→ build skipped
→ deploy skipped
```

A broken application is not automatically deployed.

---

# GitHub Actions Self-Hosted Runner

The Raspberry Pi is registered as a GitHub Actions self-hosted runner.

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

The runner is installed as a system service.

This means it continues listening for GitHub jobs after SSH logout and automatically starts after reboot.

Check status:

```bash
cd ~/actions-runner
sudo ./svc.sh status
```

Start:

```bash
cd ~/actions-runner
sudo ./svc.sh start
```

Stop:

```bash
cd ~/actions-runner
sudo ./svc.sh stop
```

Restart:

```bash
cd ~/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

Run manually in foreground:

```bash
cd ~/actions-runner
./run.sh
```

`./run.sh` stops when the terminal session is closed, so the system service should normally be used.

---

# Runner sudo Permission

The GitHub Actions runner must be able to run k3s without being prompted for a password.

sudoers configuration:

```text
/etc/sudoers.d/github-runner-k3s
```

Configuration:

```text
peppe ALL=(root) NOPASSWD: /usr/local/bin/k3s
```

Validate:

```bash
sudo visudo -cf /etc/sudoers.d/github-runner-k3s
```

Expected:

```text
parsed OK
```

Test non-interactive sudo:

```bash
sudo -n k3s kubectl get nodes
```

This is necessary because GitHub Actions jobs do not have an interactive terminal in which to enter a sudo password.

---

# Automated Deployment

After the Docker image has been successfully pushed to GHCR, the deployment job runs on the Raspberry Pi.

Restart:

```bash
sudo k3s kubectl rollout restart deployment/bank-marketing-api
```

Wait for completion:

```bash
sudo k3s kubectl rollout status deployment/bank-marketing-api --timeout=600s
```

The 600-second timeout is used because downloading and starting the ARM64 Docker image on the Raspberry Pi can take several minutes.

Normal development flow:

```text
edit code
→ test locally
→ git add
→ git commit
→ git push
→ GitHub tests
→ GitHub builds image
→ GHCR updated
→ Raspberry deploy job
→ Kubernetes rollout
→ new API version running
```

---

# Kubernetes

The Raspberry Pi runs:

```text
k3s
```

k3s is a lightweight Kubernetes distribution.

Check node:

```bash
sudo k3s kubectl get nodes
```

Expected:

```text
raspberrypi   Ready
```

---

# Kubernetes Deployment

Deployment manifest:

```text
k8s/deployment.yaml
```

Raw GitHub URL:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml
```

Deployment name:

```text
bank-marketing-api
```

Replicas:

```text
1
```

Image:

```text
ghcr.io/peppescavo/bank-marketing-mlops:latest
```

Container port:

```text
8000
```

Apply manually:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml
```

---

# Kubernetes Service

Service manifest:

```text
k8s/service.yaml
```

Raw GitHub URL:

```text
https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

Service:

```text
bank-marketing-api
```

Type:

```text
NodePort
```

Service port:

```text
80
```

Target container port:

```text
8000
```

NodePort:

```text
30080
```

Therefore:

```text
192.168.178.29:30080
```

routes traffic to FastAPI on:

```text
container port 8000
```

Apply manually:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

---

# First Kubernetes Deployment

If the Kubernetes resources do not exist:

```bash
sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/deployment.yaml

sudo k3s kubectl apply -f https://raw.githubusercontent.com/peppescavo/bank-marketing-mlops/master/k8s/service.yaml
```

Then verify:

```bash
sudo k3s kubectl get deployments
sudo k3s kubectl get pods
sudo k3s kubectl get services
```

After the first deployment, application updates are normally handled by GitHub Actions.

---

# Kubernetes Rolling Update

During an update Kubernetes may temporarily show two Pods:

```text
old Pod   Running
new Pod   ContainerCreating
```

When the new Pod is ready:

```text
new Pod   Running
old Pod   Terminating
```

Finally only the new Pod remains.

This behavior allows Kubernetes to replace the application without intentionally stopping the old instance before the new one is created.

---

# Useful Kubernetes Commands

Nodes:

```bash
sudo k3s kubectl get nodes
```

Pods:

```bash
sudo k3s kubectl get pods
```

Detailed Pods:

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

Describe application Pod:

```bash
sudo k3s kubectl describe pod -l app=bank-marketing-api
```

Application logs:

```bash
sudo k3s kubectl logs -l app=bank-marketing-api
```

Follow logs:

```bash
sudo k3s kubectl logs -f -l app=bank-marketing-api
```

Recent events:

```bash
sudo k3s kubectl get events --sort-by=.lastTimestamp
```

Restart deployment:

```bash
sudo k3s kubectl rollout restart deployment/bank-marketing-api
```

Wait for rollout:

```bash
sudo k3s kubectl rollout status deployment/bank-marketing-api --timeout=600s
```

Rollout history:

```bash
sudo k3s kubectl rollout history deployment/bank-marketing-api
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

Primary interface:

```text
wlan0
```

Current node IP:

```text
192.168.178.29
```

`disable-network-policy: true` is currently used as a workaround for the networking problem encountered with the k3s network policy controller on this Raspberry Pi setup.

Because the node IP is explicitly configured, the Raspberry Pi should retain the same LAN address.

---

# k3s Administration

Status:

```bash
sudo systemctl status k3s
```

Restart:

```bash
sudo systemctl restart k3s
```

Start:

```bash
sudo systemctl start k3s
```

Stop:

```bash
sudo systemctl stop k3s
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

# Headlamp

Headlamp provides a graphical interface for the k3s cluster.

URL:

```text
http://192.168.178.29:30081
```

Main application locations:

```text
Workloads
→ Deployments
→ bank-marketing-api
```

and:

```text
Workloads
→ Pods
```

Network configuration:

```text
Network
→ Services
→ bank-marketing-api
```

The service should show:

```text
Type: NodePort
Port: 80
TargetPort: 8000
NodePort: 30080
```

Generate Headlamp admin token:

```bash
sudo k3s kubectl create token headlamp-admin -n kube-system
```

---

# Network

Show interfaces:

```bash
ip -br addr
```

Current primary interface:

```text
wlan0
```

Current Raspberry Pi IPv4:

```text
192.168.178.29
```

Ping:

```bash
ping 192.168.178.29
```

Test API:

```bash
curl http://192.168.178.29:30080/health
```

Expected:

```json
{"status":"ok"}
```

Swagger:

```text
http://192.168.178.29:30080/docs
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
│   └── bank_marketing/
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
│   ├── __init__.py
│   ├── api.py
│   ├── predict.py
│   └── train.py
│
├── tests/
│   └── test_api.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

# Development Workflow

Typical development cycle:

```bash
git status
```

Run tests:

```bash
python -m pytest -v
```

Then:

```bash
git add .
git commit -m "Describe the change"
git push
```

After `git push`, no manual deployment should normally be necessary.

GitHub Actions handles:

```text
test
→ build
→ registry
→ deployment
```

---

# Troubleshooting

## Tests fail

Run locally:

```bash
python -m pytest -v
```

If the tests fail in GitHub Actions, the Docker build and deployment should not start.

---

## API unavailable

Check Pods:

```bash
sudo k3s kubectl get pods
```

Check Service:

```bash
sudo k3s kubectl get svc bank-marketing-api
```

Test:

```bash
curl http://192.168.178.29:30080/health
```

---

## Pod stuck in ContainerCreating

Run:

```bash
sudo k3s kubectl describe pod -l app=bank-marketing-api
```

and:

```bash
sudo k3s kubectl get events --sort-by=.lastTimestamp
```

The Docker image is relatively large, so pulling it on the Raspberry Pi can take several minutes.

---

## Pod crashes

Check logs:

```bash
sudo k3s kubectl logs -l app=bank-marketing-api
```

---

## Deployment job fails with sudo error

Typical error:

```text
sudo: a terminal is required to read the password
sudo: a password is required
```

Check:

```bash
sudo -n k3s kubectl get nodes
```

If this fails, inspect:

```text
/etc/sudoers.d/github-runner-k3s
```

Expected rule:

```text
peppe ALL=(root) NOPASSWD: /usr/local/bin/k3s
```

---

## Deployment times out

Check Pods:

```bash
sudo k3s kubectl get pods
```

Check events:

```bash
sudo k3s kubectl get events --sort-by=.lastTimestamp
```

The CI deployment currently allows:

```text
600 seconds
```

for the Kubernetes rollout.

---

## GitHub runner offline

Check:

```bash
cd ~/actions-runner
sudo ./svc.sh status
```

GitHub location:

```text
Repository
→ Settings
→ Actions
→ Runners
```

Expected runner:

```text
raspberrypi
```

Expected labels:

```text
self-hosted
Linux
ARM64
```

---

## k3s unavailable

Check:

```bash
sudo systemctl status k3s
```

Logs:

```bash
sudo journalctl -u k3s -n 100 --no-pager
```

---

# Current Status

Implemented:

- data ingestion
- train/test split
- leakage-aware feature selection
- categorical preprocessing
- numerical preprocessing
- XGBoost classifier
- scikit-learn Pipeline
- model serialization
- evaluation metrics
- FastAPI REST API
- Pydantic validation
- Swagger UI
- Docker container
- multi-architecture Docker build
- AMD64 support
- ARM64 support
- GitHub Actions
- GitHub Container Registry
- automated API tests
- CI test gate
- Raspberry Pi self-hosted GitHub runner
- k3s Kubernetes cluster
- Kubernetes Deployment
- Kubernetes NodePort Service
- automatic deployment
- Kubernetes rolling update
- Headlamp Kubernetes UI
- API accessible from the local network

---

# Possible Future Improvements

Possible extensions include:

- Kubernetes liveness probe
- Kubernetes readiness probe
- CPU requests
- memory requests
- CPU limits
- memory limits
- versioned Docker image tags instead of only `latest`
- automatic rollback
- model versioning
- MLflow
- prediction monitoring
- model drift monitoring
- structured logging
- Prometheus
- Grafana
- Kubernetes Ingress
- HTTPS
- DNS/domain name
- GitOps with Argo CD or Flux
- Terraform
- managed Kubernetes deployment in Azure, AWS or GCP

These are extensions rather than requirements for the current project.

---

# Summary

The project demonstrates a complete small-scale MLOps deployment:

```text
Machine Learning
      |
      v
Automated Tests
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
Self-hosted Runner
      |
      v
Kubernetes / k3s
      |
      v
Raspberry Pi
      |
      v
REST API
```

A normal source-code change can follow this path automatically:

```text
git push
→ tests
→ Docker build
→ container registry
→ Kubernetes rollout
→ updated ML API
```

The project therefore covers both machine learning development and the main engineering components required to turn a trained model into a deployable service.