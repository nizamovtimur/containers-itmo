# containers-itmo/qa/main.py
import json
import logging
from aiohttp import web
from database import add_chunks, get_chunks
from llm_prompting import get_answer

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
# Обработчик для записи в файл
file_handler = logging.FileHandler('/app/logs/qa.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


routes = web.RouteTableDef()

@routes.post("/qa/")
async def qa(request: web.Request) -> web.Response:
    """Возвращает ответ на вопрос пользователя или найденные фрагменты."""
    try:
        data = await request.json()
        question = data.get("question", "")
    except Exception as e:
        logging.error(f"Bad Request: {e}")
        return web.Response(
            text=f"Bad Request: Отсутствует вопрос в запросе! Подробнее: {e}",
            status=400,
            content_type='text/plain; charset=utf-8'
        )

    if len(question) < 3:
        logging.warning("Вопрос слишком короткий.")
        return web.Response(
            text="Bad Request: Вопрос слишком короткий!",
            status=400,
            content_type='text/plain; charset=utf-8'
        )

    # Получаем ближайшие фрагменты
    chunks = get_chunks(question)
    if not chunks:
        # Если подходящих фрагментов не найдено
        return web.Response(
            text="Ответ не найден",
            status=404,
            content_type='text/plain; charset=utf-8'
        )

    # Получаем ответ от LLM или возвращаем найденные фрагменты
    answer = get_answer("\n=====\n".join(chunks), question)

    if not answer:
        return web.Response(
            text="Ответ не найден",
            status=404,
            content_type='text/plain; charset=utf-8'
        )

    return web.json_response(
        {"answer": answer},
        dumps=lambda x: json.dumps(x, ensure_ascii=False)
    )

@routes.get("/health")
async def health(request: web.Request) -> web.Response:
    """Эндпоинт для проверки состояния приложения."""
    return web.Response(
        text="OK",
        status=200,
        content_type='text/plain',
        charset='utf-8'
    )

if __name__ == "__main__":
    try:
        add_chunks()
    except Exception as e:
        logging.error(f"Error during add_chunks: {e}")
    logging.info("Starting QA Service")
    app = web.Application()
    app.add_routes(routes)
    try:
        web.run_app(app, port=8080)
    except Exception as e:
        logging.error(f"Error while running app: {e}")