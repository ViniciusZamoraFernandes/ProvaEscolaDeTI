from datetime import datetime, timezone, timedelta

from app.models import Senha, TipoSenha, StatusSenha
from app.storage import storage


FUSO = timezone(timedelta(hours=-3))

RAZAO_PREFERENCIAL = 2


def agora() -> datetime:
    return datetime.now(FUSO)


def emitir_senha(tipo: TipoSenha) -> Senha:
    data_atual = agora().date().isoformat()

    def operacao(dados: dict):
        if dados.get("data") != data_atual:
            dados["data"] = data_atual
            dados["sequencia"] = 0

        dados["sequencia"] += 1

        codigo = f"E{dados['sequencia']:03d}"

        senha = Senha(
            codigo=codigo,
            tipo=tipo,
            emissao=agora(),
            status=StatusSenha.AGUARDANDO,
        )

        dados.setdefault("senhas", [])
        dados["senhas"].append(senha.to_dict())

        return senha

    return storage.executar_atomico(operacao)


def obter_proxima_senha() -> Senha | None:

    def operacao(dados: dict):
        senhas = dados.get("senhas", [])

        aguardando = [
            senha
            for senha in senhas
            if senha["status"] == StatusSenha.AGUARDANDO.value
        ]

        if not aguardando:
            return None

        preferenciais = [
            senha
            for senha in aguardando
            if senha["tipo"] == TipoSenha.PREFERENCIAL.value
        ]

        normais = [
            senha
            for senha in aguardando
            if senha["tipo"] == TipoSenha.NORMAL.value
        ]

        preferenciais_chamadas = 0

        for senha in reversed(senhas):
            if senha["status"] != StatusSenha.CHAMADA.value:
                continue

            if senha["tipo"] == TipoSenha.PREFERENCIAL.value:
                preferenciais_chamadas += 1
            else:
                break

        if preferenciais and (
            preferenciais_chamadas < RAZAO_PREFERENCIAL
            or not normais
        ):
            proxima = preferenciais[0]
        else:
            proxima = normais[0]

        proxima["status"] = StatusSenha.CHAMADA.value
        proxima["chamada_em"] = agora().isoformat()

        return Senha.model_validate(proxima)

    return storage.executar_atomico(operacao)


def obter_painel() -> list[Senha]:

    dados = storage.carregar()

    chamadas = [
        senha
        for senha in dados.get("senhas", [])
        if senha["status"] in (
            StatusSenha.CHAMADA.value,
            StatusSenha.CONCLUIDA.value,
        )
    ]

    chamadas.sort(
        key=lambda senha: senha.get("chamada_em", ""),
        reverse=True,
    )

    return [
        Senha.model_validate(senha)
        for senha in chamadas[:5]
    ]
