# app/services/relatorio_service.py

from datetime import datetime
from tkinter import Tk, filedialog

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors

from app.repositories.orcamento_repository import OrcamentoRepository
from app.repositories.despesa_repository import DespesaRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository


class RelatorioService:
    def __init__(self):
        self.projeto_repo = ProjetoRepository()
        self.cliente_repo = ClienteRepository()
        self.orc_repo = OrcamentoRepository()
        self.desp_repo = DespesaRepository()

    # ---------------------------------------------------------------------
    #     BUSCAS
    # ---------------------------------------------------------------------

    def buscar_projeto_com_cliente(self, numero_os):
        projeto = self.projeto_repo.buscar_por_os(numero_os)
        if not projeto:
            return None

        cliente = self.cliente_repo.buscar_por_id(projeto.id_cliente)

        return {
            "numero_os": projeto.numero_os,
            "cliente": cliente.nome if cliente else "Não cadastrado",
            "endereco": projeto.endereco_obra,
            "responsavel": projeto.nome_responsavel
        }

    def buscar_orcamento(self, numero_os):
        dados = self.orc_repo.buscar_por_os(numero_os)
        if not dados:
            return None
        return [
            float(dados.mao_de_obra or 0),
            float(dados.alimentacao or 0),
            float(dados.hospedagem or 0),
            float(dados.viagem or 0),
            float(dados.seguranca_trabalho or 0),
            float(dados.material or 0),
            float(dados.equipamento or 0),
            float(dados.andaime or 0),
            float(dados.documentacao or 0),
            float(dados.outros or 0),
        ]

    def buscar_despesas(self, numero_os):
        dados = self.desp_repo.buscar_por_os(numero_os)
        if not dados:
            return None
        return [
            float(dados.mao_de_obra or 0),
            float(dados.alimentacao or 0),
            float(dados.hospedagem or 0),
            float(dados.viagem or 0),
            float(dados.seguranca_trabalho or 0),
            float(dados.material or 0),
            float(dados.equipamento or 0),
            float(dados.andaime or 0),
            float(dados.documentacao or 0),
            float(dados.outros or 0),
        ]

    # ---------------------------------------------------------------------
    #     GRÁFICOS
    # ---------------------------------------------------------------------

    def criar_grafico_barras(self, orcamento, despesas):
        d = Drawing(500, 300)

        itens = [
            "Mão-de-obra", "Alimentação", "Hospedagem", "Viagem",
            "Segurança", "Material", "Equipamento", "Andaime",
            "Documento", "Outros"
        ]

        data = [
            orcamento or [0]*10,
            despesas or [0]*10
        ]

        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 200
        bc.width = 400
        bc.data = data
        bc.strokeColor = colors.black
        bc.categoryAxis.categoryNames = itens
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontSize = 6

        bc.bars[0].fillColor = colors.green
        bc.bars[1].fillColor = colors.red

        legend = Legend()
        legend.x = 400
        legend.y = 270
        legend.fontSize = 8
        legend.colorNamePairs = [
            (colors.green, "Orçado"),
            (colors.red, "Realizado")
        ]

        d.add(bc)
        d.add(legend)
        d.add(String(250, 280, "Comparativo Orçado vs Realizado", fontSize=10, textAnchor='middle'))
        return d

    def criar_grafico_pizza(self, despesas):
        d = Drawing(400, 300)

        itens = [
            "Mão-de-obra", "Alimentação", "Hospedagem", "Viagem",
            "Segurança", "Material", "Equipamento", "Andaime",
            "Documento", "Outros"
        ]

        cores = [
            colors.blue, colors.green, colors.red, colors.yellow,
            colors.purple, colors.orange, colors.cyan, colors.pink,
            colors.gray, colors.brown
        ]

        data = []
        labels = []

        for i, valor in enumerate(despesas):
            if valor > 0:
                data.append(valor)
                labels.append(itens[i])

        if not data:
            d.add(String(200, 150, "Sem dados de despesas", fontSize=10, textAnchor='middle'))
            return d

        pie = Pie()
        pie.x = 100
        pie.y = 50
        pie.width = 200
        pie.height = 200
        pie.data = data
        pie.labels = labels
        pie.slices.fontSize = 8

        for i in range(len(data)):
            pie.slices[i].fillColor = cores[i % len(cores)]

        d.add(pie)
        d.add(String(200, 270, "Distribuição das Despesas", fontSize=10, textAnchor='middle'))
        return d

    # ---------------------------------------------------------------------
    #     GERAÇÃO DO RELATÓRIO
    # ---------------------------------------------------------------------

    def gerar_relatorio_por_os(self, numero_os):
        projeto = self.buscar_projeto_com_cliente(numero_os)
        if not projeto:
            raise ValueError("❌ OS não localizada.")

        orcamento = self.buscar_orcamento(numero_os)
        despesas = self.buscar_despesas(numero_os)

        # janela de escolha de arquivo
        root = Tk()
        root.withdraw()

        filename = f"Relatorio_Financeiro_OS_{numero_os}.pdf"
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename,
            title="Salvar relatório em..."
        )

        if not caminho:
            raise Exception("❌ Salvamento cancelado.")

        # cria PDF
        c = canvas.Canvas(caminho, pagesize=letter)

        y = 750

        # Cabeçalho
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Relatório Financeiro - OS {projeto['numero_os']}")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Cliente: {projeto['cliente']}")
        y -= 20
        c.drawString(50, y, f"Endereço: {projeto['endereco']}")
        y -= 20
        c.drawString(50, y, f"Responsável: {projeto['responsavel']}")
        y -= 40

        # Barras
        self.criar_grafico_barras(orcamento, despesas).drawOn(c, 50, y - 300)

        # Nova página
        c.showPage()
        self.criar_grafico_pizza(despesas).drawOn(c, 100, 400)

        c.setFont("Helvetica", 9)
        c.drawString(50, 30, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        c.save()

        print(f"✅ Relatório salvo em: {caminho}")
        return caminho
