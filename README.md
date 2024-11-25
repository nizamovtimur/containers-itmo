# Лабораторные работы по курсу ИТМО "Контейнеризация и оркестрация приложений"

[[notion](https://jasper-cause-ce0.notion.site/3b2e4b7180954cbbad6c0449db638d6b)]

Выполнили: Неронов Роман, Низамов Тимур — AI Talent Hub

## Лабораторные работы
 - [Лабораторная работа 1](https://github.com/nizamovtimur/containers-itmo/tree/lab1)
 - [Лабораторная работа 2](https://github.com/nizamovtimur/containers-itmo/tree/lab2)
 - [Лабораторная работа 3](https://github.com/nizamovtimur/containers-itmo/tree/lab3)
 - [Лабораторная работа 4](https://github.com/nizamovtimur/containers-itmo/tree/lab4)

## Описание тестового приложения

Чат-бот ИИ-персоны "Аристотель", который отвечает на вопросы по книге "Метафизика" и состоит из сервисов:

 - db: база данных PostgreSQL с расширением PGVector
 - db-migrate: выполнение миграций в среде python с помощью alembic
 - chatbot: обработчики событий чат-бота Telegram
 - qa: микросервис RAG-системы для ответов на вопросы по книге Аристотеля "Метафизика"
