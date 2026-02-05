# ==============================================================================
# 1. IMPORTAÇÃO E CONFIGURAÇÃO (Mantida)
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import time 
import requests 
from streamlit_lottie import st_lottie 
from streamlit_option_menu import option_menu

import assistente_ia
import hub_conteudo
import nutri_vision 

st.set_page_config(page_title="Health Tracker | DPJ", page_icon="🩺", layout="wide")

# ==============================================================================
# 2. CSS CUSTOMIZADO (O "PULO DO GATO" PARA O DESIGN MODERNO)
# ==============================================================================
st.markdown("""
<style>
    /* Fundo da página e fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }

    /* Estilização da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Cards de Métricas Customizados */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #F1F5F9;
        flex: 1;
        text-align: left;
    }

    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .metric-value {
        color: #1E293B;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 5px;
    }

    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 5px;
    }
    
    .delta-positive { color: #10B981; } /* Verde para progresso bom */
    .delta-negative { color: #EF4444; } /* Vermelho para alerta */

    /* Botões Modernos */
    div.stButton > button {
        border-radius: 10px;
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #e63939;
        box-shadow: 0 10px 15px -3px rgba(255, 75, 75, 0.3);
    }
    
    /* Estilo para o Pódio de Ranking */
    .ranking-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid #F1F5F9;
    }
    .first-place { border-color: #FFD700; background: linear-gradient(180deg, #FFFDF0 0%, #FFFFFF 100%); }
    .second-place { border-color: #C0C0C0; }
    .third-place { border-color: #CD7F32; }

    .medal { font-size: 2.5rem; display: block; margin-bottom: 10px; }
    .ranking-name { font-weight: 700; color: #1E293B; font-size: 1.2rem; }
    .ranking-value { color: #3B82F6; font-weight: 800; font-size: 1.5rem; }
    
    /* Estilização avançada do Toggle Switch (Estilo ON/OFF) */
    div[data-testid="stCheckbox"] {
        background-color: #F1F5F9;
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid #E2E8F0;
        width: fit-content;
    }
    
    /* Quando está LIGADO (ON) - Gradiente Azul/Ciano */
    div[data-testid="stCheckbox"] label[data-checked="true"] div[role="checkbox"] {
        background: linear-gradient(90deg, #00B4DB 0%, #0083B0 100%) !important;
        border: none !important;
    }
    
    /* Quando está DESLIGADO (OFF) - Gradiente Vermelho/Rosa */
    div[data-testid="stCheckbox"] label[data-checked="false"] div[role="checkbox"] {
        background: linear-gradient(90deg, #FF512F 0%, #DD2476) !important;
        border: none !important;
    }
    
    /* Deixa a "bolinha" do switch branca e bonita */
    div[role="checkbox"] > div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)



# ==============================================================================
# 3. FUNÇÕES DE SUPORTE (DADOS E ANIMAÇÃO)
# ==============================================================================
DATA_FILE = "Série histórica das medições - Grupo DPJ.xlsx"

def load_data():
    if not os.path.exists(DATA_FILE): return pd.DataFrame()
    try: return pd.read_excel(DATA_FILE, engine='openpyxl')
    except: return pd.DataFrame()

def save_data(df):
    try:
        df.to_excel(DATA_FILE, index=False, engine='openpyxl')
        return True
    except PermissionError:
        st.error("⚠️ O arquivo Excel está ABERTO! Feche-o para salvar.")
        return False



def render_modern_metric(label, value, delta_val, suffix="", is_good_up=True, sftg="",target=""):
    # Lógica de cor para o delta (Evolução Total)
    if delta_val > 0:
        status = "positive" if is_good_up else "negative"
        icon = "▲"
    elif delta_val < 0:
        status = "positive" if not is_good_up else "negative"
        icon = "▼"
    else:
        status = "neutral"
        icon = "●"
    
    # Construção da String de Meta
    target_html = ""
    if target is not None:
        target_html = f'<span style="color: #94A3B8; font-size: 1rem; font-weight: 500; margin-left: 8px; position:relative">/ {target}{sftg}</span>'

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div style="display: flex; align-items: baseline;">
                <span class="metric-value">{value}</span>
                {target_html}
            </div>
            <div class="delta-badge {status}">{icon} {abs(delta_val):.1f}{suffix} total</div>
        </div>
    """, unsafe_allow_html=True)
    

