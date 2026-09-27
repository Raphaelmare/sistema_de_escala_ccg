from pydantic import BaseModel


class SalaCreate(BaseModel):
    nome: str
    livro_nome: str
    licao_inicial: int = 1
    licao_limit: int = 50
    licao_atual: int = 1


class SalaUpdate(BaseModel):
    nome: str | None = None
    livro_nome: str | None = None
    licao_inicial: int | None = None
    licao_limit: int | None = None
    licao_atual: int | None = None
