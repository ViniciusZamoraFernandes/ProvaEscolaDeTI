from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models import TipoSenha
from app.services.senha_service import emitir_senha


app = FastAPI()


class EmitirSenhaRequest(BaseModel):
    tipo: TipoSenha


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/senhas")
def criar_senha(body: EmitirSenhaRequest):
    senha = emitir_senha(body.tipo)

    return JSONResponse(
        status_code=201,
        content=senha.to_dict(),
    )
