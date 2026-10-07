from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class TipoSenha(str, Enum):
    NORMAL = "normal"
    PREFERENCIAL = "preferencial"


class StatusSenha(str, Enum):
    AGUARDANDO = "aguardando"
    CHAMADA = "chamada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class Senha(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    codigo: str
    tipo: TipoSenha
    emissao: datetime
    status: StatusSenha

    def to_dict(self) -> dict:
        return self.model_dump()
