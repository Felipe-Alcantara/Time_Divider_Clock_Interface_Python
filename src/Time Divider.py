import matplotlib.pyplot as plt
import numpy as np
import datetime
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from matplotlib.patches import Wedge

def normalizar_hora(h_str: str) -> str:
    """
    Se o usuário digitou algo sem ':', adiciona ':00'.
    Ex.: '16' => '16:00'; '07' => '07:00'; '07:30' permanece igual.
    """
    h_str = h_str.strip()
    if h_str and ":" not in h_str:
        h_str += ":00"
    return h_str

def gerar_grafico():
    try:
        # Obtém as entradas do usuário
        hora_atual_input = entrada_horario.get().strip()
        end_time_input = entrada_end_time.get().strip()
        tempo_total_input = entrada_tempo.get().strip()
        atividades_input = entrada_atividades.get().strip()

        # 1) PROCESSA O HORÁRIO DE INÍCIO
        if hora_atual_input == "":
            # Se o usuário não informou, pega o horário atual do sistema
            hora_atual = datetime.datetime.now().replace(second=0, microsecond=0)
        else:
            # Normaliza o texto caso seja só "16" => "16:00"
            hora_atual_input = normalizar_hora(hora_atual_input)
            try:
                hoje = datetime.datetime.now().date()
                parsed_time = datetime.datetime.strptime(hora_atual_input, "%H:%M").time()
                hora_atual = datetime.datetime.combine(hoje, parsed_time)
            except ValueError:
                messagebox.showerror("Erro", "Horário inicial inválido! Use HH:MM (ex: 16 ou 16:00).")
                return

        # 2) PROCESSA O TEMPO TOTAL OU O HORÁRIO FINAL
        if end_time_input == "" and tempo_total_input == "":
            messagebox.showerror("Erro", "Por favor, insira o tempo total OU o horário final disponível.")
            return

        if end_time_input:
            # Normaliza, caso seja só "18" => "18:00"
            end_time_input = normalizar_hora(end_time_input)
            try:
                hoje = datetime.datetime.now().date()
                parsed_end_time = datetime.datetime.strptime(end_time_input, "%H:%M").time()
                end_time = datetime.datetime.combine(hoje, parsed_end_time)

                tempo_total = (end_time - hora_atual).total_seconds() / 3600.0
                if tempo_total <= 0:
                    messagebox.showerror("Erro", "O horário final deve ser maior que o horário inicial.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Horário final inválido! Use HH:MM (ex: 19 ou 19:00).")
                return
        else:
            # Tempo total
            try:
                if ":" in tempo_total_input:
                    horas, minutos = map(int, tempo_total_input.split(":"))
                    tempo_total = horas + minutos / 60.0
                else:
                    tempo_total = float(tempo_total_input)

                if tempo_total <= 0:
                    messagebox.showerror("Erro", "O tempo total deve ser um número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Tempo total inválido! Use HH:MM ou somente horas (ex: 1.5).")
                return

        # 3) PROCESSA AS ATIVIDADES
        atividades = [atividade.strip() for atividade in atividades_input.split(",") if atividade.strip() != ""]
        if not atividades:
            messagebox.showerror("Erro", "Por favor, insira pelo menos uma atividade.")
            return

        if len(set(atividades)) != len(atividades):
            messagebox.showerror("Erro", "Existem atividades duplicadas! Use nomes únicos.")
            return

        quantidade_atividades = len(atividades)
        tempo_por_atividade = tempo_total / quantidade_atividades
        tempos = [tempo_por_atividade] * quantidade_atividades

        # 4) CALCULA OS HORÁRIOS DE INÍCIO E FIM DE CADA ATIVIDADE
        horarios_inicio = [hora_atual]
        horarios_fim = []
        for tempo in tempos:
            horario_fim = horarios_inicio[-1] + datetime.timedelta(hours=tempo)
            horarios_fim.append(horario_fim)
            if len(horarios_inicio) < quantidade_atividades:
                horarios_inicio.append(horario_fim)

        def hora_para_angulo_graus(horario):
            # Converte o horário para ângulo no formato de 12h
            hora_decimal = (horario.hour % 12) + horario.minute / 60.0
            # Cada hora = 30 graus. 0h = 90 graus. Negativo para girar no sentido correto.
            angulo = (-hora_decimal * 30 + 90) % 360
            return angulo

        # 5) CRIA A FIGURA DO RELÓGIO
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        ax.axis('off')

        # Desenha o círculo do relógio
        circle = plt.Circle((0, 0), 1, color='white', ec='black', lw=2)
        ax.add_artist(circle)

        # Desenha as marcações das horas
        for i in range(12):
            angulo = np.deg2rad(90 - i * 30)
            x_interior = 0.9 * np.cos(angulo)
            y_interior = 0.9 * np.sin(angulo)
            x_exterior = np.cos(angulo)
            y_exterior = np.sin(angulo)
            ax.plot([x_interior, x_exterior], [y_interior, y_exterior], color='black', lw=2)

        # Desenha os números das horas
        for i in range(12):
            angulo = np.deg2rad(90 - i * 30)
            x_num = 0.75 * np.cos(angulo)
            y_num = 0.75 * np.sin(angulo)
            hora = i if i != 0 else 12
            ax.text(x_num, y_num, str(hora), ha='center', va='center', fontsize=14)

        # Gera cores distintas para as atividades
        cmap = plt.cm.get_cmap('tab20', quantidade_atividades)
        cores = [cmap(i) for i in range(quantidade_atividades)]

        # 6) DESENHA OS SETORES PARA CADA ATIVIDADE
        for i in range(quantidade_atividades):
            angulo_inicio = hora_para_angulo_graus(horarios_inicio[i])
            angulo_fim = hora_para_angulo_graus(horarios_fim[i])
            if angulo_inicio <= angulo_fim:
                angulo_inicio += 360

            wedge = Wedge(
                center=(0, 0),
                r=1,
                theta1=angulo_fim,
                theta2=angulo_inicio,
                facecolor=cores[i],
                edgecolor='black',
                lw=1,
                alpha=0.7
            )
            ax.add_patch(wedge)

            # Texto no centro do setor
            angulo_texto = (angulo_fim + angulo_inicio) / 2 % 360
            angulo_texto_rad = np.deg2rad(angulo_texto)
            x_text = 1.2 * np.cos(angulo_texto_rad)
            y_text = 1.2 * np.sin(angulo_texto_rad)

            horario_inicio_str = horarios_inicio[i].strftime("%H:%M")
            horario_fim_str = horarios_fim[i].strftime("%H:%M")
            ax.text(x_text, y_text, f"{atividades[i]}\n{horario_inicio_str}-{horario_fim_str}",
                    ha='center', va='center', fontsize=10)

        # Adiciona a legenda
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label=atividades[i],
                   markerfacecolor=cores[i], markersize=10)
            for i in range(quantidade_atividades)
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.2, 1.1))

        plt.title('Divisão do Tempo no Relógio', y=1.08)

        # Salva e exibe o gráfico
        plt.savefig(
            'divisao_tempo_relogio_{}.png'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')),
            dpi=300, bbox_inches='tight'
        )
        plt.show()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")

