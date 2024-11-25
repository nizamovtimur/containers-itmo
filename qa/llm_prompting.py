# containers-itmo/qa/llm_prompting.py
import logging
from config import Config
from yandex_chain import YandexLLM

if Config.YANDEX_API_KEY and Config.YANDEX_FOLDER_ID:
    llm = YandexLLM(
        folder_id=Config.YANDEX_FOLDER_ID,
        api_key=Config.YANDEX_API_KEY,
        use_lite=False,
    )
    logging.info("Используется YandexLLM для генерации ответов.")
else:
    llm = None
    logging.info("YandexLLM не настроен. Будут возвращаться только найденные фрагменты.")

def get_answer(context: str, question: str) -> str:
    """Возвращает сгенерированный LLM ответ на вопрос пользователя
    по заданному фрагменту в соответствии с промптом или просто возвращает фрагменты.

    Args:
        context (str): текст документа (или фрагмента документа)
        question (str): вопрос пользователя

    Returns:
        str: ответ на вопрос или найденные фрагменты
    """
    if llm:
        query = {"context": context, "question": question}
        try:
            answer = llm.invoke(query)
            return answer
        except Exception as e:
            logging.error(e)
            return "Произошла ошибка при генерации ответа."
    else:
        # Возвращаем найденные фрагменты, если LLM не настроен
        return context