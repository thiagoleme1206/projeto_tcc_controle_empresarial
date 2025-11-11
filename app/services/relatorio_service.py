# app/services/relatorio_service.py

from app.database.db_connection import DatabaseConnection
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from tkinter import Tk, filedialog
import os

class RelatorioService:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def buscar_projeto_por_os(self, numero_os):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.numero_os, c.nome, p.endereco_obra, p.nome_responsavel
            FROM projetos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.numero_os = %s
        """, (numero_os,))
        return cursor.fetchone()

    def buscar_dados_orcamento(self, numero_os):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mao_de_obra, alimentacao, hospedagem, viagem,
                   seguranca_trabalho, material, equipamento, andaime,
                   documentacao, outros
            FROM orcamentos
            WHERE numero_os_projeto = %s
        """, (numero_os,))
        return cursor.fetchone()

    def buscar_dados_despesas(self, numero_os):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                   material, equipamento, andaime, documentacao, outros
            FROM despesas
            WHERE numero_os_projeto = %s
        """, (numero_os,))
        return cursor.fetchone()

    def criar_grafico_barras(self, orcamento, despesas):
        d = Drawing(500, 300)
        itens = ["Mão-de-obra", "Alimentação", "Hospedagem", "Viagem", 
                "Segurança", "Material", "Equipamento", "Andaime", 
                "Documentação", "Outros"]

        # Certificando-se de que estamos manipulando corretamente os valores
        data_orcado = [float(v or 0) for v in orcamento]  # Convertendo valores de orcamento
        data_realizado = [float(despesas[i] or 0) for i in range(10)]  # Corrigindo acesso a despesas

        # Gráfico de barras comparando orçado vs realizado
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 200
        bc.width = 400
        bc.data = [data_orcado, data_realizado]
        bc.strokeColor = colors.black
        bc.categoryAxis.categoryNames = itens
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontSize = 6
        bc.bars[0].fillColor = colors.green  # Cor para orçado
        bc.bars[1].fillColor = colors.red  # Cor para realizado

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

    def criar_grafico_pizza_despesas(self, despesas):
        d = Drawing(400, 300)
        itens = ["Mão-de-obra", "Alimentação", "Hospedagem", "Viagem", 
                "Segurança", "Material", "Equipamento", "Andaime", 
                "Documentação", "Outros"]
        cores = [colors.blue, colors.green, colors.red, colors.yellow,
                colors.purple, colors.orange, colors.cyan, colors.pink,
                colors.gray, colors.brown]

        data = []
        labels = []

        # Garantir que só vamos pegar as despesas que não são nulas ou zero
        for i, valor in enumerate(despesas):
            if valor and float(valor) > 0:
                data.append(float(valor))
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
            pie.slices[i].fillColor = cores[i % len(cores)]  # Aplicando cores ao gráfico

        d.add(pie)
        d.add(String(200, 270, "Distribuição das Despesas", fontSize=10, textAnchor='middle'))
        return d

    def gerar_relatorio_por_os(self, numero_os):
        projeto = self.buscar_projeto_por_os(numero_os)
        if not projeto:
            raise ValueError("OS não localizada.")

        orcamento = self.buscar_dados_orcamento(numero_os)
        despesas = self.buscar_dados_despesas(numero_os)

        # Caminho de salvamento automático
        root = Tk()
        root.withdraw()  # Oculta a janela principal do Tkinter

        filename_sugerido = f"Relatorio_Financeiro_OS_{numero_os}.pdf"
        caminho_completo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename_sugerido,
            title="Salvar relatório em..."
        )

        if not caminho_completo:
            raise Exception("Operação de salvamento cancelada pelo usuário.")

        # Criação do PDF
        c = canvas.Canvas(caminho_completo, pagesize=letter)
        top = 750

        # Cabeçalho
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, top, f"Relatório Financeiro - OS {projeto[0]}")
        top -= 30
        c.setFont("Helvetica", 12)
        c.drawString(50, top, f"Cliente: {projeto[1]}")
        top -= 20
        c.drawString(50, top, f"Endereço: {projeto[2]}")
        top -= 20
        c.drawString(50, top, f"Responsável: {projeto[3]}")
        top -= 40

        # Gráfico de barras
        self.criar_grafico_barras(orcamento, despesas).drawOn(c, 50, top - 300)

        # Nova página para gráfico de pizza
        c.showPage()
        self.criar_grafico_pizza_despesas(despesas).drawOn(c, 100, 400)

        # Rodapé
        c.setFont("Helvetica", 9)
        c.drawString(50, 30, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        c.save()
        print(f"✅ Relatório salvo automaticamente em: {caminho_completo}")
