# Sistema de Mensagens de Progresso Automáticas

## Descrição

Este sistema garante que o usuário sempre veja mensagens de progresso durante o carregamento de respostas, mesmo quando o servidor não envia atualizações por um período prolongado.

## Funcionalidades

### 1. Timeout Configurável
- **Localização**: `src/config/progressConfig.js`
- **Parâmetro**: `TIMEOUT_SECONDS` (padrão: 15 segundos)
- **Função**: Define o tempo máximo sem atualizações antes de gerar uma mensagem automática

### 2. Mensagens Automáticas
- **Localização**: `src/config/progressConfig.js`
- **Array**: `MESSAGES`
- **Função**: Lista de mensagens que são exibidas aleatoriamente quando o timeout é atingido

### 3. Gerenciamento Inteligente
- **Hook**: `src/hooks/useProgressTimeout.js`
- **Funcionalidades**:
  - Inicia timeout quando uma requisição começa
  - Para timeout quando uma resposta parcial chega
  - Limpa timeout quando a requisição termina
  - Gera mensagens automáticas em intervalos regulares

## Como Funciona

1. **Início da Requisição**: Quando o usuário envia uma pergunta, o sistema inicia um timer
2. **Atualizações do Servidor**: Cada mensagem de progresso do servidor reinicia o timer
3. **Timeout Atingido**: Se não há atualizações por X segundos, uma mensagem automática é gerada
4. **Repetição**: O processo se repete até que uma resposta final chegue
5. **Limpeza**: Todos os timers são limpos quando a requisição termina

## Configuração

Para alterar o comportamento do sistema, edite `src/config/progressConfig.js`:

```javascript
export const PROGRESS_CONFIG = {
  // Altere este valor para modificar o timeout (em segundos)
  TIMEOUT_SECONDS: 15,
  
  // Adicione ou modifique mensagens aqui
  MESSAGES: [
    "Sua mensagem personalizada...",
    // ... outras mensagens
  ]
};
```

## Estados Monitorados

- **isLoading**: Indica se há uma requisição em andamento
- **partialResponse**: Indica se já chegou alguma resposta parcial do servidor
- **currentProgressMessage**: A mensagem de progresso atual sendo exibida

## Integração

O sistema está integrado em:
- `App.jsx`: Componente principal que gerencia os estados
- `createHandleSubmit.js`: Lógica de envio que controla os timers
- `MessageList.jsx`: Componente que exibe as mensagens de progresso