# --------------------------------------------------------------------
# Configura a janela Tkinter
root = Tk()
root.title("⏱️ Time Divider - Gerador de Gráfico de Atividades")
root.geometry("850x450")
root.configure(bg='#f0f4f8')
root.resizable(False, False)

# Configuração de estilos modernos
style = ttk.Style(root)
style.theme_use('clam')

# Cores modernas
COR_BG = '#f0f4f8'
COR_FRAME = '#ffffff'
COR_PRIMARIA = '#3b82f6'
COR_SECUNDARIA = '#8b5cf6'
COR_TEXTO = '#1e293b'
COR_TEXTO_CLARO = '#64748b'
COR_BOTAO = '#3b82f6'
COR_BOTAO_HOVER = '#2563eb'

# Estilos personalizados
style.configure('Title.TLabel', 
                background=COR_FRAME, 
                foreground=COR_TEXTO,
                font=('Segoe UI', 18, 'bold'))

style.configure('Subtitle.TLabel', 
                background=COR_FRAME, 
                foreground=COR_TEXTO_CLARO,
                font=('Segoe UI', 9))

style.configure('Label.TLabel', 
                background=COR_FRAME, 
                foreground=COR_TEXTO,
                font=('Segoe UI', 10))

style.configure('Hint.TLabel', 
                background=COR_FRAME, 
                foreground=COR_TEXTO_CLARO,
                font=('Segoe UI', 9, 'italic'))

style.configure('Custom.TEntry',
                fieldbackground='white',
                borderwidth=2,
                relief='solid')

style.configure('Generate.TButton',
                font=('Segoe UI', 11, 'bold'),
                background=COR_BOTAO,
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=12)

style.map('Generate.TButton',
          background=[('active', COR_BOTAO_HOVER)])

# Frame principal com sombra simulada
shadow_frame = ttk.Frame(root, style='Card.TFrame')
shadow_frame.place(relx=0.5, rely=0.5, anchor='center', width=800, height=400)

