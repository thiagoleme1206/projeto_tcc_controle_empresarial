from app.models.projeto_model import Projeto
from app.database.db_connection import DatabaseConnection

class ProjetoRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar(self, projeto: Projeto):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO projetos (
                tipo, id_cliente, cliente_nome, cliente_cpf_cnpj, data_os,
                numero_proposta, valor_servico, valor_material, total,
                endereco_obra, cidade_obra, estado_obra, contato,
                nome_responsavel, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING numero_os
        """, (
            projeto.tipo,
            projeto.id_cliente,
            projeto.cliente_nome,
            projeto.cliente_cpf_cnpj,
            projeto.data_os,
            projeto.numero_proposta,
            projeto.valor_servico,
            projeto.valor_material,
            projeto.total,
            projeto.endereco_obra,
            projeto.cidade_obra,
            projeto.estado_obra,
            projeto.contato,
            projeto.nome_responsavel,
            projeto.status
        ))

        numero_os_gerado = cursor.fetchone()[0]
        projeto.numero_os = numero_os_gerado  # atualiza no objeto

        self.conn.commit()
        return numero_os_gerado

    def listar(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                numero_os, tipo, id_cliente, cliente_nome, cliente_cpf_cnpj,
                data_os, numero_proposta, valor_servico, valor_material, total,
                endereco_obra, cidade_obra, estado_obra, contato,
                nome_responsavel, status
            FROM projetos
            ORDER BY data_os DESC
        """)
        rows = cursor.fetchall()
        return [Projeto(*row) for row in rows]

    def buscar_por_os(self, numero_os):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                numero_os, tipo, id_cliente, cliente_nome, cliente_cpf_cnpj,
                data_os, numero_proposta, valor_servico, valor_material, total,
                endereco_obra, cidade_obra, estado_obra, contato,
                nome_responsavel, status
            FROM projetos
            WHERE numero_os = %s
        """, (numero_os,))
        row = cursor.fetchone()
        return Projeto(*row) if row else None

    def atualizar(self, projeto: Projeto):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE projetos SET
                tipo = %s, id_cliente = %s, cliente_nome = %s, cliente_cpf_cnpj = %s,
                data_os = %s, numero_proposta = %s, valor_servico = %s,
                valor_material = %s, total = %s, endereco_obra = %s,
                cidade_obra = %s, estado_obra = %s, contato = %s,
                nome_responsavel = %s, status = %s
            WHERE numero_os = %s
        """, (
            projeto.tipo, projeto.id_cliente, projeto.cliente_nome,
            projeto.cliente_cpf_cnpj, projeto.data_os, projeto.numero_proposta,
            projeto.valor_servico, projeto.valor_material, projeto.total,
            projeto.endereco_obra, projeto.cidade_obra, projeto.estado_obra,
            projeto.contato, projeto.nome_responsavel, projeto.status,
            projeto.numero_os
        ))
        self.conn.commit()

    def deletar(self, numero_os):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projetos WHERE numero_os = %s", (numero_os,))
        self.conn.commit()