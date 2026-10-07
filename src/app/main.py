from flask import Flask, jsonify, request

from app.models import TIPOS_VALIDOS
from app.services.senha_service import (
    emitir_senha,
    obter_painel,
    obter_proxima_senha,
    concluir_senha,
    rechamar_senha,
    cancelar_senha,
)


app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return jsonify({
        "status": "ok"
    }), 200


@app.post("/senhas")
def criar_senha():

    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify({
            "erro": "tipo_invalido"
        }), 422

    tipo = body.get("tipo")

    if tipo not in TIPOS_VALIDOS:
        return jsonify({
            "erro": "tipo_invalido"
        }), 422

    senha = emitir_senha(tipo)

    return jsonify(senha.to_dict()), 201


@app.get("/senhas/proxima")
def proxima_senha():

    senha = obter_proxima_senha()

    if senha is None:
        return jsonify({
            "erro": "fila_vazia"
        }), 404

    return jsonify(senha.to_dict()), 200


@app.get("/painel")
def painel():

    chamadas = obter_painel()

    return jsonify({
        "chamadas": [
            senha.to_dict()
            for senha in chamadas
        ]
    }), 200


@app.post("/senhas/<codigo>/concluir")
def concluir(codigo):

    senha, erro = concluir_senha(codigo)

    if erro == "senha_nao_encontrada":
        return jsonify({
            "erro": erro
        }), 404

    if erro == "senha_nao_chamada":
        return jsonify({
            "erro": erro
        }), 409

    return jsonify({
        "status": "concluida",
        "observacao": senha.to_dict()
    }), 200


@app.post("/senhas/<codigo>/rechamar")
def rechamar(codigo):

    senha, erro = rechamar_senha(codigo)

    if erro == "senha_nao_encontrada":
        return jsonify({
            "erro": erro
        }), 404

    if erro == "senha_nao_chamada":
        return jsonify({
            "erro": erro
        }), 409

    return jsonify({
        "status": "chamada",
        "observacao": senha.to_dict()
    }), 200


@app.post("/senhas/<codigo>/cancelar")
def cancelar(codigo):

    senha, erro = cancelar_senha(codigo)

    if erro == "senha_nao_encontrada":
        return jsonify({
            "erro": erro
        }), 404

    if erro == "senha_nao_aguardando":
        return jsonify({
            "erro": erro
        }), 409

    return jsonify({
        "status": "cancelada",
        "observacao": senha.to_dict()
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
    )
