import asyncio

from fastapi import FastAPI, APIRouter

from routes import user_router, queue_router
from routes.message_queue import init_queue_connection

router = APIRouter()

app = FastAPI()

app.include_router(user_router, prefix="/api")
app.include_router(queue_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(init_queue_connection(loop))
    if not loop.is_running():
        loop.run_forever()


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down")
