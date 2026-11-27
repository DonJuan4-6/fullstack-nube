from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class _ObjectIdPydanticAnnotation:
    """Adaptador para validar y serializar ObjectId de MongoDB en Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("ID invalido de MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )

# Tipo de dato reutilizable para Pydantic
PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]

class CursoIdiomaBase(BaseModel):
    estudiante: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre del estudiante",
        example="María Pérez"
    )
    idioma_nivel: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Idioma y nivel del curso",
        example="Inglés B1"
    )
    valor_curso: float = Field(
        ...,
        ge=0,
        description="Valor del curso",
        example=350000
    )
    pagado: bool = Field(
        default=False,
        description="Indica si el curso fue pagado"
    )
    imagen_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="URL de la imagen del estudiante o matrícula"
    )
    estudiante_nombre: Optional[str] = Field(
        None,
        max_length=150,
        description="Nombre del estudiante asociado a la matrícula"
    )
    idioma: Optional[str] = Field(
        None,
        max_length=100,
        description="Idioma del curso"
    )


class CursoIdiomaCreate(CursoIdiomaBase):
    """Modelo utilizado para recibir solicitudes de creación."""
    pass


class CursoIdiomaUpdate(BaseModel):
    """Modelo para solicitudes PUT con campos opcionales."""
    estudiante: Optional[str] = Field(None, min_length=3, max_length=150)
    idioma_nivel: Optional[str] = Field(None, min_length=2, max_length=100)
    valor_curso: Optional[float] = Field(None, ge=0)
    pagado: Optional[bool] = None
    imagen_url: Optional[str] = Field(None, max_length=2048)
    estudiante_nombre: Optional[str] = Field(None, max_length=150)
    idioma: Optional[str] = Field(None, max_length=100)


class EstudianteBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    documento: str = Field(..., min_length=1, max_length=30)
    correo: str = Field(..., min_length=3, max_length=254)
    telefono: str = Field(..., min_length=1, max_length=20)


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    documento: Optional[str] = Field(None, min_length=1, max_length=30)
    correo: Optional[str] = Field(None, min_length=3, max_length=254)
    telefono: Optional[str] = Field(None, min_length=1, max_length=20)


class Estudiante(EstudianteBase):
    id: PyObjectId = Field(alias="_id", description="Identificador unico de MongoDB")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class CursoIdioma(CursoIdiomaBase):
    """Modelo de respuesta con el ID de MongoDB y la fecha de matrícula."""
    id: PyObjectId = Field(alias="_id", description="Identificador unico de ObjectId de MongoDB")
    fecha_matricula: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de registro de la matrícula"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "654321789abcdef012345678",
                "estudiante": "María Pérez",
                "idioma_nivel": "Inglés B1",
                "valor_curso": 350000,
                "pagado": False,
                "imagen_url": "https://example.com/estudiante.jpg",
                "fecha_matricula": "2026-11-05T18:30:00"
            }
        }
    )
