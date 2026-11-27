from datetime import datetime
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    """Valida y serializa identificadores ObjectId de MongoDB."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(value):
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str) and ObjectId.is_valid(value):
                return value
            raise ValueError("ID invalido de MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]


class TareaBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    completada: bool = False


class TareaCreate(TareaBase):
    pass


class TareaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    completada: Optional[bool] = None


class Tarea(TareaBase):
    id: PyObjectId = Field(alias="_id")
    fecha_creacion: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class CursoIdiomaBase(BaseModel):
    estudiante: str = Field(..., min_length=3, max_length=150)
    idioma_nivel: str = Field(..., min_length=2, max_length=100)
    valor_curso: float = Field(..., ge=0)
    pagado: bool = False
    imagen_url: Optional[str] = Field(None, max_length=2048)
    estudiante_nombre: Optional[str] = Field(None, max_length=150)
    idioma: Optional[str] = Field(None, max_length=100)


class CursoIdiomaCreate(CursoIdiomaBase):
    pass


class CursoIdiomaUpdate(BaseModel):
    estudiante: Optional[str] = Field(None, min_length=3, max_length=150)
    idioma_nivel: Optional[str] = Field(None, min_length=2, max_length=100)
    valor_curso: Optional[float] = Field(None, ge=0)
    pagado: Optional[bool] = None
    imagen_url: Optional[str] = Field(None, max_length=2048)
    estudiante_nombre: Optional[str] = Field(None, max_length=150)
    idioma: Optional[str] = Field(None, max_length=100)


class CursoIdioma(CursoIdiomaBase):
    id: PyObjectId = Field(alias="_id")
    fecha_matricula: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


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
    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
