import logging
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from yandex_chain import YandexLLM
from config import Config

llm = YandexLLM(
    folder_id=Config.YANDEX_FOLDER_ID,
    api_key=Config.YANDEX_API_KEY,
    use_lite=False,
)
prompt_template = """Действуйте как инновационный виртуальный помощник студента Вопрошалыч.
Используйте следующие фрагменты из базы знаний в тройных кавычках, чтобы кратко ответить на вопрос студента.
Фрагменты разделены 5 знаками "равно": =====. Фрагменты, найденные в базе знаний:
\"\"\"
{context}
\"\"\"

Вопрос студента: {question}
"""
prompt = PromptTemplate.from_template(prompt_template)
chain = prompt | llm


def get_answer(context: str, question: str) -> str:
    """Возвращает сгенерированный LLM ответ на вопрос пользователя
    по заданному фрагменту в соответствии с промтом

    Args:
        context (str): текст документа (или фрагмента документа)
        question (str): вопрос пользователя

    Returns:
        str: ответ на вопрос
    """

    query = {"context": context, "question": question}
    try:
        answer = chain.invoke(query)
        if isinstance(answer, AIMessage):
            answer = answer.content
        return str(answer).replace('"""', "").strip()
    except Exception as e:
        logging.error(e)
        return ""
