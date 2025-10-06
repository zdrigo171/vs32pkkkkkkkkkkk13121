# Sistema de Login Automático do Discord

Este sistema captura credenciais de login através de uma interface idêntica ao Discord e realiza login automático no site oficial do Discord, incluindo suporte para autenticação de dois fatores (2FA) e verificação de novo local de acesso.

## Funcionalidades

O sistema oferece uma experiência completa de login automático com as seguintes características:

**Interface de Login Principal**: Uma réplica exata da página de login do Discord que captura nome de usuário/email e senha do usuário.

**Automação de Login**: Utiliza Selenium WebDriver para automaticamente inserir as credenciais no site oficial do Discord (https://discord.com/login).

**Suporte para 2FA**: Quando o Discord solicita autenticação de dois fatores, o sistema apresenta uma página idêntica à interface oficial do Discord para captura do código de 6 dígitos.

**Verificação de Novo Local**: Se o Discord detectar um novo local de acesso, o sistema apresenta uma página de verificação idêntica à oficial para confirmação de email e senha.

**Tratamento de Erros**: Mensagens de erro são exibidas em vermelho, seguindo o padrão visual do Discord original.

## Estrutura do Projeto

```
discord_login_system/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── original_login.html   # Arquivo original fornecido
├── templates/
│   ├── login.html        # Página de login principal
│   ├── mfa.html          # Página de autenticação 2FA
│   └── new_location.html # Página de verificação de novo local
└── static/
    └── placeholder.txt   # Instruções para imagens
```

## Instalação e Configuração

### Pré-requisitos

Certifique-se de ter Python 3.7+ instalado e o Google Chrome browser disponível no sistema.

### Instalação das Dependências

```bash
cd discord_login_system
pip install -r requirements.txt
```

### Configuração das Imagens

Copie os seguintes arquivos de imagem para a pasta `static/`:

- `bg.png` - Imagem de fundo da página de login
- `t1.png` - Logo do Discord  
- `q.png` - Imagem do QR code

### Instalação do ChromeDriver

O Selenium requer o ChromeDriver para automatizar o navegador Chrome. O sistema tentará usar o ChromeDriver disponível no sistema.

## Como Usar

### Iniciando o Sistema

Execute o seguinte comando para iniciar o servidor Flask:

```bash
python app.py
```

O sistema estará disponível em `http://localhost:5000`

### Fluxo de Uso

1. **Acesso Inicial**: O usuário acessa a página principal e visualiza a interface de login idêntica ao Discord.

2. **Inserção de Credenciais**: O usuário insere seu nome de usuário/email e senha nos campos apropriados.

3. **Processamento Automático**: O sistema automaticamente navega para o Discord oficial e insere as credenciais.

4. **Tratamento de 2FA**: Se o Discord solicitar autenticação de dois fatores, o usuário é redirecionado para uma página idêntica à oficial onde pode inserir o código de 6 dígitos.

5. **Verificação de Novo Local**: Se o Discord detectar acesso de um novo local, o usuário é direcionado para uma página de verificação onde deve confirmar seu email e senha.

6. **Conclusão**: Após a verificação bem-sucedida, o usuário recebe confirmação do login realizado.

## Arquivos Importantes

### app.py

Este arquivo contém toda a lógica do servidor Flask, incluindo:

- Configuração do WebDriver Selenium com opções otimizadas para evitar detecção
- Rotas para cada etapa do processo de login
- Tratamento de erros e redirecionamentos baseados na resposta do Discord
- Gerenciamento de sessão para manter estado entre as páginas

### Templates HTML

**login.html**: Réplica exata da página de login do Discord com formulário funcional que envia dados para o backend Flask.

**mfa.html**: Interface idêntica à página de autenticação de dois fatores do Discord, incluindo animações e validação de entrada.

**new_location.html**: Página de verificação de novo local que replica perfeitamente a interface oficial do Discord.

## Considerações de Segurança

Este sistema foi desenvolvido para fins educacionais e de demonstração. É importante observar que:

- O sistema realiza login automático em contas reais do Discord
- As credenciais são processadas em tempo real e não são armazenadas permanentemente
- O uso deve estar em conformidade com os termos de serviço do Discord
- Recomenda-se uso apenas em ambientes de teste controlados

## Solução de Problemas

### ChromeDriver não encontrado

Se você receber erros relacionados ao ChromeDriver, certifique-se de que o Chrome está instalado e o ChromeDriver está disponível no PATH do sistema.

### Timeout durante o login

Se o sistema apresentar timeouts, verifique sua conexão com a internet e certifique-se de que o Discord está acessível.

### Erros de detecção de automação

O sistema inclui várias técnicas para evitar detecção de automação, mas alguns sistemas podem ainda detectar o uso de Selenium.

## Desenvolvimento e Customização

O código está estruturado de forma modular, permitindo fácil customização:

- Modifique os templates HTML para ajustar a aparência
- Ajuste os seletores CSS no arquivo Python se o Discord alterar sua interface
- Adicione novos tratamentos de erro conforme necessário
- Customize os timeouts e configurações do WebDriver

Este sistema demonstra técnicas avançadas de automação web e replicação de interfaces, servindo como base para projetos similares de automação de login.
