from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from rasa.utils.endpoints import EndpointConfig
from sanic import Blueprint, response
import aio_pika
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class RabbitMQInput(InputChannel):
    @classmethod
    def name(cls):
        return "rabbitmq"

    def __init__(self, queue_name="rasa_queue", host="localhost"):
        self.queue_name = queue_name
        self.host = host

    async def _consume(self, on_new_message):
        connection = await aio_pika.connect_robust(host=self.host)
        channel = await connection.channel()
        queue = await channel.declare_queue(self.queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    sender = data.get("sender", "user")
                    text = data.get("message", "")

                    await on_new_message(
                        UserMessage(text, None, sender_id=sender)
                    )

    def blueprint(self, on_new_message):
        bp = Blueprint("rabbitmq_channel", __name__)

        @bp.listener("after_server_start")
        async def setup(_app, _loop):
            _loop.create_task(self._consume(on_new_message))

        return bp
