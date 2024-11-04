import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy import create_engine
from config import Config
from database import (
    add_user,
    get_user_id,
    check_spam,
    add_question_answer,
    rate_answer,
)
from strings import Strings


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
dp = Dispatcher()


@dp.callback_query()
async def tg_rate(callback_query: CallbackQuery):
    """Обработчик события (для чат-бота Telegram), при котором пользователь оценивает
    ответ на вопрос

    Args:
        callback_query (CallbackQuery): запрос при нажатии на inline-кнопку
    """

    score, question_answer_id = map(int, str(callback_query.data).split())
    if rate_answer(engine, question_answer_id, score):
        await callback_query.answer(text=Strings.ThanksForFeedback)


async def get_answer(question: str) -> str:
    """Получение ответа на вопрос с использованием микросервиса

    Args:
        question (str): вопрос пользователя

    Returns:
        str: ответ на вопрос и ссылка на страницу в вики-системе
    """

    question = question.strip().lower()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{Config.QA_HOST}/qa/", json={"question": question}
        ) as response:
            if response.status == 200:
                resp = await response.json()
                return resp["answer"]
            else:
                return ""


@dp.message(CommandStart())
async def tg_start(message: Message):
    """Обработчик события (для чат-бота Telegram), при котором пользователь отправляет
    команду /start

    Args:
        message (Message): сообщение пользователя
    """
    if message.from_user is not None:
        is_user_added, _ = add_user(
            engine,
            telegram_id=message.from_user.id,
            username=str(message.from_user.username),
        )
        if is_user_added:
            await message.answer(text=Strings.FirstMessage)


@dp.message()
async def tg_answer(message: Message):
    """Обработчик события (для чат-бота Telegram), при котором пользователь задаёт
    вопрос чат-боту

    После отображения ответа на вопрос чат-бот отправляет inline-кнопки для оценивания
    ответа

    Args:
        message (Message): сообщение с вопросом пользователя
    """
    if message.from_user is None:
        return
    if message.text is None or len(str(message.text)) < 4:
        await message.answer(text=Strings.Less4Symbols)
        return
    user_id = get_user_id(engine, telegram_id=message.from_user.id)
    if user_id is None:
        await message.answer(text=Strings.NoneUserTelegram)
        return
    if check_spam(engine, user_id):
        await message.answer(text=Strings.SpamWarning)
        return
    answer = await get_answer(message.text)
    if len(answer) < 5:
        await message.answer(text=Strings.NotFound)
        return
    question_answer_id = add_question_answer(engine, message.text, answer, user_id)
    await message.answer(
        text=answer if len(answer) > 0 else Strings.NotAnswer,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👎", callback_data=f"1 {question_answer_id}"
                    ),
                    InlineKeyboardButton(
                        text="❤", callback_data=f"5 {question_answer_id}"
                    ),
                ]
            ]
        ),
    )


async def main() -> None:
    tg_bot = Bot(token=Config.TG_ACCESS_TOKEN)
    await dp.start_polling(tg_bot)


if __name__ == "__main__":
    asyncio.run(main())
