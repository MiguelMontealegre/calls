import asyncio
import websockets
import json
from termcolor import colored
client_id = "asdfasdf"



import asyncio
import websockets
import json



import asyncio
import ssl
import websockets

    
async def test_wss_connection(uri):
    # Crear un contexto SSL para verificar el certificado
    ssl_context = ssl.create_default_context()

    try:
        # Intentar conectarse al servidor
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("Conexión segura y certificado válido.")
    except ssl.SSLError as e:
        print(f"Error de SSL: {e}")
    except Exception as e:
        print(f"Error en la conexión: {e}")

# URL del servidor WSS
uri = "wss://backpy.robin-ai.xyz:8005/ws/alksjdfl/test"

# Ejecutar la prueba
asyncio.run(test_wss_connection(uri))




async def send_messages(websocket):
    """Handle sending messages to the WebSocket server."""
    while True:
        # Read input from the command line without blocking
        user_input = await asyncio.to_thread(input, "Enter message to send: ")
        
        # Create a dictionary with the data you want to send
        message_data = {
            "type": "user_message",
            "data" :  
                { 
                "client_id": client_id,
                "history": None,
                "role": "user",
                "content": user_input
                }
        }
        
        # Convert the dictionary to a JSON string
        message_json = json.dumps(message_data)
        
        # Send the JSON data to the WebSocket server
        await websocket.send(message_json)
        print(f"Sent: {message_json}")


async def receive_messages(websocket):
    """Handle receiving messages from the WebSocket server."""
    while True:
        # Wait for and receive a message from the server
        response = await websocket.recv()
        data = json.loads(response)
        sender_type = data.get("data", {}).get("sender_type", "default_value")

        if sender_type == "user":
            print(colored(data, 'blue'))
        elif sender_type == "agent":
            print(colored(data, 'yellow'))
        elif sender_type == "system":
            print(colored(data, 'green'))
        elif sender_type == "execution":
            print(colored(data, 'magenta'))
        elif sender_type == "requested_execution":
            print(colored(data, 'red'))
        else:
            print(colored(data, 'red'))

async def send_heartbeat(websocket, interval=1):
    """Send a heartbeat message to keep the WebSocket connection alive."""
    while True:
        try:
            heartbeat_message = {
                "type": "heartbeat",
                "data": {
                    "client_id": client_id
                }
            }
            await websocket.send(json.dumps(heartbeat_message))
            print(colored("Heartbeat sent", "green"))
        except websockets.ConnectionClosed as e:
            print(colored(f"Failed to send heartbeat: {e}", 'red'))
            break
        await asyncio.sleep(interval)



async def main():
    uri = "ws://localhost:8005/ws/your_client_id"  # Replace with your WebSocket URL
    uri = "wss://workflow.robin-ai.xyz:31861/ws/ff5e147af5d140f1/asdfasdf"
    uriad = "wss://robin-ai.xyz:30463/ws/your_client_id"  # Replace with your WebSocket URL
    uri = "wss://workflow.robin-ai.xyz:30091/ws/c9b82706d50f4cc1/asdfpredict"
    uri = "wss://workflow.robin-ai.xyz:30101/ws/f03ee12212ae4868/test"  # Replace with your WebSocket URL
    uri = "wss://backpy.robin-ai.xyz:8005/ws/alksjdfl/test"  # Replace with your WebSocket URL
    uri = "wss://workflow.robin-ai.xyz:30122/ws/f634a23179d3471b/asdf"  # Replace with your WebSocket URL
    async with websockets.connect(uri, timeout=120, open_timeout= 120) as websocket:
        print("Connected to WebSocket server")
        
        # Create two tasks: one for sending and one for receiving
        send_task = asyncio.create_task(send_messages(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))
        
        # Run both tasks concurrently
        await asyncio.gather(send_task, receive_task)

# Run the client "dame la informacion mas relevantes sobre este archivo"
# Run the client "What is the City with more customers?"
# Busca informacion de las ultimas noticia de Trump"
# hola mi email es wlkjaldkfaj@gmail.com y mi numero de pedido es TCKT-0984092834950 y mi nombre el Willliam Leonardo, dame la informacion de mi pedido
asyncio.run(main())
