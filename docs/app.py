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

def converter_hex_para_rgba(hex_color, alpha):
    """Converte cor hexadecimal para rgba com transparência"""
    # Remove o # se existir
    hex_color = hex_color.lstrip('#')
    # Converte para RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'

def normalizar_hora(h_str):
    """Normaliza entrada de hora (adiciona :00 se necessário)"""
    h_str = h_str.strip()
    if h_str and ":" not in h_str:
        h_str += ":00"
    return h_str

def validar_formato_hora(hora_str):
    """Valida se a string está no formato HH:MM"""
    hora_str = hora_str.strip()
    if not hora_str or ":" not in hora_str:
        return False
    
    try:
        partes = hora_str.split(":")
        if len(partes) != 2:
            return False
        
        horas = int(partes[0])
        minutos = int(partes[1])
        
        if horas < 0 or horas > 23:
            return False
        if minutos < 0 or minutos > 59:
            return False
        
        return True
    except:
        return False

def hora_string_para_datetime(hora_str):
    """Converte string HH:MM para datetime de forma compatível com Brython"""
    try:
        partes = hora_str.split(":")
        horas = int(partes[0])
        minutos = int(partes[1])
        
        # Usar datetime diretamente sem strptime
        hoje = datetime.now().date()
        hora_obj = datetime(hoje.year, hoje.month, hoje.day, horas, minutos, 0)
        return hora_obj
    except Exception as e:
        return None

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
            
            if not validar_formato_hora(hora_inicio_str):
                mostrar_erro(f"❌ Horário inicial inválido! Use HH:MM (ex: 14:00). Valor: '{hora_inicio_str}'")
                return
            
            hora_inicio = hora_string_para_datetime(hora_inicio_str)
            if hora_inicio is None:
                mostrar_erro(f"❌ Erro ao processar horário inicial: '{hora_inicio_str}'")
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
            
            if not validar_formato_hora(horario_final_str):
                mostrar_erro(f"❌ Horário final inválido! Use HH:MM. Valor: '{horario_final_str}'")
                return
            
            hora_final = hora_string_para_datetime(horario_final_str)
            if hora_final is None:
                mostrar_erro(f"❌ Erro ao processar horário final: '{horario_final_str}'")
                return
            
            tempo_total_horas = (hora_final - hora_inicio).total_seconds() / 3600.0
            if tempo_total_horas <= 0:
                mostrar_erro("❌ O horário final deve ser maior que o inicial")
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
                    
                if tempo_total_horas > 24:
                    mostrar_erro("❌ O tempo total não pode ser maior que 24 horas")
                    return
                    
            except ValueError as e:
                mostrar_erro(f"❌ Tempo total inválido! Use HH:MM ou decimal (ex: 2:30 ou 2.5). Valor: '{tempo_total_str}'")
                return
            except Exception as e:
                mostrar_erro(f"❌ Erro ao processar tempo total: {str(e)}")
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
        # Cada atividade será um bloco contínuo no gráfico
        dados_atividades = []
        cores_atividades_grafico = []
        labels_atividades = []
        
        # Calcular a posição inicial no relógio (em graus a partir das 12h)
        hora_12h = hora_inicio.hour % 12
        minutos = hora_inicio.minute
        
        # Converter para ângulo: 12h = 0°, 1h = 30°, etc.
        angulo_inicial = (hora_12h * 30) + (minutos * 0.5)  # 0.5° por minuto
        
        # Adicionar bloco vazio inicial se necessário
        if angulo_inicial > 0.1:  # Mais de ~12 segundos
            dados_atividades.append(angulo_inicial)
            cores_atividades_grafico.append('rgba(200, 200, 200, 0.1)')
            labels_atividades.append('Livre')
        
        # Adicionar as atividades diretamente
        for i in range(num_atividades):
            # Calcular o ângulo em graus que essa atividade ocupa
            angulo_graus = tempo_por_atividade * 30  # 30° por hora
            dados_atividades.append(angulo_graus)
            # Adicionar transparência (alpha) às cores das atividades
            cor_base = CORES[i % len(CORES)]
            # Converter hex para rgba com alpha 0.7
            cor_rgba = converter_hex_para_rgba(cor_base, 0.7)
            cores_atividades_grafico.append(cor_rgba)
            labels_atividades.append(atividades[i])
        
        # Calcular quanto espaço vazio temos no final (se houver)
        total_usado = sum(dados_atividades)
        espaco_vazio = 360 - total_usado
        
        if espaco_vazio > 0.1:  # Se sobrar mais de 0.1°
            dados_atividades.append(espaco_vazio)
            cores_atividades_grafico.append('rgba(200, 200, 200, 0.1)')
            labels_atividades.append('Livre')
        
        # O gráfico sempre começa às 12h no topo (rotação -90)
        rotacao_inicial = -90
        
        # 6. CRIAR/ATUALIZAR GRÁFICO COM CHART.JS
        criar_grafico_chartjs(dados_atividades, cores_atividades_grafico, labels_atividades, 
                              horarios_inicio, horarios_fim, atividades, rotacao_inicial)
        
        # 7. CRIAR LEGENDA (usar cores originais das atividades)
        cores_atividades = [CORES[i % len(CORES)] for i in range(num_atividades)]
        criar_legenda(atividades, horarios_inicio, horarios_fim, cores_atividades)
        
        # Mostrar container do gráfico
        grafico_container.style.display = "block"
        
        # 8. SALVAR NO HISTÓRICO
        dados_form = {
            'horarioInicio': hora_inicio_str if hora_inicio_str else '',
            'tempoTotal': tempo_total_str,
            'horarioFinal': horario_final_str,
            'atividades': atividades_str
        }
        window.salvarNoHistorico(dados_form)
        
        # Scroll suave até o gráfico
        grafico_container.scrollIntoView({"behavior": "smooth", "block": "start"})
        
    except Exception as e:
        mostrar_erro(f"❌ Erro inesperado: {str(e)}")
        window.console.log(f"Erro detalhado: {e}")

