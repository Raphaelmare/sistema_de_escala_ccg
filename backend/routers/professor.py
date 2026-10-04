from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import get_current_user

router = APIRouter(prefix="/professor", tags=["professor"])


@router.get("/minha-proxima-escala")
def minha_proxima_escala(current_user=Depends(get_current_user)):
    professor = current_user
    if (professor.get("tipo_usuario") or "").upper() != "PROFESSOR":
        raise HTTPException(status_code=403, detail="Acesso restrito ao professor.")

    professor_id = professor["id"]
    equipes_result = get_supabase().table("equipe_membros").select("equipe_id").eq("professor_id", professor_id).execute().data or []
    equipe_ids = [item["equipe_id"] for item in equipes_result]

    if not equipe_ids:
        return {
            "professor": professor.get("nome"),
            "sala": "",
            "livro": "",
            "equipe": "",
            "parceiro": "",
            "data_domingo": None,
            "numero_licao": None,
            "mensagem": "Nenhuma escala encontrada. Você não possui uma próxima escala cadastrada no momento. Caso isso esteja incorreto, entre em contato com o administrador.",
        }

    escalas = (
        get_supabase()
        .table("escalas")
        .select("*")
        .in_("equipe_id", equipe_ids)
        .gte("data_domingo", str(date.today()))
        .order("data_domingo")
        .limit(1)
        .execute()
        .data
        or []
    )
    proxima = escalas[0] if escalas else None

    if not proxima:
        return {
            "professor": professor.get("nome"),
            "sala": "",
            "livro": "",
            "equipe": "",
            "parceiro": "",
            "data_domingo": None,
            "numero_licao": None,
            "mensagem": "Nenhuma escala encontrada. Você não possui uma próxima escala cadastrada no momento. Caso isso esteja incorreto, entre em contato com o administrador.",
        }

    equipe_data = get_supabase().table("equipes").select("*").eq("id", proxima["equipe_id"]).limit(1).execute().data or []
    sala_data = get_supabase().table("salas").select("*").eq("id", equipe_data[0]["sala_id"]).limit(1).execute().data or []

    membros = get_supabase().table("equipe_membros").select("professor_id").eq("equipe_id", proxima["equipe_id"]).execute().data or []
    outros_ids = [item["professor_id"] for item in membros if item["professor_id"] != professor_id]
    parceiros = []
    for other_id in outros_ids:
        usuario = get_supabase().table("usuarios").select("nome").eq("id", other_id).limit(1).execute().data or []
        if usuario:
            parceiros.append(usuario[0].get("nome"))

    return {
        "professor": professor.get("nome"),
        "sala": sala_data[0].get("nome") if sala_data else "",
        "livro": sala_data[0].get("livro_nome") if sala_data else "",
        "equipe": equipe_data[0].get("nome") if equipe_data else "",
        "parceiro": ", ".join(parceiros) if parceiros else "",
        "data_domingo": proxima.get("data_domingo"),
        "numero_licao": proxima.get("numero_licao"),
    }
