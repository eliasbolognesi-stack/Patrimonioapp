# 🏛️ Frontend - Sistema de Patrimônio

Interface web moderna com tema Dark Red Aesthetic para o sistema de gerenciamento de patrimônios.

## 📁 Estrutura de Arquivos

```
frontend/
├── index.html           # Página de login
├── registro.html        # Página de registro/cadastro
├── dashboard.html       # Dashboard principal (requer login)
├── style.css           # Estilos CSS (tema Dark Red)
├── script.js           # Funções utilitárias compartilhadas
└── README.md           # Este arquivo
```

## 🚀 Como Usar

### 1. Abrir no Navegador

Abra o arquivo `index.html` no seu navegador:

```bash
# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

Ou simplesmente duplo-clique em `index.html`.

### 2. Credenciais de Demo (Login)

Use as seguintes credenciais para acessar:

- **Email:** `admin@patrimonio.com`
- **Senha:** `admin123`

### 3. Navegar pelo Sistema

#### 🔐 Tela de Login (`index.html`)
- Insira seu email e senha
- Opção "Manter-me conectado"
- Link para "Esqueceu a senha?"
- Link para criar nova conta

#### 📝 Tela de Registro (`registro.html`)
- Preencher dados pessoais
- Selecionar departamento
- Campo de confirmação de senha
- Validação em tempo real
- Requisitos de senha informados

#### 📊 Dashboard (`dashboard.html`)
Após fazer login, você terá acesso a:

1. **Dashboard** - Página inicial com:
   - Estatísticas em tempo real
   - Gráficos de patrimônios
   - Tabela dos últimos patrimônios adicionados
   - Status geral do sistema

2. **Patrimônios** - Lista completa com:
   - Tabela de todos os bens
   - Busca e filtros
   - Ações (editar, dar baixa, deletar)

3. **Adicionar Bem** - Formulário para:
   - Cadastrar novo patrimônio
   - Preencher todos os detalhes
   - Selecionar categoria e localização

4. **Relatórios** - Análises com:
   - Resumo geral
   - Breakdown por status
   - Opções de exportar (PDF, CSV)
   - Impressão de relatórios

5. **Categorias** - Gerenciar:
   - Categorias de patrimônios
   - Estatísticas por categoria

## 🎨 Tema Dark Red Aesthetic

O sistema utiliza um tema moderno escuro com acentos em vermelho escuro:

### Paleta de Cores

```css
--primary-color: #8b0000;        /* Vermelho escuro principal */
--primary-dark: #640000;          /* Vermelho ainda mais escuro */
--primary-light: #b91c1c;         /* Vermelho mais claro */
--background: #0f0f0f;            /* Preto profundo */
--background-secondary: #1a1a1a;  /* Cinza muito escuro */
--background-tertiary: #2d2d2d;   /* Cinza escuro */
--text-primary: #ffffff;          /* Branco */
--text-secondary: #b0b0b0;        /* Cinza claro */
```

## 🔗 Integração com API

O sistema está pronto para se conectar com a API Flask do backend.

### Configurar URL da API

Edite o arquivo `script.js` e altere:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Chamadas à API

Use a classe `PatrimonioAPI` para fazer requisições:

```javascript
// Obter lista de patrimônios
const patrimonios = await PatrimonioAPI.getPatrimonios();

// Criar novo patrimônio
const novo = await PatrimonioAPI.createPatrimonio({
    descricao: "Notebook Dell",
    categoria: "Informática",
    valor: 3500
});

// Dar baixa em um patrimônio
await PatrimonioAPI.darBaixa(1, "Motivo da baixa");

// Obter relatório
const relatorio = await PatrimonioAPI.getRelatorioGeral();
```

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:

- ✅ Desktop (1920px e acima)
- ✅ Tablets (768px - 1024px)
- ✅ Mobile (até 768px)

Menu lateral se torna drawer em telas pequenas.

## 🛠️ Utilitários JavaScript

### Formatter

```javascript
Formatter.formatCurrency(3500)      // R$ 3.500,00
Formatter.formatDate('2024-01-15')  // 15/01/2024
Formatter.formatDateTime(...)       // 15/01/2024 10:30
```

### Validator

```javascript
Validator.isValidEmail('email@test.com')  // true/false
Validator.isValidPassword('senha123')     // true/false
Validator.isEmpty('texto')                 // false
```

### Storage

```javascript
Storage.set('user', userData)      // Salvar
Storage.get('user')                // Obter
Storage.remove('user')             // Remover
Storage.clear()                    // Limpar tudo
```

### Notify

```javascript
Notify.success('Sucesso!')
Notify.error('Erro!')
Notify.warning('Aviso!')
Notify.info('Informação!')
```

### DOM

```javascript
DOM.select('.className')           // querySelector
DOM.selectAll('.className')        // querySelectorAll
DOM.create('div', 'class', 'id')  // Criar elemento
DOM.addClass(element, 'class')     // Adicionar classe
DOM.show(element)                  // Mostrar
DOM.hide(element)                  // Esconder
```

## 🔐 Segurança

**Nota:** Este é um exemplo de demonstração. Em produção:

- Nunca armazene senhas em sessionStorage
- Use JWT ou sessões seguras no servidor
- Implemente HTTPS
- Valide todos os dados no servidor
- Implemente CORS adequadamente

## 🐛 Troubleshooting

### Página em branco

- Verifique a URL do arquivo (deve ser `file:///...`)
- Verifique o console do navegador (F12) para erros
- Limpe o cache do navegador (Ctrl+Shift+Delete)

### Não consegue conectar à API

- Verifique se a API está rodando (`python main.py`)
- Confirme a URL em `script.js`
- Verifique CORS na configuração da API

### Login não funciona

- Use as credenciais de demo: `admin@patrimonio.com` / `admin123`
- Verifique o sessionStorage no DevTools
- Limpe o sessionStorage se houver dados antigos

## 📚 Recursos Adicionais

- [CSS Reference](https://developer.mozilla.org/pt-BR/docs/Web/CSS)
- [JavaScript Guide](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript)
- [Fetch API](https://developer.mozilla.org/pt-BR/docs/Web/API/Fetch_API)
- [DOM API](https://developer.mozilla.org/pt-BR/docs/Web/API/Document_Object_Model)

## 📝 Licença

Este projeto é de código aberto e está disponível para uso livre.

---

**Desenvolvido com ❤️ em HTML, CSS e JavaScript puro**
