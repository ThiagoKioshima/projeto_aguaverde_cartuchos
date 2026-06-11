
# 🖨️ AVC Gestão — Sistema de Gerenciamento (Água Verde Cartuchos)

Sistema completo de gestão comercial, automação de PDV e inteligência de negócios desenvolvido integralmente em **Python**. O ecossistema integra o controle operacional de frente de caixa a relatórios gerenciais dinâmicos, utilizando uma arquitetura robusta conectada ao banco de dados MySQL.

---

## 📋 Funcionalidades do Sistema

| Módulo | Descrição |
| :--- | :--- |
| **🏠 Dashboard** | KPIs principais, gráficos de desempenho de vendas e alertas automáticos de estoque crítico. |
| **🛒 Nova Venda** | Interface de frente de caixa (PDV) interativa com carrinho de compras, suporte a produtos e ordens de serviços. |
| **📋 Vendas** | Histórico completo de transações comerciais com filtros avançados de busca e rotinas de cancelamento. |
| **👥 Clientes** | Cadastro estruturado e busca rápida de clientes (Pessoa Física e Jurídica). |
| **📦 Produtos** | Controle de inventário automatizado com alertas visuais para níveis de estoque abaixo do mínimo. |
| **🔧 Serviços** | Cadastro e gerenciamento de ordens de recarga de cartuchos e serviços de manutenção. |
| **🚚 Fornecedores** | Cadastro e vínculo de fornecedores aos produtos para otimização da cadeia de suprimentos. |
| **📊 Relatórios** | 7 relatórios dinâmicos e interativos para suporte analítico à tomada de decisão. |
| **👷 Funcionários** | Gestão de equipe e controle estrito de permissões (módulo restrito para perfil Administrador). |

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
* **Python 3.9** ou superior
* **MySQL Server 8.0** ou superior
* Gerenciador de pacotes `pip`

### 2. Instalar Dependências (Ambiente Python)
Clone este repositório, acesse a pasta do projeto e instale as bibliotecas necessárias executando o comando:
```bash
pip install -r requirements.txt

```

### 3. Configurar o Banco de Dados MySQL

Acesse o seu console MySQL ou ferramenta de gerência de sua preferência (como o MySQL Workbench) e crie o schema do sistema:

```sql
CREATE DATABASE gestao_avc CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE gestao_avc;

```

Em seguida, importe os arquivos de migração SQL fornecidos, respeitando a ordem de integridade das chaves estrangeiras:

```bash
mysql -u root -p gestao_avc < gestao_avc_fornecedores.sql
mysql -u root -p gestao_avc < gestao_avc_clientes.sql
mysql -u root -p gestao_avc < gestao_avc_funcionarios.sql
mysql -u root -p gestao_avc < gestao_avc_produtos.sql
mysql -u root -p gestao_avc < gestao_avc_servicos.sql
mysql -u root -p gestao_avc < gestao_avc_vendas.sql
mysql -u root -p gestao_avc < gestao_avc_itens_venda.sql

```

### 4. Configurar Credenciais de Acesso (Secrets do Streamlit)

Crie ou edite o arquivo de configuração `.streamlit/secrets.toml` na raiz do seu projeto com as suas credenciais locais do banco de dados:

```toml
db_host = "localhost"
db_user = "root"
db_password = "SUA_SENHA_AQUI"
db_name = "gestao_avc"

```

### 5. Ativos Visuais

Certifique-se de que o arquivo de imagem `logo_AVC.png` está localizado no mesmo diretório do arquivo principal de execução (`app.py`).

### 6. Executar a Aplicação Python

Inicie o servidor local do Streamlit rodando o comando:

```bash
streamlit run app.py

```

ou alternativamente:

```bash
python -m streamlit run app.py

```

Após a inicialização do script, o sistema abrirá automaticamente ou estará disponível no endereço: `http://localhost:8501`

---

## 🔐 Controle de Acesso (Níveis de Permissão)

O sistema implementa o conceito de Controle de Acesso Baseado em Funções (RBAC). Utilize as credenciais de teste abaixo para validar as diferentes visões e restrições do sistema:

| Funcionário | Senha | Nível de Acesso / Role |
| --- | --- | --- |
| Juliano Moreira Paim | `123` | Administrador (Acesso Total e Gestão) |
| Maria de Oliveira | `123` | Vendedor (Operacional / PDV) |
| Leandro Miguel da Silva | `123` | Vendedor (Operacional / PDV) |
| Thiago Kioshima | `0504` | Vendedor (Operacional / PDV) |

---

## 📊 Módulos de Business Intelligence (Relatórios)

O sistema utiliza o motor analítico do Python para processar os dados transacionais e gerar insights em tempo real através de gráficos dinâmicos:

* **Vendas por Período:** Acompanhamento cronológico (diário, semanal ou mensal) através de gráficos combinados de barras e linhas.
* **Vendas por Canal:** Distribuição percentual e volumétrica por canais de captação (Balcão, Ads, WhatsApp, etc.).
* **Vendas por Pagamento:** Análise de preferência de métodos de pagamento (Pix, Dinheiro, Cartão de Crédito/Débito).
* **Ranking de Produtos:** Identificação do *Top Itens* que geram maior faturamento e volume de saída.
* **Clientes Mais Ativos:** Curva ABC de clientes baseada no volume acumulado de compras.
* **Margem de Lucro:** Avaliação precisa em percentual (%) e valor nominal do lucro real por produto comercializado.
* **Entrega vs Balcão:** Gráfico comparativo entre modalidades de retirada e logística de entrega.

---

## 🏗️ Modelagem Relacional do Banco de Dados

O ecossistema de dados foi modelado utilizando relacionamentos relacionais estritos para garantir a integridade referencial de cada transação efetuada na frente de caixa:

```
clientes ─────────────────────────────────┐
funcionarios ──────────────────────────┐  │
                                       ↓  ↓
                                     vendas
                                       ↓
fornecedores → produtos ──────────→ itens_venda ←── servicos

```

---

## 🎨 Stack Tecnológica

* **Linguagem Base:** [Python 3.9+](https://www.python.org/) (Aplicação de conceitos avançados de POO e manipulação de dados).
* **Interface & Frontend:** [Streamlit](https://streamlit.io/) com injeção de estilo em CSS customizado para aderência à identidade visual da marca.
* **Camada de Persistência:** [MySQL 8.0](https://www.mysql.com/) para armazenamento transacional seguro.
* **Visualização Científica de Dados:** [Plotly Express](https://plotly.com/python/) (Geração de gráficos interativos de pizza, barras e linhas temporais).
* **Tipografia:** Google Fonts (*Nunito* + *Outfit*).

---



### 📂 Documentação Complementar
- [📄 Visualizar Apresentação das Interfaces (PDF)](Interface_tela_AVC.pdf)
