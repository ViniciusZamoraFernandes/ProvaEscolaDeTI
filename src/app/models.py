from dataclasses import dataclass


TIPOS_VALIDOS = {
    "normal",
    "preferencial",
}

STATUS_VALIDOS = {
    "aguardando",
    "chamada",
    "concluida",
    "cancelada",
}


@dataclass
class Senha:
    codigo: str
    tipo: str
    emissao: str
    status: str
    chamada_em: str | None = None

    def __post_init__(self):
        if self.tipo not in TIPOS_VALIDOS:
            raise ValueError("tipo_invalido")

        if self.status not in STATUS_VALIDOS:
            raise ValueError("status_invalido")

    def to_dict(self) -> dict:
        dados = {
            "codigo": self.codigo,
            "tipo": self.tipo,
            "emissao": self.emissao,
            "status": self.status,
        }

        if self.chamada_em is not None:
            dados["chamada_em"] = self.chamada_em

        return dados

    @classmethod
    def from_dict(cls, dados: dict):
        return cls(
            codigo=dados["codigo"],
            tipo=dados["tipo"],
            emissao=dados["emissao"],
            status=dados["status"],
            chamada_em=dados.get("chamada_em"),
        )

    def concluir(self):
        if self.status != "chamada":
            raise ValueError("senha_nao_chamada")

        self.status = "concluida"

    def rechamar(self, chamada_em: str):
        if self.status != "chamada":
            raise ValueError("senha_nao_chamada")

        self.status = "chamada"
        self.chamada_em = chamada_em

    def cancelar(self):
        if self.status != "aguardando":
            raise ValueError("senha_nao_aguardando")
