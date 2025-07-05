import streamlit as st
from streamlit_option_menu import option_menu

def create_sidebar():
    """Create and render the main navigation sidebar"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #667eea;">🚀 n8n Business Suite</h2>
            <p style="color: #666; font-size: 0.9rem;">Complete Business Automation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Main navigation menu
        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", 
                "Form Builder", 
                "Business Modeler", 
                "Examples", 
                "Settings", 
                "Chatbots"
            ],
            icons=[
                "speedometer2", 
                "tools", 
                "diagram-3", 
                "collection", 
                "gear", 
                "robot"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#667eea", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#eee"
                },
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        
        # Load stats from session state or defaults
        stats = st.session_state.get('app_stats', {
            'forms_created': 3,
            'webhooks_configured': 5,
            'examples_available': 50,
            'models_created': 8
        })
        
        st.metric("Forms Created", stats['forms_created'])
        st.metric("Webhooks Active", stats['webhooks_configured'])
        st.metric("Examples Available", stats['examples_available'])
        st.metric("Business Models", stats['models_created'])
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🆕 New Form", use_container_width=True):
            st.session_state.quick_action = "new_form"
        
        if st.button("🔗 Test Webhook", use_container_width=True):
            st.session_state.quick_action = "test_webhook"
        
        if st.button("📋 Load Example", use_container_width=True):
            st.session_state.quick_action = "load_example"
        
        st.markdown("---")
        
        # Help and documentation
        with st.expander("📚 Help & Documentation"):
            st.markdown("""
            **Getting Started:**
            1. Configure webhooks in Settings
            2. Create forms using Form Builder
            3. Test with examples
            4. Deploy your business processes
            
            **Need Help?**
            - Check the Examples section
            - Use the Business Modeler
            - Test webhooks before deployment
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>Built with ❤️ using Streamlit</p>
            <p>Version 1.0.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    return selected

def create_examples_sidebar():
    """Create sidebar specifically for examples page"""
    
    with st.sidebar:
        st.header("📁 Business Examples")
        
        # Categories
        categories = {
            "📝 Forms": [
                "Customer Feedback",
                "Lead Capture", 
                "Appointment Booking",
                "Support Tickets",
                "Newsletter Signup"
            ],
            "📎 Document Processing": [
                "Contract Management",
                "Invoice Processing", 
                "Report Generation",
                "NDA Handling",
                "Catalog Management"
            ],
            "🎙️ Audio Processing": [
                "Client Interviews",
                "Sales Call Analysis",
                "Pitch Recordings",
                "Voice Memos",
                "Training Audio"
            ],
            "🖼️ Image Processing": [
                "Product Photos",
                "ID Verification", 
                "Logo Management",
                "Receipt Processing",
                "Event Documentation"
            ],
            "🤖 Automation": [
                "Customer Support",
                "Sales Automation",
                "Booking Systems", 
                "Feedback Collection",
                "HR Onboarding"
            ],
            "🏢 Industry Specific": [
                "Real Estate CRM",
                "Healthcare Forms",
                "E-commerce Tools",
                "Agency Management",
                "Restaurant Orders"
            ]
        }
        
        for category, items in categories.items():
            with st.expander(category):
                for item in items:
                    if st.button(item, key=f"example_{item.replace(' ', '_').lower()}"):
                        st.session_state.selected_example = item
                        return item
        
        st.markdown("---")
        
        # Filter options
        st.subheader("🔍 Filters")
        
        industry_filter = st.selectbox(
            "Industry",
            ["All", "Real Estate", "Healthcare", "E-commerce", "SaaS", "Consulting", "Restaurant", "Retail"]
        )
        
        complexity_filter = st.selectbox(
            "Complexity",
            ["All", "Beginner", "Intermediate", "Advanced"]
        )
        
        integration_filter = st.selectbox(
            "Integration Type", 
            ["All", "Webhook Only", "API + Webhook", "File Processing", "Multi-step"]
        )
        
        # Store filters in session state
        st.session_state.example_filters = {
            "industry": industry_filter,
            "complexity": complexity_filter,
            "integration": integration_filter
        }
        
        return None

def create_settings_sidebar():
    """Create sidebar for settings page"""
    
    with st.sidebar:
        st.header("⚙️ Settings Categories")
        
        settings_sections = [
            "🔗 Webhook Management",
            "🛠️ Form Configuration", 
            "🔐 Security Settings",
            "📊 Analytics Setup",
            "🎨 UI Customization",
            "📱 Integration Settings",
            "🔄 Backup & Restore",
            "📋 Export/Import"
        ]
        
        selected_section = st.radio(
            "Select Section",
            settings_sections,
            key="settings_section"
        )
        
        st.markdown("---")
        
        # Quick settings
        st.subheader("⚡ Quick Settings")
        
        # Theme toggle
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.session_state.theme = theme
        
        # Auto-save toggle
        auto_save = st.checkbox("Auto-save forms", value=True)
        st.session_state.auto_save = auto_save
        
        # Notifications
        notifications = st.checkbox("Enable notifications", value=True)
        st.session_state.notifications = notifications
        
        st.markdown("---")
        
        # System info
        st.subheader("ℹ️ System Info")
        st.text(f"Version: 1.0.0")
        st.text(f"Forms: {len(st.session_state.get('custom_forms', {}))}")
        st.text(f"Webhooks: {len(st.session_state.get('webhooks', {}))}")
        
        return selected_section.split(" ", 1)[1]  # Remove emoji from section name