df = load_data()
if 'Data' in df.columns: df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# ==============================================================================
# 4. SISTEMA DE LOGIN (COM POPUP)
# ==============================================================================
USUARIOS = {"admin": "123456", "personal": "treino2026"}

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""
# Variável para controlar a animação de transição
if 'menu_anterior' not in st.session_state: st.session_state['menu_anterior'] = "Individual"

@st.dialog("Acesso Restrito 🔒")
def login_dialog():
    st.write("Insira suas credenciais.")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if username in USUARIOS and USUARIOS[username] == password:
            st.session_state['logado'] = True
            st.session_state['usuario_atual'] = username
            st.rerun()
        else:
            st.error("Dados incorretos.")

def logout():
    st.session_state['logado'] = False
    st.session_state['usuario_atual'] = ""
    st.rerun()

# ==============================================================================
# 5. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=80)
    st.markdown("### Painel Saúde DPJ")
    st.markdown("---")
    
    if not st.session_state['logado']:
        if st.button("🔐 Área Restrita"): login_dialog()
    else:
        st.success(f"Olá, {st.session_state['usuario_atual'].capitalize()}!")
        if st.button("Sair"): logout()
    
    st.markdown("---")
    
    if not df.empty and 'Pessoa' in df.columns:
        pessoas = df['Pessoa'].unique()
        selected_person = st.selectbox("Visualizar Membro:", pessoas)
    else:
        selected_person = "Ninguém"

# ==============================================================================
# 6. MENU E ANIMAÇÃO DE TRANSIÇÃO
# ==============================================================================

if st.session_state['logado']:
    opcoes = ["Individual", "Ranking", "Dicas", "Assistente IA", "Nutri-Vision"]
    icones = ["person-circle", "trophy-fill", "lightbulb", "robot", "camera-fill"]
else:
    opcoes = ["Individual", "Ranking"]
    icones = ["person-circle", "trophy-fill"]

selected = option_menu(
    menu_title=None,
    options=opcoes, 
    icons=icones, 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f8f9fa"},
        "icon": {"color": "#ffa500", "font-size": "18px"}, 
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#ff4b4b"},
    }
)


    
# ==============================================================================
# 7. LÓGICA DAS TELAS
# ==============================================================================

# Prepara dados
df_person = df[df['Pessoa'] == selected_person].sort_values(by="Data") if not df.empty else pd.DataFrame()
ultimo_registro = {}
if not df_person.empty: ultimo_registro = df_person.iloc[-1].to_dict()

