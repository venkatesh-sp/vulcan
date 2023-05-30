import os
import uuid
import json
import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel
from aio_pika import connect, Message, IncomingMessage
from fastapi import APIRouter


router = APIRouter()

load_dotenv()

# Access environment variables
amqp_host = os.getenv("AMQP_HOST", "localhost")
amqp_port = os.getenv("AMQP_PORT", 5672)
amqp_queue = os.getenv("AMQP_QUEUE", "vulcanqueue")
amqp_user = os.getenv("AMQP_USER", "guest")
amqp_password = os.getenv("AMQP_PASSWORD", "guest")


class IMessage(BaseModel):
    text: str


message_queue = asyncio.Queue()


async def on_message(message: IncomingMessage):
    print(message)
    txt = message.body.decode("utf-8")
    txt = json.loads(txt)
    message_queue.put_nowait({"message_id": message.message_id, "message": txt})


async def init_queue_connection(loop):
    connection = await connect(
        host=amqp_host,
        port=amqp_port,
        # user=amqp_user,
        # password=amqp_password,
        # virtualhost="/",
        loop=loop,
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(amqp_queue)

    await queue.consume(on_message, no_ack=True)


# Function to get a message by ID from the queue
async def get_message_by_id(message_id):
    messages = []

    # Check each message in the queue
    while not message_queue.empty():
        item = await message_queue.get()
        messages.append(item)
        print(item["message_id"], type(item["message_id"]))
        print(message_id, type(message_id))

        # Check if the message ID matches
        if item["message_id"] == message_id:
            break

    # Put the remaining messages back into the queue
    for message in messages:
        await message_queue.put(message)

    # Return the found message or None if not found
    for message in messages:
        if message["message_id"] == message_id:
            return message

    return None


@router.post("/produce")
async def produce_message(message: IMessage):
    # Publish a message to RabbitMQ
    message_id = uuid.uuid4().hex

    connection = await connect(
        host=amqp_host,
        port=amqp_port,
        # user=amqp_user,
        # password=amqp_password,
        # virtualhost="/",
    )

    channel = await connection.channel()

    await channel.default_exchange.publish(
        Message(json.dumps(message.text).encode("utf-8"), message_id=message_id),
        routing_key=amqp_queue,
    )

    await connection.close()
    return {"message": "Message sent to the queue", "message_id": message_id}


@router.get("/consume/{message_id}")
async def consume_message(message_id):
    message = await get_message_by_id(message_id)
    if message is not None:
        return {"message": message["message"]}
    else:
        return {"message": "No message found with the given id"}
