class Projeto:
    def __init__(
        self,
        numero_os,
        tipo,
        id_cliente,
        cliente_nome,
        cliente_cpf_cnpj,
        data_os,
        numero_proposta,
        valor_servico,
        valor_material,
        total,
        endereco_obra,
        cidade_obra,
        estado_obra,
        contato,
        nome_responsavel,
        status
    ):
        self.numero_os = numero_os
        self.tipo = tipo
        self.id_cliente = id_cliente
        self.cliente_nome = cliente_nome
        self.cliente_cpf_cnpj = cliente_cpf_cnpj
        self.data_os = data_os
        self.numero_proposta = numero_proposta
        self.valor_servico = valor_servico
        self.valor_material = valor_material
        self.total = total
        self.endereco_obra = endereco_obra
        self.cidade_obra = cidade_obra
        self.estado_obra = estado_obra
        self.contato = contato
        self.nome_responsavel = nome_responsavel
        self.status = status