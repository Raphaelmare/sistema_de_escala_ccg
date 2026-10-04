from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    telefone: str | None = None
    tipo_usuario: str = "PROFESSOR"
    sala_id: int | None = None


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    tipo_usuario: str | None = None
    sala_id: int | None = None
    ativo: bool | None = None
    password: str | None = None
    senha: str | None = None
