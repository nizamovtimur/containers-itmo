# containers-itmo/qa/database.py
import logging
from typing import List
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
import requests
from config import Config

from yandex_chain import YandexEmbeddings
from sentence_transformers import SentenceTransformer

class Chunk:
    """Фрагмент документа из вики-системы

    Args:
        text (str): текст фрагмента
        embedding (List[float]): векторное представление текста фрагмента
    """
    def __init__(self, text: str, embedding: List[float]):
        self.text = text
        self.embedding = embedding

class LocalEmbeddings:
    """Класс для локальных эмбеддингов с использованием sentence-transformers."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_document(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(query).tolist()

# Глобальный список для хранения фрагментов
chunks: List[Chunk] = []

# Инициализация эмбеддингового провайдера
if Config.YANDEX_API_KEY and Config.YANDEX_FOLDER_ID:
    embeddings = YandexEmbeddings(
        api_key=Config.YANDEX_API_KEY,
        folder_id=Config.YANDEX_FOLDER_ID,
    )
    logging.info("Используется YandexEmbeddings для эмбеддингов.")
else:
    embeddings = LocalEmbeddings()
    logging.info("Используется LocalEmbeddings для эмбеддингов.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4444,  # Унифицированное значение
    chunk_overlap=444,  # Унифицированное значение
    length_function=len,
    is_separator_regex=False,
)

def add_chunks():
    """Заполняет глобальный список chunks фрагментами документа."""
    logging.warning("START CREATE INDEX")
    response = requests.get(Config.TEXT_SOURCE_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        parsed_text = soup.get_text()
    else:
        logging.error(
            f"Parsing text from {Config.TEXT_SOURCE_URL} был неуспешным: HTTP STATUS CODE {response.status_code}"
        )
        raise Exception("Не удалось получить текстовый источник.")
    documents = [Document(page_content=parsed_text)]
    all_splits = text_splitter.split_documents(documents)
    for chunk in all_splits:
        embedding = embeddings.embed_document(chunk.page_content)
        if embedding:
            chunks.append(Chunk(text=chunk.page_content, embedding=embedding))
    logging.warning("INDEX CREATED")

def get_chunks(question: str) -> List[str]:
    """Возвращает ближайшие к вопросу фрагменты документа.

    Args:
        question (str): вопрос пользователя

    Returns:
        List[str]: список текстов трёх ближайших к вопросу фрагментов
    """
    question_embedding = embeddings.embed_query(question)
    if not question_embedding:
        return []
    similarities = []
    for chunk in chunks:
        sim = cosine_similarity(
            [question_embedding],
            [chunk.embedding]
        )[0][0]
        similarities.append((sim, chunk.text))
    # Сортируем по убыванию похожести и берем top 3
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [text for _, text in similarities[:3]]
    return top_chunks