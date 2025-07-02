# src/deep_searcher/utils/streaming_utils.py
import asyncio
import json
from typing import Any, Dict

class StreamCallbackHandler:
    """
    A handler to manage sending Server-Sent Events (SSE) updates.
    This class is designed to be passed into long-running processes to stream
    progress back to a client.
    """
    def __init__(self):
        self.queue = asyncio.Queue()

    async def send_update(self, event_type: str, data: Dict[str, Any]):
        """
        Puts a new update message into the queue.

        Args:
            event_type: A string identifier for the event (e.g., 'log', 'progress', 'final_result').
            data: A JSON-serializable dictionary containing the event data.
        """
        message = {
            "event": event_type,
            "data": data
        }
        await self.queue.put(message)

    async def stream_generator(self):
        """
        An async generator that yields formatted SSE messages from the queue.
        This is intended to be used with FastAPI's StreamingResponse.
        """
        while True:
            message = await self.queue.get()
            
            event = message['event']
            # Convert data dict to a JSON string
            data_json = json.dumps(message['data'])
            
            # SSE format:
            # event: <event_type>
            # data: <json_string>
            # \n
            yield f"event: {event}\n"
            yield f"data: {data_json}\n\n"
            
            # The 'end_stream' event is a special signal to stop the generator.
            if event == 'end_stream':
                break