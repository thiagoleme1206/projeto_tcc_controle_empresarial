# app/models/receita_model.py

class Receita:
    def __init__(
        self,
        numero_os_projeto,
        data_receita,
        nf,
        cliente,
        valor_servico=None,
        valor_material=None,
        imposto=None,
        icms=None,
        valor_liquido=None,  # <-- agora é um atributo comum
        id_receita=None
    ):
        self.id_receita = id_receita
        self.numero_os_projeto = numero_os_projeto
        self.data_receita = data_receita
        self.nf = nf
        self.cliente = cliente
        self.valor_servico = valor_servico
        self.valor_material = valor_material
        self.imposto = imposto
        self.icms = icms
        self.valor_liquido = valor_liquido  # <-- será setado no service
