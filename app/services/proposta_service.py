from app.repositories.proposta_repository import PropostaRepository
from app.models.proposta_model import Proposta

class PropostaService:
    def __init__(self):
        self.repo = PropostaRepository()

    def listar_propostas(self):
        return self.repo.listar_todas()

    def cadastrar_proposta(self, titulo, descricao, valor, status):
        proposta = Proposta(None, titulo, descricao, valor, status, None)
        self.repo.inserir(proposta)

    def atualizar_proposta(self, id, titulo, descricao, valor, status):
        proposta = Proposta(id, titulo, descricao, valor, status, None)
        self.repo.atualizar(proposta)

    def deletar_proposta(self, id):
        self.repo.deletar(id)