# --- TELA 1: INDIVIDUAL ---
if selected == "Individual":
    st.markdown(f"<h2 style='margin-bottom: 25px;'>📊 Dashboard: {selected_person}</h2>", unsafe_allow_html=True)
    
    # SÓ MOSTRA O FORMULÁRIO SE ESTIVER LOGADO
    if st.session_state['logado']:
        with st.expander("📝 Nova Medição (Acesso Restrito)", expanded=False):
            with st.form("entry_form"):
                date_input = st.date_input("Data", datetime.today())
                col_f1, col_f2 = st.columns(2)
                
                def get_v(k, d): return float(ultimo_registro[k]) if k in ultimo_registro else d
                
                with col_f1:
                    peso = st.number_input("Peso (kg)", value=get_v('Peso', 70.0))
                    gordura = st.number_input("% Gordura", value=get_v('Perc_Gordura', 20.0))
                    visc = st.number_input("Visceral", value=get_v('Visceral', 5.0))
                    imc_val = st.number_input("IMC", value=get_v('IMC', 24.0))
                with col_f2:
                    musc = st.number_input("% Músculo", value=get_v('Perc_Musc', 30.0))
                    rm = st.number_input("Taxa Metabólica", value=int(get_v('RM', 1500)))
                    idade = st.number_input("Idade", value=int(get_v('Idade', 30)))
                
                if st.form_submit_button("💾 Salvar Dados", use_container_width=True):
                    new_data = {
                        "Pessoa": selected_person, "Data": pd.to_datetime(date_input),
                        "Peso": peso, "IMC": imc_val, "Perc_Gordura": gordura, 
                        "Perc_Musc": musc, "RM": rm, "Idade": idade, "Visceral": visc
                    }
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    if save_data(df): st.success("Salvo! Recarregue a página.")
    else:
        st.info("Faça login na barra lateral para cadastrar novas medições.",icon="🔐")

    if not df_person.empty:
        curr = df_person.iloc[-1]
        first = df_person.iloc[0]   if len(df_person) > 1 else curr
        
        # Grid de Métricas Premium
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:  
    # Aqui definimos a meta, por exemplo, 70.0kg
            meta_peso = 70.0 
            render_modern_metric(
            label="Peso", 
            value=f"{curr['Peso']}kg", 
            delta_val=curr['Peso'] - first['Peso'], 
            suffix="kg", 
            is_good_up=False,
            target=meta_peso,
            sftg="kg")
        with m2: render_modern_metric("% Gordura", f"{curr['Perc_Gordura']}%", round(curr['Perc_Gordura']-first['Perc_Gordura'],2), "%", False,sftg="")
        with m3: render_modern_metric("% Músculo", f"{curr['Perc_Musc']}%", round(curr['Perc_Musc']-first['Perc_Musc'],2), "%", True,sftg="")
        with m4: render_modern_metric("Visceral", f"{(curr['Visceral'])}", round(curr['Visceral']-first['Visceral'],2), "", False,sftg="")
        with m5: render_modern_metric("Idade Corp", f"{(curr['Idade'])}", round(curr['Idade']-first['Idade'],2), "a", False,sftg="")
        st.info(f"💡 Os indicadores acima mostram sua evolução total desde a primeira medição em **{first['Data'].strftime('%d/%m/%Y')}**.")
        st.divider()

        # Gráficos de Alta Performance
        g1, g2 = st.columns(2)
        
        with g1:
            fig_peso = go.Figure()
            fig_peso.add_trace(go.Scatter(x=df_person["Data"], y=df_person["Peso"], mode='lines+markers',
                                         line=dict(color='#3B82F6', width=4, shape='spline'),
                                         fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'))
            fig_peso.update_layout(title="Tendência de Peso", plot_bgcolor='white', margin=dict(t=40, b=0))
            st.plotly_chart(fig_peso, use_container_width=True)

        with g2:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(x=df_person["Data"], y=df_person["Perc_Gordura"], name="% Gordura", 
                                         line=dict(color='#EF4444', width=3, shape='spline')))
            fig_comp.add_trace(go.Scatter(x=df_person["Data"], y=df_person["Perc_Musc"], name="% Músculo", 
                                         line=dict(color='#10B981', width=3, shape='spline')))
            fig_comp.update_layout(title="Composição Corporal", plot_bgcolor='white', margin=dict(t=40, b=0))
            st.plotly_chart(fig_comp, use_container_width=True)

        # Indicadores Metabólicos (Gauge IMC)
        st.markdown("### 📌 Fisiologia")
        c_imc, c_rm = st.columns([1, 2])
        
        with c_imc:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=curr['IMC'],
                gauge={'axis': {'range': [15, 40]}, 'bar': {'color': "#1E293B"},
                       'steps': [{'range': [0, 25], 'color': "#D1FAE5"}, {'range': [25, 30], 'color': "#FEF3C7"}, {'range': [30, 40], 'color': "#FEE2E2"}]}))
            fig_gauge.update_layout(height=600, title="IMC")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with c_rm:
            fig_rm = px.bar(df_person.tail(8), x="Data", y="RM", title="Taxa Metabólica (kcal)", color_discrete_sequence=['#8B5CF6'])
            fig_rm.update_layout(plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rm, use_container_width=True)
# --- TELA 2: RANKING ---

