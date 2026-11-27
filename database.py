"""Configuración de la conexión asíncrona a MongoDB mediante Motor."""

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGO_URL", default=config("MONGODB_URL", default="mongodb://localhost:27017"))
DATABASE_NAME = config("DATABASE_NAME", default="curso_idioma_db")

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

coleccion_matriculas = database["matriculas"]

async def verificar_conexion():
    """Funcion de comprobacion de estado de la conexion al iniciar la API"""
    try:
        await client.admin.command('ping')
        print(f"Conexion exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error de conexion a MongoDB: {e}")