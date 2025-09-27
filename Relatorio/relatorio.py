import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import psycopg2
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.legends import Legend
import os
from decimal import Decimal

class RelatorioFinanceiroComGraficos:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise Financeira de Projetos com Gráficos")
        self.root.geometry("900x650")
        
        # Configuração do tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Gerar Relatório Financeiro com Gráficos",
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(pady=(10, 20))
        
        # Frame de entrada
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Campo para número da OS
        self.os_label = ctk.CTkLabel(
            self.input_frame, 
            text="Número da OS:",
            font=("Arial", 12)
        )
        self.os_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.os_entry = ctk.CTkEntry(
            self.input_frame,
            width=200,
            font=("Arial", 12)
        )
        self.os_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.os_entry.bind("<Return>", lambda e: self.gerar_relatorio())
        
        # Botão de gerar relatório
        self.gerar_btn = ctk.CTkButton(
            self.input_frame,
            text="Gerar Relatório PDF",
            command=self.gerar_relatorio,
            font=("Arial", 12, "bold")
        )
        self.gerar_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Frame de visualização
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Texto de pré-visualização
        self.preview_label = ctk.CTkLabel(
            self.preview_frame, 
            text="Pré-visualização do Relatório",
            font=("Arial", 14, "bold")
        )
        self.preview_label.pack(pady=(5, 10))
        
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        
        self.status_bar = ctk.CTkLabel(
            root,
            textvariable=self.status_var,
            font=("Arial", 10),
            anchor="w"
        )
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Configuração do banco de dados
        self.db_config = {
            'host': 'localhost',
            'database': 'projeto_final',
            'user': 'postgres',
            'password': 'Edu1Sal2'
        }
        
    def conectar_banco(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{str(e)}")
            return None
    
    def buscar_dados_projeto(self, os_numero):
        conn = self.conectar_banco()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            
            # Buscar dados do projeto
            cursor.execute("""
                SELECT p.numero_os, p.tipo, p.cliente_nome, p.cliente_cpf_cnpj, 
                       p.endereco_obra, p.cidade_obra, p.estado_obra, p.contato, 
                       p.nome_responsavel, p.status, p.valor_servico, p.valor_material,
                       c.nome as cliente_nome_completo
                FROM projetos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE p.numero_os = %s
            """, (os_numero,))
            
            projeto = cursor.fetchone()
            if not projeto:
                return None
                
            # Buscar orçamento
            cursor.execute("""
                SELECT mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                       material, equipamento, andaime, documentacao, outros, total
                FROM orcamentos
                WHERE numero_os_projeto = %s
            """, (os_numero,))
            
            orcamento = cursor.fetchone()
            
            # Buscar despesas
            cursor.execute("""
                SELECT SUM(mao_de_obra), SUM(alimentacao), SUM(hospedagem), SUM(viagem), 
                       SUM(seguranca_trabalho), SUM(material), SUM(equipamento), 
                       SUM(andaime), SUM(documentacao), SUM(outros), SUM(total)
                FROM despesas
                WHERE numero_os_projeto = %s
            """, (os_numero,))
            
            despesas = cursor.fetchone()
            
            # Buscar receitas
            cursor.execute("""
                SELECT SUM(valor_servico), SUM(valor_material), SUM(valor_liquido)
                FROM receitas
                WHERE numero_os_projeto = %s
            """, (os_numero,))
            
            receitas = cursor.fetchone()
            
            return {
                'projeto': projeto,
                'orcamento': orcamento,
                'despesas': despesas,
                'receitas': receitas
            }
            
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar dados:\n{str(e)}")
            return None
        finally:
            conn.close()
    
    def formatar_moeda(self, valor):
        if valor is None:
            return "R$ 0,00"
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def calcular_diferenca(self, orcado, realizado):
        if orcado is None or realizado is None or orcado == 0:
            return ("-", "-")
            
        diff_valor = realizado - orcado
        diff_percent = (diff_valor / orcado) * 100
        
        sinal = "+" if diff_valor >= 0 else "-"
        return (
            f"{sinal}{abs(diff_percent):.0f}%",
            f"{sinal}{self.formatar_moeda(abs(diff_valor))}"
        )
    
    def criar_grafico_barras(self, orcamento, despesas, width=6*inch, height=3*inch):
        """Cria um gráfico de barras comparando orçado vs realizado"""
        d = Drawing(width, height)
        
        itens = [
            "Mão-de-obra", "Alimentação", "Hospedagem", "Viagem", 
            "Segurança", "Material", "Equipamentos", "Andaime", 
            "Documentação", "Outros"
        ]
        
        # Dados para o gráfico - convertendo Decimal para float
        data_orcado = [float(orcamento[i]) if orcamento and orcamento[i] else 0 for i in range(10)]
        data_realizado = [float(despesas[i]) if despesas and despesas[i] else 0 for i in range(10)]
        
        # Ajustar valores muito pequenos para visualização
        data_orcado = [max(val, 100) for val in data_orcado]  # Mínimo de R$ 100 para aparecer no gráfico
        data_realizado = [max(val, 100) for val in data_realizado]
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = height - 100
        bc.width = width - 100
        bc.data = [data_orcado, data_realizado]
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(max(data_orcado), max(data_realizado)) * 1.2
        bc.valueAxis.valueStep = max(max(data_orcado), max(data_realizado)) / 5
        bc.categoryAxis.categoryNames = itens
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 8
        bc.groupSpacing = 10
        bc.barSpacing = 2
        bc.bars[0].fillColor = colors.blue
        bc.bars[1].fillColor = colors.green
        
        # Legenda
        legend = Legend()
        legend.alignment = 'right'
        legend.x = width - 100
        legend.y = height - 30
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.colorNamePairs = [
            (colors.blue, 'Orçado'),
            (colors.green, 'Realizado')
        ]
        
        d.add(bc)
        d.add(legend)
        d.add(String(width/2, height-20, 'Comparativo Orçado vs Realizado', 
            fontName='Helvetica-Bold', fontSize=10))
        
        return d
    
    def criar_grafico_pizza_despesas(self, despesas, width=4*inch, height=4*inch):
        """Cria um gráfico de pizza com a distribuição das despesas"""
        d = Drawing(width, height)
        
        itens = [
            "Mão-de-obra", "Alimentação", "Hospedagem", "Viagem", 
            "Segurança", "Material", "Equipamentos", "Andaime", 
            "Documentação", "Outros"
        ]
        
        # Dados para o gráfico (ignorando valores zero)
        data = []
        labels = []
        cores = [
            colors.blue, colors.green, colors.red, colors.yellow,
            colors.purple, colors.orange, colors.cyan, colors.pink,
            colors.lightgreen, colors.gray
        ]
        
        if despesas:
            for i in range(10):
                if despesas[i] and float(despesas[i]) > 0:  # Convertendo para float
                    data.append(float(despesas[i]))  # Convertendo para float
                    labels.append(itens[i])
        
        if not data:  # Se não houver dados válidos
            d.add(String(width/2, height/2, 'Sem dados de despesas', 
                        fontName='Helvetica', fontSize=10, textAnchor='middle'))
            return d
        
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = width - 100
        pie.height = height - 100
        pie.data = data
        pie.labels = labels
        pie.slices.strokeWidth = 0.5
        pie.slices.fontName = 'Helvetica'
        pie.slices.fontSize = 8
        
        # Atribuir cores
        for i in range(len(data)):
            pie.slices[i].fillColor = cores[i % len(cores)]
        
        d.add(pie)
        d.add(String(width/2, height-20, 'Distribuição das Despesas', 
                    fontName='Helvetica-Bold', fontSize=10))
        
        return d
    
    def criar_grafico_lucro(self, orc_total, despesa_total, receita_total, width=6*inch, height=3*inch):
        """Cria um gráfico comparando lucro planejado e realizado"""
        d = Drawing(width, height)
        
        # Calcular lucros - convertendo para float
        orc_total = float(orc_total) if orc_total else 0
        despesa_total = float(despesa_total) if despesa_total else 0
        receita_total = float(receita_total) if receita_total else 0
        
        lucro_planejado = orc_total - despesa_total
        lucro_realizado = receita_total - despesa_total
        
        # Dados para o gráfico
        data = [
            [orc_total, despesa_total, lucro_planejado],
            [receita_total, despesa_total, lucro_realizado]
        ]
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = height - 100
        bc.width = width - 100
        bc.data = data
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(max(row) for row in data) * 1.2
        bc.valueAxis.valueStep = max(max(row) for row in data) / 5
        bc.categoryAxis.categoryNames = ['Planejado', 'Realizado']
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 8
        bc.groupSpacing = 15
        bc.barSpacing = 2
        bc.bars[0].fillColor = colors.blue    # Receitas
        bc.bars[1].fillColor = colors.red     # Despesas
        bc.bars[2].fillColor = colors.green   # Lucro
        
        # Legenda
        legend = Legend()
        legend.alignment = 'right'
        legend.x = width - 100
        legend.y = height - 30
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.colorNamePairs = [
            (colors.blue, 'Receitas'),
            (colors.red, 'Despesas'),
            (colors.green, 'Lucro')
        ]
        
        d.add(bc)
        d.add(legend)
        d.add(String(width/2, height-20, 'Análise de Lucro: Planejado vs Realizado', 
            fontName='Helvetica-Bold', fontSize=10))
        
        return d
    
    def gerar_relatorio(self):
        os_numero = self.os_entry.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite o número da OS!")
            return
            
        self.status_var.set("Buscando dados no banco...")
        self.root.update()
        
        dados = self.buscar_dados_projeto(os_numero)
        if not dados:
            messagebox.showwarning("Aviso", f"OS {os_numero} não encontrada!")
            self.status_var.set("Pronto")
            return
            
        projeto = dados['projeto']
        orcamento = dados['orcamento']
        despesas = dados['despesas']
        receitas = dados['receitas']
        
        # Atualizar pré-visualização
        self.atualizar_preview(projeto, orcamento, despesas, receitas)
        
        # Gerar PDF
        self.status_var.set("Gerando PDF...")
        self.root.update()
        
        self.criar_pdf(projeto, orcamento, despesas, receitas, os_numero)
        
        self.status_var.set("Relatório gerado com sucesso!")
        
    def atualizar_preview(self, projeto, orcamento, despesas, receitas):
        self.preview_text.delete(1.0, tk.END)
        
        # Cabeçalho
        self.preview_text.insert(tk.END, "ANÁLISE FINANCEIRA DO PROJETO\n\n", "header")
        
        # Dados do cliente
        self.preview_text.insert(tk.END, "Código do Cliente:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[0]} - {projeto[12]}\n\n")
        
        self.preview_text.insert(tk.END, "CPF / CNPJ:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[3]}\n\n")
        
        self.preview_text.insert(tk.END, "Endereço:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[4]} - {projeto[5]}/{projeto[6]}\n\n")
        
        self.preview_text.insert(tk.END, "Contato:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[7]} - {projeto[8]}\n\n")
        
        self.preview_text.insert(tk.END, "Tipo de Projeto:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[1]}\n\n")
        
        self.preview_text.insert(tk.END, "-"*50 + "\n\n")
        
        # Despesas do projeto
        self.preview_text.insert(tk.END, "DESPESAS DO PROJETO\n\n", "header")
        
        # Cálculos de despesas
        total_orcado = orcamento[10] if orcamento else 0
        total_realizado = despesas[10] if despesas else 0
        diff_percent, diff_valor = self.calcular_diferenca(total_orcado, total_realizado)
        
        # Tabela de despesas
        tabela_despesas = [
            ["Item", "Orçado", "Realizado", "Δ %", "Δ R$"],
            ["Total", 
             self.formatar_moeda(total_orcado), 
             self.formatar_moeda(total_realizado), 
             diff_percent, 
             diff_valor]
        ]
        
        # Adicionar itens individuais
        itens = [
            ("Mão-de-obra", 0, 0),
            ("Alimentação", 1, 1),
            ("Hospedagem", 2, 2),
            ("Viagem", 3, 3),
            ("Seg. do Trabalho", 4, 4),
            ("Material", 5, 5),
            ("Equipamentos", 6, 6),
            ("Andaime", 7, 7),
            ("Documentação", 8, 8),
            ("Outros", 9, 9)
        ]
        
        for nome, idx_orc, idx_desp in itens:
            orc_item = orcamento[idx_orc] if orcamento else 0
            desp_item = despesas[idx_desp] if despesas else 0
            dp, dv = self.calcular_diferenca(orc_item, desp_item)
            
            tabela_despesas.append([
                nome,
                self.formatar_moeda(orc_item),
                self.formatar_moeda(desp_item),
                dp,
                dv
            ])
        
        # Adicionar tabela ao preview
        for linha in tabela_despesas:
            self.preview_text.insert(tk.END, f"{linha[0]:<20} {linha[1]:>15} {linha[2]:>15} {linha[3]:>10} {linha[4]:>15}\n")
        
        self.preview_text.insert(tk.END, "\n" + "-"*50 + "\n\n")
        
        # Status do projeto
        self.preview_text.insert(tk.END, "Status do projeto:\n", "bold")
        self.preview_text.insert(tk.END, f"{projeto[9]}\n\n")
        
        # Cálculo do lucro operacional
        receita_servico = receitas[0] if receitas else 0
        receita_material = receitas[1] if receitas else 0
        receita_total = receita_servico + receita_material
        
        orc_servico = projeto[10] if projeto[10] else 0
        orc_material = projeto[11] if projeto[11] else 0
        orc_total = orc_servico + orc_material
        
        despesa_total = despesas[10] if despesas else 0
        
        lucro_planejado = orc_total - (total_orcado if total_orcado else 0)
        lucro_realizado = receita_total - (despesa_total if despesa_total else 0)
        
        perc_planejado = (lucro_planejado / orc_total * 100) if orc_total != 0 else 0
        perc_realizado = (lucro_realizado / receita_total * 100) if receita_total != 0 else 0
        
        # Tabela de resultados
        self.preview_text.insert(tk.END, "\n")
        self.preview_text.insert(tk.END, f"{'':<15} {'Receitas':>15} {'Despesas':>15} {'Lucro operacional':>20}\n")
        self.preview_text.insert(tk.END, f"{'Planejado':<15} {self.formatar_moeda(orc_total):>15} {self.formatar_moeda(total_orcado):>15} {self.formatar_moeda(lucro_planejado):>20} ({perc_planejado:.2f}%)\n")
        self.preview_text.insert(tk.END, f"{'Realizado':<15} {self.formatar_moeda(receita_total):>15} {self.formatar_moeda(despesa_total):>15} {self.formatar_moeda(lucro_realizado):>20} ({perc_realizado:.2f}%)\n")
        
        # Configurar tags para formatação
        self.preview_text.tag_config("header", font=("Arial", 12, "bold"))
        self.preview_text.tag_config("bold", font=("Arial", 10, "bold"))
    
    def criar_pdf(self, projeto, orcamento, despesas, receitas, os_numero):
        # Configurações do PDF
        filename = f"Relatorio_Financeiro_OS_{os_numero}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Margens e espaçamentos
        left_margin = 50
        right_margin = width - 50
        top_margin = height - 50
        line_height = 20
        section_spacing = 30
        
        # --- PÁGINA 1 ---
        
        # Cabeçalho
        y = top_margin
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_margin, y, "ANÁLISE FINANCEIRA DO PROJETO")
        c.line(left_margin, y-5, right_margin, y-5)
        y -= line_height * 2
        
        # Dados do cliente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Código do Cliente:")
        c.setFont("Helvetica", 12)
        cliente_nome = projeto[12] if projeto[12] else "Não informado"
        c.drawString(left_margin + 130, y, f"{projeto[0]} - {cliente_nome}")
        y -= line_height
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "CPF / CNPJ:")
        c.setFont("Helvetica", 12)
        cpf_cnpj = projeto[3] if projeto[3] else "Não informado"
        c.drawString(left_margin + 130, y, cpf_cnpj)
        y -= line_height
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Endereço:")
        c.setFont("Helvetica", 12)
        endereco = projeto[4] if projeto[4] else "Não informado"
        cidade = projeto[5] if projeto[5] else "Não informado"
        estado = projeto[6] if projeto[6] else "Não informado"
        c.drawString(left_margin + 130, y, f"{endereco} - {cidade}/{estado}")
        y -= line_height
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Contato:")
        c.setFont("Helvetica", 12)
        contato = projeto[7] if projeto[7] else "Não informado"
        responsavel = projeto[8] if projeto[8] else "Não informado"
        c.drawString(left_margin + 130, y, f"{contato} - {responsavel}")
        y -= line_height
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Tipo de Projeto:")
        c.setFont("Helvetica", 12)
        tipo_projeto = projeto[1] if projeto[1] else "Não informado"
        c.drawString(left_margin + 130, y, tipo_projeto)
        y -= section_spacing
        
        # Linha divisória
        c.line(left_margin, y, right_margin, y)
        y -= section_spacing
        
        # Seção DESPESAS DO PROJETO
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y, "DESPESAS DO PROJETO")
        y -= line_height * 2
        
        # Tabela de despesas
        total_orcado = orcamento[10] if orcamento else 0
        total_realizado = despesas[10] if despesas else 0
        diff_percent, diff_valor = self.calcular_diferenca(total_orcado, total_realizado)
        
        data = [
            ["Item", "Orçado", "Realizado", "Δ %", "Δ R$"],
            ["Total", 
            self.formatar_moeda(total_orcado), 
            self.formatar_moeda(total_realizado), 
            diff_percent, 
            diff_valor]
        ]
        
        itens = [
            ("Mão-de-obra", 0, 0),
            ("Alimentação", 1, 1),
            ("Hospedagem", 2, 2),
            ("Viagem", 3, 3),
            ("Seg. do Trabalho", 4, 4),
            ("Material", 5, 5),
            ("Equipamentos", 6, 6),
            ("Andaime", 7, 7),
            ("Documentação", 8, 8),
            ("Outros", 9, 9)
        ]
        
        for nome, idx_orc, idx_desp in itens:
            orc_item = orcamento[idx_orc] if orcamento else 0
            desp_item = despesas[idx_desp] if despesas else 0
            dp, dv = self.calcular_diferenca(orc_item, desp_item)
            
            data.append([
                nome,
                self.formatar_moeda(orc_item),
                self.formatar_moeda(desp_item),
                dp,
                dv
            ])
        
        table = Table(data, colWidths=[120, 80, 80, 60, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # Posicionar tabela com espaçamento adequado
        table.wrapOn(c, width - 100, height)
        table.drawOn(c, left_margin, y - (len(data) * 20))
        y -= (len(data) * 20) + section_spacing
        
        # Gráfico de barras comparativo (posicionado abaixo da tabela)
        if orcamento and despesas:
            grafico_barras = self.criar_grafico_barras(orcamento, despesas, width=6*inch, height=3*inch)
            grafico_barras.drawOn(c, left_margin, y - 200)
            y -= 250  # Espaço após o gráfico
        
        # Nova página para os demais gráficos e resultados
        c.showPage()

        # --- PÁGINA 2 ---
        y = top_margin
        
        # Seção RESULTADOS FINANCEIROS (primeiro na segunda página)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y, "RESULTADOS FINANCEIROS")
        y -= line_height * 2
        
        # Cálculo do lucro operacional
        receita_servico = receitas[0] if receitas else 0
        receita_material = receitas[1] if receitas else 0
        receita_total = receita_servico + receita_material
        
        orc_servico = projeto[10] if projeto[10] else 0
        orc_material = projeto[11] if projeto[11] else 0
        orc_total = orc_servico + orc_material
        
        despesa_total = despesas[10] if despesas else 0
        
        lucro_planejado = orc_total - (total_orcado if total_orcado else 0)
        lucro_realizado = receita_total - (despesa_total if despesa_total else 0)
        
        perc_planejado = (lucro_planejado / orc_total * 100) if orc_total != 0 else 0
        perc_realizado = (lucro_realizado / receita_total * 100) if receita_total != 0 else 0
        
        # Tabela de resultados
        result_data = [
            ["", "Receitas", "Despesas", "Lucro operacional", "%"],
            ["Planejado", 
            self.formatar_moeda(orc_total), 
            self.formatar_moeda(total_orcado), 
            self.formatar_moeda(lucro_planejado),
            f"{perc_planejado:.2f}%"],
            ["Realizado", 
            self.formatar_moeda(receita_total), 
            self.formatar_moeda(despesa_total), 
            self.formatar_moeda(lucro_realizado),
            f"{perc_realizado:.2f}%"]
        ]
        
        result_table = Table(result_data, colWidths=[80, 80, 80, 100, 60])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        result_table.wrapOn(c, width - 100, height)
        result_table.drawOn(c, left_margin, y - 80)
        y -= 120
        
        # Gráfico de análise de lucro
        grafico_lucro = self.criar_grafico_lucro(orc_total, despesa_total, receita_total, width=6*inch, height=3*inch)
        grafico_lucro.drawOn(c, left_margin, y - 200)
        y -= 250
        
        # Gráfico de pizza das despesas (apenas se houver despesas)
        if despesas:
            grafico_pizza = self.criar_grafico_pizza_despesas(despesas, width=4*inch, height=4*inch)
            grafico_pizza.drawOn(c, width/2 - 50, y - 200)
        
        # Rodapé
        c.setFont("Helvetica", 8)
        c.drawString(left_margin, 30, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Salvar PDF
        c.save()
        
        # Abrir o PDF automaticamente
        os.startfile(filename)
        
        

if __name__ == "__main__":
    root = ctk.CTk()
    app = RelatorioFinanceiroComGraficos(root)
    root.mainloop()