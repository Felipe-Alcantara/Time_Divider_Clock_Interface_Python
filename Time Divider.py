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
root.title("Gerador de Gráfico de Atividades")
root.geometry("700x250")

style = ttk.Style(root)
style.theme_use('clam')

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Horário de início
ttk.Label(mainframe, text="Horário de início (HH:MM):").grid(row=1, column=1, sticky=W)
entrada_horario = ttk.Entry(mainframe, width=15)
entrada_horario.grid(row=1, column=2, sticky=(W, E))
ttk.Label(mainframe, text="(Deixe em branco p/ atual)").grid(row=1, column=3, columnspan=3, sticky=W)

# Frame para Tempo total e horário final
frame_tempo = ttk.Frame(mainframe)
frame_tempo.grid(row=2, column=1, columnspan=6, sticky=(W, E))

ttk.Label(frame_tempo, text="Tempo total (HH:MM ou horas):").grid(row=1, column=1, sticky=W)
entrada_tempo = ttk.Entry(frame_tempo, width=10)
entrada_tempo.grid(row=1, column=2, sticky=(W, E))
ttk.Label(frame_tempo, text="Ex: 1:30 ou 1.5").grid(row=1, column=3, padx=(5, 25), sticky=W)

ttk.Label(frame_tempo, text="Ok, se preferir:").grid(row=1, column=4, padx=10)
ttk.Label(frame_tempo, text="Até qual horário (HH:MM):").grid(row=1, column=5, sticky=W)
entrada_end_time = ttk.Entry(frame_tempo, width=10)
entrada_end_time.grid(row=1, column=6, sticky=(W, E))
ttk.Label(frame_tempo, text="(Ignora tempo total)").grid(row=1, column=7, padx=(5, 0), sticky=W)

# Atividades
ttk.Label(mainframe, text="Atividades (separadas por vírgula):").grid(row=3, column=1, sticky=W)
entrada_atividades = ttk.Entry(mainframe, width=50)
entrada_atividades.grid(row=3, column=2, columnspan=4, sticky=(W, E))
ttk.Label(mainframe, text="Ex: Estudar, Exercício, Lazer").grid(row=4, column=2, columnspan=4, sticky=W)

# Botão
ttk.Button(mainframe, text="Gerar Gráfico", command=gerar_grafico).grid(row=5, column=2, pady=10)

# Espaçamento
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()
