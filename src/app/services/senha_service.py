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
            dados["preferenciais_chamadas"] = 0

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

        preferenciais_chamadas = dados.get(
            "preferenciais_chamadas",
            0,
        )

        deve_chamar_preferencial = (
            preferenciais
            and (
                preferenciais_chamadas < RAZAO_PREFERENCIAL
                or not normais
            )
        )

        if deve_chamar_preferencial:
            proxima = preferenciais[0]
            dados["preferenciais_chamadas"] = (
                preferenciais_chamadas + 1
            )
        elif normais:
            proxima = normais[0]
            dados["preferenciais_chamadas"] = 0
        else:
            proxima = preferenciais[0]
            dados["preferenciais_chamadas"] = (
                preferenciais_chamadas + 1
            )

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


def concluir_senha(codigo):

    def operacao(dados):
        senha_dados = _buscar_senha(dados, codigo)

        if senha_dados is None:
            return None, "senha_nao_encontrada"

        senha = Senha.from_dict(senha_dados)

        try:
            senha.concluir()
        except ValueError as erro:
            return None, str(erro)

        senha_dados.update(senha.to_dict())

        return senha, None

    return storage.executar_atomico(operacao)


def rechamar_senha(codigo):

    def operacao(dados):
        senha_dados = _buscar_senha(dados, codigo)

        if senha_dados is None:
            return None, "senha_nao_encontrada"

        senha = Senha.from_dict(senha_dados)

        try:
            senha.rechamar(agora())
        except ValueError as erro:
            return None, str(erro)

        senha_dados.update(senha.to_dict())

        return senha, None

    return storage.executar_atomico(operacao)


def cancelar_senha(codigo):

    def operacao(dados):
        senha_dados = _buscar_senha(dados, codigo)

        if senha_dados is None:
            return None, "senha_nao_encontrada"

        senha = Senha.from_dict(senha_dados)

        try:
            senha.cancelar()
        except ValueError as erro:
            return None, str(erro)

        senha_dados.update(senha.to_dict())

        return senha, None

    return storage.executar_atomico(operacao)


def _buscar_senha(dados, codigo):
    for senha in dados.get("senhas", []):
        if senha["codigo"] == codigo:
            return senha

    return None
