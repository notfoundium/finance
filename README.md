
# Finance project

Для работы docker compose необходимо, чтобы были созданы следующие конфиг файлы:

Содержимое конфига */etc/finance.env*:

DATABASE_URL=postgresql+psycopg2://{username}:{password}@finance_db:5432/postgres
DATABASE_URL_ASYNC=postgresql+asyncpg://{username}:{password}@finance_db:5432/postgres
RABBITMQ_DEFAULT_USER={username}
RABBITMQ_DEFAULT_PASS={password}
RABBITMQ_DEFAULT_VHOST=financevhost

Содержимое конфига */etc/finance_db.env*

POSTGRES_USER={username}
POSTGRES_PASSWORD={password}
POSTGRES_DB=postgres

Конфиг finance_prometheus.yml поместить в директорию /etc

Для корректной работы также необходимо вручную добавить директории

/data/finance_grafana_data
/data/finance_prometheus_data

# Техническое задание к проекту

**Реализовать сервис, через который можно получать курсы валютных пар с биржи**

Необходимо, чтобы сервис возвращал курсы по следующим валютным парам:
BTC-to-[RUB|USD]
ETH-to-[RUB|USD]
USDTTRC-to-[RUB|USD]
USDTERC-to-[RUB|USD]

**Требования:**
- FastAPI в качестве фреймворка и ассинхронная имплементация сервиса
- Использование очередей (RMQ, ZeroMQ, etc)
- Сервис может обработать до 1500 запросов в ед. времени
- Обновление курсов происходит не дольше чем раз в 5 секунд
- Сервис работает отказаустойчиво (если одна из бирж перестаёт возвращать курсы, то сервис продолжает работать по другой)
- Уровни логирования должны быть разделены на CRITICAL, ERROR, WARNING, INFO, DEBUG 
- Курсы необходимо получать c Binance, либо c coingeko. Разработанный API сервис при GET запросе на /courses c опциональными query параметрами, должен возвращать ответ формата 
```
  {
    "exchanger": "binance", 
    "courses": [
      {
        "direction": "BTC-USD",
        "value": 54000.000123
      }
    ]
  }
```
- Работа с биржей происходит по websocket’ам, если биржа это поддерживает
- Нагрузочное тестирование реализовать через locust. Скрины прикрепить в readme
- Необходимо реализовать версионирование API

**Сдача проекта:**
- Опубликовать проект необходимо в github
- Проект должен быть собран в docker контейнеры и в docker-compose файл. Для запуска проекта должно быть достаточно набрать команду `docker compose up --build`
- README заполнить информацией по запуску, заполнению секретов и прикрепить отчет о тестировании

**Будет плюсом:**
- Использование reverse proxy в качестве балансировщика запросов
- Использование postgres с автоматическим накатываением миграций
- Использование одного из популярных инструментов для кэширования
- FastAPI в качестве фреймворка и ассинхронная имплементация сервиса
- Использование метрик (grafana, kuma, etc)