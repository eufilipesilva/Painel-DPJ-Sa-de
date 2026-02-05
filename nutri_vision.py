import streamlit as st
import google.generativeai as genai
import PIL.Image
import time

def configurar_ia():
    try:
        # Busca a chave no cofre de segredos do Streamlit
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error("❌ Erro: Chave API não configurada nos Secrets.")
        return False
        

def exibir_nutri_vision(dados_aluno):
    st.title("📸 Nutri-Vision - Analise o seu prato")
    st.markdown("Envie a foto e receba a análise nutricional ultra-rápida.")

    if not configurar_ia():
        st.stop()

    perfil_aluno = f"""
    Aluno: {dados_aluno.get('Pessoa')}.
    Peso: {dados_aluno.get('Peso')}kg.
    """

    with st.container(border=True):
        uploaded_file = st.file_uploader("Foto da refeição", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = PIL.Image.open(uploaded_file)
            st.image(image, caption='Sua refeição', width=350)
            
            obs = st.text_input("Observação (opcional)", key="obs_nutri_25")
            
            if st.button("🔍 Analisar Agora", type="primary"):
                
                prompt_sistema = f"""
                Atue como Nutricionista Esportivo.
                Analise a imagem.
                {perfil_aluno}
                Obs: {obs}
                
                1. Identifique os alimentos.
                2. Estime calorias e macros.
                3. Dê um veredito (Ótimo / Cuidado / Ruim).
                Use emojis e português do Brasil.
                """

                resposta_box = st.empty()
                full_text = ""

                with st.spinner('Processando imagem com Gemini 2.5...'):
                    try:
                        # --- ATUALIZAÇÃO DO MODELO AQUI ---
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        response = model.generate_content(
                            [prompt_sistema, image],
                            stream=True
                        )
                        
                        for chunk in response:
                            full_text += chunk.text
                            resposta_box.markdown(full_text + "▌")
                        
                        resposta_box.markdown(full_text)
                        st.success("Análise concluída!")

                    except Exception as e:

                        st.error(f"Erro na análise: {e}")


