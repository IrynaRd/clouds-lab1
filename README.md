# Flask REST API (imdb)

## Опис застосунку

REST API застосунок для роботи з фільмами та користувачами на Flask із базою даних MySQL.

- **Swagger UI** — `http://app-load-balancer-105476553.eu-central-1.elb.amazonaws.com/apidocs`

## Публічна адреса

`http://app-load-balancer-105476553.eu-central-1.elb.amazonaws.com`

## Структура проєкту

```text
databases-labs/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── my_project/
│   ├── controller/
│   │   ├── film_controller.py
│   │   ├── user_controller.py
│   │   ├── review_controller.py
│   │   └── procedure_controller.py
│   ├── dao/
│   │   ├── film_dao.py
│   │   ├── user_dao.py
│   │   ├── review_dao.py
│   │   └── procedure_dao.py
│   ├── domain/
│   │   ├── models.py
│   │   └── schemas.py
│   ├── service/
│   │   ├── film_service.py
│   │   ├── user_service.py
│   │   ├── review_service.py
│   │   └── procedure_service.py
│   ├── database.py
│   └── queries_for_postman.md
├── terraform/
│   ├── providers.tf
│   ├── vars.tf
│   ├── network.tf
│   ├── security.tf
│   ├── ecr.tf
│   ├── ecs.tf
│   ├── alb.tf
│   ├── rds.tf
│   ├── iam.tf
│   ├── oidc.tf
│   ├── logs.tf
│   └── outputs.tf
├── app.py
├── init.sql
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .env
├── .gitignore
├── .dockerignore
└── README.md
```