from aiohttp import web
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config import Config
from database import Chunk, add_chunks, get_chunks
from llm_prompting import get_answer

routes = web.RouteTableDef()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4096,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)


@routes.post("/qa/")
async def qa(request: web.Request) -> web.Response:
    """Возвращает ответ на вопрос пользователя

    Args:
        request (web.Request): запрос, содержащий `question`

    Returns:
        web.Response: ответ
    """
    try:
        question = (await request.json())["question"]
    except Exception as e:
        return web.Response(
            text=f"Bad Request: There is no question in request! More details: {e}",
            status=400,
        )
    if len(question) < 3:
        return web.Response(text="Bad Request: Question is too short!", status=400)
    chunks = get_chunks(engine=engine, question=question)
    answer = get_answer("\n=====\n".join(chunks), question)
    if "ответ не найден" in answer.lower():
        return web.Response(text="Answer not found", status=404)
    return web.json_response({"answer": answer})


if __name__ == "__main__":
    with Session(engine) as session:
        questions = session.scalars(select(Chunk)).first()
        if questions is None:
            add_chunks(engine)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
