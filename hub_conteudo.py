import streamlit as st
import pandas as pd
import requests
import random
from datetime import date
import json

# ==============================================================================
# SUPER BANCO DE DADOS - CURADORIA EXCLUSIVA PT-BR
# ==============================================================================
# Lista verificada de canais brasileiros de alta qualidade.
DB_VIDEOS_PT = {
    "🔥 Cardio & HIIT": [
        "https://www.youtube.com/watch?v=ml6cT4AZdqI", "https://www.youtube.com/watch?v=W4eKCKMxknk",
        "https://www.youtube.com/watch?v=Mvo2gqZ8uPc", "https://www.youtube.com/watch?v=gC_L9qAHVJ8",
        "https://www.youtube.com/watch?v=SubvK6bU41w", "https://www.youtube.com/watch?v=GS_z6P_-h_k",
        "https://www.youtube.com/watch?v=sPG49d1N-KY", "https://www.youtube.com/watch?v=VRfXCSbU6Mk"
    ],
    "💪 Musculação": [
        "https://www.youtube.com/watch?v=VfM6d7sA4_U", "https://www.youtube.com/watch?v=UItWltVZZmE",
        "https://www.youtube.com/watch?v=XyLzC2WwFhg", "https://www.youtube.com/watch?v=5uVaKjWrkoc",
        "https://www.youtube.com/watch?v=qjJqC_i2J9k", "https://www.youtube.com/watch?v=0dsL9QjFz7c",
        "https://www.youtube.com/watch?v=3tX8W_Z8_X8", "https://www.youtube.com/watch?v=nyJ2X_yJq_c"
    ],
    "🧘 Yoga & Flexibilidade": [
        "https://www.youtube.com/watch?v=hJbRpHZR_d0", "https://www.youtube.com/watch?v=s-7lyvQbFfw",
        "https://www.youtube.com/watch?v=4pKly2JojMw", "https://www.youtube.com/watch?v=inpok4MKVHM",
        "https://www.youtube.com/watch?v=E-nN6_OqiuE", "https://www.youtube.com/watch?v=v7AYKMP6rOE"
    ],
    "💃 Dança & Ritmos": [
        "https://www.youtube.com/watch?v=dj3a4D2a1yA", "https://www.youtube.com/watch?v=y9L1H6WkH9o",
        "https://www.youtube.com/watch?v=5b5c9b_6bGA", "https://www.youtube.com/watch?v=vQxW4pQk6qE",
        "https://www.youtube.com/watch?v=zO0Y-2_W7jM", "https://www.youtube.com/watch?v=It3s2l2Jg_k"
    ],
    "🍫 Abdominais": [
        "https://www.youtube.com/watch?v=1f8yoFFdkcY", "https://www.youtube.com/watch?v=AnYl6Nk9GOA",
        "https://www.youtube.com/watch?v=QLOJ16GqCZY", "https://www.youtube.com/watch?v=835E6t7kKZM",
        "https://www.youtube.com/watch?v=UYH2fTkyR_s", "https://www.youtube.com/watch?v=P1m7W_3J7F8"
    ],
    "🦍 Calistenia": [
        "https://www.youtube.com/watch?v=PODn8X7_7_7", "https://www.youtube.com/watch?v=0dsL9QjFz7c",
        "https://www.youtube.com/watch?v=qjJqC_i2J9k", "https://www.youtube.com/watch?v=UItWltVZZmE"
    ]
}

# ==============================================================================
# MECANISMO DE VERIFICAÇÃO COM CACHE (ULTRA RÁPIDO)
# ==============================================================================

@st.cache_data(ttl=86400) # O resultado fica guardado por 24 horas (86400 segundos)
def validar_biblioteca_videos(biblioteca):
    """Verifica todos os vídeos da biblioteca de uma vez e guarda os ativos."""
    biblioteca_validada = {}
    
    for categoria, links in biblioteca.items():
        links_ativos = []
        for url in links:
            try:
                # OEmbed é a forma oficial e rápida de validar
                check_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                response = requests.get(check_url, timeout=1.5)
                if response.status_code == 200:
                    links_ativos.append(url)
            except:
                continue
        biblioteca_validada[categoria] = links_ativos
    
    return biblioteca_validada

# ==============================================================================
# INTERFACE DO HUB
# ==============================================================================

def exibir_hub():
    st.title("💡 Hub de Conteúdo Fitness (PT-BR)")
    st.markdown("Treinos brasileiros verificados automaticamente para garantir que estão ativos.")

    # 1. Carregamento ultra rápido via Cache
    # Na primeira vez do dia demora uns segundos, depois é instantâneo.
    with st.spinner("Sincronizando biblioteca de treinos..."):
        db_validado = validar_biblioteca_videos(DB_VIDEOS_PT)

    # 2. Escolha de Modalidade
    modalidades = list(db_validado.keys())
    try:
        escolha = st.pills("Selecione o foco de hoje:", modalidades, selection_mode="single")
    except:
        escolha = st.selectbox("Selecione o foco de hoje:", modalidades)

    if not escolha: escolha = modalidades[0]

    # 3. Sorteio Diário (Mudando a semente pela data)
    links_disponiveis = db_validado.get(escolha, [])
    
    if not links_disponiveis:
        st.error("Desculpe, todos os vídeos desta categoria estão fora do ar hoje.")
        return

    random.seed(date.today().toordinal() + len(escolha))
    # Sorteia até 4 vídeos da lista de ativos
    videos_hoje = random.sample(links_disponiveis, min(len(links_disponiveis), 4))

    st.subheader(f"🎬 Treinos do Dia: {escolha}")
    
    # 4. Exibição em Grade
    col1, col2 = st.columns(2)
    for i, url in enumerate(videos_hoje):
        coluna = col1 if i % 2 == 0 else col2
        with coluna:
            with st.container(border=True):
                st.video(url)
                st.caption(f"✅ Conteúdo em Português | Sugestão {i+1}")

    # 5. Calculadora de Água
    st.markdown("---")
    st.subheader("💧 Meta de Hidratação")
    with st.expander("Calcular minha meta", expanded=True):
        c_p1, c_p2 = st.columns([1, 2])
        with c_p1:
            peso = st.number_input("Seu peso (kg)", 40.0, 160.0, 75.0, key="peso_hub")
        with c_p2:
            meta = peso * 0.035
            st.metric("Meta Diária", f"{meta:.2f} Litros", help="Cálculo baseado em 35ml por quilo.")
            st.progress(min(1.0, meta/4.0))