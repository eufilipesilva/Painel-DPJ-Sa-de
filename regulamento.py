import streamlit as st
import google.generativeai as genai
import PIL.Image
import time


def exibir_regulamento(dados_aluno):

    st.set_page_config(page_title="🗒️ Regulamento do Projeto:", layout="wide")


    # --- TEXTO FIEL AO ARQUIVO ---
    st.title("Modelo de Pontuação – Competição dos 100 Dias (Bioimpedância): ")

    st.header("🤓 Objetivo: ")
    st.write("Gerar um score final único por participante, considerando a evolução em: peso corporal, percentual de gordura, massa muscular e gordura visceral, aplicando pesos diferentes conforme a dificuldade fisiológica de cada indicador.")

    st.header("⚙️ Lógica do Modelo: ")
    st.markdown("""
    1) Calcular a evolução percentual de cada indicador em relação ao valor inicial. 
    2) Ajustar o sinal conforme a direção desejada (redução de gordura e peso; aumento de massa muscular).
    3) Aplicar pesos de dificuldade. 
    4) Somar para obter um score final. 
    """)

    st.header("⚙️ Fórmula de Evolução Normalizada: ")
    st.markdown("""
    Fórmula de Evolução Normalizada
    Evolução = (Valor Final - Valor Inicial) / Valor Inicial. 
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.header("⚙️ Direção do Ganho: ")
        st.markdown("""
                    
        * 🔽 **Peso:** redução é positiva (multiplicar por -1)
        * 🔽 **% Gordura:** redução é positiva (multiplicar por -1)
        * 🔽 **Gordura visceral:** redução é positiva (multiplicar por -1)
        * 🔼 **Massa muscular:** aumento é positivo (multiplicar por +1)
        """)

    with col2:
        st.header("⚖️ Pesos de Dificuldade:")
        #Configuração do CSS específico para a tabela de pesos
        st.markdown("""
        <style>
            .tabela-verde thead tr th {
                background-color: #4CAF50 !important;
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)
        #Renderização da tabela dentro da div identificada
        st.markdown('<div class="tabela-verde">', unsafe_allow_html=True)
        st.markdown("""
        | Indicador | Peso |
        | :--- | :--- |
        | Massa muscular | 0,40 |
        | % Gordura | 0,30 |
        | Gordura visceral | 0,20 |
        | Peso corporal | 0,10 |
        """) 
        st.markdown('</div>', unsafe_allow_html=True)

        # Fórmula Final do Score [cite: 17, 18]
    st.header("🧪 Fórmula Final do Score:")
    st.latex(r"Score = (\Delta Músculo\% \times 0,40) + (\Delta Gordura\% \times -0,30) + (\Delta Visceral\% \times -0,20) + (\Delta Peso\% \times -0,10)")
    st.latex(r"\Delta = \frac{Valor Final - Valor Inicial}{Valor Inicial}")

    # CSS para personalizar o st.expander
    st.markdown("""
    <style>
        /* 1. Cor de fundo e borda do cabeçalho do expander */
        div[data-testid="stExpander"] details summary {
            background-color: #ff4b4b !important; /* Cor vermelho */
            color: white !important;             /* Cor do Texto */
            border-radius: 8px;                  /* Arredondamento */
        }

        /* 2. Cor do ícone (setinha) do expander */
        div[data-testid="stExpander"] details summary svg {
            fill: white !important;
        }

        /* 3. Cor do texto dentro do cabeçalho (parágrafo) */
        div[data-testid="stExpander"] details summary p {
            color: white !important;
            font-weight: bold;
        }

        /* 4. Opcional: Cor da borda do conteúdo interno */
        div[data-testid="stExpander"] {
            border: 1px solid #ff4b4b !important;
            border-radius: 8px;
        }
                
        div[data-testid="stNotification"] {
            border: 1px solid #ff4b4b !important;
            border-radius: 8px;
        }         
    </style>
    """, unsafe_allow_html=True)
    with st.expander("Veja um exemplo prático do cálculo: "):
            st.markdown("""
            ### 📝 Exemplo de Cálculo: Participante Anônimo

            #### 1. Evolução Individual (Δ%)
            * **Massa Muscular:** De 30,% para 31,5% → **+5%** 
            * **% Gordura:** De 20% para 18% → **-10%** 
            * **Gordura Visceral:** De 10 para 9 → **-10%** 
            * **Peso Corporal:** De 80kg para 76kg → **-5%** 
            #### 2. Aplicação dos Pesos
            | Indicador | Evolução | Peso | Parcial |
            | :--- | :--- | :--- | :--- |
            | Músculo | +0,05 | 0,40 | 0,020 |
            | % Gordura | +0,10 | 0,30 | 0,030 |
            | G. Visceral | +0,10 | 0,20 | 0,020 |
            | Peso | +0,05 | 0,10 | 0,005 |

            **Score Final = 0,020 + 0,030 + 0,020 + 0,005 = 0,075 (ou 7,50 pontos)**
            """)



    st.divider()
    st.header("👨‍⚕️ Boas Práticas e Alertas: ")
    st.markdown("""
    * Medir em jejum e no mesmo horário.
    * Evitar treino nas 12h anteriores.
    * Evitar álcool nas 24h anteriores.
    """)
    st.error("""
    ☣️ A bioimpedância é sensível à hidratação, sono e ingestão de alimentos.
    """,)

   