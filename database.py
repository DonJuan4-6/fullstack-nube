"""
Modulo de base de datos (database.py)
Gestione la conexión asincrona a MongoDB utilizando Motor
"""

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGO_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="adso_db")

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

coleccion_tareas = database["tareas"]

async def verificar_conexion():
    """Funcion de comprobacion de estado de la conexion al iniciar la API"""
    try:
        await client.admin_command('ping')
        print(f"Conexion exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error de conexion a MongoDB: {e}")