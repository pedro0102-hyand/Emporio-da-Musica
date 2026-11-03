import os
import uuid
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.agent import build_agent

st.set_page_config(page_title="Empório da Música - Atendimento", page_icon="🎸", layout="wide",initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF5722;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 0.8rem;
    }
    .info-card {
        background-color: rgba(255, 87, 34, 0.05);
        border-left: 4px solid #FF5722;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.image("https://img.icons8.com/color/96/guitar.png", width=80)
    st.markdown("## 🎸 Empório da Música")
    st.markdown("*Sua música começa aqui.*")
    st.divider()

    st.markdown("### 📍 Informações da Loja")
    st.markdown("""
    **Endereço:**  
    Rua 14 de Maio, 3200 - Centro  
    Campo Grande - MS, 79202-333  

    **Horário de Atendimento:**  
    • Segunda a Sexta: 09h às 18h  
    • Sábado: 09h às 13h  
    • Domingo e Feriados: Fechado  

    **Contatos:**  
    📞 (67) 3341-4444  
    ✉️ contato@emporiodamusica.com.br
    """)
    
    st.divider()

    if st.button("🔄 Nova Conversa / Limpar Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Seja muito bem-vindo(a) à Empório da Música! 🎸\n\nSou o assistente virtual da loja e posso te ajudar a consultar nosso catálogo de instrumentos, acompanhar o status do seu pedido ou tirar dúvidas sobre nossas políticas de entrega e troca.\n\nComo posso te ajudar hoje?"}
    ]

@st.cache_resource
def load_agent():
    return build_agent()

try:
    agent = load_agent()
except Exception as e:
    st.error(f"⚠️ Erro ao inicializar o agente. Verifique se a variável `GROQ_API_KEY` está configurada no arquivo `.env`. Detalhes: {e}")
    st.stop()

st.markdown('<div class="main-header">🎸 Empório da Música</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Atendimento Virtual Inteligente — Campo Grande / MS</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-card">
    💡 <b>Exemplos de perguntas:</b> 
    <i>"Quais opções de violões custam até R$ 1000?"</i> | 
    <i>"Qual o status do pedido 1?"</i> | 
    <i>"Como funciona a política de devolução?"</i>
</div>
""", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem para a Empório da Música..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando sistemas da loja..."):
            try:
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                inputs = {"messages": [("user", prompt)]}
                response = agent.invoke(inputs, config=config)
                
                bot_response = response["messages"][-1].content
                st.markdown(bot_response)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                error_msg = f"❌ Desculpe, ocorreu um erro ao processar sua solicitação: {e}"
                st.error(error_msg)