import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import base64

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AVC Gestão",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 10px !important;
    width: 100%;
    margin-bottom: 2px;
    padding: 4px 8px !important;
    font-size: 0.85rem !important;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,215,0,0.2) !important;
    border-color: #ffd700 !important;
}
[data-testid="stSidebar"] .stButton button p {
    font-size: 0.85rem !important;
    line-height: 1.3 !important;
}

/* Main area */
.main .block-container {
    padding-top: 1.5rem;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 5px solid;
    margin-bottom: 12px;
}
.kpi-value {
    font-family: 'Nunito', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    margin: 0;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.8rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-top: 4px;
}
.kpi-card.blue  { border-color: #2563eb; }
.kpi-card.green { border-color: #16a34a; }
.kpi-card.amber { border-color: #d97706; }
.kpi-card.red   { border-color: #dc2626; }
.kpi-card.purple{ border-color: #7c3aed; }
.kpi-card.cyan  { border-color: #0891b2; }

.kpi-value.blue  { color: #2563eb; }
.kpi-value.green { color: #16a34a; }
.kpi-value.amber { color: #d97706; }
.kpi-value.red   { color: #dc2626; }
.kpi-value.purple{ color: #7c3aed; }
.kpi-value.cyan  { color: #0891b2; }

/* Section titles */
.section-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 24px 0 12px 0;
    border-bottom: 3px solid #ffd700;
    padding-bottom: 6px;
    display: inline-block;
}

/* Alert boxes */
.alert-low {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 4px 0;
    font-size: 0.9rem;
}
.alert-critical {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 4px 0;
    font-size: 0.9rem;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-pf { background: #dbeafe; color: #1d4ed8; }
.badge-pj { background: #f3e8ff; color: #7c3aed; }
.badge-ativa { background: #dcfce7; color: #15803d; }
.badge-cancelada { background: #fee2e2; color: #b91c1c; }

/* Logo area */
.logo-container {
    text-align: center;
    padding: 10px 10px 4px;
}
</style>
""", unsafe_allow_html=True)

# ─── Database Connection ──────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets.get("db_host", "localhost"),
        user=st.secrets.get("db_user", "root"),
        password=st.secrets.get("db_password", ""),
        database=st.secrets.get("db_name", "gestao_avc"),
        charset="utf8mb4"
    )

def run_query(sql, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=params)
        return df
    except Exception as e:
        conn.reconnect()
        return pd.read_sql(sql, get_connection(), params=params)

def execute_query(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

# ─── Auth ────────────────────────────────────────────────────────────────────
def login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        try:
            st.image("logo_AVC.png", width=300)
        except:
            st.title("🖨️ Água Verde Cartuchos")
        st.markdown("### Acesso ao Sistema")
        nome = st.selectbox("Funcionário", [""] + list(run_query("SELECT nome FROM funcionarios ORDER BY nome")["nome"]))
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if nome:
                row = run_query(
                    "SELECT id_funcionario, nome, nivel_acesso FROM funcionarios WHERE nome=%s AND senha=%s",
                    params=(nome, senha)
                )
                if len(row) > 0:
                    st.session_state.user = row.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
            else:
                st.warning("Selecione um funcionário.")

# ─── Sidebar Nav ─────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            st.image("logo_AVC.png", width=160)
        except:
            st.markdown("## 🖨️ AVC Gestão")
        st.markdown('</div>', unsafe_allow_html=True)

        user = st.session_state.user
        st.markdown(f"👤 **{user['nome'].split()[0]}** — *{user['nivel_acesso']}*")
        st.markdown("---")

        pages = ["🏠 Dashboard", "🛒 Nova Venda", "📋 Vendas", "👥 Clientes",
                 "📦 Produtos", "🔧 Serviços", "🚚 Fornecedores", "📊 Relatórios"]
        if user["nivel_acesso"] == "Admin":
            pages.append("👷 Funcionários")

        for p in pages:
            if st.button(p, key=f"nav_{p}"):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Sair"):
            del st.session_state.user
            st.session_state.page = "🏠 Dashboard"
            st.rerun()

# ─── Pages ───────────────────────────────────────────────────────────────────

def dashboard():
    st.markdown('<p class="section-title">📊 Dashboard Geral</p>', unsafe_allow_html=True)

    # KPIs
    total_vendas = run_query("SELECT COUNT(*) as n FROM vendas WHERE status='Ativa'").iloc[0]["n"]
    faturamento = run_query(
        "SELECT COALESCE(SUM(iv.quantidade * iv.valor_unitario),0) as t FROM itens_venda iv JOIN vendas v ON iv.id_venda=v.id_venda WHERE v.status='Ativa'"
    ).iloc[0]["t"]
    clientes = run_query("SELECT COUNT(*) as n FROM clientes").iloc[0]["n"]
    produtos_estoque = run_query("SELECT COUNT(*) as n FROM produtos WHERE estoque_atual > 0").iloc[0]["n"]
    estoque_baixo = run_query("SELECT COUNT(*) as n FROM produtos WHERE estoque_atual <= 5").iloc[0]["n"]
    vendas_mes = run_query(
        "SELECT COUNT(*) as n FROM vendas WHERE MONTH(data_venda)=MONTH(CURDATE()) AND YEAR(data_venda)=YEAR(CURDATE()) AND status='Ativa'"
    ).iloc[0]["n"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="kpi-card blue">
            <p class="kpi-value blue">R$ {faturamento:,.2f}</p>
            <p class="kpi-label">💰 Faturamento Total</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card green">
            <p class="kpi-value green">{total_vendas:,}</p>
            <p class="kpi-label">🛒 Vendas Ativas</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card amber">
            <p class="kpi-value amber">{vendas_mes}</p>
            <p class="kpi-label">📅 Vendas Este Mês</p></div>""", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(f"""<div class="kpi-card purple">
            <p class="kpi-value purple">{clientes}</p>
            <p class="kpi-label">👥 Clientes Cadastrados</p></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="kpi-card cyan">
            <p class="kpi-value cyan">{produtos_estoque}</p>
            <p class="kpi-label">📦 Produtos em Estoque</p></div>""", unsafe_allow_html=True)
    with c6:
        cor = "red" if estoque_baixo > 0 else "green"
        st.markdown(f"""<div class="kpi-card {cor}">
            <p class="kpi-value {cor}">{estoque_baixo}</p>
            <p class="kpi-label">⚠️ Estoque Crítico (≤5)</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        # Vendas por mês
        df_mes = run_query("""
            SELECT DATE_FORMAT(v.data_venda,'%Y-%m') as mes,
                   SUM(iv.quantidade * iv.valor_unitario) as total
            FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE v.status='Ativa'
            GROUP BY mes ORDER BY mes DESC LIMIT 6
        """)
        df_mes = df_mes.sort_values("mes")
        if not df_mes.empty:
            fig = px.bar(df_mes, x="mes", y="total", title="💰 Faturamento por Mês",
                         color_discrete_sequence=["#2563eb"],
                         labels={"mes": "Mês", "total": "Faturamento (R$)"})
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              title_font_size=14, height=300, margin=dict(t=40,b=20,l=20,r=20))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Métodos de pagamento
        df_pag = run_query("""
            SELECT metodo_pagamento as metodo, COUNT(*) as qtd
            FROM vendas WHERE status='Ativa' AND metodo_pagamento IS NOT NULL
            GROUP BY metodo_pagamento
        """)
        if not df_pag.empty:
            fig2 = px.pie(df_pag, names="metodo", values="qtd",
                          title="💳 Métodos de Pagamento",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(height=300, margin=dict(t=40,b=20,l=20,r=20))
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Top produtos
        df_top = run_query("""
            SELECT COALESCE(p.nome_produto, s.nome_servico) as item,
                   SUM(iv.quantidade) as vendidos
            FROM itens_venda iv
            LEFT JOIN produtos p ON iv.id_produto=p.id_produto
            LEFT JOIN servicos s ON iv.id_servico=s.id_servico
            JOIN vendas v ON iv.id_venda=v.id_venda
            WHERE v.status='Ativa'
            GROUP BY item ORDER BY vendidos DESC LIMIT 8
        """)
        if not df_top.empty:
            fig3 = px.bar(df_top, x="vendidos", y="item", orientation="h",
                          title="🏆 Top Itens Vendidos",
                          color_discrete_sequence=["#16a34a"],
                          labels={"vendidos": "Qtd Vendida", "item": ""})
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               height=320, margin=dict(t=40,b=20,l=20,r=20))
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Estoque baixo alert
        st.markdown('<p class="section-title">⚠️ Alertas de Estoque</p>', unsafe_allow_html=True)
        df_alerta = run_query("SELECT nome_produto, estoque_atual FROM produtos WHERE estoque_atual <= 10 ORDER BY estoque_atual")
        if df_alerta.empty:
            st.success("✅ Estoque saudável!")
        else:
            for _, r in df_alerta.iterrows():
                cls = "alert-critical" if r.estoque_atual <= 3 else "alert-low"
                icon = "🔴" if r.estoque_atual <= 3 else "🟡"
                st.markdown(f'<div class="{cls}">{icon} <b>{r.nome_produto}</b> — {r.estoque_atual} un.</div>',
                            unsafe_allow_html=True)

# ─── Nova Venda ───────────────────────────────────────────────────────────────
def nova_venda():
    st.markdown('<p class="section-title">🛒 Registrar Nova Venda</p>', unsafe_allow_html=True)

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    col1, col2 = st.columns(2)
    with col1:
        df_cli = run_query("SELECT id_cliente, nome FROM clientes ORDER BY nome")
        opcoes_cli = ["Sem cadastro"] + [f"{r.id_cliente} – {r.nome}" for _, r in df_cli.iterrows()]
        cliente_sel = st.selectbox("Cliente", opcoes_cli)

        metodo = st.selectbox("Método de Pagamento", ["Din", "Pix", "Cred", "Deb", "Outro"])
        canal = st.selectbox("Canal", ["Cliente", "Balcão", "Ads", "WhatsApp", "Outro"])
        entrega = st.radio("Entrega?", ["Não", "Sim"], horizontal=True)

    with col2:
        tipo_item = st.radio("Tipo", ["Produto", "Serviço"], horizontal=True)
        if tipo_item == "Produto":
            df_prod = run_query("SELECT id_produto, nome_produto, preco_venda, estoque_atual FROM produtos WHERE estoque_atual > 0 ORDER BY nome_produto")
            item_sel = st.selectbox("Produto", [f"{r.id_produto} – {r.nome_produto} (R${r.preco_venda:.2f}) [{r.estoque_atual} un]" for _, r in df_prod.iterrows()])
            preco_sug = 0.0
            if item_sel and len(df_prod):
                id_p = int(item_sel.split(" – ")[0])
                row = df_prod[df_prod.id_produto == id_p]
                if len(row): preco_sug = float(row.iloc[0]["preco_venda"])
        else:
            df_svc = run_query("SELECT id_servico, nome_servico, preco_venda FROM servicos ORDER BY nome_servico")
            item_sel = st.selectbox("Serviço", [f"{r.id_servico} – {r.nome_servico} (R${r.preco_venda:.2f})" for _, r in df_svc.iterrows()])
            preco_sug = 0.0
            if item_sel and len(df_svc):
                id_s = int(item_sel.split(" – ")[0])
                row = df_svc[df_svc.id_servico == id_s]
                if len(row): preco_sug = float(row.iloc[0]["preco_venda"])

        qtd = st.number_input("Quantidade", min_value=1, value=1)
        preco = st.number_input("Preço unitário (R$)", min_value=0.01, value=preco_sug, step=0.5)

        if st.button("➕ Adicionar ao Carrinho", use_container_width=True):
            if item_sel:
                nome_item = item_sel.split(" – ")[1].split(" (")[0]
                id_num = int(item_sel.split(" – ")[0])
                st.session_state.carrinho.append({
                    "tipo": tipo_item,
                    "id": id_num,
                    "nome": nome_item,
                    "qtd": qtd,
                    "preco": preco,
                    "subtotal": round(qtd * preco, 2)
                })
                st.rerun()

    # Carrinho
    st.markdown("---")
    st.markdown('<p class="section-title">🛍️ Carrinho</p>', unsafe_allow_html=True)

    if not st.session_state.carrinho:
        st.info("Carrinho vazio. Adicione itens acima.")
    else:
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_cart[["tipo","nome","qtd","preco","subtotal"]].rename(columns={
            "tipo":"Tipo","nome":"Item","qtd":"Qtd","preco":"Preço (R$)","subtotal":"Subtotal (R$)"
        }), use_container_width=True, hide_index=True)

        total = sum(i["subtotal"] for i in st.session_state.carrinho)
        st.markdown(f"### 💰 Total: **R$ {total:.2f}**")

        c_rem, c_fin = st.columns(2)
        with c_rem:
            idx_rem = st.number_input("Remover item nº", min_value=1, max_value=len(st.session_state.carrinho), value=1)
            if st.button("🗑️ Remover"):
                st.session_state.carrinho.pop(idx_rem - 1)
                st.rerun()
        with c_fin:
            if st.button("✅ Finalizar Venda", use_container_width=True, type="primary"):
                try:
                    id_cli = None
                    if cliente_sel != "Sem cadastro":
                        id_cli = int(cliente_sel.split(" – ")[0])
                    id_func = st.session_state.user["id_funcionario"]
                    ent = "S" if entrega == "Sim" else "N"
                    id_venda = execute_query(
                        "INSERT INTO vendas (metodo_pagamento, canal, entrega, id_cliente, id_funcionario) VALUES (%s,%s,%s,%s,%s)",
                        (metodo, canal, ent, id_cli, id_func)
                    )
                    for item in st.session_state.carrinho:
                        if item["tipo"] == "Produto":
                            execute_query(
                                "INSERT INTO itens_venda (id_venda, id_produto, quantidade, valor_unitario) VALUES (%s,%s,%s,%s)",
                                (id_venda, item["id"], item["qtd"], item["preco"])
                            )
                            execute_query(
                                "UPDATE produtos SET estoque_atual = estoque_atual - %s WHERE id_produto=%s",
                                (item["qtd"], item["id"])
                            )
                        else:
                            execute_query(
                                "INSERT INTO itens_venda (id_venda, id_servico, quantidade, valor_unitario) VALUES (%s,%s,%s,%s)",
                                (id_venda, item["id"], item["qtd"], item["preco"])
                            )
                    st.session_state.carrinho = []
                    st.success(f"✅ Venda #{id_venda} registrada com sucesso! Total: R$ {total:.2f}")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.button("🧹 Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

# ─── Vendas ───────────────────────────────────────────────────────────────────
def vendas():
    st.markdown('<p class="section-title">📋 Histórico de Vendas</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        dt_ini = st.date_input("Data início", value=date(2025, 11, 1))
    with col2:
        dt_fim = st.date_input("Data fim", value=date.today())
    with col3:
        status_f = st.selectbox("Status", ["Todos", "Ativa", "Cancelada"])

    df = run_query(f"""
        SELECT v.id_venda, v.data_venda, c.nome as cliente,
               f.nome as vendedor, v.metodo_pagamento, v.canal,
               v.entrega, v.status,
               COALESCE(SUM(iv.quantidade*iv.valor_unitario),0) as total
        FROM vendas v
        LEFT JOIN clientes c ON v.id_cliente=c.id_cliente
        LEFT JOIN funcionarios f ON v.id_funcionario=f.id_funcionario
        LEFT JOIN itens_venda iv ON v.id_venda=iv.id_venda
        WHERE DATE(v.data_venda) BETWEEN '{dt_ini}' AND '{dt_fim}'
        {"AND v.status='"+status_f+"'" if status_f != "Todos" else ""}
        GROUP BY v.id_venda
        ORDER BY v.data_venda DESC
    """)

    st.markdown(f"**{len(df)} vendas** | Total: R$ **{df['total'].sum():,.2f}**")
    st.dataframe(df.rename(columns={
        "id_venda":"#","data_venda":"Data","cliente":"Cliente","vendedor":"Vendedor",
        "metodo_pagamento":"Pagamento","canal":"Canal","entrega":"Entrega","status":"Status","total":"Total (R$)"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Cancelar venda**")
    id_can = st.number_input("ID da venda", min_value=1, step=1)
    motivo = st.text_input("Motivo do cancelamento")
    if st.button("❌ Cancelar Venda"):
        execute_query("UPDATE vendas SET status='Cancelada', motivo_cancelamento=%s WHERE id_venda=%s",
                      (motivo, id_can))
        st.success("Venda cancelada.")
        st.rerun()

# ─── Clientes ────────────────────────────────────────────────────────────────
def clientes():
    st.markdown('<p class="section-title">👥 Clientes</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Cliente"])
    with tab1:
        busca = st.text_input("🔍 Buscar cliente")
        df = run_query(f"SELECT * FROM clientes {'WHERE nome LIKE %s OR whatsapp LIKE %s' if busca else ''} ORDER BY nome",
                       params=(f"%{busca}%", f"%{busca}%") if busca else None)
        st.dataframe(df.rename(columns={"id_cliente":"ID","nome":"Nome","whatsapp":"WhatsApp","tipo_cliente":"Tipo"}),
                     use_container_width=True, hide_index=True)

    with tab2:
        nome = st.text_input("Nome *")
        whatsapp = st.text_input("WhatsApp")
        tipo = st.radio("Tipo", ["PF", "PJ"], horizontal=True)
        if st.button("Salvar Cliente", type="primary"):
            if nome:
                execute_query("INSERT INTO clientes (nome, whatsapp, tipo_cliente) VALUES (%s,%s,%s)",
                              (nome, whatsapp or None, tipo))
                st.success("Cliente cadastrado!")
                st.rerun()
            else:
                st.error("Nome obrigatório.")

# ─── Produtos ────────────────────────────────────────────────────────────────
def produtos():
    st.markdown('<p class="section-title">📦 Produtos</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Novo Produto", "🔄 Atualizar Estoque"])
    with tab1:
        df = run_query("""
            SELECT p.id_produto, p.nome_produto, p.preco_custo, p.preco_venda,
                   p.estoque_atual, f.nome_fantasia as fornecedor
            FROM produtos p LEFT JOIN fornecedores f ON p.id_fornecedor=f.id_fornecedor
            ORDER BY p.nome_produto
        """)
        # Highlight estoque baixo
        def highlight(val):
            if isinstance(val, (int, float)):
                if val <= 3: return "background-color:#fee2e2; color:#b91c1c; font-weight:bold"
                if val <= 10: return "background-color:#fff7ed; color:#d97706"
            return ""
        st.dataframe(df.rename(columns={
            "id_produto":"ID","nome_produto":"Produto","preco_custo":"Custo (R$)",
            "preco_venda":"Venda (R$)","estoque_atual":"Estoque","fornecedor":"Fornecedor"
        }).style.map(highlight, subset=["Estoque"]), use_container_width=True, hide_index=True)

    with tab2:
        df_forn = run_query("SELECT id_fornecedor, nome_fantasia FROM fornecedores ORDER BY nome_fantasia")
        nome_p = st.text_input("Nome do produto *")
        desc = st.text_area("Descrição")
        c1, c2 = st.columns(2)
        with c1: custo = st.number_input("Preço de custo", min_value=0.0, step=0.5)
        with c2: venda = st.number_input("Preço de venda", min_value=0.0, step=0.5)
        estoque = st.number_input("Estoque inicial", min_value=0, value=0)
        forn_opts = [f"{r.id_fornecedor} – {r.nome_fantasia}" for _, r in df_forn.iterrows()]
        forn_sel = st.selectbox("Fornecedor", forn_opts)
        if st.button("Salvar Produto", type="primary"):
            if nome_p:
                id_f = int(forn_sel.split(" – ")[0])
                execute_query("INSERT INTO produtos (nome_produto, descricao, preco_custo, preco_venda, estoque_atual, id_fornecedor) VALUES (%s,%s,%s,%s,%s,%s)",
                              (nome_p, desc or None, custo, venda, estoque, id_f))
                st.success("Produto cadastrado!")
                st.rerun()

    with tab3:
        df_p = run_query("SELECT id_produto, nome_produto, estoque_atual FROM produtos ORDER BY nome_produto")
        p_opts = [f"{r.id_produto} – {r.nome_produto} (atual: {r.estoque_atual})" for _, r in df_p.iterrows()]
        p_sel = st.selectbox("Produto", p_opts)
        op = st.radio("Operação", ["Adicionar", "Subtrair", "Definir"], horizontal=True)
        qtd = st.number_input("Quantidade", min_value=0, value=1)
        if st.button("Atualizar Estoque", type="primary"):
            id_p = int(p_sel.split(" – ")[0])
            if op == "Adicionar":
                sql = "UPDATE produtos SET estoque_atual = estoque_atual + %s WHERE id_produto=%s"
            elif op == "Subtrair":
                sql = "UPDATE produtos SET estoque_atual = GREATEST(0, estoque_atual - %s) WHERE id_produto=%s"
            else:
                sql = "UPDATE produtos SET estoque_atual = %s WHERE id_produto=%s"
            execute_query(sql, (qtd, id_p))
            st.success("Estoque atualizado!")
            st.rerun()

# ─── Serviços ────────────────────────────────────────────────────────────────
def servicos():
    st.markdown('<p class="section-title">🔧 Serviços</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Serviço"])
    with tab1:
        df = run_query("SELECT * FROM servicos ORDER BY nome_servico")
        st.dataframe(df.rename(columns={"id_servico":"ID","nome_servico":"Serviço","preco_venda":"Preço (R$)"}),
                     use_container_width=True, hide_index=True)
    with tab2:
        nome_s = st.text_input("Nome do serviço *")
        preco_s = st.number_input("Preço (R$)", min_value=0.01, step=5.0)
        if st.button("Salvar Serviço", type="primary"):
            if nome_s:
                execute_query("INSERT INTO servicos (nome_servico, preco_venda) VALUES (%s,%s)", (nome_s, preco_s))
                st.success("Serviço cadastrado!")
                st.rerun()

# ─── Fornecedores ─────────────────────────────────────────────────────────────
def fornecedores():
    st.markdown('<p class="section-title">🚚 Fornecedores</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Fornecedor"])
    with tab1:
        df = run_query("SELECT * FROM fornecedores ORDER BY nome_fantasia")
        st.dataframe(df.rename(columns={"id_fornecedor":"ID","nome_fantasia":"Fornecedor","cnpj":"CNPJ","contato":"Contato"}),
                     use_container_width=True, hide_index=True)
    with tab2:
        nome_f = st.text_input("Nome fantasia *")
        cnpj = st.text_input("CNPJ")
        contato = st.text_input("Contato")
        if st.button("Salvar Fornecedor", type="primary"):
            if nome_f:
                execute_query("INSERT INTO fornecedores (nome_fantasia, cnpj, contato) VALUES (%s,%s,%s)",
                              (nome_f, cnpj or None, contato or None))
                st.success("Fornecedor cadastrado!")
                st.rerun()

# ─── Funcionários ─────────────────────────────────────────────────────────────
def funcionarios():
    st.markdown('<p class="section-title">👷 Funcionários</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Funcionário"])
    with tab1:
        df = run_query("SELECT id_funcionario, nome, cargo, data_admissao, nivel_acesso FROM funcionarios ORDER BY nome")
        st.dataframe(df.rename(columns={
            "id_funcionario":"ID","nome":"Nome","cargo":"Cargo",
            "data_admissao":"Admissão","nivel_acesso":"Acesso"
        }), use_container_width=True, hide_index=True)
    with tab2:
        nome_fn = st.text_input("Nome *")
        cargo = st.text_input("Cargo")
        adm = st.date_input("Data de admissão", value=date.today())
        senha = st.text_input("Senha", value="123")
        nivel = st.radio("Nível de acesso", ["Vendedor", "Admin"], horizontal=True)
        if st.button("Salvar Funcionário", type="primary"):
            if nome_fn:
                execute_query("INSERT INTO funcionarios (nome, cargo, data_admissao, senha, nivel_acesso) VALUES (%s,%s,%s,%s,%s)",
                              (nome_fn, cargo or None, adm, senha, nivel))
                st.success("Funcionário cadastrado!")
                st.rerun()

# ─── Relatórios ───────────────────────────────────────────────────────────────
def relatorios():
    st.markdown('<p class="section-title">📊 Relatórios Dinâmicos</p>', unsafe_allow_html=True)

    tipo_rel = st.selectbox("Tipo de relatório", [
        "🔍 Relatório Detalhado por Venda",
        "Vendas por Período", "Vendas por Canal", "Vendas por Pagamento",
        "Ranking de Produtos", "Clientes Mais Ativos", "Margem de Lucro",
        "Entrega vs Balcão"
    ])

    # ── Filtros comuns de período ──────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        dt_ini = st.date_input("Data início", value=date(2025, 11, 1), key="rel_ini")
    with col2:
        dt_fim = st.date_input("Data fim", value=date.today(), key="rel_fim")

    filtro_periodo = f"DATE(v.data_venda) BETWEEN '{dt_ini}' AND '{dt_fim}' AND v.status='Ativa'"

    # ══════════════════════════════════════════════════════════════════════════
    # NOVO: Relatório Detalhado por Venda — com filtros dinâmicos
    # ══════════════════════════════════════════════════════════════════════════
    if tipo_rel == "🔍 Relatório Detalhado por Venda":
        st.markdown("#### Filtros")

        # Linha de filtros dinâmicos
        fc1, fc2, fc3, fc4 = st.columns(4)

        # Filtro: Cliente
        with fc1:
            df_cli = run_query("SELECT id_cliente, nome FROM clientes ORDER BY nome")
            opcoes_cli = ["Todos"] + [f"{r.id_cliente} – {r.nome}" for _, r in df_cli.iterrows()]
            cli_sel = st.selectbox("👤 Cliente", opcoes_cli, key="filt_cli")

        # Filtro: Produto / Serviço
        with fc2:
            df_prod = run_query("""
                SELECT 'P' as tipo, id_produto as id, nome_produto as nome FROM produtos
                UNION ALL
                SELECT 'S', id_servico, nome_servico FROM servicos
                ORDER BY nome
            """)
            opcoes_prod = ["Todos"] + [
                f"{'Produto' if r.tipo=='P' else 'Serviço'}: {r.nome}"
                for _, r in df_prod.iterrows()
            ]
            prod_sel = st.selectbox("📦 Produto / Serviço", opcoes_prod, key="filt_prod")

        # Filtro: Vendedor
        with fc3:
            df_func = run_query("SELECT id_funcionario, nome FROM funcionarios ORDER BY nome")
            opcoes_func = ["Todos"] + [f"{r.id_funcionario} – {r.nome}" for _, r in df_func.iterrows()]
            func_sel = st.selectbox("👷 Vendedor", opcoes_func, key="filt_func")

        # Filtro: Método de pagamento
        with fc4:
            df_pag = run_query("SELECT DISTINCT metodo_pagamento FROM vendas WHERE metodo_pagamento IS NOT NULL ORDER BY metodo_pagamento")
            opcoes_pag = ["Todos"] + list(df_pag["metodo_pagamento"])
            pag_sel = st.selectbox("💳 Pagamento", opcoes_pag, key="filt_pag")

        # Monta cláusulas WHERE dinamicamente
        where_clauses = [f"DATE(v.data_venda) BETWEEN '{dt_ini}' AND '{dt_fim}'", "v.status='Ativa'"]

        if cli_sel != "Todos":
            id_cli = int(cli_sel.split(" – ")[0])
            where_clauses.append(f"v.id_cliente = {id_cli}")

        if func_sel != "Todos":
            id_func = int(func_sel.split(" – ")[0])
            where_clauses.append(f"v.id_funcionario = {id_func}")

        if pag_sel != "Todos":
            where_clauses.append(f"v.metodo_pagamento = '{pag_sel}'")

        # Filtro de produto/serviço requer join em itens_venda
        prod_join_filter = ""
        if prod_sel != "Todos":
            tipo_item = "P" if prod_sel.startswith("Produto:") else "S"
            nome_item = prod_sel.split(": ", 1)[1]
            if tipo_item == "P":
                row_p = df_prod[(df_prod["tipo"] == "P") & (df_prod["nome"] == nome_item)]
                if not row_p.empty:
                    pid = int(row_p.iloc[0]["id"])
                    prod_join_filter = f"AND iv2.id_produto = {pid}"
            else:
                row_s = df_prod[(df_prod["tipo"] == "S") & (df_prod["nome"] == nome_item)]
                if not row_s.empty:
                    sid = int(row_s.iloc[0]["id"])
                    prod_join_filter = f"AND iv2.id_servico = {sid}"

            # Adiciona subquery para filtrar apenas vendas que contém esse item
            where_clauses.append(f"""v.id_venda IN (
                SELECT iv2.id_venda FROM itens_venda iv2
                WHERE 1=1 {prod_join_filter}
            )""")

        where_sql = " AND ".join(where_clauses)

        # Query principal — detalhes de cada venda
        df_det = run_query(f"""
            SELECT
                v.id_venda AS `#Venda`,
                DATE_FORMAT(v.data_venda, '%d/%m/%Y %H:%i') AS `Data`,
                COALESCE(c.nome, 'Sem cadastro') AS `Cliente`,
                c.tipo_cliente AS `Tipo`,
                f.nome AS `Vendedor`,
                v.canal AS `Canal`,
                v.metodo_pagamento AS `Pagamento`,
                CASE WHEN v.entrega='S' THEN '🚚 Entrega' ELSE '🏪 Balcão' END AS `Modalidade`,
                COUNT(iv.id_item) AS `Itens`,
                SUM(iv.quantidade * iv.valor_unitario) AS `Total (R$)`
            FROM vendas v
            LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
            LEFT JOIN funcionarios f ON v.id_funcionario = f.id_funcionario
            JOIN itens_venda iv ON v.id_venda = iv.id_venda
            WHERE {where_sql}
            GROUP BY v.id_venda
            ORDER BY v.data_venda DESC
        """)

        # Query de itens detalhados para a mesma seleção
        df_itens = run_query(f"""
            SELECT
                v.id_venda AS `#Venda`,
                DATE_FORMAT(v.data_venda, '%d/%m/%Y') AS `Data`,
                COALESCE(c.nome, 'Sem cadastro') AS `Cliente`,
                f.nome AS `Vendedor`,
                COALESCE(p.nome_produto, s.nome_servico) AS `Item`,
                CASE WHEN iv.id_produto IS NOT NULL THEN 'Produto' ELSE 'Serviço' END AS `Tipo`,
                iv.quantidade AS `Qtd`,
                iv.valor_unitario AS `Preço Unit. (R$)`,
                (iv.quantidade * iv.valor_unitario) AS `Subtotal (R$)`
            FROM vendas v
            LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
            LEFT JOIN funcionarios f ON v.id_funcionario = f.id_funcionario
            JOIN itens_venda iv ON v.id_venda = iv.id_venda
            LEFT JOIN produtos p ON iv.id_produto = p.id_produto
            LEFT JOIN servicos s ON iv.id_servico = s.id_servico
            WHERE {where_sql}
            ORDER BY v.data_venda DESC, v.id_venda, iv.id_item
        """)

        # ── KPIs do filtro ────────────────────────────────────────────────────
        if not df_det.empty:
            total_fat = df_det["Total (R$)"].sum()
            total_vendas_n = len(df_det)
            ticket_medio = total_fat / total_vendas_n if total_vendas_n else 0
            total_itens = df_det["Itens"].sum()

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f"""<div class="kpi-card blue">
                <p class="kpi-value blue">R$ {total_fat:,.2f}</p>
                <p class="kpi-label">💰 Faturamento</p></div>""", unsafe_allow_html=True)
            k2.markdown(f"""<div class="kpi-card green">
                <p class="kpi-value green">{total_vendas_n}</p>
                <p class="kpi-label">🛒 Vendas</p></div>""", unsafe_allow_html=True)
            k3.markdown(f"""<div class="kpi-card amber">
                <p class="kpi-value amber">R$ {ticket_medio:,.2f}</p>
                <p class="kpi-label">🎯 Ticket Médio</p></div>""", unsafe_allow_html=True)
            k4.markdown(f"""<div class="kpi-card purple">
                <p class="kpi-value purple">{int(total_itens)}</p>
                <p class="kpi-label">📦 Itens Vendidos</p></div>""", unsafe_allow_html=True)

            st.markdown("---")

            # ── Gráficos de apoio ──────────────────────────────────────────────
            gc1, gc2 = st.columns(2)

            with gc1:
                # Faturamento por vendedor
                df_por_vend = (
                    df_det.groupby("Vendedor", dropna=False)["Total (R$)"]
                    .sum().reset_index().sort_values("Total (R$)", ascending=False)
                )
                fig_v = px.bar(df_por_vend, x="Vendedor", y="Total (R$)",
                               title="💰 Faturamento por Vendedor",
                               color_discrete_sequence=["#7c3aed"],
                               text_auto=".2s")
                fig_v.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300,
                                    margin=dict(t=40,b=20,l=10,r=10))
                st.plotly_chart(fig_v, use_container_width=True)

            with gc2:
                # Faturamento por cliente (top 8)
                df_por_cli2 = (
                    df_det.groupby("Cliente", dropna=False)["Total (R$)"]
                    .sum().reset_index().sort_values("Total (R$)", ascending=False).head(8)
                )
                fig_c = px.bar(df_por_cli2, x="Total (R$)", y="Cliente",
                               title="👤 Top Clientes (faturamento)",
                               orientation="h", color_discrete_sequence=["#d97706"],
                               text_auto=".2s")
                fig_c.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300,
                                    margin=dict(t=40,b=20,l=10,r=10))
                st.plotly_chart(fig_c, use_container_width=True)

            gc3, gc4 = st.columns(2)

            with gc3:
                # Ranking de itens no período/filtro
                df_rank_item = (
                    df_itens.groupby(["Item","Tipo"])["Subtotal (R$)"]
                    .sum().reset_index().sort_values("Subtotal (R$)", ascending=False).head(10)
                )
                fig_i = px.bar(df_rank_item, x="Subtotal (R$)", y="Item",
                               orientation="h", color="Tipo",
                               title="🏆 Itens Mais Vendidos (R$)",
                               color_discrete_map={"Produto":"#2563eb","Serviço":"#16a34a"})
                fig_i.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320,
                                    margin=dict(t=40,b=20,l=10,r=10))
                st.plotly_chart(fig_i, use_container_width=True)

            with gc4:
                # Evolução faturamento por dia
                df_evo = run_query(f"""
                    SELECT DATE(v.data_venda) as dia,
                           SUM(iv.quantidade*iv.valor_unitario) as faturamento
                    FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
                    WHERE {where_sql}
                    GROUP BY dia ORDER BY dia
                """)
                if not df_evo.empty:
                    fig_evo = px.line(df_evo, x="dia", y="faturamento",
                                     title="📈 Evolução Diária (R$)",
                                     markers=True, color_discrete_sequence=["#0891b2"])
                    fig_evo.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320,
                                          margin=dict(t=40,b=20,l=10,r=10))
                    st.plotly_chart(fig_evo, use_container_width=True)

            st.markdown("---")

            # ── Tabelas ────────────────────────────────────────────────────────
            tab_res, tab_det = st.tabs(["📋 Resumo por Venda", "🔎 Itens Detalhados"])

            with tab_res:
                st.markdown(f"**{total_vendas_n} vendas encontradas** — Total: R$ **{total_fat:,.2f}**")
                st.dataframe(df_det, use_container_width=True, hide_index=True)

            with tab_det:
                st.markdown(f"**{len(df_itens)} linhas de item**")
                st.dataframe(df_itens, use_container_width=True, hide_index=True)

            # ── Exportar CSV ───────────────────────────────────────────────────
            st.markdown("---")
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv_res = df_det.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar Resumo (CSV)", csv_res,
                                   file_name=f"relatorio_vendas_{dt_ini}_{dt_fim}.csv",
                                   mime="text/csv")
            with col_exp2:
                csv_det = df_itens.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar Itens Detalhados (CSV)", csv_det,
                                   file_name=f"relatorio_itens_{dt_ini}_{dt_fim}.csv",
                                   mime="text/csv")
        else:
            st.info("Nenhuma venda encontrada com os filtros selecionados.")

    # ══════════════════════════════════════════════════════════════════════════
    # Relatórios originais — mantidos integralmente
    # ══════════════════════════════════════════════════════════════════════════
    elif tipo_rel == "Vendas por Período":
        agrupar = st.selectbox("Agrupar por", ["Dia", "Semana", "Mês"])
        fmt = {"Dia": "%Y-%m-%d", "Semana": "%x W%v", "Mês": "%Y-%m"}[agrupar]
        df = run_query(f"""
            SELECT DATE_FORMAT(v.data_venda,'{fmt}') as periodo,
                   COUNT(DISTINCT v.id_venda) as qtd_vendas,
                   SUM(iv.quantidade*iv.valor_unitario) as faturamento
            FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE {filtro_periodo}
            GROUP BY periodo ORDER BY periodo
        """)
        if not df.empty:
            fig = px.bar(df, x="periodo", y="faturamento", title=f"Faturamento por {agrupar}",
                         text_auto=".2s", color_discrete_sequence=["#2563eb"])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.line(df, x="periodo", y="qtd_vendas", title=f"Quantidade de Vendas por {agrupar}",
                           markers=True, color_discrete_sequence=["#16a34a"])
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Vendas por Canal":
        df = run_query(f"""
            SELECT v.canal, COUNT(DISTINCT v.id_venda) as qtd,
                   SUM(iv.quantidade*iv.valor_unitario) as faturamento
            FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE {filtro_periodo} AND v.canal IS NOT NULL
            GROUP BY v.canal
        """)
        if not df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.pie(df, names="canal", values="faturamento", title="Faturamento por Canal",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig2 = px.bar(df, x="canal", y="qtd", title="Quantidade por Canal",
                              color_discrete_sequence=["#7c3aed"])
                fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Vendas por Pagamento":
        df = run_query(f"""
            SELECT v.metodo_pagamento as pagamento, COUNT(DISTINCT v.id_venda) as qtd,
                   SUM(iv.quantidade*iv.valor_unitario) as faturamento
            FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE {filtro_periodo} AND v.metodo_pagamento IS NOT NULL
            GROUP BY v.metodo_pagamento
        """)
        if not df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.pie(df, names="pagamento", values="faturamento",
                             title="Faturamento por Pagamento",
                             color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig2 = px.bar(df, x="pagamento", y="qtd", title="Qtd Vendas por Pagamento",
                              color="pagamento", color_discrete_sequence=px.colors.qualitative.Set2)
                fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Ranking de Produtos":
        df = run_query(f"""
            SELECT COALESCE(p.nome_produto, s.nome_servico) as item,
                   CASE WHEN iv.id_produto IS NOT NULL THEN 'Produto' ELSE 'Serviço' END as tipo,
                   SUM(iv.quantidade) as qtd_vendida,
                   SUM(iv.quantidade*iv.valor_unitario) as faturamento
            FROM itens_venda iv
            LEFT JOIN produtos p ON iv.id_produto=p.id_produto
            LEFT JOIN servicos s ON iv.id_servico=s.id_servico
            JOIN vendas v ON iv.id_venda=v.id_venda
            WHERE {filtro_periodo}
            GROUP BY item, tipo ORDER BY faturamento DESC LIMIT 15
        """)
        if not df.empty:
            fig = px.bar(df, x="faturamento", y="item", orientation="h", color="tipo",
                         title="Top Itens por Faturamento",
                         color_discrete_map={"Produto":"#2563eb","Serviço":"#16a34a"})
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Clientes Mais Ativos":
        df = run_query(f"""
            SELECT COALESCE(c.nome, 'Sem cadastro') as cliente,
                   COUNT(DISTINCT v.id_venda) as compras,
                   SUM(iv.quantidade*iv.valor_unitario) as total_gasto
            FROM vendas v
            LEFT JOIN clientes c ON v.id_cliente=c.id_cliente
            JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE {filtro_periodo}
            GROUP BY cliente ORDER BY total_gasto DESC LIMIT 15
        """)
        if not df.empty:
            fig = px.bar(df, x="total_gasto", y="cliente", orientation="h",
                         title="Clientes por Total Gasto", color_discrete_sequence=["#d97706"])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Margem de Lucro":
        df = run_query(f"""
            SELECT p.nome_produto as produto,
                   SUM(iv.quantidade) as vendidos,
                   p.preco_custo,
                   AVG(iv.valor_unitario) as preco_medio_venda,
                   SUM(iv.quantidade*(iv.valor_unitario - p.preco_custo)) as lucro_total
            FROM itens_venda iv
            JOIN produtos p ON iv.id_produto=p.id_produto
            JOIN vendas v ON iv.id_venda=v.id_venda
            WHERE {filtro_periodo}
            GROUP BY p.id_produto ORDER BY lucro_total DESC
        """)
        if not df.empty:
            df["margem_%"] = ((df["preco_medio_venda"] - df["preco_custo"]) / df["preco_custo"] * 100).round(1)
            fig = px.bar(df, x="produto", y="margem_%", title="Margem de Lucro por Produto (%)",
                         color="margem_%", color_continuous_scale="RdYlGn")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.bar(df, x="produto", y="lucro_total", title="Lucro Total por Produto (R$)",
                          color_discrete_sequence=["#16a34a"])
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif tipo_rel == "Entrega vs Balcão":
        df = run_query(f"""
            SELECT CASE WHEN v.entrega='S' THEN 'Entrega' ELSE 'Balcão/Local' END as tipo,
                   COUNT(DISTINCT v.id_venda) as qtd,
                   SUM(iv.quantidade*iv.valor_unitario) as faturamento
            FROM vendas v JOIN itens_venda iv ON v.id_venda=iv.id_venda
            WHERE {filtro_periodo}
            GROUP BY tipo
        """)
        if not df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.pie(df, names="tipo", values="qtd", title="Qtd Vendas por Modalidade",
                             color_discrete_sequence=["#2563eb","#16a34a"])
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig2 = px.pie(df, names="tipo", values="faturamento", title="Faturamento por Modalidade",
                              color_discrete_sequence=["#2563eb","#16a34a"])
                st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

# ─── Router ───────────────────────────────────────────────────────────────────
def main():
    if "user" not in st.session_state:
        login()
        return

    if "page" not in st.session_state:
        st.session_state.page = "🏠 Dashboard"

    sidebar()

    page = st.session_state.page
    if page == "🏠 Dashboard":
        dashboard()
    elif page == "🛒 Nova Venda":
        nova_venda()
    elif page == "📋 Vendas":
        vendas()
    elif page == "👥 Clientes":
        clientes()
    elif page == "📦 Produtos":
        produtos()
    elif page == "🔧 Serviços":
        servicos()
    elif page == "🚚 Fornecedores":
        fornecedores()
    elif page == "📊 Relatórios":
        relatorios()
    elif page == "👷 Funcionários":
        if st.session_state.user["nivel_acesso"] == "Admin":
            funcionarios()
        else:
            st.warning("Acesso restrito.")

if __name__ == "__main__":
    main()
