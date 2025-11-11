from app.models.projeto_model import Projeto
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository

class ProjetoService:
    def __init__(self):
        self.repo = ProjetoRepository()
        self.cliente_repo = ClienteRepository()

    def criar_projeto(self, projeto: Projeto):
        # 🔍 Validação: cliente deve existir
        cliente = self.cliente_repo.buscar_por_id(projeto.id_cliente)
        if not cliente:
            raise ValueError("Cliente informado não existe.")

        # 🔍 Validações de campos obrigatórios
        if not projeto.numero_proposta or not projeto.numero_proposta.strip():
            raise ValueError("Número da proposta é obrigatório.")
        if not projeto.tipo.strip():
            raise ValueError("Tipo do projeto é obrigatório.")
        if not projeto.cliente_nome.strip():
            raise ValueError("Nome do cliente é obrigatório.")
        if not projeto.cliente_cpf_cnpj.strip():
            raise ValueError("CPF/CNPJ do cliente é obrigatório.")
        if not projeto.data_os:
            raise ValueError("Data da OS é obrigatória.")
        if not projeto.estado_obra or len(projeto.estado_obra.strip()) != 2:
            raise ValueError("Estado da obra deve ter 2 letras (UF).")

        # 🔢 Calcula total se necessário
        if projeto.total is None:
            projeto.total = (projeto.valor_servico or 0) + (projeto.valor_material or 0)

        # ✅ Cria o projeto e retorna o número gerado
        numero_os = self.repo.criar(projeto)
        return numero_os

    def listar_projetos(self):
        return self.repo.listar()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def atualizar_projeto(self, projeto: Projeto):
        existente = self.repo.buscar_por_os(projeto.numero_os)
        if not existente:
            raise ValueError(f"Projeto com OS {projeto.numero_os} não encontrado.")
        if not projeto.estado_obra or len(projeto.estado_obra.strip()) != 2:
            raise ValueError("UF inválido. Deve conter 2 letras.")
        if projeto.total is None:
            projeto.total = (projeto.valor_servico or 0) + (projeto.valor_material or 0)
        self.repo.atualizar(projeto)

    def excluir_projeto(self, numero_os: int):
        existente = self.repo.buscar_por_os(numero_os)
        if not existente:
            return False
        self.repo.deletar(numero_os)
        return True