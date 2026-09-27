from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.salas import SalaCreate, SalaUpdate

router = APIRouter(prefix="/salas", tags=["salas"])


@router.get("")
def list_salas(current_user=Depends(require_admin)):
    data = get_supabase().table("salas").select("*").order("id").execute()
    return data.data or []


@router.get("/{sala_id}")
def get_sala(sala_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("salas").select("*").eq("id", sala_id).limit(1).execute()
    if not data.data:
        raise HTTPException(status_code=404, detail="Sala não encontrada.")
    return data.data[0]


@router.post("")
def create_sala(payload: SalaCreate, current_user=Depends(require_admin)):
    existing = get_supabase().table("salas").select("id").eq("nome", payload.nome).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Sala já cadastrada.")

    created = get_supabase().table("salas").insert({
        "nome": payload.nome,
        "livro_nome": payload.livro_nome,
        "licao_inicial": payload.licao_inicial,
        "licao_limit": payload.licao_limit,
        "licao_atual": payload.licao_atual,
    }).execute()
    return {"status": "ok", "sala": created.data[0]}


@router.put("/{sala_id}")
def update_sala(sala_id: int, payload: SalaUpdate, current_user=Depends(require_admin)):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return {"status": "ok", "sala": None}
    updated = get_supabase().table("salas").update(data).eq("id", sala_id).execute()
    return {"status": "ok", "sala": updated.data[0] if updated.data else None}


@router.delete("/{sala_id}")
def delete_sala(sala_id: int, current_user=Depends(require_admin)):
    get_supabase().table("salas").delete().eq("id", sala_id).execute()
    return {"status": "ok"}
