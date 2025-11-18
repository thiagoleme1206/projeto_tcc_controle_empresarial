from app.models.orcamento_model import Orcamento
from app.repositories.orcamento_repository import OrcamentoRepository
from app.repositories.projeto_repository import ProjetoRepository

class OrcamentoService:
    def __init__(self):
        self.repo = OrcamentoRepository()
        self.projeto_repo = ProjetoRepository()

    # --------------------------------
    # Helpers
    # --------------------------------

    def _to_float(self, value, default=0.0):
        """Converte valores numéricos com segurança."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _validar_campos_numericos(self, orcamento: Orcamento):
        """Normaliza campos numéricos evitando erros na UI."""
        orcamento.mao_de_obra = self._to_float(orcamento.mao_de_obra)
        orcamento.alimentacao = self._to_float(orcamento.alimentacao)
        orcamento.hospedagem = self._to_float(orcamento.hospedagem)
        orcamento.viagem = self._to_float(orcamento.viagem)
        orcamento.seguranca_trabalho = self._to_float(orcamento.seguranca_trabalho)
        orcamento.material = self._to_float(orcamento.material)
        orcamento.equipamento = self._to_float(orcamento.equipamento)
        orcamento.andaime = self._to_float(orcamento.andaime)
        orcamento.documentacao = self._to_float(orcamento.documentacao)
        orcamento.outros = self._to_float(orcamento.outros)

    def _os_existe(self, numero_os):
        """Verifica se a OS existe no sistema."""
        return self.projeto_repo.buscar_por_os(numero_os) is not None

    def _validar_orcamento_existe(self, id_orcamento):
        orc = self.repo.buscar_por_id(id_orcamento)
        if not orc:
            raise ValueError(f"❌ Orçamento com ID {id_orcamento} não encontrado.")
        return orc

    # --------------------------------
    # Operações principais
    # --------------------------------

    def criar_orcamento(self, orcamento: Orcamento):
        if not self._os_existe(orcamento.numero_os):
            raise ValueError("❌ OS informada não está cadastrada no sistema.")

        self._validar_campos_numericos(orcamento)

        return self.repo.criar(orcamento)

    def listar_orcamentos(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def buscar_por_id(self, id_orcamento: int):
        return self.repo.buscar_por_id(id_orcamento)

    def atualizar_orcamento(self, orcamento: Orcamento):
        # Verifica existência da OS
        if not self._os_existe(orcamento.numero_os):
            raise ValueError("❌ OS informada não pertence a nenhum projeto registrado.")

        # Verifica se o orçamento existe
        self._validar_orcamento_existe(orcamento.id_orcamento)

        self._validar_campos_numericos(orcamento)

        self.repo.atualizar(orcamento)

    def excluir_orcamento(self, id_orcamento: int):
        self._validar_orcamento_existe(id_orcamento)
        return self.repo.excluir(id_orcamento)
