from app.repositories.cliente_repository import ClienteRepository
from app.models.clientes_model import Cliente
import psycopg2

class ClienteService:
    def __init__(self):
        self.repo = ClienteRepository()

    def listar_clientes(self):
        return self.repo.listar_todos()

    def buscar_cliente(self, id_cliente: int):
        return self.repo.buscar_por_id(id_cliente)

    def criar_cliente(self, cpf_cnpj: str, nome: str):
        cpf_cnpj = cpf_cnpj.strip()
        nome = nome.strip()

        if not cpf_cnpj or not nome:
            raise ValueError("❌ CPF/CNPJ e Nome são obrigatórios.")

        # opcional -> evitar duplicidade
        existente = self.repo.buscar_por_cpf_cnpj(cpf_cnpj)
        if existente:
            raise ValueError("❌ Já existe um cliente cadastrado com este CPF/CNPJ.")

        return self.repo.criar_cliente(cpf_cnpj, nome)

    def atualizar_cliente(self, id_cliente: int, cpf_cnpj: str, nome: str):
        cpf_cnpj = cpf_cnpj.strip()
        nome = nome.strip()

        if not cpf_cnpj or not nome:
            raise ValueError("❌ CPF/CNPJ e Nome são obrigatórios para atualizar.")

        cliente_existente = self.repo.buscar_por_id(id_cliente)
        if not cliente_existente:
            raise ValueError(f"❌ Cliente com ID {id_cliente} não encontrado.")

        # opcional -> evitar CPF duplicado em outro cliente
        duplicado = self.repo.buscar_por_cpf_cnpj(cpf_cnpj)
        if duplicado and duplicado.id != id_cliente:
            raise ValueError("❌ CPF/CNPJ já está associado a outro cliente.")

        self.repo.atualizar_cliente(id_cliente, cpf_cnpj, nome)
        return True

    def excluir_cliente(self, id_cliente: int):
        cliente = self.repo.buscar_por_id(id_cliente)
        if not cliente:
            raise ValueError("❌ Cliente não encontrado.")

        try:
            self.repo.excluir_cliente(id_cliente)
            return True

        except psycopg2.errors.ForeignKeyViolation:
            raise ValueError("❌ Não é possível excluir: cliente está vinculado a um ou mais projetos.")

        except Exception as e:
            raise Exception(f"❌ Erro inesperado ao excluir cliente: {e}")
