# Sentinel Monitor – API DevOps Lab

Projeto de laboratório DevOps que integra desenvolvimento de API, conteinerização, Kubernetes, infraestrutura como código e observabilidade.

## 📌 Visão geral

Este lab implementa o **Sentinel Monitor v1.0**, uma API em Flask que:

- Recebe métricas de servidores (CPU e RAM) via endpoint HTTP.
- Classifica automaticamente o estado em `NORMAL`, `WARNING` ou `CRITICAL`.
- Armazena os dados em um banco **PostgreSQL**.
- Expõe um endpoint de **alertas** com os últimos eventos fora do normal.

Em volta da API, o projeto pratica:

- **Docker / Docker Compose** para empacotar e subir API + banco.
- **Kubernetes** para Deployments e Services da API e do Postgres.
- **Terraform + kind + Helm** para criar um cluster Kubernetes local e instalar o stack de monitoramento (**Prometheus + Grafana**).

## 🧩 Arquitetura resumida

- `app.py`: API Flask (Sentinel Monitor) que recebe e consulta métricas.
- `docker-compose.yml`: sobe `minha-api` (Flask) e `db` (Postgres) em containers.
- `k8s-deployment.yaml`: Deployments + Services para API e banco no Kubernetes.
- `devops-terraform/main.tf`: cria um cluster kind e instala `kube-prometheus-stack` (Prometheus + Grafana) via Helm.

Fluxo principal:

1. Clientes enviam métricas para `POST /metrics` da API.
2. A API calcula o status (NORMAL/WARNING/CRITICAL) e grava em Postgres.
3. O endpoint `GET /alerts` retorna os últimos alertas (status != NORMAL).
4. A infra roda em containers (Docker) ou no cluster Kubernetes criado pelo Terraform.

## 🚀 Como rodar com Docker Compose

Pré‑requisitos:

- Docker instalado
- Docker Compose disponível no ambiente

Passos:

```bash
cd desafio-docker

docker-compose up -d
docker-compose ps
```

Endpoints principais (via Compose):

- API base: `http://localhost:8080/`
- Healthcheck: `http://localhost:8080/health`
- Envio de métricas: `POST http://localhost:8080/metrics`
- Listagem de alertas: `GET http://localhost:8080/alerts`

Exemplos de requisições:

```bash
curl -X POST http://localhost:8080/metrics \
  -H "Content-Type: application/json" \
  -d '{"hostname": "server-app-1", "cpu": 92, "ram": 80}'

curl -X POST http://localhost:8080/metrics \
  -H "Content-Type: application/json" \
  -d '{"hostname": "server-db-1", "cpu": 55, "ram": 90}'

curl http://localhost:8080/alerts
```

## ☸️ Como rodar no Kubernetes

Com um cluster Kubernetes já disponível (ex.: kind, minikube, k3d etc.):

```bash
cd desafio-docker

kubectl apply -f k8s-deployment.yaml

kubectl get pods
kubectl get svc
```

O manifesto cria:

- `Deployment postgres-db` + `Service db` (PostgreSQL).
- `Deployment sentinel-api` (API Flask).
- `Service sentinel-service` do tipo **NodePort** (porta 30000/tcp por padrão).

Para acessar a API no cluster (exemplos):

```bash
# Usando NodePort padrão 30000 em um nó local
curl http://localhost:30000/alerts

# Ou via port-forward
kubectl port-forward svc/sentinel-service 8081:80
curl http://localhost:8081/alerts
```

## 🛠️ Infraestrutura com Terraform, kind e Helm

Na pasta `devops-terraform/`:

- `terraform.tfstate`: estado do Terraform.
- `main.tf`: define:
  - Provider **kind** para criar um cluster Kubernetes local (`kind_cluster.meu_cluster`).
  - Provider **helm** apontando para esse cluster.
  - `helm_release.monitoramento` com o chart `kube-prometheus-stack`, que sobe Prometheus + Grafana no namespace `monitoring`.

Execução típica:

```bash
cd devops-terraform

terraform init
terraform apply
```

Isso irá:

1. Criar um cluster kind chamado `lab-devops-tf`.
2. Instalar o stack de monitoramento (Prometheus + Grafana) via Helm.

Depois do apply, o Grafana normalmente fica exposto via Service no namespace `monitoring`. Você pode obter a senha admin assim:

```bash
kubectl get secret --namespace monitoring stack-monitoramento-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

## 📡 Endpoints da API

- `GET /`  
  Retorna uma mensagem simples de versão do sistema (`Sentinel Monitor v1.0`).

- `GET /health`  
  Healthcheck da aplicação.

- `POST /metrics`  
  Corpo esperado (JSON):
  ```json
  {
    "hostname": "server-app-1",
    "cpu": 92,
    "ram": 80
  }
  ```
  A API grava a métrica em Postgres com o status calculado.

- `GET /alerts`  
  Retorna os últimos alertas (status diferente de NORMAL), ordenados por data de criação.

## 📚 Tecnologias utilizadas

- Python + Flask
- PostgreSQL
- Docker & Docker Compose
- Kubernetes (Deployments, Services, NodePort)
- Terraform
- kind (Kubernetes in Docker)
- Helm (kube-prometheus-stack)
- Prometheus & Grafana

## 💡 Ideias de evolução

- Expor métricas da própria API via Prometheus (endpoint `/metrics`).
- Criar dashboards dedicados no Grafana para os dados da tabela `server_metrics`.
- Adicionar autenticação/autorização na API.
- Criar pipeline CI/CD para build de imagem, testes e deploy automático no cluster.
