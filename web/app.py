from browser import document, window, alert
from datetime import datetime, timedelta
import json

# Referências aos elementos do DOM
btn_gerar = document["btn-gerar"]
btn_baixar = document["btn-baixar"]
input_horario = document["horario-inicio"]
input_tempo = document["tempo-total"]
input_final = document["horario-final"]
input_atividades = document["atividades"]
mensagem_erro = document["mensagem-erro"]
grafico_container = document["grafico-container"]
canvas = document["grafico-relogio"]

# Variável global para o gráfico
grafico_atual = None

# Paleta de cores moderna
CORES = [
    '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
    '#06b6d4', '#6366f1', '#f43f5e', '#84cc16', '#a855f7',
    '#14b8a6', '#f97316', '#22c55e', '#e11d48', '#eab308'
]

def normalizar_hora(h_str):
    """Normaliza entrada de hora (adiciona :00 se necessário)"""
    h_str = h_str.strip()
    if h_str and ":" not in h_str:
        h_str += ":00"
    return h_str

def mostrar_erro(mensagem):
    """Exibe mensagem de erro"""
    mensagem_erro.textContent = mensagem
    mensagem_erro.style.display = "block"
    grafico_container.style.display = "none"
    
def esconder_erro():
    """Esconde mensagem de erro"""
    mensagem_erro.style.display = "none"

def hora_para_angulo(hora_datetime):
    """Converte datetime para ângulo no relógio (0° = 12h, sentido horário)"""
    hora_decimal = (hora_datetime.hour % 12) + hora_datetime.minute / 60.0
    # No Chart.js, 0° é no topo (12h), e vai no sentido horário
    # Cada hora = 30° (360° / 12 horas)
    angulo = hora_decimal * 30
    return angulo

