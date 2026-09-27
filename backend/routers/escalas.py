from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.escalas import EscalaCreate, EscalaUpdate

router = APIRouter(prefix="/escalas", tags=["escalas"])


def get_sundays_of_month(year: int, month: int):
    ultimo_dia = monthrange(year, month)[1]
    domingos = []
    for dia in range(1, ultimo_dia + 1):
        current = date(year, month, dia)
        if current.weekday() == 6:
            domingos.append(current.isoformat())
    return domingos


@router.get("")
def list_escalas(current_user=Depends(require_admin)):
    data = get_supabase().table("escalas").select("*").order("data_domingo").execute()
    return data.data or []


@router.get("/sala/{sala_id}")
def list_escalas_sala(sala_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("escalas").select("*").eq("sala_id", sala_id).order("data_domingo").execute()
    return data.data or []


@router.get("/proximas")
def proximas_escalas(current_user=Depends(require_admin)):
    data = get_supabase().table("escalas").select("*").gte("data_domingo", str(date.today())).order("data_domingo").limit(20).execute()
    return data.data or []


@router.post("")
def create_escala(payload: EscalaCreate, current_user=Depends(require_admin)):
    equipe_id = payload.equipe_id or payload.dupla_id
    if equipe_id is None:
        raise HTTPException(status_code=400, detail="Informe uma equipe válida.")

    equipe = get_supabase().table("equipes").select("id, sala_id").eq("id", equipe_id).limit(1).execute().data or []
    if not equipe:
        raise HTTPException(status_code=400, detail="Equipe não encontrada.")
    if equipe[0].get("sala_id") != payload.sala_id:
        raise HTTPException(status_code=400, detail="A equipe selecionada não pertence à sala informada.")

    existing = get_supabase().table("escalas").select("id").eq("sala_id", payload.sala_id).eq("data_domingo", payload.data_domingo).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Já existe uma escala cadastrada para esta sala neste domingo.")

    created = get_supabase().table("escalas").insert({
        "data_domingo": payload.data_domingo,
        "semana_numero": payload.semana_numero,
        "sala_id": payload.sala_id,
        "equipe_id": equipe_id,
        "dupla_id": payload.dupla_id,
        "numero_licao": payload.numero_licao,
        "observacao": payload.observacao,
    }).execute()
    return {"status": "ok", "escala": created.data[0]}


@router.put("/{escala_id}")
def update_escala(escala_id: int, payload: EscalaUpdate, current_user=Depends(require_admin)):
    data = payload.model_dump(exclude_unset=True)
    updated = get_supabase().table("escalas").update(data).eq("id", escala_id).execute()
    return {"status": "ok", "escala": updated.data[0] if updated.data else None}


@router.delete("/{escala_id}")
def delete_escala(escala_id: int, current_user=Depends(require_admin)):
    get_supabase().table("escalas").delete().eq("id", escala_id).execute()
    return {"status": "ok"}


@router.post("/gerar-mensal")
def gerar_escala_mensal(payload: dict, current_user=Depends(require_admin)):
    try:
        ano = int(payload.get("ano") or date.today().year)
        mes = int(payload.get("mes") or date.today().month)
        sala_id = int(payload.get("sala_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Informe mês, ano e sala válidos.")

    if not 1 <= mes <= 12:
        raise HTTPException(status_code=400, detail="Mês inválido.")

    sala = get_supabase().table("salas").select("*").eq("id", sala_id).limit(1).execute().data or []
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada.")

    equipes = get_supabase().table("equipes").select("*").eq("sala_id", sala_id).order("id").execute().data or []
    if not equipes:
        raise HTTPException(status_code=400, detail="Não existem equipes cadastradas para esta sala. Cadastre pelo menos uma equipe antes de gerar a escala.")

    domingos = get_sundays_of_month(ano, mes)
    if not domingos:
        raise HTTPException(status_code=400, detail="Nenhum domingo foi encontrado para o mês selecionado.")

    existentes = {
        item["data_domingo"]
        for item in get_supabase().table("escalas").select("data_domingo").eq("sala_id", sala_id).in_("data_domingo", domingos).execute().data or []
    }

    liacao_atual = int(sala[0].get("licao_atual") or sala[0].get("licao_inicial") or 1)
    liacao_limit = int(sala[0].get("licao_limit") or 50)
    registros = []

    for indice, data_domingo in enumerate(domingos):
        if data_domingo in existentes:
            continue

        equipe = equipes[indice % len(equipes)]
        numero_licao = liacao_atual + indice
        if numero_licao > liacao_limit:
            break

        registros.append({
            "data_domingo": data_domingo,
            "semana_numero": date.fromisoformat(data_domingo).isocalendar().week,
            "sala_id": sala_id,
            "equipe_id": equipe["id"],
            "dupla_id": None,
            "numero_licao": numero_licao,
            "observacao": f"Gerada automaticamente - {mes}/{ano} - Sala {sala[0].get('nome', '')}",
        })

    if not registros:
        raise HTTPException(status_code=400, detail="Não foi possível gerar novas escalas neste mês. Verifique as lições, as equipes da sala ou as datas já cadastradas.")

    created = get_supabase().table("escalas").insert(registros).execute()
    ultimo_numero = registros[-1]["numero_licao"] + 1
    get_supabase().table("salas").update({"licao_atual": ultimo_numero}).eq("id", sala_id).execute()

    return {"status": "ok", "mes": mes, "ano": ano, "geradas": len(created.data or []), "itens": created.data or []}


@router.post("/gerar-proximo-domingo/{sala_id}")
def gerar_proximo_domingo(sala_id: int, current_user=Depends(require_admin)):
    hoje = date.today()
    dias = (6 - hoje.weekday()) % 7
    domingo = hoje + __import__("datetime").timedelta(days=dias)

    equipes = get_supabase().table("equipes").select("*").eq("sala_id", sala_id).order("id").execute().data or []
    if not equipes:
        raise HTTPException(status_code=400, detail="Não é possível gerar a escala. Cadastre pelo menos uma equipe para esta sala.")

    sala = get_supabase().table("salas").select("*").eq("id", sala_id).single().execute().data
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada.")

    numero_licao = sala.get("licao_atual", 1)
    if numero_licao > sala.get("licao_limit", 50):
        raise HTTPException(status_code=400, detail="O limite de lições desta sala foi atingido.")

    equipe = equipes[0]
    created = get_supabase().table("escalas").insert({
        "data_domingo": str(domingo),
        "sala_id": sala_id,
        "equipe_id": equipe["id"],
        "dupla_id": None,
        "numero_licao": numero_licao,
        "observacao": None,
    }).execute()

    get_supabase().table("salas").update({"licao_atual": numero_licao + 1}).eq("id", sala_id).execute()
    return {"status": "ok", "escala": created.data[0]}
