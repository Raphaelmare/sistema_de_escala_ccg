from pydantic import BaseModel


class EscalaCreate(BaseModel):
    data_domingo: str
    semana_numero: int | None = None
    sala_id: int
    equipe_id: int | None = None
    dupla_id: int | None = None
    numero_licao: int
    observacao: str | None = None


class EscalaUpdate(BaseModel):
    data_domingo: str | None = None
    semana_numero: int | None = None
    sala_id: int | None = None
    equipe_id: int | None = None
    dupla_id: int | None = None
    numero_licao: int | None = None
    observacao: str | None = None