elif selected == "Ranking":
    st.markdown("# 🏆 Leaderboard do Grupo")
    
    if not df.empty:
        # Centralizando o botão Toggle ON/OFF
        _, col_toggle, _ = st.columns([1, 1, 1])
        with col_toggle:
            modo_30_dias = st.toggle("Modo: Últimos 30 Dias", value=False)
            periodo_texto = "Últimos 30 Dias" if modo_30_dias else "Todo o Período"

        st.divider()

        # Lógica de Filtro Corrigida
        def filtrar_por_periodo(group, trinta_dias):
            group = group.sort_values('Data')
            ultimo = group.iloc[-1]
            if trinta_dias:
                data_corte = ultimo['Data'] - pd.Timedelta(days=30)
                # Garante que pega a medição mais antiga dentro do período de 30 dias
                dados_recentes = group[group['Data'] >= data_corte]
                primeiro = dados_recentes.iloc[0] if not dados_recentes.empty else group.iloc[0]
            else:
                primeiro = group.iloc[0]
            
            return pd.Series({
                'Ganho_Musculo': ultimo['Perc_Musc'] - primeiro['Perc_Musc'],
                'Perda_Gordura': primeiro['Perc_Gordura'] - ultimo['Perc_Gordura'],
                'Peso_Atual': ultimo['Peso'],
                'Data_Referencia': primeiro['Data'] # Guardamos para o caption
            })

        ranking_df = df.sort_values('Data').groupby('Pessoa').apply(
            filtrar_por_periodo, trinta_dias=modo_30_dias
        ).reset_index()

        # Legenda informativa
        data_min = ranking_df['Data_Referencia'].min().strftime('%d/%m/%Y')
        st.caption(f"📊 Comparando dados atuais com a base de: **{data_min}**")

        # --- PÓDIO ---
        st.subheader(f"🔥 Top Evolução: Massa Magra ({periodo_texto})")
        top_musculo = ranking_df.sort_values("Ganho_Musculo", ascending=False).head(3)
        cols = st.columns(3)
        medalhas = ["🥇", "🥈", "🥉"]
        classes = ["first-place", "second-place", "third-place"] # Classes CSS que definimos antes

        for i, (idx, row) in enumerate(top_musculo.iterrows()):
            with cols[i]:
                # Card de pódio com cores de metal
                st.markdown(f"""
                    <div class="ranking-card {classes[i] if i < len(classes) else ''}">
                        <span class="medal">{medalhas[i]}</span>
                        <div class="ranking-name">{row['Pessoa']}</div>
                        <div class="ranking-value">+{max(0, row['Ganho_Musculo']):.1f}%</div>
                        <div style="color: #64748B; font-size: 0.8rem;">músculo no período</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- TABELAS E MAPA ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"### 💧 Foco: Gordura ({periodo_texto})")
            gord_df = ranking_df.sort_values("Perda_Gordura", ascending=False)[['Pessoa', 'Perda_Gordura']]
            st.dataframe(gord_df.rename(columns={'Perda_Gordura': 'Eliminado (%)'}), hide_index=True, use_container_width=True)

        with col_g2:
            st.markdown("### ⚖️ Peso Atual")
            st.dataframe(ranking_df.sort_values("Peso_Atual")[['Pessoa', 'Peso_Atual']], hide_index=True, use_container_width=True)

        st.divider()
        st.markdown(f"### 🗺️ Mapa de Resultados ({periodo_texto})")
        fig_mapa = px.scatter(ranking_df, x="Ganho_Musculo", y="Perda_Gordura", text="Pessoa", 
                              size="Peso_Atual", color="Pessoa", template="plotly_white")
        fig_mapa.update_layout(margin=dict(t=0, b=0))
        st.plotly_chart(fig_mapa, use_container_width=True)

# --- TELAS RESTRITAS ---
elif selected == "Dicas" and st.session_state['logado']:
    hub_conteudo.exibir_hub()

elif selected == "Assistente IA" and st.session_state['logado']:
    if not df_person.empty: assistente_ia.exibir_assistente(ultimo_registro)
    else: st.warning("Selecione alguém com dados primeiro.")

elif selected == "Nutri-Vision" and st.session_state['logado']:
    if not df_person.empty: nutri_vision.exibir_nutri_vision(ultimo_registro)

    else: st.warning("Selecione alguém com dados primeiro.")