style.configure('Card.TFrame', background=COR_FRAME, relief='flat')

mainframe = ttk.Frame(shadow_frame, padding="30 30 30 30", style='Card.TFrame')
mainframe.pack(fill='both', expand=True)

# Cabeçalho
header_frame = ttk.Frame(mainframe, style='Card.TFrame')
header_frame.grid(row=0, column=0, columnspan=8, pady=(0, 20), sticky=(W, E))

ttk.Label(header_frame, text="⏱️ Time Divider", style='Title.TLabel').pack(anchor='center')
ttk.Label(header_frame, text="Organize seu tempo visualmente em um relógio analógico", 
          style='Subtitle.TLabel').pack(anchor='center', pady=(5, 0))

# Separador
separator1 = ttk.Separator(mainframe, orient='horizontal')
separator1.grid(row=1, column=0, columnspan=8, sticky=(W, E), pady=(0, 20))

# Seção 1: Horário de início
section1_frame = ttk.Frame(mainframe, style='Card.TFrame')
section1_frame.grid(row=2, column=0, columnspan=8, sticky=(W, E), pady=(0, 15))

ttk.Label(section1_frame, text="🕐 Horário de Início", style='Label.TLabel').grid(row=0, column=0, sticky=W, padx=(0, 15))
entrada_horario = ttk.Entry(section1_frame, width=15, style='Custom.TEntry', font=('Segoe UI', 10))
entrada_horario.grid(row=0, column=1, sticky=W, padx=(0, 10))
ttk.Label(section1_frame, text="(Deixe em branco para usar o horário atual)", style='Hint.TLabel').grid(row=0, column=2, sticky=W)

# Seção 2: Tempo total ou horário final
section2_frame = ttk.Frame(mainframe, style='Card.TFrame')
section2_frame.grid(row=3, column=0, columnspan=8, sticky=(W, E), pady=(0, 15))

ttk.Label(section2_frame, text="⏳ Duração Total", style='Label.TLabel').grid(row=0, column=0, sticky=W, padx=(0, 15))
entrada_tempo = ttk.Entry(section2_frame, width=12, style='Custom.TEntry', font=('Segoe UI', 10))
entrada_tempo.grid(row=0, column=1, sticky=W, padx=(0, 10))
ttk.Label(section2_frame, text="Ex: 1:30 ou 1.5", style='Hint.TLabel').grid(row=0, column=2, sticky=W, padx=(0, 30))

ttk.Label(section2_frame, text="ou", style='Hint.TLabel').grid(row=0, column=3, padx=15)

ttk.Label(section2_frame, text="🎯 Horário Final", style='Label.TLabel').grid(row=0, column=4, sticky=W, padx=(0, 15))
entrada_end_time = ttk.Entry(section2_frame, width=12, style='Custom.TEntry', font=('Segoe UI', 10))
entrada_end_time.grid(row=0, column=5, sticky=W, padx=(0, 10))
ttk.Label(section2_frame, text="Ex: 18:00", style='Hint.TLabel').grid(row=0, column=6, sticky=W)

# Seção 3: Atividades
section3_frame = ttk.Frame(mainframe, style='Card.TFrame')
section3_frame.grid(row=4, column=0, columnspan=8, sticky=(W, E), pady=(0, 15))

ttk.Label(section3_frame, text="📋 Atividades", style='Label.TLabel').grid(row=0, column=0, sticky=W, padx=(0, 15))
entrada_atividades = ttk.Entry(section3_frame, width=60, style='Custom.TEntry', font=('Segoe UI', 10))
entrada_atividades.grid(row=0, column=1, sticky=(W, E), padx=(0, 10))
ttk.Label(section3_frame, text="Separe com vírgula - Ex: Estudar, Exercício, Lazer", 
          style='Hint.TLabel').grid(row=1, column=1, sticky=W, pady=(5, 0))

section3_frame.columnconfigure(1, weight=1)

# Separador
separator2 = ttk.Separator(mainframe, orient='horizontal')
separator2.grid(row=5, column=0, columnspan=8, sticky=(W, E), pady=(15, 20))

# Botão de gerar - centralizado
button_frame = ttk.Frame(mainframe, style='Card.TFrame')
button_frame.grid(row=6, column=0, columnspan=8)

gerar_btn = ttk.Button(button_frame, text="✨ Gerar Gráfico", command=gerar_grafico, style='Generate.TButton')
gerar_btn.pack()

# Configurações de grid weight
mainframe.columnconfigure(0, weight=1)

root.mainloop()