from app.repositories.cliente_repository import ClienteRepository
from app.models.clientes_model import Cliente
import psycopg2

class ClienteService:
    def __init__(self):
        self.repo = ClienteRepository()

    def listar_clientes(self):
        return self.repo.listar_todos()

    def buscar_cliente(self, id_cliente):
        return self.repo.buscar_por_id(id_cliente)

    def criar_cliente(self, cpf_cnpj, nome):
        cpf_cnpj = cpf_cnpj.strip()
        nome = nome.strip()

        if not cpf_cnpj or not nome:
            raise ValueError("❌ CPF/CNPJ e Nome são obrigatórios e não podem estar em branco.")

        return self.repo.criar_cliente(cpf_cnpj, nome)

    def atualizar_cliente(self, id_cliente, cpf_cnpj, nome):
        cpf_cnpj = cpf_cnpj.strip()
        nome = nome.strip()

        if not cpf_cnpj or not nome:
            raise ValueError("❌ CPF/CNPJ e Nome são obrigatórios para atualização.")

        cliente_existente = self.repo.buscar_por_id(id_cliente)
        if not cliente_existente:
            raise ValueError(f"❌ Cliente com ID {id_cliente} não encontrado.")

        self.repo.atualizar_cliente(id_cliente, cpf_cnpj, nome)

    def excluir_cliente(self, id_cliente):
        cliente = self.repo.buscar_por_id(id_cliente)
        if not cliente:
            return None
        try:
            self.repo.excluir_cliente(id_cliente)
            return True
        except psycopg2.errors.ForeignKeyViolation:
            raise ValueError("❌ Este cliente está vinculado a um ou mais projetos e não pode ser excluído.")
    