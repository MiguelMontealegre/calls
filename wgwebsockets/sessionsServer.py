import asyncio
import json
import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from websockets import connect
from auth import *
from endpoints import fetch_user_keys
from conf import *
from urllib.parse import urljoin
from proxy_web_socket import  WebSocketProcessor
from load_balancer import LoadlBalancerManager
import logging
logger = logging.getLogger(__name__)


app = FastAPI()

# Configuración CORS
origins = ["*"]  # Permite cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)


user_keys = [] # Lista para almacenar los usuarios obtenida del endpoint
endpoints_back = []
load_balancer_manager = None



@app.on_event("startup")
async def startup():
    """Código a ejecutar al iniciar la aplicación."""
    logger.info("Starting application...")
    # Code to run on startup
    global user_keys
    global endpoints_back
    global load_balancer_manager
    try:
        user_keys = await fetch_user_keys(backurl_users)
        user_keys = user_keys.get('users')
        endpoints_back = await fetch_user_keys(backurl_endpoints)
        endpoints_back = endpoints_back.get('endpoints')
        load_balancer_manager = LoadlBalancerManager(endpoints_back)
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


# Validar si el cliente es válido
def validate_client(client_id: str, key: str) -> bool:
    """
    Valida si un cliente es válido basándose en la lista de usuarios sincronizada.
    
    Args:
        client_id (str): ID del cliente.
        key (str): Clave del cliente.
    
    Returns:
        bool: True si el cliente es válido, False de lo contrario.
    """
    for user in user_keys:
        if str(user["id"]) == client_id and user["key"] == key:
            if not load_balancer_manager.is_active(client_id):
                return True
    return False


# Endpoint WebSocket con autenticación y validación
@app.websocket("/asr/{client_id}/{key}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, key):
    # Validar el cliente antes de continuar
    if not validate_client(client_id, key):
        logger.error(f"Invalid client: {client_id}")
        await websocket.close(code=1008)  # Código de cierre para políticas de violación
        raise HTTPException(status_code=401, detail="Unauthorized client.")

    available_endpoint = load_balancer_manager.get_available_endpoint() 
    # Agregar el cliente a las conexiones activas
    await load_balancer_manager.add(client_id, websocket, available_endpoint)

    # Conectar al servidor WebSocket de destino
    server_url  = urljoin(available_endpoint, client_id)
    try:
        proxy = WebSocketProcessor(websocket, server_url, load_balancer_manager, client_id)
        await proxy.start()
        await proxy.disconnect_event.wait()  # Espera a que se señale el evento
    except Exception as e:
        logger.error(f"Error handling WebSocket connection: {e}")
    finally:
        # Eliminar cliente de las conexiones activas al desconectarse
        await load_balancer_manager.remove(client_id)
        # Verificar si el WebSocket está abierto antes de cerrarlo
        try:
            await websocket.close()
        except Exception as e:
            logger.info(f"Websocket was close {e}")
        