import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import CONFIANCA_ALTA, CONFIANCA_MINIMA

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos"]


class Assistente:
    """Quem conversa com o cidadão: atende, guarda o histórico e calcula indicadores."""

    def __init__(self, nome, base, pasta_dados="data"):
        self.nome = nome
        self.base = base
        self.pasta_dados = pasta_dados
        self.arq_historico = os.path.join(pasta_dados, "historico.json")
        self.arq_notas = os.path.join(pasta_dados, "notas.json")
        self.arq_csv = os.path.join(pasta_dados, "atendimentos.csv")
        self.historico = self._ler_lista(self.arq_historico)
        self.notas = self._ler_lista(self.arq_notas)

    # ---------- arquivos ----------

    def _ler_lista(self, caminho):
        """Lê uma lista de um JSON. Arquivo ausente ou corrompido vira lista vazia."""
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
            print(f"Aviso: {caminho} não tem o formato esperado e será recriado.")
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            print(f"Aviso: não foi possível ler {caminho}. Um novo arquivo será criado.")
        return []

    def _salvar_lista(self, caminho, dados):
        try:
            os.makedirs(self.pasta_dados, exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print(f"Aviso: não foi possível salvar {caminho}.")

    # ---------- entradas do usuário ----------

    def _ler_opcao(self, texto, maximo):
        """Pede um número de 0 até maximo. Repete se a entrada for inválida."""
        while True:
            entrada = input(texto).strip()
            if entrada.isdecimal() and 0 <= int(entrada) <= maximo:
                return int(entrada)
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")

    def _ler_nota(self):
        while True:
            entrada = input("Dê uma nota de 1 a 5 para a facilidade de uso: ").strip()
            if entrada.isdecimal() and 1 <= int(entrada) <= 5:
                return int(entrada)
            print("Nota inválida. Digite um número de 1 a 5.")

    def _ler_sn(self, texto):
        """Pede s ou n. Devolve True para s e False para n."""
        while True:
            resposta = input(texto).strip().lower()
            if resposta == "s":
                return True
            if resposta == "n":
                return False
            print("Resposta inválida. Digite s para sim ou n para não.")

    def _tem_dado_pessoal(self, texto):
        """Bloqueia perguntas com 8 ou mais dígitos ou com @."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return digitos >= 8 or "@" in texto

    # ---------- atendimento ----------

    def iniciar(self):
        """Menu principal."""
        print(f"=== {self.nome} ===")
        print("Orientações para jovens no primeiro emprego.")
        print("Nunca digite nome, CPF, telefone ou e-mail.")
        print("Aviso: este assistente NÃO é um canal oficial.")
        while True:
            print("\nMenu:")
            print("  1. Fazer uma pergunta")
            print("  2. Navegar por categorias")
            print("  3. Ver indicadores")
            print("  4. Exportar atendimentos para CSV")
            print("  0. Sair")
            opcao = self._ler_opcao("Escolha uma opção: ", 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self._sair()
                break

    def perguntar(self):
        """Atendimento por texto livre. Usa base.buscar() e orientacao.exibir()."""
        inicio = None
        tentativas = 0
        ultima_pergunta = ""
        id_encontrado = None
        encontrou = False

        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if texto == "0":
                if tentativas > 0:
                    tempo = round(time.time() - inicio, 1)
                    self.registrar("pergunta", ultima_pergunta, id_encontrado,
                                   encontrou, False, tentativas, tempo)
                return

            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida.")
                continue

            if self._tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            if inicio is None:
                inicio = time.time()
            tentativas += 1
            ultima_pergunta = texto

            resultados = self.base.buscar(texto)
            if not resultados or resultados[0][0] < CONFIANCA_MINIMA:
                encontrou = False
                id_encontrado = None
                self._mostrar_nao_encontrado()
                continue

            pontos, melhor = resultados[0]
            encontrou = True
            id_encontrado = melhor.id
            alternativas = [r for r in resultados[1:3] if r[0] >= CONFIANCA_MINIMA]
            self._mostrar_resposta(pontos, melhor, alternativas)

            if self._ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): "):
                tempo = round(time.time() - inicio, 1)
                self.registrar("pergunta", texto, melhor.id, True, True,
                               tentativas, tempo)
                # começa um novo atendimento
                inicio = None
                tentativas = 0
                ultima_pergunta = ""
                id_encontrado = None
                encontrou = False
            else:
                print("Tente escrever sua dúvida com outras palavras.")

    def _mostrar_resposta(self, pontos, melhor, alternativas):
        if pontos >= CONFIANCA_ALTA:
            nivel = "ALTA"
        else:
            nivel = "MÉDIA"
        print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)\n")
        melhor.exibir()
        if alternativas:
            print("\nTalvez ajude também:")
            for pontos_alt, alternativa in alternativas:
                print(f"  - {alternativa.titulo} ({pontos_alt} pontos)")

    def _mostrar_nao_encontrado(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras, como o nome do documento ou do direito.")
        print("Categorias disponíveis: " + ", ".join(self.base.categorias()))
        print("Você também pode voltar ao menu e usar a navegação por categorias.")

    def navegar(self):
        """Navegação por categorias, com 0 para voltar em todas as telas."""
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias disponíveis.")
            return
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            escolha = self._ler_opcao("Escolha uma categoria: ", len(categorias))
            if escolha == 0:
                return
            self._navegar_orientacoes(categorias[escolha - 1])

    def _navegar_orientacoes(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            inicio = time.time()
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")
            escolha = self._ler_opcao("Escolha uma orientação: ", len(orientacoes))
            if escolha == 0:
                return
            orientacao = orientacoes[escolha - 1]
            print()
            orientacao.exibir()
            ajudou = self._ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", orientacao.titulo, orientacao.id,
                           True, ajudou, 1, tempo)

    # ---------- histórico, indicadores e CSV ----------

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        """Guarda um atendimento em data/historico.json."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
        }
        self.historico.append(atendimento)
        self._salvar_lista(self.arq_historico, self.historico)

    def indicadores(self):
        """Calcula e mostra os indicadores. Devolve um dicionário com os valores."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return None

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudados = [a for a in self.historico if a.get("ajudou")]

        pct_encontrou = round(len(encontrados) / total * 100, 1)
        pct_ajudou = round(len(ajudados) / total * 100, 1)

        if encontrados:
            soma = sum(a.get("tempo_segundos", 0) for a in encontrados)
            tempo_medio = round(soma / len(encontrados), 1)
        else:
            tempo_medio = 0

        soma_tentativas = sum(a.get("tentativas", 0) for a in self.historico)
        tentativas_medias = round(soma_tentativas / total, 1)

        notas_validas = [n for n in self.notas if isinstance(n, int) and 1 <= n <= 5]
        if notas_validas:
            facilidade = round(sum(notas_validas) / len(notas_validas), 1)
        else:
            facilidade = None

        sem_solucao = []
        for atendimento in self.historico:
            pergunta = atendimento.get("pergunta", "")
            if not atendimento.get("ajudou") and pergunta not in sem_solucao:
                sem_solucao.append(pergunta)

        print("\n=== Indicadores ===")
        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada: {pct_encontrou}%")
        print(f"Taxa de acerto (ajudou): {pct_ajudou}%")
        print(f"Tempo médio para encontrar: {tempo_medio} s")
        print(f"Tentativas por atendimento: {tentativas_medias}")
        if facilidade is None:
            print("Facilidade de uso (1 a 5): sem notas ainda")
        else:
            print(f"Facilidade de uso (1 a 5): {facilidade}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  - Nenhuma")

        return {
            "total": total,
            "pct_encontrou": pct_encontrou,
            "pct_ajudou": pct_ajudou,
            "tempo_medio": tempo_medio,
            "tentativas_medias": tentativas_medias,
            "facilidade": facilidade,
            "sem_solucao": sem_solucao,
        }

    def exportar_csv(self):
        """Exporta o histórico para data/atendimentos.csv com csv.DictWriter."""
        if not self.historico:
            print("Não há atendimentos para exportar.")
            return
        try:
            os.makedirs(self.pasta_dados, exist_ok=True)
            with open(self.arq_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            print(f"Atendimentos exportados para {self.arq_csv}")
        except OSError:
            print("Aviso: não foi possível exportar o CSV.")

    def _sair(self):
        print()
        nota = self._ler_nota()
        self.notas.append(nota)
        self._salvar_lista(self.arq_notas, self.notas)
        self.exportar_csv()
        print("Obrigado! Até a próxima.")
