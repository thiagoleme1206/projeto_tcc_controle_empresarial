# app/services/projeto_service.py

from app.models.projeto_model import Projeto
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository

class ProjetoService:
    def __init__(self):
        self.repo = ProjetoRepository()
        self.cliente_repo = ClienteRepository()

    # --------------------------------
    # Helpers e validadores
    # --------------------------------

    def _to_float(self, valor, default=0.0):
        try:
            return float(valor)
        except (TypeError, ValueError):
            return default

    def _validar_uf(self, uf):
        if not uf or len(uf.strip()) != 2:
            raise ValueError("❌ O estado (UF) deve conter exatamente 2 letras.")

    def _validar_campos_obrigatorios(self, projeto: Projeto):
        if not projeto.tipo or not projeto.tipo.strip():
            raise ValueError("❌ O tipo do projeto é obrigatório.")

        if not projeto.numero_proposta or not projeto.numero_proposta.strip():
            raise ValueError("❌ O número da proposta é obrigatório.")

        if not projeto.cliente_nome or not projeto.cliente_nome.strip():
            raise ValueError("❌ O nome do cliente é obrigatório.")

        if not projeto.cliente_cpf_cnpj or not projeto.cliente_cpf_cnpj.strip():
            raise ValueError("❌ O CPF/CNPJ do cliente é obrigatório.")

        if not projeto.data_os:
            raise ValueError("❌ A data da OS é obrigatória.")

        self._validar_uf(projeto.estado_obra)

    def _normalizar_numeros(self, projeto: Projeto):
        projeto.valor_servico = self._to_float(projeto.valor_servico)
        projeto.valor_material = self._to_float(projeto.valor_material)
        projeto.total = self._to_float(projeto.total)

        # Se total não for informado, recalcula corretamente
        if projeto.total == 0:
            projeto.total = projeto.valor_servico + projeto.valor_material

    def _validar_cliente(self, id_cliente):
        cliente = self.cliente_repo.buscar_por_id(id_cliente)
        if not cliente:
            raise ValueError("❌ Cliente informado não está cadastrado.")
        return cliente

    def _validar_projeto_existe(self, numero_os):
        projeto = self.repo.buscar_por_os(numero_os)
        if not projeto:
            raise ValueError(f"❌ Projeto com número OS {numero_os} não encontrado.")
        return projeto

    # --------------------------------
    # Operações principais
    # --------------------------------

    def criar_projeto(self, projeto: Projeto):
        # Valida cliente
        self._validar_cliente(projeto.id_cliente)

        # Valida campos obrigatórios
        self._validar_campos_obrigatorios(projeto)

        # Normaliza valores numéricos
        self._normalizar_numeros(projeto)

        # Cria projeto e retorna o número da OS
        return self.repo.criar(projeto)

    def listar_projetos(self):
        return self.repo.listar()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def atualizar_projeto(self, projeto: Projeto):
        # Garante que o projeto existe
        self._validar_projeto_existe(projeto.numero_os)

        # Reaplica validação e normalização
        self._validar_campos_obrigatorios(projeto)
        self._normalizar_numeros(projeto)

        self.repo.atualizar(projeto)

    def excluir_projeto(self, numero_os: int):
        self._validar_projeto_existe(numero_os)
        self.repo.deletar(numero_os)
        return True
