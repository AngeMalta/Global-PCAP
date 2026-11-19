import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(PASTA_DADOS, "base_conhecimento.json"))
    if not base.carregar():  # lê o JSON e cria os objetos Orientacao
        print("Não foi possível carregar a base de conhecimento.")
        print("Verifique o arquivo data/base_conhecimento.json e tente de novo.")
        return

    assistente = Assistente("Citizen Assist AI", base, PASTA_DADOS)
    try:
        assistente.iniciar()
    except (KeyboardInterrupt, EOFError):
        print("\nAtendimento encerrado.")


if __name__ == "__main__":
    main()
