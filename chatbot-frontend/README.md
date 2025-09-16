# 🤖 SIAN - Sistema Inteligente de Arquivos Nacionais

Uma interface moderna e intuitiva para consultas arquivísticas inteligentes, conectada ao banco de dados do AtoM (Access to Memory).

## ✨ Características

- 🔍 **Busca Inteligente**: IA especializada em consultas arquivísticas
- 💬 **Interface de Chat**: Conversação natural com o sistema
- 📱 **Design Responsivo**: Funciona perfeitamente em desktop e mobile
- 🔗 **Links Sugeridos**: Recursos relacionados exibidos dinamicamente
- ⚡ **Streaming em Tempo Real**: Respostas progressivas para melhor UX

## 🚀 Tecnologias

- **React 18** - Framework principal
- **Create React App** - Build tool e dev server
- **CSS Modules** - Estilização modular
- **Design System Gov.br** - Componentes governamentais

## 📦 Instalação

```bash
# Clone o repositório
git clone [url-do-repositorio]

# Entre no diretório
cd chatbot-frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm start
```

## 🛠️ Scripts Disponíveis

```bash
npm start            # Servidor de desenvolvimento
npm run build        # Build para produção
npm test             # Executar testes
npm run eject        # Ejetar configuração CRA
```

## 🏗️ Estrutura do Projeto

```
src/
├── components/          # Componentes React
│   ├── Header/         # Cabeçalho da aplicação
│   ├── ChatHeader/     # Cabeçalho do chat
│   ├── MessageList/    # Lista de mensagens
│   ├── InputForm/      # Formulário de entrada
│   ├── Sidebar/        # Barra lateral com links
│   └── Footer/         # Rodapé
├── icons/              # Ícones SVG
├── logic/              # Lógica de negócio
└── App.jsx            # Componente principal
```

## 🎨 Funcionalidades

### Interface Principal
- **Header Governamental**: Design seguindo padrões gov.br
- **Chat Interativo**: Conversação fluida com a IA
- **Sidebar Responsiva**: Links sugeridos com scroll independente
- **Footer Compacto**: Informações institucionais

### Experiência do Usuário
- **Scroll Independente**: Chat e sidebar com rolagem separada
- **Input Fixo**: Campo de entrada sempre visível
- **Feedback Visual**: Indicadores de carregamento e progresso
- **Design Adaptativo**: Layout otimizado para diferentes telas

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Customização
- **Cores**: Modifique as variáveis CSS nos arquivos `.module.css`
- **Layout**: Ajuste breakpoints no `App.css`
- **Componentes**: Personalize componentes individuais

## 📱 Responsividade

- **Desktop**: Layout completo com sidebar visível
- **Tablet**: Sidebar colapsável
- **Mobile**: Interface otimizada para toque

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

## 🏛️ Sobre

Desenvolvido para o **Arquivo Nacional** como parte do sistema SIAN, facilitando o acesso democrático à informação arquivística através de tecnologia de ponta.

---

**SIAN** • *Sistema Inteligente de Arquivos Nacionais* • Dataprev © 2025