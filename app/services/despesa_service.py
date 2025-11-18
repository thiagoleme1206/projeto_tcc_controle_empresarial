from app.repositories.despesa_repository import DespesaRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.models.despesa_model import Despesa

class DespesaService:
    CAMPOS_VALORES = [
        "mao_de_obra", "alimentacao", "hospedagem", "viagem", "seguranca_trabalho",
        "material", "equipamento", "andaime", "documentacao", "outros"
    ]

    def __init__(self):
        self.repo = DespesaRepository()
        self.projeto_repo = ProjetoRepository()

    # -------------------------------------
    # 🔧 Conversores / Validadores privados
    # -------------------------------------

    def _converter_para_zero(self, valor):
        try:
            return float(valor) if valor not in (None, "") else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _padronizar_valores(self, despesa: Despesa):
        """
        Converte todos os campos numéricos da lista CAMPOS_VALORES para float,
        evitando repetição de código.
        """
        for campo in self.CAMPOS_VALORES:
            valor = getattr(despesa, campo)
            setattr(despesa, campo, self._converter_para_zero(valor))

    def _validar_os_existente(self, numero_os_projeto):
        if not self.projeto_repo.buscar_por_os(numero_os_projeto):
            raise ValueError("❌ Número de OS não encontrado no sistema.")
        return True

    # -------------------------------------
    # Métodos públicos
    # -------------------------------------

    def criar_despesa(self, despesa: Despesa):
        self._validar_os_existente(despesa.numero_os_projeto)
        self._padronizar_valores(despesa)
        return self.repo.criar(despesa)

    def listar_despesas(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os_projeto):
        return self.repo.buscar_por_os(numero_os_projeto)

    def buscar_por_id(self, id_despesa):
        return self.repo.buscar_por_id(id_despesa)

    def atualizar_despesa(self, despesa: Despesa):
        self._validar_os_existente(despesa.numero_os_projeto)
        self._padronizar_valores(despesa)
        self.repo.atualizar(despesa)
        return True

    def excluir_despesa(self, id_despesa: int):
        return self.repo.excluir(id_despesa)
