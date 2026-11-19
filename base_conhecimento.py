import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c",
           "º": "o", "ª": "a"}

# Palavras comuns que não ajudam a achar o título (ajuste explicado no README)
PALAVRAS_COMUNS = ["como", "para", "qual", "quais", "onde", "quando",
                   "preciso", "posso", "quero", "tenho", "minha", "quanto"]

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
CONFIANCA_ALTA = 6
CONFIANCA_MINIMA = 3


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação, com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Devolve True se deu certo."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Erro: o arquivo {self.caminho} não foi encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"Erro: o arquivo {self.caminho} está corrompido.")
            return False
        except OSError:
            print(f"Erro: não foi possível abrir {self.caminho}.")
            return False

        if not isinstance(dados, list):
            print("Erro: a base de conhecimento deve ser uma lista de orientações.")
            return False

        for registro in dados:
            if self._registro_valido(registro):
                campos = {campo: registro[campo] for campo in CAMPOS}
                self.orientacoes.append(Orientacao(**campos))
            else:
                print("Aviso: um registro incompleto da base foi ignorado.")

        return len(self.orientacoes) > 0

    def _registro_valido(self, registro):
        if not isinstance(registro, dict):
            return False
        for campo in CAMPOS:
            if campo not in registro:
                return False
        if not isinstance(registro["palavras_chave"], list):
            return False
        if not isinstance(registro["documentos"], list):
            return False
        return True

    def categorias(self):
        """Lista as categorias, sem repetir, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Calcula os pontos de uma orientação para uma pergunta."""
        texto = normalizar(pergunta)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in texto:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        ja_contadas = []
        for palavra in texto.split():
            if len(palavra) < 4 or palavra in PALAVRAS_COMUNS:
                continue
            if palavra in ja_contadas:
                continue
            ja_contadas.append(palavra)
            if " " + palavra + " " in titulo:
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))

        def pegar_pontos(tupla):
            return tupla[0]

        resultados.sort(key=pegar_pontos, reverse=True)
        return resultados
