# ⏱️ Time Divider - Versão Web

Versão web do Time Divider desenvolvida com **Brython** (Python no navegador), HTML5, CSS3 e Chart.js.

## 🌐 Como Usar

### Opção 1: Abrir Localmente

1. Navegue até a pasta `web/`
2. Abra o arquivo `index.html` diretamente no seu navegador
3. Pronto! A aplicação está rodando

### Opção 2: Servidor HTTP Local

Para melhor compatibilidade, use um servidor HTTP local:

#### Python 3:
```bash
cd web
python -m http.server 8000
```

Depois acesse: `http://localhost:8000`

#### Node.js (http-server):
```bash
cd web
npx http-server -p 8000
```

## ✨ Funcionalidades

- ✅ **100% Web**: Roda direto no navegador sem instalações
- ✅ **Python no Browser**: Lógica escrita em Python usando Brython
- ✅ **Interface Moderna**: Design responsivo e atraente
- ✅ **Gráfico Interativo**: Visualização em relógio polar com Chart.js
- ✅ **Download de Imagem**: Salve o gráfico como PNG
- ✅ **Validações**: Feedback instantâneo de erros

## 🎨 Tecnologias

- **Brython 3.12.3**: Python 3 no navegador
- **Chart.js 4.4.0**: Biblioteca de gráficos
- **HTML5 + CSS3**: Interface moderna
- **Responsive Design**: Funciona em desktop e mobile

## 📋 Exemplo de Uso

1. **Horário de Início**: `14:00` (ou deixe em branco para usar atual)
2. **Duração Total**: `3:00` (3 horas)
3. **Atividades**: `Estudar, Exercício, Lazer`
4. Clique em **✨ Gerar Gráfico**

## 🔧 Estrutura dos Arquivos

```
web/
├── index.html      # Estrutura HTML principal
├── styles.css      # Estilos modernos
├── app.py          # Lógica em Python (Brython)
└── README.md       # Esta documentação
```

## 🌍 Deploy

Para fazer deploy online, você pode usar:

- **GitHub Pages**: Faça commit da pasta `web/` e ative Pages
- **Netlify**: Arraste a pasta `web/` para o Netlify Drop
- **Vercel**: `vercel web/` na linha de comando
- **Surge.sh**: `surge web/`

## 📝 Notas

- O Brython executa Python diretamente no navegador
- Não requer backend ou servidor Python
- Todos os cálculos são feitos no lado do cliente
- Funciona offline após o primeiro carregamento

## 🐛 Troubleshooting

Se o gráfico não aparecer:
- Verifique o console do navegador (F12)
- Certifique-se de que tem conexão com internet (CDNs)
- Tente abrir em modo anônimo
- Use um navegador moderno (Chrome, Firefox, Edge)

## 📄 Licença

MIT License - Mesmo do projeto principal