def gerar_grafico(event):
    """Função principal para gerar o gráfico"""
    global grafico_atual
    
    try:
        esconder_erro()
        
        # 1. PROCESSAR HORÁRIO DE INÍCIO
        hora_inicio_str = input_horario.value.strip()
        if hora_inicio_str == "":
            hora_inicio = datetime.now().replace(second=0, microsecond=0)
        else:
            hora_inicio_str = normalizar_hora(hora_inicio_str)
            try:
                hora_obj = datetime.strptime(hora_inicio_str, "%H:%M")
                hoje = datetime.now().date()
                hora_inicio = datetime.combine(hoje, hora_obj.time())
            except:
                mostrar_erro("❌ Horário inicial inválido! Use o formato HH:MM (ex: 16:00)")
                return
        
        # 2. PROCESSAR TEMPO TOTAL OU HORÁRIO FINAL
        tempo_total_str = input_tempo.value.strip()
        horario_final_str = input_final.value.strip()
        
        if tempo_total_str == "" and horario_final_str == "":
            mostrar_erro("❌ Preencha a Duração Total OU o Horário Final")
            return
        
        if horario_final_str:
            # Usar horário final
            horario_final_str = normalizar_hora(horario_final_str)
            try:
                hora_obj = datetime.strptime(horario_final_str, "%H:%M")
                hoje = datetime.now().date()
                hora_final = datetime.combine(hoje, hora_obj.time())
                
                tempo_total_horas = (hora_final - hora_inicio).total_seconds() / 3600.0
                if tempo_total_horas <= 0:
                    mostrar_erro("❌ O horário final deve ser maior que o inicial")
                    return
            except:
                mostrar_erro("❌ Horário final inválido! Use o formato HH:MM")
                return
        else:
            # Usar tempo total
            try:
                if ":" in tempo_total_str:
                    partes = tempo_total_str.split(":")
                    horas = int(partes[0])
                    minutos = int(partes[1])
                    tempo_total_horas = horas + minutos / 60.0
                else:
                    tempo_total_horas = float(tempo_total_str)
                
                if tempo_total_horas <= 0:
                    mostrar_erro("❌ O tempo total deve ser positivo")
                    return
            except:
                mostrar_erro("❌ Tempo total inválido! Use HH:MM ou horas decimais (ex: 1.5)")
                return
        
        # 3. PROCESSAR ATIVIDADES
        atividades_str = input_atividades.value.strip()
        if not atividades_str:
            mostrar_erro("❌ Insira pelo menos uma atividade")
            return
        
        atividades = [a.strip() for a in atividades_str.split(",") if a.strip()]
        if not atividades:
            mostrar_erro("❌ Insira pelo menos uma atividade válida")
            return
        
        if len(set(atividades)) != len(atividades):
            mostrar_erro("❌ Existem atividades duplicadas! Use nomes únicos")
            return
        
        # 4. CALCULAR TEMPOS E HORÁRIOS
        num_atividades = len(atividades)
        tempo_por_atividade = tempo_total_horas / num_atividades
        
        horarios_inicio = []
        horarios_fim = []
        hora_atual = hora_inicio
        
        for i in range(num_atividades):
            horarios_inicio.append(hora_atual)
            hora_atual = hora_atual + timedelta(hours=tempo_por_atividade)
            horarios_fim.append(hora_atual)
        
        # 5. PREPARAR DADOS PARA O GRÁFICO
        # Precisamos preencher 12 horas completas (360°) no relógio
        # Criar array de 12 horas, cada uma com 30°
        dados_por_hora = [0] * 12  # 12 posições, uma para cada hora
        cores_por_hora = ['rgba(200, 200, 200, 0.1)'] * 12  # Cor cinza transparente padrão
        labels_por_hora = [''] * 12  # Sem label por padrão
        
        # Preencher as horas com as atividades
        for i in range(num_atividades):
            hora_ini = horarios_inicio[i].hour % 12
            hora_fim = horarios_fim[i].hour % 12
            minutos_ini = horarios_inicio[i].minute
            minutos_fim = horarios_fim[i].minute
            
            # Calcular quantos "slots" de hora essa atividade ocupa
            tempo_horas = tempo_por_atividade
            
            # Posição inicial no relógio (0-11)
            pos_inicial = hora_ini
            
            # Distribuir a atividade pelas horas que ela ocupa
            horas_restantes = tempo_horas
            pos_atual = pos_inicial
            
            while horas_restantes > 0:
                # Quanto dessa hora pertence a essa atividade
                if pos_atual == pos_inicial and minutos_ini > 0:
                    # Primeira hora pode começar no meio
                    fracao_hora = min(1 - (minutos_ini / 60), horas_restantes)
                else:
                    fracao_hora = min(1, horas_restantes)
                
                # Se essa posição ainda não foi preenchida, preencher
                if dados_por_hora[pos_atual] == 0:
                    dados_por_hora[pos_atual] = fracao_hora * 30  # Converter para graus
                    cores_por_hora[pos_atual] = CORES[i % len(CORES)]
                    labels_por_hora[pos_atual] = atividades[i]
                else:
                    # Acumular na mesma hora (se houver sobreposição)
                    dados_por_hora[pos_atual] += fracao_hora * 30
                
                horas_restantes -= fracao_hora
                pos_atual = (pos_atual + 1) % 12
        
        # Garantir que todas as posições tenham pelo menos um valor mínimo para aparecer
        for i in range(12):
            if dados_por_hora[i] == 0:
                dados_por_hora[i] = 30  # 30° = 1 hora completa vazia
        
        # 6. CRIAR/ATUALIZAR GRÁFICO COM CHART.JS
        criar_grafico_chartjs(dados_por_hora, cores_por_hora, labels_por_hora, 
                              horarios_inicio, horarios_fim, atividades)
        
        # 7. CRIAR LEGENDA (usar cores originais das atividades)
        cores_atividades = [CORES[i % len(CORES)] for i in range(num_atividades)]
        criar_legenda(atividades, horarios_inicio, horarios_fim, cores_atividades)
        
        # Mostrar container do gráfico
        grafico_container.style.display = "block"
        
        # Scroll suave até o gráfico
        grafico_container.scrollIntoView({"behavior": "smooth", "block": "start"})
        
    except Exception as e:
        mostrar_erro(f"❌ Erro inesperado: {str(e)}")
        window.console.log(f"Erro detalhado: {e}")

