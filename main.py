from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import (
    coleccion_estudiantes,
    coleccion_matriculas,
    coleccion_tareas,
    verificar_conexion,
)
from models import (
    CursoIdioma,
    CursoIdiomaCreate,
    CursoIdiomaUpdate,
    Estudiante,
    EstudianteCreate,
    EstudianteUpdate,
    Tarea,
    TareaCreate,
    TareaUpdate,
)

app = FastAPI(
    title="API Global Speak",
    description="API RESTful asíncrona para tareas, estudiantes y matrículas",
    version="1.0.0",
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
        "mensaje": "Bienvenido a la API de Global Speak",
        "documentacion": "/docs",
    }


@app.post(
    "/tareas",
    response_model=Tarea,
    status_code=status.HTTP_201_CREATED,
    tags=["Tareas"],
    summary="Crear una nueva tarea",
)
async def create_tarea(tarea_in: TareaCreate):
    tarea_existente = await coleccion_tareas.find_one({"titulo": tarea_in.titulo})
    if tarea_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una tarea registrada con el título '{tarea_in.titulo}'.",
        )

    nueva_tarea = tarea_in.model_dump()
    nueva_tarea["fecha_creacion"] = datetime.now()
    resultado = await coleccion_tareas.insert_one(nueva_tarea)
    return await coleccion_tareas.find_one({"_id": resultado.inserted_id})


@app.get(
    "/tareas",
    response_model=List[Tarea],
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Listar todas las tareas",
)
async def get_tareas():
    tareas = []
    async for documento in coleccion_tareas.find():
        tareas.append(documento)
    return tareas


@app.get(
    "/tareas/{id}",
    response_model=Tarea,
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Buscar tarea por ObjectId",
)
async def get_tarea_por_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB",
        )

    tarea = await coleccion_tareas.find_one({"_id": ObjectId(id)})
    if tarea:
        return tarea
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La tarea con ID '{id}' no fue encontrada en la base de datos",
    )


@app.put(
    "/tareas/{id}",
    response_model=Tarea,
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Actualizar una tarea",
)
async def update_tarea(id: str, tarea_update: TareaUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    object_id = ObjectId(id)
    datos_a_actualizar = tarea_update.model_dump(exclude_unset=True)
    if datos_a_actualizar:
        await coleccion_tareas.update_one(
            {"_id": object_id},
            {"$set": datos_a_actualizar},
        )

    tarea = await coleccion_tareas.find_one({"_id": object_id})
    if tarea:
        return tarea
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. La tarea con ID '{id}' no existe",
    )


@app.delete(
    "/tareas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Eliminar una tarea",
)
async def delete_tarea(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    resultado = await coleccion_tareas.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 1:
        return {"mensaje": f"Tarea con ID '{id}' eliminada exitosamente de MongoDB"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. La tarea con ID '{id}' no existe en la base de datos",
    )


@app.get(
    "/estudiantes",
    response_model=List[Estudiante],
    status_code=status.HTTP_200_OK,
    tags=["Estudiantes"],
    summary="Listar los estudiantes registrados",
)
async def get_estudiantes():
    estudiantes = []
    async for documento in coleccion_estudiantes.find().sort("nombre", 1):
        estudiantes.append(documento)
    return estudiantes


@app.post(
    "/estudiantes",
    response_model=Estudiante,
    status_code=status.HTTP_201_CREATED,
    tags=["Estudiantes"],
    summary="Registrar un estudiante",
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
    summary="Actualizar un estudiante",
)
async def update_estudiante(id: str, estudiante_update: EstudianteUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    object_id = ObjectId(id)
    datos_a_actualizar = estudiante_update.model_dump(exclude_unset=True)
    if datos_a_actualizar:
        await coleccion_estudiantes.update_one(
            {"_id": object_id},
            {"$set": datos_a_actualizar},
        )

    estudiante = await coleccion_estudiantes.find_one({"_id": object_id})
    if estudiante:
        return estudiante
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El estudiante con ID '{id}' no fue encontrado",
    )


@app.delete(
    "/estudiantes/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Estudiantes"],
    summary="Eliminar un estudiante",
)
async def delete_estudiante(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    resultado = await coleccion_estudiantes.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 1:
        return {"mensaje": f"Estudiante con ID '{id}' eliminado exitosamente"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El estudiante con ID '{id}' no fue encontrado",
    )


@app.post(
    "/matriculas",
    response_model=CursoIdioma,
    status_code=status.HTTP_201_CREATED,
    tags=["Matrículas"],
    summary="Crear una nueva matrícula",
)
async def create_matricula(matricula_in: CursoIdiomaCreate):
    nueva_matricula = matricula_in.model_dump()
    nueva_matricula["fecha_matricula"] = datetime.now()
    resultado = await coleccion_matriculas.insert_one(nueva_matricula)
    return await coleccion_matriculas.find_one({"_id": resultado.inserted_id})


@app.get(
    "/matriculas/pendientes",
    response_model=List[CursoIdioma],
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Listar matrículas con pago pendiente",
)
async def get_matriculas_pendientes():
    matriculas = []
    async for documento in coleccion_matriculas.find({"pagado": False}):
        matriculas.append(documento)
    return matriculas


@app.get(
    "/matriculas",
    response_model=List[CursoIdioma],
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Listar todas las matrículas",
)
async def get_matriculas():
    matriculas = []
    async for documento in coleccion_matriculas.find():
        matriculas.append(documento)
    return matriculas


@app.get(
    "/matriculas/{id}",
    response_model=CursoIdioma,
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Buscar matrícula por ObjectId",
)
async def get_matricula_por_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB",
        )

    matricula = await coleccion_matriculas.find_one({"_id": ObjectId(id)})
    if matricula:
        return matricula
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La matrícula con ID '{id}' no fue encontrada en la base de datos",
    )


@app.put(
    "/matriculas/{id}",
    response_model=CursoIdioma,
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Actualizar campos de una matrícula",
)
async def update_matricula(id: str, matricula_update: CursoIdiomaUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    object_id = ObjectId(id)
    datos_a_actualizar = matricula_update.model_dump(exclude_unset=True)
    if datos_a_actualizar:
        await coleccion_matriculas.update_one(
            {"_id": object_id},
            {"$set": datos_a_actualizar},
        )

    matricula = await coleccion_matriculas.find_one({"_id": object_id})
    if matricula:
        return matricula
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. La matrícula con ID '{id}' no existe",
    )


@app.delete(
    "/matriculas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Matrículas"],
    summary="Eliminar una matrícula",
)
async def delete_matricula(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido",
        )

    resultado = await coleccion_matriculas.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 1:
        return {"mensaje": f"Matrícula con ID '{id}' eliminada exitosamente de MongoDB"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. La matrícula con ID '{id}' no existe en la base de datos",
    )
