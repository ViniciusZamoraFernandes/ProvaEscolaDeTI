from datetime import datetime, timezone, timedelta

from app.config import PREFIXO, RAZAO_PREFERENCIAL
from app.models import Senha
from app.storage import storage


FUSO = timezone(timedelta(hours=-3))


def agora():
    return datetime.now(FUSO).isoformat()


def data_atual():
    return datetime.now(FUSO).date().isoformat()


def emitir_senha(tipo):
    def operacao(dados):

        if dados.get("data") != data_atual():
            dados["data"] = data_atual()
            dados["sequencia"] = 0

        dados["sequencia"] += 1

        codigo = f"{PREFIXO}{dados['sequencia']:03d}"

        senha = Senha(
            codigo=codigo,
            tipo=tipo,
            emissao=agora(),
            status="aguardando",
        )

        dados.setdefault("senhas", [])
        dados["senhas"].append(senha.to_dict())

        return senha

    return storage.executar_atomico(operacao)


def obter_proxima_senha():

    def operacao(dados):
        senhas = dados.get("senhas", [])

        aguardando = [
            senha
            for senha in senhas
            if senha["status"] == "aguardando"
        ]

        if not aguardando:
            return None

        preferenciais = [
            senha
            for senha in aguardando
            if senha["tipo"] == "preferencial"
        ]

        normais = [
            senha
            for senha in aguardando
            if senha["tipo"] == "normal"
        ]

        quantidade_preferenciais = 0

        for senha in reversed(senhas):

            if senha["status"] != "chamada":
                continue

            if senha["tipo"] == "preferencial":
                quantidade_preferenciais += 1
            else:
                break

        if preferenciais and (
            quantidade_preferenciais < RAZAO_PREFERENCIAL
            or not normais
        ):
            proxima = preferenciais[0]

        elif normais:
            proxima = normais[0]

        else:
            proxima = preferenciais[0]

        proxima["status"] = "chamada"
        proxima["chamada_em"] = agora()

        return Senha.from_dict(proxima)

    return storage.executar_atomico(operacao)


def obter_painel():

    dados = storage.ler()

    chamadas = [
        senha
        for senha in dados.get("senhas", [])
        if senha.get("chamada_em") is not None
    ]

    chamadas.sort(
        key=lambda senha: senha["chamada_em"],
        reverse=True,
    )

    return [
        Senha.from_dict(senha)
        for senha in chamadas[:5]
    ]
