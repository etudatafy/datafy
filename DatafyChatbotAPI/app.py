import streamlit as st
import requests

# FastAPI backend endpoint
API_URL = "http://localhost:8000/query"

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Destek AL - Eğitim Asistanı",
    page_icon="🎓",
    layout="wide"
)

# CSS stillerini uygula
st.markdown("""
<style>
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .rehberlik-badge {
        background-color: #E6F3FF;
        color: #0066CC;
    }
    .oneri-badge {
        background-color: #EAFEF1;
        color: #007944;
    }
    .motivasyon-badge {
        background-color: #FFF2E6;
        color: #FF8000;
    }
    .koc-badge {
        background-color: #F0E6FF;
        color: #6600CC;
    }
    .stChat message.user p {
        font-size: 16px !important;
    }
    .stChat message.assistant p {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# Ajan bilgileri
agent_info = {
    "rehberlik": {
        "emoji": "🧭",
        "title": "Rehberlik Ajanı",
        "description": "Eğitim ve kariyer yolculuğunuzda size rehberlik eder. Eğitim planlaması, okul/bölüm seçimi, sınav hazırlığı konularında destek sağlar."
    },
    "öneri": {
        "emoji": "💡",
        "title": "Öneri Ajanı",
        "description": "Çalışma kaynaklarını, öğrenme tekniklerini ve eğitim araçlarını tavsiye eder. Öğrenme sürecinizi daha etkili hale getirmenize yardımcı olur."
    },
    "motivasyon": {
        "emoji": "✨",
        "title": "Motivasyon Ajanı",
        "description": "Motivasyonunuzu artıracak, stres ve kaygılarınızla başa çıkmanıza yardımcı olacak destekleyici tavsiyeler sunar."
    },
    "koç": {
        "emoji": "👨‍🏫",
        "title": "Koç Eşleştirme Ajanı",
        "description": "İhtiyaçlarınıza ve hedeflerinize en uygun eğitim koçlarını bulmanıza yardımcı olur."
    }
}

# Sidebar içeriği
with st.sidebar:
    st.title("🎓 Destek AL")
    st.subheader("Eğitim Asistanı")
    
    st.markdown("---")
    st.markdown("### Ajanlarımız")
    
    # Her ajan için bilgi göster
    for agent_key, agent_data in agent_info.items():
        st.markdown(f"**{agent_data['emoji']} {agent_data['title']}**")
        st.markdown(f"{agent_data['description']}")
        st.markdown("---")
    
    st.caption("© 2025 Destek AL Eğitim Asistanı")

# Initialize conversation history in session_state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Ana içerik
st.title("Eğitim Asistanı Sohbeti")
st.markdown("Eğitim ve öğrenimle ilgili sorularınızı ajanlarımıza sorabilirsiniz. Sorunuza uygun ajan seçilecektir.")

# Geçmiş mesajları göster
for message in st.session_state.conversation:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(message["message"])
    else:
        agent_type = message.get("agent_type", "rehberlik")
        agent_data = agent_info.get(agent_type, agent_info["rehberlik"])
        
        with st.chat_message("assistant", avatar=agent_data["emoji"]):
            # Ajan badge'i göster
            st.markdown(f"""<div class="agent-badge {agent_type}-badge">
                            {agent_data['emoji']} {agent_data['title']}
                            </div>""", 
                        unsafe_allow_html=True)
            st.write(message["content"])

# Kullanıcı giriş alanı
user_input = st.chat_input("Sorunuzu buraya yazın...")

if user_input:
    # Kullanıcı mesajını göster
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    
    # Kullanıcı mesajını geçmişe ekle
    st.session_state.conversation.append({
        "role": "user",
        "message": user_input
    })
    
    # FastAPI'ye istek gönder
    with st.spinner("Yanıt hazırlanıyor..."):
        payload = {
            "query": user_input,
            "user_id": "streamlit_user"
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            response_data = response.json()
            
            if response.status_code == 200:
                # Ajan türü ve yanıtı al
                agent_type = response_data.get("agent", "rehberlik")
                content = response_data.get("response", "")
                
                # Ajan bilgilerini al (varsayılan olarak rehberlik kullan)
                agent_data = agent_info.get(agent_type, agent_info["rehberlik"])
                
                # Asistan yanıtını göster
                with st.chat_message("assistant", avatar=agent_data["emoji"]):
                    # Ajan badge'i göster
                    st.markdown(f"""<div class="agent-badge {agent_type}-badge">
                                {agent_data['emoji']} {agent_data['title']}
                                </div>""", 
                                unsafe_allow_html=True)
                    st.write(content)
                
                # Yanıtı geçmişe ekle
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": content,
                    "agent_type": agent_type
                })
            else:
                error_message = response_data.get("detail", "Bilinmeyen bir hata oluştu.")
                with st.chat_message("assistant", avatar="❌"):
                    st.error(f"Hata: {error_message}")
                    
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": f"Hata: {error_message}",
                    "agent_type": "error"
                })
                
        except Exception as e:
            with st.chat_message("assistant", avatar="❌"):
                st.error(f"Bağlantı hatası: {str(e)}")
            
            st.session_state.conversation.append({
                "role": "assistant",
                "content": f"Bağlantı hatası: {str(e)}",
                "agent_type": "error"
            })