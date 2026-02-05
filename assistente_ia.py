import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DA CHAVE E CONEXÃO
# ==============================================================================
def configurar_ia():
    # --- SUA CHAVE ESTÁ AQUI ---
    MINHA_CHAVE = "AIzaSyDWwJ9L6L2i6AjZup-Gn1Dv7XUiNk_-eGY" 
    # -------------------------
    
    # Removido o bloco "if" que estava atrapalhando.
    # Agora ele tenta conectar direto.

    try:
        genai.configure(api_key=MINHA_CHAVE)
        return True
    except Exception as e:
        st.error(f"Erro ao conectar no Google: {e}")
        return False

# ==============================================================================
# 2. FUNÇÃO QUE CRIA O PDF
# ==============================================================================
def gerar_pdf(texto_treino, nome_aluno):
    """Gera um PDF simples com o conteúdo da IA"""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho do PDF
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt=f"Plano Personalizado - {nome_aluno}", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, txt="Gerado por IA - Painel Grupo DPJ", ln=True, align='C')
    pdf.ln(10) # Pula uma linha
    
    # Corpo do texto
    pdf.set_font("Arial", size=12)
    
    # Tratamento de caracteres especiais (acentos) para não travar o PDF
    # O FPDF básico não aceita emojis, então eles podem sumir ou virar '?'
    texto_formatado = texto_treino.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 10, txt=texto_formatado)
    
    # Retorna o arquivo pronto para download
    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# 3. TELA PRINCIPAL DO CHAT
# ==============================================================================
def exibir_assistente(dados_aluno):
    # --- Cabeçalho ---
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🤖 Personal AI")
    with col2:
        if st.button("Limpar Chat"):
            st.session_state.messages = []
            if "ultimo_treino" in st.session_state:
                del st.session_state["ultimo_treino"]
            st.rerun()

    # Tenta conectar. Se falhar, para por aqui.
    if not configurar_ia():
        return

    # --- Mostra o Histórico de Mensagens ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Botão de Download (Aparece se houver um treino salvo) ---
    if "ultimo_treino" in st.session_state:
        st.markdown("---")
        st.info("💡 Um novo plano foi gerado. Baixe para levar com você!")
        
        pdf_bytes = gerar_pdf(st.session_state["ultimo_treino"], dados_aluno.get('Pessoa', 'Aluno'))
        
        st.download_button(
            label="📄 Baixar PDF do Treino/Dieta",
            data=pdf_bytes,
            file_name="plano_personalizado_dpj.pdf",
            mime="application/pdf",
            type="primary"
        )

    # --- Área de Digitação ---
    if prompt := st.chat_input("Ex: Monte um treino de pernas avançado..."):
        # 1. Mostra a pergunta do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Contexto para a IA
        contexto = f"""
        Você é o Personal Trainer oficial do Grupo DPJ.
        Aluno: {dados_aluno.get('Pessoa')}.
        Métricas Atuais: Peso {dados_aluno.get('Peso')}kg, IMC {dados_aluno.get('IMC')}, Gordura {dados_aluno.get('Perc_Gordura')}%.
        
        INSTRUÇÃO: Responda de forma completa. Use listas e tópicos.
        Evite usar muitos emojis no meio das palavras para facilitar a leitura no PDF.
        """

        # 3. Gera a resposta
        with st.chat_message("assistant"):
            try:
                # Usando o modelo Flash (rápido e barato)
                # Se der erro 404, mude para 'gemini-1.5-pro'
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content(
                    [contexto, prompt],
                    stream=True # Efeito de digitação
                )
                
                placeholder = st.empty()
                full_response = ""
                
                # Renderiza palavra por palavra
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                
                # Salva no histórico
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # --- Lógica do Filtro Inteligente ---
                # Só mostra o botão de download se tiver essas palavras:
                palavras_chave = ["treino", "série", "repetições", "descanso", "dieta", "calorias", "café", "almoço", "jantar", "exercício", "supino", "agachamento"]
                
                eh_conteudo_relevante = any(palavra in full_response.lower() for palavra in palavras_chave)

                if eh_conteudo_relevante:
                    # Salva o texto para o PDF e recarrega a página para mostrar o botão
                    st.session_state["ultimo_treino"] = full_response
                    st.rerun()
                else:
                    # Se for conversa fiada, remove o botão anterior (se existir)
                    if "ultimo_treino" in st.session_state:
                        del st.session_state["ultimo_treino"]
                        st.rerun()
            
            except Exception as e:
                st.error(f"Erro na IA: {e}")