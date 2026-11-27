from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import coleccion_estudiantes, coleccion_matriculas, verificar_conexion
from models import (
    CursoIdioma,
    CursoIdiomaCreate,
    CursoIdiomaUpdate,
    Estudiante,
    EstudianteCreate,
    EstudianteUpdate,
)

app = FastAPI(
    title="API Centro de Idiomas Global Speak",
    description="API RESTful asíncrona para gestionar matrículas de cursos de idiomas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()


@app.get("/", tags=["Raíz"])
async def root():
    return {
        "mensaje": "Bienvenido a la API del Centro de Idiomas Global Speak",
        "documentacion": "/docs"
    }


@app.post(
    "/matriculas",
    response_model=CursoIdioma,
    status_code=status.HTTP_201_CREATED,
    tags=["Matrículas"],
    summary="Crear una nueva matrícula"
)
async def create_matricula(matricula_in: CursoIdiomaCreate):
    """Guarda una matrícula en la colección 'matriculas' de MongoDB."""
    nueva_matricula = matricula_in.model_dump()
    nueva_matricula["fecha_matricula"] = datetime.now()

    resultado = await coleccion_matriculas.insert_one(nueva_matricula)
    matricula_creada = await coleccion_matriculas.find_one(
        {"_id": resultado.inserted_id}
    )
    return matricula_creada


@app.get(
    "/estudiantes",
    response_model=List[Estudiante],
    status_code=status.HTTP_200_OK,
    tags=["Estudiantes"],
    summary="Listar los estudiantes registrados"
)
async def get_estudiantes():
    """Devuelve los estudiantes registrados."""
    estudiantes = []
    cursor = coleccion_estudiantes.find().sort("nombre", 1)
    async for documento in cursor:
        estudiantes.append(documento)
    return estudiantes


@app.post(
    "/estudiantes",
    response_model=Estudiante,
    status_code=status.HTTP_201_CREATED,
    tags=["Estudiantes"],
    summary="Registrar un estudiante"
)
async def create_estudiante(estudiante_in: EstudianteCreate):
    estudiante = estudiante_in.model_dump()
    resultado = await coleccion_estudiantes.insert_one(estudiante)
    return await coleccion_estudiantes.find_one({"_id": resultado.inserted_id})


@app.put(
    "/estudiantes/{id}",
    response_model=Estudiante,
    status_code=status.HTTP_200_OK,
    tags=["Estudiantes"],
    summary="Actualizar un estudiante"
)
async def update_estudiante(id: str, estudiante_update: EstudianteUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido"
        )

    object_id = ObjectId(id)
    datos_a_actualizar = estudiante_update.model_dump(exclude_unset=True)

    if datos_a_actualizar:
        await coleccion_estudiantes.update_one(
            {"_id": object_id},
            {"$set": datos_a_actualizar}
        )

    estudiante = await coleccion_estudiantes.find_one({"_id": object_id})
    if estudiante:
        return estudiante

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El estudiante con ID '{id}' no fue encontrado"
    )


@app.delete(
    "/estudiantes/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Estudiantes"],
    summary="Eliminar un estudiante"
)
async def delete_estudiante(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido"
        )

    resultado = await coleccion_estudiantes.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 1:
        return {"mensaje": f"Estudiante con ID '{id}' eliminado exitosamente"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El estudiante con ID '{id}' no fue encontrado"
    )


@app.get(
    "/matriculas/pendientes",
    response_model=List[CursoIdioma],
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Listar matrículas con pago pendiente"
)
async def get_matriculas_pendientes():
    """Recupera las matrículas cuyo campo 'pagado' es falso."""
    matriculas = []
    cursor = coleccion_matriculas.find({"pagado": False})
    async for documento in cursor:
        matriculas.append(documento)
    return matriculas


@app.get(
    "/matriculas",
    response_model=List[CursoIdioma],
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Listar todas las matrículas"
)
async def get_matriculas():
    """Recupera todos los documentos de la colección de matrículas."""
    matriculas = []
    cursor = coleccion_matriculas.find()
    async for documento in cursor:
        matriculas.append(documento)
    return matriculas


@app.get(
    "/matriculas/{id}",
    response_model=CursoIdioma,
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Buscar matrícula por ObjectId"
)
async def get_matricula_por_id(id: str):
    """Busca una matrícula específica por su ObjectId de MongoDB."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB"
        )

    matricula = await coleccion_matriculas.find_one({"_id": ObjectId(id)})
    if matricula:
        return matricula

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La matrícula con ID '{id}' no fue encontrada en la base de datos"
    )


@app.put(
    "/matriculas/{id}",
    response_model=CursoIdioma,
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Actualizar campos de una matrícula"
)
async def update_matricula(id: str, matricula_update: CursoIdiomaUpdate):
    """Actualiza los campos de una matrícula por su _id."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido"
        )

    object_id = ObjectId(id)
    datos_a_actualizar = matricula_update.model_dump(exclude_unset=True)

    if datos_a_actualizar:
        resultado_actualizacion = await coleccion_matriculas.update_one(
            {"_id": object_id},
            {"$set": datos_a_actualizar}
        )

        if resultado_actualizacion.modified_count == 1 or resultado_actualizacion.matched_count == 1:
            return await coleccion_matriculas.find_one({"_id": object_id})

    matricula_existente = await coleccion_matriculas.find_one({"_id": object_id})
    if matricula_existente:
        return matricula_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. La matrícula con ID '{id}' no existe"
    )


@app.delete(
    "/matriculas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Eliminar una matrícula"
)
async def delete_matricula(id: str):
    """Elimina una matrícula de MongoDB por su ObjectId."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido"
        )

    resultado_eliminacion = await coleccion_matriculas.delete_one(
        {"_id": ObjectId(id)}
    )

    if resultado_eliminacion.deleted_count == 1:
        return {"mensaje": f"Matrícula con ID '{id}' eliminada exitosamente de MongoDB"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. La matrícula con ID '{id}' no existe en la base de datos"
    )