def criar_grafico_chartjs(dados, cores, labels, horarios_inicio, horarios_fim, atividades):
    """Cria o gráfico de relógio usando Chart.js (tipo Doughnut)"""
    global grafico_atual
    
    # Destruir gráfico anterior se existir
    if grafico_atual is not None:
        grafico_atual.destroy()
    
    # Preparar dados no formato Chart.js
    Chart = window.Chart
    
    # Plugin para desenhar números do relógio
    plugin_numeros = {
        'id': 'numerosRelogio',
        'afterDatasetsDraw': lambda chart, args, options: desenhar_numeros_relogio(chart)
    }
    
    config = {
        'type': 'doughnut',
        'data': {
            'labels': ['12h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h'],
            'datasets': [{
                'data': dados,  # Array de 12 valores (30° cada)
                'backgroundColor': cores,
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': True,
            'rotation': -90,  # Começa no topo (12h)
            'circumference': 360,
            'cutout': '35%',
            'layout': {
                'padding': {
                    'top': 60,
                    'bottom': 60,
                    'left': 60,
                    'right': 60
                }
            },
            'plugins': {
                'legend': {
                    'display': False
                },
                'title': {
                    'display': True,
                    'text': '⏱️ Divisão do Tempo no Relógio',
                    'font': {
                        'size': 18,
                        'weight': 'bold',
                        'family': "'Segoe UI', sans-serif"
                    },
                    'color': '#1e293b',
                    'padding': {
                        'top': 10,
                        'bottom': 30
                    }
                },
                'tooltip': {
                    'enabled': True,
                    'callbacks': {
                        'label': lambda context: labels[context.dataIndex] if labels[context.dataIndex] else 'Livre'
                    }
                }
            }
        },
        'plugins': [plugin_numeros]
    }
    
    ctx = canvas.getContext('2d')
    grafico_atual = Chart.new(ctx, config)

def desenhar_numeros_relogio(chart):
    """Desenha os números de 1-12 ao redor do relógio"""
    ctx = chart.ctx
    
    # Pegar dimensões do canvas
    width = chart.canvas.width
    height = chart.canvas.height
    center_x = width / 2
    center_y = height / 2
    
    # Raio para os números (fora do gráfico)
    radius = min(width, height) / 2.3
    
    ctx.save()
    ctx.font = 'bold 22px Segoe UI'
    ctx.fillStyle = '#1e293b'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    
    # Números do relógio
    numeros = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    for i, num in enumerate(numeros):
        # Ângulo para cada número (12 no topo = -90°)
        angulo = (i * 30 - 90) * window.Math.PI / 180
        x = center_x + radius * window.Math.cos(angulo)
        y = center_y + radius * window.Math.sin(angulo)
        ctx.fillText(str(num), x, y)
    
    ctx.restore()

def criar_legenda(atividades, horarios_inicio, horarios_fim, cores):
    """Cria a legenda personalizada das atividades"""
    legenda_div = document["legenda-atividades"]
    legenda_div.innerHTML = ""
    
    for i, atividade in enumerate(atividades):
        item_html = f"""
        <div class="legenda-item">
            <div class="legenda-cor" style="background-color: {cores[i]};"></div>
            <div class="legenda-texto">
                <div class="legenda-atividade">{atividade}</div>
                <div class="legenda-horario">{horarios_inicio[i].strftime('%H:%M')} - {horarios_fim[i].strftime('%H:%M')}</div>
            </div>
        </div>
        """
        legenda_div.innerHTML += item_html

def baixar_grafico(event):
    """Baixa o gráfico como imagem PNG"""
    if grafico_atual is None:
        alert("⚠️ Gere um gráfico primeiro!")
        return
    
    # Pegar a imagem do canvas
    url = canvas.toDataURL('image/png')
    
    # Criar link de download
    link = document.createElement('a')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    link.download = f'time_divider_{timestamp}.png'
    link.href = url
    link.click()

# Eventos
btn_gerar.bind("click", gerar_grafico)
btn_baixar.bind("click", baixar_grafico)

# Permite Enter nos inputs
def submit_on_enter(event):
    if event.key == "Enter":
        gerar_grafico(event)

input_horario.bind("keypress", submit_on_enter)
input_tempo.bind("keypress", submit_on_enter)
input_final.bind("keypress", submit_on_enter)
input_atividades.bind("keypress", submit_on_enter)

window.console.log("✅ Time Divider Web carregado com sucesso!")
