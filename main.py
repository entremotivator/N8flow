import streamlit as st
import requests
from datetime import datetime
import json
import os
from pathlib import Path
import sys

# Add the current directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from utils.webhook_manager import WebhookManager
from utils.form_builder import FormBuilder
from utils.business_modeler import BusinessModeler
from components.sidebar import create_sidebar
from components.settings import SettingsManager

# Page configuration
st.set_page_config(
    page_title="n8n Business Suite", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# Initialize session state
if 'webhook_manager' not in st.session_state:
    st.session_state.webhook_manager = WebhookManager()

if 'form_builder' not in st.session_state:
    st.session_state.form_builder = FormBuilder()

if 'business_modeler' not in st.session_state:
    st.session_state.business_modeler = BusinessModeler()

if 'settings_manager' not in st.session_state:
    st.session_state.settings_manager = SettingsManager()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚀 n8n Business Suite</h1>
    <p>Complete Local Business Tools with n8n Integration</p>
    <p>Form Builder • Business Modeler • 50+ Examples • Webhook Management</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
page = create_sidebar()

# Main content based on selected page
if page == "Dashboard":
    st.header("📊 Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>50+</h3>
            <p>Business Examples</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>15</h3>
            <p>Form Templates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>8</h3>
            <p>Business Models</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>∞</h3>
            <p>Webhook Configs</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛠️ Create New Form", use_container_width=True):
            st.session_state.current_page = "Form Builder"
            st.rerun()
    
    with col2:
        if st.button("🏗️ Business Modeler", use_container_width=True):
            st.session_state.current_page = "Business Modeler"
            st.rerun()
    
    with col3:
        if st.button("📋 Browse Examples", use_container_width=True):
            st.session_state.current_page = "Examples"
            st.rerun()

elif page == "Form Builder":
    st.header("🛠️ Custom Business Form Builder")
    
    # Global webhook input
    webhook_url = st.text_input("🔗 Enter your n8n Webhook URL", value="https://your-n8n-webhook.com")
    
    # Form builder interface
    with st.form("custom_form"):
        form_name = st.text_input("Form Name", value="My Business Form")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
        
        with col2:
            business_type = st.selectbox("Business Type", [
                "Real Estate", "Coaching", "E-commerce", "Agency", "Healthcare",
                "Consulting", "SaaS", "Restaurant", "Retail", "Manufacturing"
            ])
            appointment_date = st.date_input("Appointment Date", value=datetime.now())
            subscribe = st.checkbox("Subscribe to newsletter")
        
        message = st.text_area("Message")
        
        # File uploads
        uploaded_pdfs = st.file_uploader("📎 Upload PDFs", accept_multiple_files=True, type=["pdf"])
        uploaded_images = st.file_uploader("🖼️ Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        uploaded_audio = st.file_uploader("🎙️ Upload Audio Files", accept_multiple_files=True, type=["mp3", "wav", "m4a"])
        
        submitted = st.form_submit_button("Submit to n8n")
        
        if submitted:
            payload = {
                "form_name": form_name,
                "name": name,
                "email": email,
                "phone": phone,
                "business_type": business_type,
                "appointment_date": str(appointment_date),
                "subscribe": subscribe,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            files = {}
            
            for i, file in enumerate(uploaded_pdfs):
                files[f"pdf_{i}"] = (file.name, file.getvalue(), file.type)
            
            for i, file in enumerate(uploaded_images):
                files[f"image_{i}"] = (file.name, file.getvalue(), file.type)
            
            for i, file in enumerate(uploaded_audio):
                files[f"audio_{i}"] = (file.name, file.getvalue(), file.type)
            
            if webhook_url and webhook_url != "https://your-n8n-webhook.com":
                try:
                    response = requests.post(webhook_url, data=payload, files=files)
                    if response.status_code == 200:
                        st.success("✅ Data sent to n8n successfully!")
                        st.json(payload)
                    else:
                        st.error(f"❌ Failed to send. Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
            else:
                st.warning("Please enter a valid n8n webhook URL.")

elif page == "Business Modeler":
    st.header("🏗️ Business Process Modeler")
    st.session_state.business_modeler.render()

elif page == "Examples":
    st.header("📋 Business Examples & Templates")
    
    # Load and display examples
    from examples.business_examples import BusinessExamples
    examples = BusinessExamples()
    examples.render()

elif page == "Settings":
    st.header("⚙️ Settings & Webhook Management")
    st.session_state.settings_manager.render()

elif page == "Chatbots":
    st.header("🤖 Embedded Chatbots")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Support Bot", "Sales Bot", "Booking Assistant", "Feedback Bot", "HR Bot"
    ])
    
    with tab1:
        st.subheader("Customer Support Bot")
        chatbot_url = st.text_input("Support Bot URL", value="https://your-support-chatbot.com")
        if chatbot_url and chatbot_url != "https://your-support-chatbot.com":
            st.components.v1.iframe(chatbot_url, height=400)
        else:
            st.info("Enter a valid chatbot URL to embed the support bot")
    
    with tab2:
        st.subheader("Sales Bot")
        chatbot_url = st.text_input("Sales Bot URL", value="https://your-sales-chatbot.com")
        if chatbot_url and chatbot_url != "https://your-sales-chatbot.com":
            st.components.v1.iframe(chatbot_url, height=400)
        else:
            st.info("Enter a valid chatbot URL to embed the sales bot")
    
    with tab3:
        st.subheader("Booking Assistant")
        chatbot_url = st.text_input("Booking Bot URL", value="https://your-booking-chatbot.com")
        if chatbot_url and chatbot_url != "https://your-booking-chatbot.com":
            st.components.v1.iframe(chatbot_url, height=400)
        else:
            st.info("Enter a valid chatbot URL to embed the booking assistant")
    
    with tab4:
        st.subheader("Feedback Collector")
        chatbot_url = st.text_input("Feedback Bot URL", value="https://your-feedback-chatbot.com")
        if chatbot_url and chatbot_url != "https://your-feedback-chatbot.com":
            st.components.v1.iframe(chatbot_url, height=400)
        else:
            st.info("Enter a valid chatbot URL to embed the feedback bot")
    
    with tab5:
        st.subheader("HR Onboarding Bot")
        chatbot_url = st.text_input("HR Bot URL", value="https://your-hr-chatbot.com")
        if chatbot_url and chatbot_url != "https://your-hr-chatbot.com":
            st.components.v1.iframe(chatbot_url, height=400)
        else:
            st.info("Enter a valid chatbot URL to embed the HR bot")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 n8n Business Suite - Streamline your business processes with powerful automation</p>
    <p>Built with ❤️ using Streamlit and n8n</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass

