# template-devops-project
Full DevOps Service in 1 Project


Проект для определения универсального DevOps сервиса.

В качестве app будет приложение-соцсеть. В принципе можно использвоать любое приложение.

## Структура

```
.
├── app/
│   └── main.py
├── docker/
│   └── Dockerfile
├── k8s/
│   └── deployment.yaml
├── terraform/
│   └── main.tf
├── monitoring/
│   └── prometheus.yml
├── ci/
│   └── pipeline.yml
└── README.md
```

## Архитектура

Проект реализован как шаблон DevOps-проекта с контейнеризированным приложением и базовой инфраструктурой для развертывания:

- Приложение находится в директории `app/` и запускается как Python-скрипт.
- Docker-контейнер описан в `docker/Dockerfile` для упаковки приложения.
- Kubernetes-манифест в `k8s/` предназначен для деплоя контейнера в кластер.
- Terraform-шаблоны в `terraform/` используются для инфраструктурного provisioning.
- CI/CD-пайплайн в `ci/pipeline.yml` описывает сборку, тестирование и деплой.
- Мониторинг настроен через `monitoring/` с примером Prometheus.

## Технологический стек

- Python 3.11
- Docker
- Kubernetes
- Terraform
- Azure DevOps Pipelines (YAML)
- Prometheus
- Git

## Быстрый старт

### Локальный запуск

```bash
python app/main.py
```

### Сборка Docker-образа

```bash
docker build -t template-devops-project -f docker/Dockerfile .
```

### Запуск контейнера

```bash
docker run --rm -p 8080:8080 template-devops-project
```

### Доступные HTTP endpoint

- `GET /` — базовый ответ сервиса
- `GET /health` — проверка живости/готовности
- `GET /load` — создает CPU-нагрузку на несколько секунд

### Примеры проверки

```bash
curl -i http://localhost:8080/
curl -i http://localhost:8080/health
curl -i http://localhost:8080/load
```

### Логирование

Приложение логирует каждый входящий запрос в `stdout`.

Если приложение запущено в контейнере, логи можно смотреть через:

```bash
docker logs <container-id>
```

