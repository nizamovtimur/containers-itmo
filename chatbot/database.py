from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Engine,
    ForeignKey,
    Text,
    func,
    select,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


class User(Base):
    """Пользователь чат-бота

    Args:
        id (int): id пользователя
        telegram_id (int): id пользователя Telegram
        username (str): username пользователя Telegram
        question_answers (List[QuestionAnswer]): вопросы пользователя
        created_at (datetime): время создания
        updated_at (datetime): время обновления
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[int] = mapped_column(Text())

    question_answers: Mapped[List["QuestionAnswer"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(QuestionAnswer.created_at)",
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuestionAnswer(Base):
    """Вопрос пользователя с ответом на него

    Args:
        id (int): id ответа
        question (str): вопрос пользователя
        answer (str | None): ответ на вопрос пользователя
        score (int | None): оценка пользователем ответа
        user_id (int): id пользователя, задавшего вопрос
        user (User): пользователь, задавший вопрос
        created_at (datetime): время создания модели
        updated_at (datetime): время обновления модели
    """

    __tablename__ = "question_answer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text())
    answer: Mapped[Optional[str]] = mapped_column(Text())
    score: Mapped[Optional[int]] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="question_answers")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def add_user(engine: Engine, telegram_id: int, username: str) -> tuple[bool, int]:
    """Функция добавления в БД пользователя виртуального помощника

    Args:
        engine (Engine): подключение к БД
        telegram_id (int): id пользователя Telegram

    Returns:
        tuple[bool, int]: добавился пользователь или нет, какой у него id в БД
    """

    with Session(engine) as session:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            return True, user.id
        return False, user.id


def get_user_id(engine: Engine, telegram_id: int) -> int | None:
    """Функция получения из БД пользователя

    Args:
        engine (Engine): подключение к БД
        telegram_id (int): id пользователя Telegram

    Returns:
        int | None: id пользователя или None
    """

    with Session(engine) as session:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            return None
        return user.id


def check_spam(engine: Engine, user_id: int) -> bool:
    """Функция проверки на спам

    Args:
        engine (Engine): подключение к БД
        user_id (int): id пользователя

    Returns:
        bool: пользователь задал пять вопросов за последнюю минуту
    """

    return False

    with Session(engine) as session:
        user = session.scalars(select(User).where(User.id == user_id)).first()
        if user is None:
            return False
        if len(user.question_answers) > 5:
            minute_ago = datetime.now() - timedelta(minutes=1)
            fifth_message_date = user.question_answers[4].created_at
            return minute_ago < fifth_message_date.replace(tzinfo=None)
        return False


def add_question_answer(
    engine: Engine, question: str, answer: str, user_id: int
) -> int:
    """Функция добавления в БД вопроса пользователя с ответом на него

    Args:
        engine (Engine): подключение к БД
        question (str): вопрос пользователя
        answer (str): ответ на вопрос пользователя
        user_id (int): id пользователя

    Returns:
        int: id вопроса с ответом на него
    """

    with Session(engine) as session:
        question_answer = QuestionAnswer(
            question=question,
            answer=answer,
            user_id=user_id,
        )
        session.add(question_answer)
        session.flush()
        session.refresh(question_answer)
        session.commit()
        if question_answer.id is None:
            return 0
        return question_answer.id


def rate_answer(engine: Engine, question_answer_id: int, score: int) -> bool:
    """Функция оценивания ответа на вопрос

    Args:
        engine (Engine): подключение к БД
        question_answer_id (int): id вопроса с ответом
        score (int): оценка ответа

    Returns:
        bool: удалось добавить в БД оценку ответа или нет
    """

    with Session(engine) as session:
        question_answer = session.scalars(
            select(QuestionAnswer).where(QuestionAnswer.id == question_answer_id)
        ).first()
        if question_answer is None:
            return False
        question_answer.score = score
        session.commit()
        return True
