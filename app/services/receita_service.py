# app/services/receita_service.py

from app.models.receita_model import Receita
from app.repositories.receita_repository import ReceitaRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository

class ReceitaService:
    def __init__(self):
        self.repo = ReceitaRepository()
        self.projeto_repo = ProjetoRepository()
        self.cliente_repo = ClienteRepository()

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _to_float(self, valor, default=0.0):
        """Converte valores para float de forma segura."""
        if valor is None:
            return default
        try:
            # suporta "1.234,50"
            valor = str(valor).replace(".", "").replace(",", ".")
            return float(valor)
        except ValueError:
            return default

    def _validar_os_existente(self, numero_os):
        projeto = self.projeto_repo.buscar_por_os(numero_os)
        if not projeto:
            raise ValueError("❌ Número de OS não localizado na base de projetos.")
        return projeto

    def _validar_receita_existe(self, id_receita):
        receita = self.repo.buscar_por_id(id_receita)
        if not receita:
            raise ValueError(f"❌ Receita com ID {id_receita} não encontrada.")
        return receita

    def _calcular_valor_liquido(self, receita: Receita):
        servico = self._to_float(receita.valor_servico)
        material = self._to_float(receita.valor_material)
        perc_imposto = self._to_float(receita.imposto)
        perc_icms = self._to_float(receita.icms)

        if servico > 0:
            valor_imposto = servico * (perc_imposto / 100)
            receita.valor_liquido = servico - valor_imposto
            return

        if material > 0:
            valor_imposto = material * (perc_imposto / 100)
            base_icms = material - valor_imposto
            valor_icms = base_icms * (perc_icms / 100)
            receita.valor_liquido = material - valor_imposto - valor_icms
            return

        receita.valor_liquido = 0.0

    # ---------------------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------------------

    def criar_receita(self, receita: Receita):
        # valida OS
        self._validar_os_existente(receita.numero_os_projeto)

        # recalcula
        self._calcular_valor_liquido(receita)

        return self.repo.criar(receita)

    def listar_receitas(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def buscar_por_id(self, id_receita: int):
        return self.repo.buscar_por_id(id_receita)

    def atualizar_receita(self, receita: Receita):
        # Verifica se a receita existe
        self._validar_receita_existe(receita.id_receita)

        # Verifica OS
        self._validar_os_existente(receita.numero_os_projeto)

        # Recalcula liquido
        self._calcular_valor_liquido(receita)

        self.repo.atualizar(receita)
        return True

    def excluir_receita(self, id_receita: int):
        self._validar_receita_existe(id_receita)
        return self.repo.excluir(id_receita)
