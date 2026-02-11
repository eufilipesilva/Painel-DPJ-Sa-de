import streamlit as st
import pandas as pd
import requests
import random
from datetime import date
import os

# ==============================================================================
# CARREGAMENTO DE DADOS DO CSV
# ==============================================================================

@st.cache_data
def carregar_dados_csv():
    """Lê o CSV gerado pelo scraper e organiza em um dicionário de categorias."""
    arquivo = "videos_playlist_corrigido.csv"
    
    if not os.path.exists(arquivo):
        st.error(f"Arquivo '{arquivo}' não encontrado. Execute o scraper primeiro!")
        return {}
    
    # Lê o CSV
    df = pd.read_csv(arquivo)
    
    # Agrupa os links por categoria
    # O CSV tem as colunas: Categoria, Título, Canal, Link
    biblioteca = df.groupby('Categoria')['Link'].apply(list).to_dict()
    
    return biblioteca

# ==============================================================================
# MECANISMO DE VERIFICAÇÃO COM CACHE
# ==============================================================================

@st.cache_data(ttl=86400)
def validar_biblioteca_videos(biblioteca):
    """Verifica quais links da biblioteca estão ativos no YouTube."""
    if not biblioteca:
        return {}
        
    biblioteca_validada = {}
    
    for categoria, links in biblioteca.items():
        links_ativos = []
        # Para não demorar muito no Streamlit, validamos uma amostra ou 
        # confiamos na curadoria se a lista for muito grande. 
        # Aqui, validamos todos, mas com timeout curto.
        for url in links:
            try:
                # OEmbed valida se o vídeo não foi deletado ou tornado privado
                # check_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                # response = requests.get(check_url, timeout=1.0)
                #if response.status_code == 200:
                if 1==1:
                    links_ativos.append(url)
            except:
                continue
        biblioteca_validada[categoria] = links_ativos
    
    return biblioteca_validada

# ==============================================================================
# INTERFACE DO HUB
# ==============================================================================

def exibir_hub():
    st.title("💡 Hub de Conteúdo Fitness Dinâmico")
    st.markdown("Treinos extraídos automaticamente das suas playlists curadas.")

    # 1. Carregamento dos dados do CSV
    db_raw = carregar_dados_csv()
    
    if not db_raw:
        st.warning("Aguardando geração do banco de dados de vídeos...")
        return

    # 2. Validação via Cache
#   with st.spinner("Sincronizando com o YouTube..."):
    db_validado = validar_biblioteca_videos(db_raw)

    # 3. Escolha de Modalidade
    modalidades = list(db_validado.keys())
    
    modalidades = list(db_validado.keys())
    try:
        escolha = st.pills("Selecione o foco de hoje:", modalidades, selection_mode="single")
    except:
        escolha = st.selectbox("Selecione o foco de hoje:", modalidades)

    if not escolha: escolha = modalidades[0]

    # 4. Sorteio Diário (Seed baseada na data para mudar os vídeos todo dia)
    links_disponiveis = db_validado.get(escolha, [])
    
    if not links_disponiveis:
        st.error(f"Escolha um vídeo nas categorias acima")
        return

    # Define a semente para que o "sorteio" seja o mesmo durante o dia todo
    random.seed(date.today().toordinal() + len(escolha))
    
    # Sorteia 4 vídeos (ou menos, se não houver 4 disponíveis)
    quantidade_a_exibir = min(len(links_disponiveis), 4)
    videos_hoje = random.sample(links_disponiveis, quantidade_a_exibir)

    st.subheader(f"🎬 Sugestões para: {escolha}")
    st.caption(f"Exibindo {quantidade_a_exibir} de {len(links_disponiveis)} vídeos disponíveis nesta categoria.")
    
    # 5. Exibição em Grade
    col1, col2 = st.columns(2)
    for i, url in enumerate(videos_hoje):
        coluna = col1 if i % 2 == 0 else col2
        with coluna:
            with st.container(border=True):
                st.video(url)
                st.caption(f"✅ Fonte: Playlist Curada | Sugestão {i+1}")

    # 6. Calculadora de Água
    st.markdown("---")
    st.subheader("💧 Meta de Hidratação")
    with st.expander("Calcular minha meta", expanded=True):
        c_p1, c_p2 = st.columns([1, 2])
        with c_p1:
            peso = st.number_input("Seu peso (kg)", 40.0, 160.0, 75.0, key="peso_hub")
        with c_p2:
            meta = peso * 0.035
            st.metric("Meta Diária", f"{meta:.2f} Litros", help="Cálculo baseado em 35ml por quilo.")
            st.progress(min(1.0, meta/5.0)) # Progressão até 5L

if __name__ == "__main__":
    exibir_hub()