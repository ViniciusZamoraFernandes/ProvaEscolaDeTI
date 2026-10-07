import json
import threading

from app.config import ARQUIVO_DADOS, DATA_DIR


class Storage:
    def __init__(self):
        self.lock = threading.Lock()

        self.memoria = {
            "data": None,
            "sequencia": 0,
            "senhas": [],
        }

        self.usar_arquivo = self._inicializar()

    def _inicializar(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)

            if ARQUIVO_DADOS.exists():
                self.memoria = self._carregar_arquivo()
            else:
                self._salvar_arquivo(self.memoria)

            return True

        except (OSError, json.JSONDecodeError):
            return False

    def _carregar_arquivo(self):
        with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def _salvar_arquivo(self, dados):
        arquivo_temporario = ARQUIVO_DADOS.with_suffix(".tmp")

        with arquivo_temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=2,
            )

        arquivo_temporario.replace(ARQUIVO_DADOS)

    def executar_atomico(self, operacao):
        with self.lock:

            if self.usar_arquivo:
                try:
                    self.memoria = self._carregar_arquivo()
                except (OSError, json.JSONDecodeError):
                    self.usar_arquivo = False

            resultado = operacao(self.memoria)

            if self.usar_arquivo:
                try:
                    self._salvar_arquivo(self.memoria)
                except OSError:
                    self.usar_arquivo = False

            return resultado

    def ler(self):
        with self.lock:

            if self.usar_arquivo:
                try:
                    self.memoria = self._carregar_arquivo()
                except (OSError, json.JSONDecodeError):
                    self.usar_arquivo = False

            return self.memoria.copy()


storage = Storage()
