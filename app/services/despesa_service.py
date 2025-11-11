# app/services/despesa_service.py

from app.repositories.despesa_repository import DespesaRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.models.despesa_model import Despesa

class DespesaService:
    def __init__(self):
        self.repo = DespesaRepository()
        self.projeto_repo = ProjetoRepository()

    def _converter_para_zero(self, valor):
        try:
            return float(valor) if valor is not None else 0.0
        except ValueError:
            return 0.0

    def validar_os_existente(self, numero_os_projeto):
        projeto = self.projeto_repo.buscar_por_os(numero_os_projeto)
        if not projeto:
            raise ValueError("❌ Número de OS não encontrado no sistema.")
        return True

    def criar_despesa(self, despesa: Despesa):
        self.validar_os_existente(despesa.numero_os_projeto)

        # Converte todos os valores numéricos nulos ou vazios para zero
        despesa.mao_de_obra = self._converter_para_zero(despesa.mao_de_obra)
        despesa.alimentacao = self._converter_para_zero(despesa.alimentacao)
        despesa.hospedagem = self._converter_para_zero(despesa.hospedagem)
        despesa.viagem = self._converter_para_zero(despesa.viagem)
        despesa.seguranca_trabalho = self._converter_para_zero(despesa.seguranca_trabalho)
        despesa.material = self._converter_para_zero(despesa.material)
        despesa.equipamento = self._converter_para_zero(despesa.equipamento)
        despesa.andaime = self._converter_para_zero(despesa.andaime)
        despesa.documentacao = self._converter_para_zero(despesa.documentacao)
        despesa.outros = self._converter_para_zero(despesa.outros)

        return self.repo.criar(despesa)

    def listar_despesas(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os_projeto):
        return self.repo.buscar_por_os(numero_os_projeto)

    def buscar_por_id(self, id_despesa):
        return self.repo.buscar_por_id(id_despesa)

    def atualizar_despesa(self, despesa: Despesa):
        self.validar_os_existente(despesa.numero_os_projeto)

        despesa.mao_de_obra = self._converter_para_zero(despesa.mao_de_obra)
        despesa.alimentacao = self._converter_para_zero(despesa.alimentacao)
        despesa.hospedagem = self._converter_para_zero(despesa.hospedagem)
        despesa.viagem = self._converter_para_zero(despesa.viagem)
        despesa.seguranca_trabalho = self._converter_para_zero(despesa.seguranca_trabalho)
        despesa.material = self._converter_para_zero(despesa.material)
        despesa.equipamento = self._converter_para_zero(despesa.equipamento)
        despesa.andaime = self._converter_para_zero(despesa.andaime)
        despesa.documentacao = self._converter_para_zero(despesa.documentacao)
        despesa.outros = self._converter_para_zero(despesa.outros)

        self.repo.atualizar(despesa)

    def excluir_despesa(self, id_despesa):
        return self.repo.excluir(id_despesa)
