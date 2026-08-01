# MAIN-324 — Kubernetes: multi-node, Service/Ingress, liveness/readiness

**Статус:** Done
**Репозиторий:** https://github.com/trawwa/template-devops-project

## Цель задачи

Развернуть приложение в multi-node Kubernetes-кластере (minikube) с настроенными
Service, Ingress и liveness/readiness пробами, подтвердив каждый пункт
воспроизводимой командой и её выводом, а не описанием "на словах".

## Acceptance Criteria и подтверждение

| AC | Подтверждение |
|---|---|
| Кластер поднят как multi-node | `kubectl get nodes -o wide` — 2 ноды в статусе `Ready` |
| Приложение задеплоено на обе ноды | Поды `Running` без затяжных рестартов на control-plane и на второй ноде |
| Service (ClusterIP) настроен и работает | `kubectl port-forward svc/my-service` + `curl localhost:8080/health` → `{"status":"ok"}` |
| Ingress настроен и даёт доступ снаружи | Подтверждено двумя независимыми способами — см. раздел "Сетевая диагностика" ниже |
| Liveness probe реально перезапускает под при сбое | `kubectl describe pod` зафиксировал `Readiness probe failed` → `Liveness probe failed` (x7) → `Killing ... will be restarted`, `Restart Count: 2` |
| Readiness probe реально исключает под из Service при сбое | Зафиксировано в том же Events-логе, под ушёл из `Ready` до перезапуска |

## Ход работы и технические решения

### 1. Multi-node кластер
`minikube start --nodes 2` изначально дал зависшую вторую ноду (`NotReady`,
CNI не проинициализировался — кластер до этого 61 день жил как single-node).
Решение: `minikube delete` + чистый старт с нуля вместо реанимации.

### 2. Сборка и загрузка образа на multi-node
- `minikube image build` падал на попытке прочитать `venv/bin/python`
  (Windows не читает symlink из venv в build context) → добавлен `.dockerignore`.
- `ImagePullBackOff` на второй ноде — тег `:latest` по умолчанию имеет
  `imagePullPolicy: Always`, под пытался тянуть образ из внешнего реестра →
  `imagePullPolicy: Never` + `minikube image load`.
- `minikube docker-env` оказался официально несовместим с multi-node
  (`ENV_MULTINODE_CONFLICT`) → сборка на хосте (`docker build`) + `docker save`
  в tar + `minikube image load <tar>`.

### 3. Liveness/readiness — реальный тест сбоя
Первая попытка — `kubectl exec` + `kill -9 1` — не сработала: PID 1 в
контейнере без init-обвязки (tini/dumb-init) игнорирует сигналы, отправленные
изнутри своего PID-неймспейса, даже `SIGKILL`. Пересмотрен подход: программная
поломка `/health` через env-флаг `FAIL_HEALTH=true` в самом приложении.
После правки кэш Docker не сразу подхватил изменения — потребовалась смена
тега `:latest` → `:v2` для гарантированной пересборки слоя.

Финальный контролируемый тест дал полную ожидаемую цепочку в Events:
`Readiness probe failed` → `Liveness probe failed` (x7) → `Killing ... will be
restarted`, `Restart Count: 2`.

### 4. Сетевая диагностика Ingress (самая долгая часть)
Прямой `curl app.local/health` с хоста давал `Empty reply from server`, при
этом `/etc/hosts` и конфиг Ingress были валидны, а `nginx-controller`
подтверждал `Backend successfully reloaded`.

Диагностика по цепочке от простого к сложному:
1. `kubectl port-forward svc/my-service` + curl — сработал → Service→Pod здоровы.
2. `minikube tunnel` — не помог. Причина: `ingress-nginx-controller` — сервис
   типа `NodePort`, а не `LoadBalancer`, tunnel к нему не относится.
3. Прямой `curl` на `NodePort` с хоста — пусто, в том числе с корректным
   актуальным номером порта, полученным через `kubectl get svc ... jsonpath`.
4. `curl --resolve app.local:<NodePort>:<node-ip>` (эмуляция DNS без правки
   `hosts`) — тоже `Empty reply`, что окончательно исключило hosts-файл и DNS
   как причину.
5. `kubectl exec` в app-под + `wget` на IP пода ingress-controller **изнутри
   кластера** — сработал, вернул `{"status":"ok"}`. Это доказало, что вся
   цепочка Ingress→Service→Pod технически исправна.
6. `minikube service ingress-nginx-controller -n ingress-nginx --url` —
   поднял корректно проксируемый под Windows `localhost`-порт;
   `curl -H "Host: app.local" http://127.0.0.1:<PORT>/health` вернул
   `{"status":"ok"}`.

**Вывод:** проблема не в конфигурации Ingress/Service/приложения, а в
известном сетевом ограничении связки Windows + Docker Desktop + minikube
`docker` driver — прямой доступ с хоста к `NodePort` по IP ноды в этой
конфигурации не работает в принципе. Рабочий и подтверждённый обходной путь —
`minikube service <name> -n <ns> --url`.

## Итоговое состояние

- Все AC подтверждены воспроизводимыми командами и их фактическим выводом.
- Единственное известное ограничение (прямой хост→NodePort доступ на Windows)
  задокументировано, не является багом конфигурации и не блокирует задачу.
- Полный хронологический разбор всех технических граблей — в отдельном
  постмортеме `postmortem-main-324-multinode-debugging.md`.

## Что это дало

Помимо закрытия тикета — набор проверенных на практике, а не вычитанных в
туториале фактов: поведение PID 1 без init-обвязки при сигналах изнутри
неймспейса, официальная несовместимость `minikube docker-env` с multi-node,
привязка Docker layer cache к содержимому, а не к тегу, и сетевые особенности
NodePort на Windows+docker driver. Хороший материал для STAR-историй на
собеседовании (MAIN-440).
