from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models import TipoSenha
from app.services.senha_service import (
    emitir_senha,
    obter_painel,
    obter_proxima_senha,
)


app = FastAPI()


class EmitirSenhaRequest(BaseModel):
    tipo: TipoSenha


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={"erro": "tipo_invalido"},
    )


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


@app.get("/senhas/proxima")
def proxima_senha():
    senha = obter_proxima_senha()

    if senha is None:
        return JSONResponse(
            status_code=404,
            content={"erro": "fila_vazia"},
        )

    return JSONResponse(
        status_code=200,
        content=senha.to_dict(),
    )


@app.get("/painel")
def painel():
    chamadas = obter_painel()

    return JSONResponse(
        status_code=200,
        content={
            "chamadas": [
                senha.to_dict()
                for senha in chamadas
            ]
        },
    )
