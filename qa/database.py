import logging
from typing import Iterable
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.sqlalchemy import Vector
import requests
from sqlalchemy import Engine, Text, Column, DateTime, func, select
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column
from yandex_chain import YandexEmbeddings
from config import Config


Base = declarative_base()
yandex_embeddings = YandexEmbeddings(
    api_key=Config.YANDEX_API_KEY,
    folder_id=Config.YANDEX_FOLDER_ID,
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4444,
    chunk_overlap=444,
    length_function=len,
    is_separator_regex=False,
)


class Chunk(Base):
    """Фрагмент документа из вики-системы

    Args:
        text (str): текст фрагмента
        embedding (Vector): векторное представление текста фрагмента размерностью 256
        created_at (datetime): время создания
        updated_at (datetime): время обновления
    """

    __tablename__ = "chunk"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text())
    embedding: Mapped[Vector] = mapped_column(Vector(256))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def add_chunks(engine: Engine):
    """Пересоздаёт векторный индекс текстов для ответов на вопросы.
    При этом обрабатываются страницы, не имеющие вложенных страниц.

    Args:
        engine (Engine): экземпляр подключения к БД
    """

    logging.warning("START CREATE INDEX")
    response = requests.get(Config.TEXT_SOURCE_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        parsed_text = soup.get_text()
    else:
        logging.error(
            f"Parsing text from {Config.TEXT_SOURCE_URL} was not successful: HTTP STATUS CODE {response.status_code}"
        )
        raise
    documents = [Document(page_content=parsed_text)]
    all_splits = text_splitter.split_documents(documents)
    with Session(engine) as session:
        session.query(Chunk).delete()
        for chunk in all_splits:
            session.add(
                Chunk(
                    text=chunk.page_content,
                    embedding=yandex_embeddings.embed_document(chunk.page_content),
                )
            )
        session.commit()
    logging.warning("INDEX CREATED")


def get_chunks(engine: Engine, question: str) -> Iterable[str]:
    """Возвращает ближайший к вопросу фрагмент документа Chunk из векторной базы данных

    Args:
        engine (Engine): экземпляр подключения к БД
        question (str): вопрос пользователя

    Returns:
        Iterable[str]: список текстов трёх ближайших к вопросу фрагментов
    """

    with Session(engine) as session:
        return session.scalars(
            select(Chunk.text)
            .order_by(
                Chunk.embedding.cosine_distance(yandex_embeddings.embed_query(question))
            )
            .limit(3)
        ).all()
