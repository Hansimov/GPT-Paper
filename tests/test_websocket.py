import asyncio
import websockets
from datetime import datetime


async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")
    greeting = f"Message Received at {datetime.now()}"
    await websocket.send(greeting)
    print(f"> {greeting}")


port = 29999

start_server = websockets.serve(hello, "localhost", 29999)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


"""
%%javascript
ws = new WebSocket("ws://localhost:29999");
ws.onopen = function() {
    console.log("Connection is Established");
    url = window.location.href;
    ws.send(`message from ${url}`);
};
ws.onmessage = function(evt) {
    var received_msg = evt.data;
    console.log(received_msg);
};
"""