def criar_grafico_chartjs(dados, cores, labels, horarios_inicio, horarios_fim, atividades, rotacao_inicial):
    """Cria o gráfico de relógio usando Chart.js (tipo Doughnut)"""
    global grafico_atual
    
    # Destruir gráfico anterior se existir
    if grafico_atual is not None:
        grafico_atual.destroy()
    
    # Preparar dados no formato Chart.js
    Chart = window.Chart
    
    # Criar mapeamento de atividades para horários (para o tooltip)
    horarios_map = {}
    for i, ativ in enumerate(atividades):
        inicio_str = horarios_inicio[i].strftime('%H:%M')
        fim_str = horarios_fim[i].strftime('%H:%M')
        horarios_map[ativ] = f"{inicio_str} - {fim_str}"
    
    # Plugin para desenhar círculo e marcações ANTES dos dados
    plugin_fundo = {
        'id': 'fundoRelogio',
        'beforeDatasetsDraw': lambda chart, args, options: desenhar_fundo_relogio(chart)
    }
    
    # Plugin para desenhar números do relógio DEPOIS dos dados
    plugin_numeros = {
        'id': 'numerosRelogio',
        'afterDatasetsDraw': lambda chart, args, options: desenhar_numeros_relogio(chart)
    }
    
    # Função para formatar o tooltip
    def formatar_tooltip(context):
        label = labels[context.dataIndex]
        if label == 'Livre' or label == '':
            return 'Livre'
        else:
            horario = horarios_map.get(label, '')
            return f"{label}\n{horario}"
    
    config = {
        'type': 'doughnut',
        'data': {
            'labels': labels,
            'datasets': [{
                'data': dados,
                'backgroundColor': cores,
                'borderWidth': 1,
                'borderColor': '#000000',
                'circumference': 360,
                'rotation': 0
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': True,
            'rotation': rotacao_inicial,  # Usa a rotação calculada baseada no horário de início
            'circumference': 360,
            'cutout': '35%',
            'layout': {
                'padding': {
                    'top': 50,
                    'bottom': 50,
                    'left': 40,
                    'right': 40
                }
            },
            'plugins': {
                'legend': {
                    'display': False
                },
                'title': {
                    'display': False
                },
                'tooltip': {
                    'enabled': True,
                    'backgroundColor': 'rgba(0, 0, 0, 0.8)',
                    'titleFont': {
                        'size': 14,
                        'weight': 'bold'
                    },
                    'bodyFont': {
                        'size': 12
                    },
                    'padding': 12,
                    'displayColors': True,
                    'callbacks': {
                        'label': formatar_tooltip
                    }
                }
            }
        },
        'plugins': [plugin_fundo, plugin_numeros]
    }
    
    ctx = canvas.getContext('2d')
    grafico_atual = Chart.new(ctx, config)

def desenhar_fundo_relogio(chart):
    """Desenha o círculo branco e as marcações de hora ANTES dos dados"""
    ctx = chart.ctx
    
    # Obter a área do gráfico
    chartArea = chart.chartArea
    if not chartArea:
        return
    
    # Calcular centro do gráfico
    center_x = (chartArea.left + chartArea.right) / 2
    center_y = (chartArea.top + chartArea.bottom) / 2
    
    # Calcular raio do gráfico
    chart_radius = min(chartArea.right - chartArea.left, chartArea.bottom - chartArea.top) / 2
    
    ctx.save()
    
    # 1. Desenhar círculo branco de fundo com borda preta
    ctx.beginPath()
    ctx.arc(center_x, center_y, chart_radius, 0, 2 * window.Math.PI)
    ctx.fillStyle = 'white'
    ctx.fill()
    ctx.strokeStyle = '#000000'
    ctx.lineWidth = 2
    ctx.stroke()
    
    # 2. Desenhar as marcações das horas
    for i in range(12):
        angulo_graus = i * 30 - 90
        angulo_rad = angulo_graus * window.Math.PI / 180
        
        # Ponto interno (90% do raio)
        x_interno = center_x + (chart_radius * 0.9) * window.Math.cos(angulo_rad)
        y_interno = center_y + (chart_radius * 0.9) * window.Math.sin(angulo_rad)
        
        # Ponto externo (100% do raio - na borda)
        x_externo = center_x + chart_radius * window.Math.cos(angulo_rad)
        y_externo = center_y + chart_radius * window.Math.sin(angulo_rad)
        
        # Desenhar linha
        ctx.beginPath()
        ctx.moveTo(x_interno, y_interno)
        ctx.lineTo(x_externo, y_externo)
        ctx.strokeStyle = '#000000'
        ctx.lineWidth = 2
        ctx.stroke()
    
    ctx.restore()

def desenhar_numeros_relogio(chart):
    """Desenha os números de 1-12 ao redor do relógio DEPOIS dos dados"""
    ctx = chart.ctx
    
    # Obter a área do gráfico
    chartArea = chart.chartArea
    if not chartArea:
        return
    
    # Calcular centro do gráfico
    center_x = (chartArea.left + chartArea.right) / 2
    center_y = (chartArea.top + chartArea.bottom) / 2
    
    # Calcular raio do gráfico
    chart_radius = min(chartArea.right - chartArea.left, chartArea.bottom - chartArea.top) / 2
    
    ctx.save()
    
    # Desenhar os números das horas (75% do raio)
    ctx.font = 'bold 18px Segoe UI'
    ctx.fillStyle = '#1e293b'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    
    numeros = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    for i, num in enumerate(numeros):
        angulo_graus = i * 30 - 90
        angulo_rad = angulo_graus * window.Math.PI / 180
        
        # Posição dos números (75% do raio)
        x = center_x + (chart_radius * 0.75) * window.Math.cos(angulo_rad)
        y = center_y + (chart_radius * 0.75) * window.Math.sin(angulo_rad)
        
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
