from app.models.orcamento_model import Orcamento
from app.repositories.orcamento_repository import OrcamentoRepository
from app.repositories.projeto_repository import ProjetoRepository

class OrcamentoService:
    def __init__(self):
        self.repo = OrcamentoRepository()
        self.projeto_repo = ProjetoRepository()

    def validar_os_existe(self, numero_os):
        projeto = self.projeto_repo.buscar_por_os(numero_os)
        return projeto is not None

    def criar_orcamento(self, orcamento: Orcamento):
        if not self.validar_os_existe(orcamento.numero_os):
            raise ValueError("OS não localizada no sistema.")
        return self.repo.criar(orcamento)

    def listar_orcamentos(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def buscar_por_id(self, id_orcamento: int):
        return self.repo.buscar_por_id(id_orcamento)

    def atualizar_orcamento(self, orcamento: Orcamento):
        if not self.validar_os_existe(orcamento.numero_os):
            raise ValueError("OS não localizada para este orçamento.")
        self.repo.atualizar(orcamento)

    def excluir_orcamento(self, id_orcamento: int):
        return self.repo.excluir(id_orcamento)
