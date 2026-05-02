import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime


# 1. CONEXÃO
def conectar():
    return mysql.connector.connect(
        host="localhost", user="root", password="********", database="gestao_avc"
    ) #Configurar a senha


st.set_page_config(page_title="Gestão AVC Pro", layout="wide")

# --- SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso Restrito - Água Verde Cartuchos")
    with st.container(border=True):
        u_id = st.number_input("ID do Funcionário", step=1, value=1)
        u_pw = st.text_input("Senha", type="password")
        if st.form_submit_button or st.button("Entrar"):
            conn = conectar();
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM funcionarios WHERE id_funcionario = %s AND senha = %s", (u_id, u_pw))
            user = cursor.fetchone()
            if user:
                st.session_state.logado = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Acesso negado.")
    st.stop()

# --- MENU LATERAL ---
user = st.session_state.user
st.sidebar.title(f"👤 {user['nome']}")
st.sidebar.write(f"Nível: **{user['nivel_acesso']}**")

opcoes = ["📊 Dashboard & Relatórios", "🛒 Registrar Venda", "📦 Reposição de Estoque"]
if user['nivel_acesso'] == 'Admin':
    opcoes.append("👥 Gestão de Cadastros")

menu = st.sidebar.selectbox("Navegação", opcoes)
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 1. DASHBOARD & RELATÓRIOS (COM ESTORNO E FILTROS) ---
if menu == "📊 Dashboard & Relatórios":
    st.header("📊 Inteligência de Vendas e Estoque")
    try:
        conn = conectar()
        query = """
            SELECT v.id_venda, v.data_venda, c.nome as cliente, f.nome as vendedor, 
                   p.nome_produto, i.quantidade, (i.quantidade * i.valor_unitario) as total, v.status
            FROM vendas v
            JOIN itens_venda i ON v.id_venda = i.id_venda
            JOIN produtos p ON i.id_produto = p.id_produto
            JOIN clientes c ON v.id_cliente = c.id_cliente
            JOIN funcionarios f ON v.id_funcionario = f.id_funcionario
        """
        df = pd.read_sql(query, conn)
        df['data_venda'] = pd.to_datetime(df['data_venda'])

        # Filtros Dinâmicos
        col_f1, col_f2, col_f3 = st.columns(3)
        data_sel = col_f1.date_input("Filtrar Período", [df['data_venda'].min(), df['data_venda'].max()])
        vend_sel = col_f2.selectbox("Vendedor", ["Todos"] + list(df['vendedor'].unique()))
        stat_sel = col_f3.selectbox("Status", ["Todas", "Ativa", "Cancelada"])

        # Aplicação dos Filtros
        mask = (df['data_venda'].dt.date >= data_sel[0]) & (df['data_venda'].dt.date <= data_sel[1])
        if vend_sel != "Todos": mask &= (df['vendedor'] == vend_sel)
        if stat_sel != "Todas": mask &= (df['status'] == stat_sel)
        df_filtrado = df[mask]

        st.dataframe(df_filtrado, use_container_width=True)

        # Gráfico de Estoque Atual
        st.divider()
        st.subheader("📦 Relatório de Nível de Estoque")
        df_est = pd.read_sql("SELECT nome_produto, estoque_atual FROM produtos", conn)
        st.bar_chart(df_est.set_index('nome_produto'))

        # Área de Estorno (Apenas Admin)
        if user['nivel_acesso'] == 'Admin':
            with st.expander("🚨 ÁREA CRÍTICA: Estornar Venda"):
                id_estorno = st.number_input("ID da Venda para Cancelar", min_value=1)
                motivo = st.text_input("Motivo do Estorno")
                if st.button("Confirmar Cancelamento"):
                    cursor = conn.cursor()
                    # Devolve produtos ao estoque
                    cursor.execute("SELECT id_produto, quantidade FROM itens_venda WHERE id_venda = %s", (id_estorno,))
                    itens = cursor.fetchall()
                    for it in itens:
                        cursor.execute("UPDATE produtos SET estoque_atual = estoque_atual + %s WHERE id_produto = %s",
                                       (it[1], it[0]))
                    # Muda status para Cancelada
                    cursor.execute(
                        "UPDATE vendas SET status = 'Cancelada', motivo_cancelamento = %s WHERE id_venda = %s",
                        (motivo, id_estorno))
                    conn.commit();
                    st.warning(f"Venda {id_estorno} estornada!");
                    st.rerun()
        conn.close()
    except Exception as e:
        st.info("Sem dados para exibir.")

# --- 2. REGISTRAR VENDA (COM DATA RETROATIVA) ---
elif menu == "🛒 Registrar Venda":
    st.header("🛒 Lançamento de Venda")
    conn = conectar()
    clientes = pd.read_sql("SELECT id_cliente, nome FROM clientes", conn)
    produtos = pd.read_sql("SELECT id_produto, nome_produto, preco_venda, estoque_atual FROM produtos", conn)

    with st.form("venda_form"):
        col_v1, col_v2 = st.columns(2)
        data_venda = col_v1.date_input("Data da Operação", datetime.now())
        cliente_v = col_v2.selectbox("Cliente", clientes['nome'])
        prod_v = st.selectbox("Produto", produtos['nome_produto'])
        qtd_v = st.number_input("Quantidade", min_value=1, value=1)

        if st.form_submit_button("Finalizar Venda"):
            info = produtos[produtos['nome_produto'] == prod_v].iloc[0]
            if info['estoque_atual'] < qtd_v:
                st.error("Estoque insuficiente!")
            else:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO vendas (id_cliente, id_funcionario, data_venda) VALUES (%s, %s, %s)",
                               (int(clientes[clientes['nome'] == cliente_v]['id_cliente'].iloc[0]),
                                user['id_funcionario'], data_venda))
                id_v = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO itens_venda (id_venda, id_produto, quantidade, valor_unitario) VALUES (%s,%s,%s,%s)",
                    (id_v, int(info['id_produto']), qtd_v, float(info['preco_venda'])))
                cursor.execute("UPDATE produtos SET estoque_atual = estoque_atual - %s WHERE id_produto = %s",
                               (qtd_v, int(info['id_produto'])))
                conn.commit();
                st.success("Venda registrada!")
    conn.close()

# --- 3. REPOSIÇÃO DE ESTOQUE ---
elif menu == "📦 Reposição de Estoque":
    st.header("📦 Entrada de Mercadorias")
    conn = conectar()
    df_p = pd.read_sql("SELECT id_produto, nome_produto, estoque_atual FROM produtos", conn)
    sel_p = st.selectbox("Selecione o Produto", df_p['nome_produto'])
    qtd_add = st.number_input("Quantidade de Entrada", min_value=1)
    if st.button("Confirmar Entrada"):
        id_p = int(df_p[df_p['nome_produto'] == sel_p]['id_produto'].iloc[0])
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET estoque_atual = estoque_atual + %s WHERE id_produto = %s", (qtd_add, id_p))
        conn.commit();
        st.success("Estoque atualizado!");
        st.rerun()
    conn.close()