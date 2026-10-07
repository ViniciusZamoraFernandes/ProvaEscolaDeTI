from datetime import datetime, timezone, timedelta

from app.config import PREFIXO
from app.models import Senha, TipoSenha, StatusSenha
from app.storage import storage


FUSO = timezone(timedelta(hours=-3))


def agora() -> datetime:
    return datetime.now(FUSO)


def emitir_senha(tipo: TipoSenha) -> Senha:
    data_atual = agora().date().isoformat()

    def operacao(dados: dict):
        if dados.get("data") != data_atual:
            dados["data"] = data_atual
            dados["sequencia"] = 0

        dados["sequencia"] += 1

        codigo = f"{PREFIXO}{dados['sequencia']:03d}"

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
