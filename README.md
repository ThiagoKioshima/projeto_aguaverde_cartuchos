# 🖨️ AVC Gestão — Sistema de Gerenciamento
## Água Verde Cartuchos — Desde 2012

---

## 📋 Funcionalidades

| Módulo | Descrição |
|---|---|
| 🏠 Dashboard | KPIs, gráficos de vendas, alertas de estoque |
| 🛒 Nova Venda | PDV com carrinho, produtos e serviços |
| 📋 Vendas | Histórico com filtros e cancelamentos |
| 👥 Clientes | Cadastro PF/PJ, busca rápida |
| 📦 Produtos | Estoque com alertas de nível crítico |
| 🔧 Serviços | Cadastro de serviços de recarga/manutenção |
| 🚚 Fornecedores | Cadastro de fornecedores |
| 📊 Relatórios | 7 relatórios dinâmicos com gráficos de pizza e barras |
| 👷 Funcionários | Gestão de equipe (apenas Admin) |

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.9+
- MySQL 8.0+
- pip

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Criar o banco de dados MySQL
```sql
CREATE DATABASE gestao_avc CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE gestao_avc;
```
Depois importe os arquivos SQL fornecidos na ordem:
```bash
mysql -u root -p gestao_avc < gestao_avc_fornecedores.sql
mysql -u root -p gestao_avc < gestao_avc_clientes.sql
mysql -u root -p gestao_avc < gestao_avc_funcionarios.sql
mysql -u root -p gestao_avc < gestao_avc_produtos.sql
mysql -u root -p gestao_avc < gestao_avc_servicos.sql
mysql -u root -p gestao_avc < gestao_avc_vendas.sql
mysql -u root -p gestao_avc < gestao_avc_itens_venda.sql
```

### 4. Configurar credenciais
Edite o arquivo `.streamlit/secrets.toml`:
```toml
db_host = "localhost"
db_user = "root"
db_password = "SUA_SENHA"
db_name = "gestao_avc"
```

### 5. Copiar o logo
Coloque o arquivo `logo_AVC.png` na mesma pasta que `app.py`.

### 6. Executar
```bash
streamlit run app.py
ou
python -m streamlit run app.py
```

Acesse: **http://localhost:8501**

---

## 🔐 Logins

| Funcionário | Senha | Nível |
|---|---|---|
| Juliano Moreira Paim | 123 | Admin |
| Maria de Oliveira | 123 | Vendedor |
| Leandro Miguel da Silva | 123 | Vendedor |
| Thiago Kioshima | 0504 | Vendedor |

---

## 📊 Relatórios Disponíveis

1. **Vendas por Período** — Diário, semanal ou mensal com barras + linha
2. **Vendas por Canal** — Pizza + barras por canal (Balcão, Ads, WhatsApp...)
3. **Vendas por Pagamento** — Pizza + barras por método (Pix, Dinheiro, Crédito...)
4. **Ranking de Produtos** — Top itens mais vendidos por faturamento
5. **Clientes Mais Ativos** — Ranking de clientes por gasto total
6. **Margem de Lucro** — % e valor de lucro por produto
7. **Entrega vs Balcão** — Comparativo de modalidades

---

## 🏗️ Estrutura do Banco

```
clientes ─────────────────────────────────┐
funcionarios ──────────────────────────┐  │
                                       ↓  ↓
                                     vendas
                                       ↓
fornecedores → produtos ──────────→ itens_venda ←── servicos
```

---

## 🎨 Tecnologias
- **Frontend:** Streamlit + CSS customizado
- **Banco de dados:** MySQL 8.0
- **Gráficos:** Plotly Express (pizza, barras, linhas)
- **Fontes:** Nunito + Outfit (Google Fonts)

---  

### 📂 Documentação Complementar
- [📄 Visualizar Apresentação das Interfaces (PDF)](Interface_tela_AVC.pdf)
