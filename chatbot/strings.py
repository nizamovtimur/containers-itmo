class Strings:
    """Класс со строковыми представлениями отправляемых чат-ботом сообщений"""

    FirstMessage = (
        "👋🏻 Привет! Меня зовут Вопрошалыч, вы можете задать мне вопрос об обучении в Тюменском государственном университете\n\n"
        "Используется искусственный интеллект, поэтому ответы на произвольные вопросы могут содержать неточности. "
        "Продолжая работу с ботом, вы даёте согласие на обработку персональных данных и получение сообщений."
    )
    NotFound = "К сожалению, я не смог найти ответ на этот вопрос 😢, попробуйте задать другой вопрос"
    NotAnswer = "Извините, что-то пошло не так"
    ThanksForFeedback = "Спасибо за обратную связь! 🤗"
    SpamWarning = (
        "Я получил от вас больше 5 вопросов за минуту, мне нужно немного отдохнуть! 😰"
    )
    Less4Symbols = "В вопросе должно быть больше 3 символов 😉"
    NoneUserTelegram = "Для активации бота нужно отправить команду /start"
