import os
import uuid
import json
import asyncio

from dotenv import load_dotenv
from aio_pika import connect, Message, IncomingMessage
from fastapi import APIRouter, UploadFile

from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.humanname import HumanName
from hl7apy import parser


router = APIRouter()

load_dotenv()

# Access environment variables
amqp_host = os.getenv("AMQP_HOST", "localhost")
amqp_port = os.getenv("AMQP_PORT", 5672)
amqp_queue = os.getenv("AMQP_QUEUE", "vulcanqueue")
amqp_user = os.getenv("AMQP_USER", "guest")
amqp_password = os.getenv("AMQP_PASSWORD", "guest")


message_queue = asyncio.Queue()


async def on_message(message: IncomingMessage):
    print(message)
    txt = message.body.decode("utf-8")
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
            return message["message"]

    return None


@router.post("/produce")
async def produce_message(file: UploadFile):
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

    message = await file.read()

    await channel.default_exchange.publish(
        Message(message, message_id=message_id),
        routing_key=amqp_queue,
    )

    await connection.close()
    return {"message": "Message sent to the queue", "message_id": message_id}


def parse_message(msg):
    msg = parser.parse_message(
        msg.replace("\n", "\r"), find_groups=False, validation_level=2
    )
    # Extract relevant data from HL7 v2 message
    patient_id = msg.PID.PID_3.CX_1.value
    patient_name = msg.PID.PID_5.XPN_1.value
    birth_date = msg.PID.PID_7.value

    # Create FHIR resources
    patient = Patient()
    patient.id = patient_id
    patient.name = [HumanName(text=patient_name)]
    patient.birthDate = birth_date

    identifier = Identifier()
    identifier.system = "http://example.com/mrn"
    identifier.value = patient_id
    patient.identifier = [identifier]

    # Convert FHIR resources to JSON
    fhir_json = patient.json(indent=4)

    return fhir_json


@router.get("/consume/{message_id}")
async def consume_message(message_id):
    message = await get_message_by_id(message_id)
    if not message:
        return {"message": "No message found with the given id"}
    fhir_json = parse_message(message)
    return json.loads(fhir_json)
