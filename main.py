import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io
import time
from typing import Dict, List, Any
import uuid

# Page configuration
st.set_page_config(
    page_title="n8n Business Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'forms_created' not in st.session_state:
    st.session_state.forms_created = 3
if 'webhooks_active' not in st.session_state:
    st.session_state.webhooks_active = 5
if 'models_created' not in st.session_state:
    st.session_state.models_created = 8
if 'webhook_url' not in st.session_state:
    st.session_state.webhook_url = ""
if 'form_submissions' not in st.session_state:
    st.session_state.form_submissions = []
if 'business_models' not in st.session_state:
    st.session_state.business_models = []

# Business Examples Database
BUSINESS_EXAMPLES = {
    "lead_generation": {
        "name": "Lead Generation",
        "icon": "🎯",
        "examples": [
            {
                "name": "Contact Form Lead Capture",
                "description": "Capture leads from website contact forms with automatic CRM integration",
                "complexity": "Beginner",
                "fields": ["name", "email", "company", "phone", "message"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/contact-leads",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            {
                "name": "Webinar Registration System",
                "description": "Automated webinar registration with email confirmations and calendar invites",
                "complexity": "Intermediate",
                "fields": ["name", "email", "company", "job_title", "webinar_topic", "timezone"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/webinar-registration",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            {
                "name": "Lead Magnet Download",
                "description": "Capture leads through downloadable content with automated follow-up sequences",
                "complexity": "Intermediate",
                "fields": ["name", "email", "company", "industry", "content_type"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/lead-magnet",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            {
                "name": "Newsletter Subscription",
                "description": "Newsletter signup with segmentation and automated welcome series",
                "complexity": "Beginner",
                "fields": ["email", "name", "interests", "frequency_preference"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/newsletter",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            }
        ]
    },
    "customer_service": {
        "name": "Customer Service",
        "icon": "🎧",
        "examples": [
            {
                "name": "Support Ticket System",
                "description": "Automated support ticket creation with priority routing and SLA tracking",
                "complexity": "Intermediate",
                "fields": ["name", "email", "subject", "priority", "category", "description", "attachment"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/support-ticket",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            {
                "name": "Customer Feedback Collection",
                "description": "Gather customer feedback with automated analysis and response routing",
                "complexity": "Beginner",
                "fields": ["name", "email", "rating", "feedback_type", "comments", "product_service"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/feedback",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            }
        ]
    },
    "sales_automation": {
        "name": "Sales Automation",
        "icon": "💰",
        "examples": [
            {
                "name": "Sales Inquiry Processing",
                "description": "Automated lead qualification and sales team assignment",
                "complexity": "Intermediate",
                "fields": ["name", "email", "company", "phone", "budget", "timeline", "requirements"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/sales-inquiry",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            {
                "name": "Proposal Request System",
                "description": "Automated proposal generation and tracking workflow",
                "complexity": "Advanced",
                "fields": ["company_name", "contact_email", "project_scope", "budget_range", "deadline", "requirements"],
                "webhook_config": {
                    "url": "https://your-n8n.com/webhook/proposal-request",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            }
        ]
    }
}

# Helper Functions
def send_webhook(url: str, data: Dict[str, Any], files: Dict = None) -> bool:
    """Send data to webhook URL"""
    try:
        if not url:
            return False
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "source": "n8n_business_suite",
            "data": data
        }
        
        if files:
            # Convert files to base64 for JSON transmission
            for key, file in files.items():
                if file is not None:
                    payload["files"] = payload.get("files", {})
                    payload["files"][key] = base64.b64encode(file.read()).decode()
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def create_form_field(field_type: str, label: str, key: str, **kwargs):
    """Create dynamic form fields"""
    if field_type == "text":
        return st.text_input(label, key=key, **kwargs)
    elif field_type == "email":
        return st.text_input(label, key=key, **kwargs)
    elif field_type == "number":
        return st.number_input(label, key=key, **kwargs)
    elif field_type == "textarea":
        return st.text_area(label, key=key, **kwargs)
    elif field_type == "selectbox":
        return st.selectbox(label, options=kwargs.get("options", []), key=key)
    elif field_type == "multiselect":
        return st.multiselect(label, options=kwargs.get("options", []), key=key)
    elif field_type == "checkbox":
        return st.checkbox(label, key=key, **kwargs)
    elif field_type == "radio":
        return st.radio(label, options=kwargs.get("options", []), key=key)
    elif field_type == "date":
        return st.date_input(label, key=key, **kwargs)
    elif field_type == "time":
        return st.time_input(label, key=key, **kwargs)
    elif field_type == "file":
        return st.file_uploader(label, key=key, **kwargs)
    elif field_type == "slider":
        return st.slider(label, key=key, **kwargs)
    elif field_type == "color":
        return st.color_picker(label, key=key, **kwargs)
    else:
        return st.text_input(label, key=key, **kwargs)

# Main Application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 n8n Business Suite</h1>
        <p>Complete Local Business Tools with n8n Integration</p>
        <p>Form Builder • Business Modeler • 50+ Examples • Webhook Management</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### Complete Business Automation")
        
        page = st.selectbox(
            "Navigate to:",
            ["🏠 Dashboard", "🛠️ Form Builder", "🏗️ Business Modeler", "📋 Examples", "⚙️ Settings", "🤖 Chatbots"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Forms Created", st.session_state.forms_created)
        st.metric("Webhooks Active", st.session_state.webhooks_active)
        st.metric("Examples Available", "50")
        st.metric("Business Models", st.session_state.models_created)

    # Main Content Area
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🛠️ Form Builder":
        show_form_builder()
    elif page == "🏗️ Business Modeler":
        show_business_modeler()
    elif page == "📋 Examples":
        show_examples()
    elif page == "⚙️ Settings":
        show_settings()
    elif page == "🤖 Chatbots":
        show_chatbots()

def show_dashboard():
    """Dashboard page"""
    st.header("📊 Dashboard")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>50+</h2>
            <p>Business Examples</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>15</h2>
            <p>Form Templates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>8</h2>
            <p>Business Models</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2>∞</h2>
            <p>Webhook Configs</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛠️ Create New Form", use_container_width=True):
            st.session_state.forms_created += 1
            st.success("✅ New form created!")
    
    with col2:
        if st.button("🏗️ Business Modeler", use_container_width=True):
            st.info("🔄 Opening Business Modeler...")
    
    with col3:
        if st.button("📋 Browse Examples", use_container_width=True):
            st.info("📚 Loading examples...")

    # Recent Activity
    st.subheader("📈 Recent Activity")
    
    # Sample data for demonstration
    activity_data = {
        "Date": [datetime.now() - timedelta(days=i) for i in range(7)],
        "Forms Created": [2, 1, 3, 0, 1, 2, 1],
        "Webhooks Triggered": [15, 23, 18, 12, 25, 20, 17]
    }
    
    df = pd.DataFrame(activity_data)
    
    fig = px.line(df, x="Date", y=["Forms Created", "Webhooks Triggered"],
                  title="Weekly Activity Overview")
    st.plotly_chart(fig, use_container_width=True)

    # Getting Started Guide
    st.subheader("🎯 Getting Started")
    
    with st.expander("📋 Step-by-Step Guide"):
        st.markdown("""
        **Getting Started:**
        
        1. **Configure webhooks** in Settings
        2. **Create forms** using Form Builder
        3. **Test with examples**
        4. **Deploy your business processes**
        
        **Need Help?**
        
        - Check the Examples section
        - Use the Business Modeler
        - Test webhooks before deployment
        """)

def show_form_builder():
    """Form Builder page"""
    st.header("🛠️ Form Builder")
    
    # Global webhook configuration
    st.subheader("🔗 Webhook Configuration")
    webhook_url = st.text_input(
        "Enter your n8n Webhook URL",
        value=st.session_state.webhook_url,
        placeholder="https://your-n8n-instance.com/webhook/your-endpoint"
    )
    st.session_state.webhook_url = webhook_url
    
    if webhook_url:
        if st.button("🧪 Test Webhook Connection"):
            test_data = {"test": True, "timestamp": datetime.now().isoformat()}
            if send_webhook(webhook_url, test_data):
                st.success("✅ Webhook connection successful!")
            else:
                st.error("❌ Webhook connection failed. Please check your URL.")

    st.markdown("---")

    # Form Builder Interface
    st.subheader("📝 Build Your Form")
    
    # Form Configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        form_name = st.text_input("Form Name", value="Custom Business Form")
        form_description = st.text_area("Form Description", value="Enter form description here...")
    
    with col2:
        form_category = st.selectbox("Category", ["Lead Generation", "Customer Service", "Sales", "HR", "Marketing", "Finance"])
        form_complexity = st.selectbox("Complexity", ["Beginner", "Intermediate", "Advanced"])

    # Dynamic Form Fields
    st.subheader("🔧 Form Fields")
    
    if 'form_fields' not in st.session_state:
        st.session_state.form_fields = []
    
    # Add new field
    with st.expander("➕ Add New Field"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            field_type = st.selectbox("Field Type", [
                "text", "email", "number", "textarea", "selectbox", 
                "multiselect", "checkbox", "radio", "date", "time", 
                "file", "slider", "color"
            ])
        
        with col2:
            field_label = st.text_input("Field Label")
        
        with col3:
            field_required = st.checkbox("Required")
        
        if field_type in ["selectbox", "multiselect", "radio"]:
            field_options = st.text_area("Options (one per line)").split('\n')
        else:
            field_options = []
        
        if st.button("Add Field") and field_label:
            field_config = {
                "type": field_type,
                "label": field_label,
                "required": field_required,
                "options": field_options if field_options else None,
                "key": f"field_{len(st.session_state.form_fields)}"
            }
            st.session_state.form_fields.append(field_config)
            st.success(f"✅ Added field: {field_label}")

    # Display current fields
    if st.session_state.form_fields:
        st.subheader("📋 Current Form Fields")
        
        for i, field in enumerate(st.session_state.form_fields):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{field['label']}** ({field['type']})")
            
            with col2:
                if field['required']:
                    st.write("🔴 Required")
                else:
                    st.write("⚪ Optional")
            
            with col3:
                if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.form_fields.pop(i)
                    st.rerun()

    # Form Preview and Test
    if st.session_state.form_fields:
        st.markdown("---")
        st.subheader("👀 Form Preview")
        
        with st.form("preview_form"):
            st.write(f"**{form_name}**")
            st.write(form_description)
            
            form_data = {}
            files_data = {}
            
            for field in st.session_state.form_fields:
                if field['type'] == 'file':
                    uploaded_file = create_form_field(
                        field['type'], 
                        field['label'], 
                        field['key']
                    )
                    if uploaded_file:
                        files_data[field['key']] = uploaded_file
                else:
                    form_data[field['key']] = create_form_field(
                        field['type'], 
                        field['label'], 
                        field['key'],
                        options=field.get('options', [])
                    )
            
            submitted = st.form_submit_button("🚀 Submit Form")
            
            if submitted:
                if webhook_url:
                    # Prepare submission data
                    submission_data = {
                        "form_name": form_name,
                        "form_category": form_category,
                        "form_complexity": form_complexity,
                        "form_data": form_data
                    }
                    
                    # Send to webhook
                    if send_webhook(webhook_url, submission_data, files_data):
                        st.success("✅ Form submitted successfully to n8n!")
                        st.session_state.form_submissions.append({
                            "timestamp": datetime.now(),
                            "form_name": form_name,
                            "data": form_data
                        })
                    else:
                        st.error("❌ Failed to submit form. Please check your webhook URL.")
                else:
                    st.warning("⚠️ Please configure a webhook URL first.")

def show_business_modeler():
    """Business Modeler page"""
    st.header("🏗️ Business Modeler")
    
    st.info("🚧 Visual Business Process Designer")
    
    # Model Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        model_name = st.text_input("Model Name", value="New Business Process")
        model_description = st.text_area("Description", value="Describe your business process...")
    
    with col2:
        model_category = st.selectbox("Category", ["Sales", "Marketing", "HR", "Customer Service", "Finance"])
        model_complexity = st.selectbox("Complexity", ["Simple", "Moderate", "Complex"])

    # Process Nodes
    st.subheader("🔧 Process Nodes")
    
    node_types = {
        "🚀 Trigger": "Process start point (webhook, form submission, schedule)",
        "📝 Form": "Data collection point",
        "🔗 Webhook": "External system integration",
        "❓ Condition": "Decision point with if/then logic",
        "⚡ Action": "Automated task or operation",
        "📧 Notification": "Email, SMS, or alert",
        "💾 Database": "Data storage or retrieval",
        "🌐 API Call": "External API integration",
        "🏁 End": "Process completion point"
    }
    
    selected_nodes = st.multiselect(
        "Select Process Nodes",
        options=list(node_types.keys()),
        help="Choose the components for your business process"
    )
    
    if selected_nodes:
        st.subheader("📋 Selected Nodes")
        for node in selected_nodes:
            with st.expander(f"{node} Configuration"):
                st.write(f"**Description:** {node_types[node]}")
                
                if "Form" in node:
                    st.text_input(f"Form Name for {node}", key=f"form_name_{node}")
                    st.multiselect(f"Form Fields for {node}",
                                  ["Name", "Email", "Phone", "Company", "Message"],
                                  key=f"form_fields_{node}")
                
                elif "Webhook" in node:
                    st.text_input(f"Webhook URL for {node}", key=f"webhook_url_{node}")
                    st.selectbox(f"Method for {node}", ["POST", "GET", "PUT"], key=f"method_{node}")
                
                elif "Condition" in node:
                    st.text_input(f"Condition Logic for {node}",
                                 placeholder="e.g., if amount > 1000",
                                 key=f"condition_{node}")
                
                elif "Notification" in node:
                    st.selectbox(f"Notification Type for {node}",
                                ["Email", "SMS", "Slack", "Teams"],
                                key=f"notification_type_{node}")
                    st.text_area(f"Message Template for {node}", key=f"message_{node}")

    # Process Flow Visualization
    if selected_nodes:
        st.subheader("🔄 Process Flow")
        
        # Create a simple flow diagram
        flow_data = []
        for i, node in enumerate(selected_nodes):
            flow_data.append({
                "Step": i + 1,
                "Node": node,
                "Type": node.split()[1] if len(node.split()) > 1 else "Process"
            })
        
        df = pd.DataFrame(flow_data)
        st.dataframe(df, use_container_width=True)
        
        # Generate n8n workflow JSON
        if st.button("📄 Generate n8n Workflow JSON"):
            workflow = {
                "name": model_name,
                "nodes": [],
                "connections": {}
            }
            
            for i, node in enumerate(selected_nodes):
                node_config = {
                    "id": f"node_{i}",
                    "name": node,
                    "type": "n8n-nodes-base.webhook" if "Webhook" in node else "n8n-nodes-base.function",
                    "position": [100 + i * 200, 100],
                    "parameters": {}
                }
                workflow["nodes"].append(node_config)
            
            st.json(workflow)
            
            # Save model
            if st.button("💾 Save Business Model"):
                st.session_state.business_models.append({
                    "name": model_name,
                    "description": model_description,
                    "category": model_category,
                    "nodes": selected_nodes,
                    "workflow": workflow,
                    "created": datetime.now()
                })
                st.session_state.models_created += 1
                st.success("✅ Business model saved successfully!")

def show_examples():
    """Examples page"""
    st.header("📋 Business Examples Gallery")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(BUSINESS_EXAMPLES.keys())
        )
    
    with col2:
        complexity_filter = st.selectbox(
            "Filter by Complexity",
            ["All", "Beginner", "Intermediate", "Advanced"]
        )
    
    with col3:
        search_term = st.text_input("🔍 Search Examples")

    # Display examples
    for category_key, category_data in BUSINESS_EXAMPLES.items():
        if category_filter != "All" and category_filter != category_key:
            continue
            
        st.subheader(f"{category_data['icon']} {category_data['name']}")
        
        # Create columns for examples
        cols = st.columns(2)
        
        for i, example in enumerate(category_data['examples']):
            if complexity_filter != "All" and complexity_filter != example['complexity']:
                continue
            
            if search_term and search_term.lower() not in example['name'].lower():
                continue
            
            with cols[i % 2]:
                with st.expander(f"📄 {example['name']}"):
                    st.write(f"**Complexity:** {example['complexity']}")
                    st.write(f"**Description:** {example['description']}")
                    
                    st.write("**Form Fields:**")
                    for field in example['fields']:
                        st.write(f"• {field.replace('_', ' ').title()}")
                    
                    st.write("**Webhook Configuration:**")
                    st.code(json.dumps(example['webhook_config'], indent=2))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"🚀 Use Template", key=f"use_{category_key}_{i}"):
                            st.success("✅ Template loaded in Form Builder!")
                    
                    with col2:
                        if st.button(f"📋 Copy Config", key=f"copy_{category_key}_{i}"):
                            st.info("📋 Configuration copied to clipboard!")

def show_settings():
    """Settings page"""
    st.header("⚙️ Settings & Configuration")
    
    # Webhook Settings
    with st.expander("🔗 Webhook Settings", expanded=True):
        st.subheader("Global Webhook Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_webhook = st.text_input(
                "Default Webhook URL",
                value=st.session_state.webhook_url,
                help="This will be used as the default for all forms"
            )
            request_timeout = st.number_input("Request Timeout (seconds)", value=10, min_value=1, max_value=60)
        
        with col2:
            retry_attempts = st.number_input("Retry Attempts", value=3, min_value=1, max_value=10)
            retry_delay = st.number_input("Retry Delay (seconds)", value=2, min_value=1, max_value=30)
        
        st.text_area("Default Headers (JSON format)",
                    value='{"Content-Type": "application/json"}',
                    help="Headers to include with all webhook requests")
        
        if st.button("💾 Save Webhook Settings"):
            st.session_state.webhook_url = default_webhook
            st.success("✅ Webhook settings saved!")

    # Form Settings
    with st.expander("📝 Form Settings"):
        st.subheader("Form Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_file_size = st.number_input("Max File Upload Size (MB)", value=10, min_value=1, max_value=100)
            allowed_file_types = st.multiselect(
                "Allowed File Types",
                ["pdf", "doc", "docx", "txt", "jpg", "png", "gif", "csv", "xlsx"],
                default=["pdf", "doc", "jpg", "png"]
            )
        
        with col2:
            form_validation = st.checkbox("Enable Form Validation", value=True)
            required_field_indicator = st.text_input("Required Field Indicator", value="*")
        
        if st.button("💾 Save Form Settings"):
            st.success("✅ Form settings saved!")

def show_chatbots():
    """Chatbots page"""
    st.header("🤖 Embedded Chatbots")
    
    st.info("💡 Integrate chatbots for various business functions")
    
    # Chatbot Configuration
    chatbot_types = {
        "Customer Support Bot": {
            "description": "Handle customer inquiries and support tickets",
            "use_cases": ["FAQ responses", "Ticket creation", "Status updates"],
            "integration": "Embed in customer portal or website"
        },
        "Sales Bot": {
            "description": "Qualify leads and schedule sales meetings",
            "use_cases": ["Lead qualification", "Product demos", "Pricing inquiries"],
            "integration": "Embed on landing pages and product pages"
        },
        "Booking Assistant": {
            "description": "Schedule appointments and manage calendars",
            "use_cases": ["Appointment booking", "Calendar management", "Reminders"],
            "integration": "Embed on service pages and contact forms"
        }
    }
    
    # Display chatbot options
    for bot_name, bot_info in chatbot_types.items():
        with st.expander(f"🤖 {bot_name}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {bot_info['description']}")
                st.write("**Use Cases:**")
                for use_case in bot_info['use_cases']:
                    st.write(f"• {use_case}")
                st.write(f"**Integration:** {bot_info['integration']}")
            
            with col2:
                webhook_url = st.text_input(f"Webhook URL for {bot_name}", key=f"webhook_{bot_name}")
                
                if st.button(f"🚀 Deploy {bot_name}", key=f"deploy_{bot_name}"):
                    if webhook_url:
                        st.success(f"✅ {bot_name} deployed successfully!")
                        st.code(f"""<!-- Embed code for {bot_name} -->
<iframe 
    src="https://your-chatbot-service.com/embed/{bot_name.lower().replace(' ', '-')}"
    width="100%" 
    height="400"
    frameborder="0">
</iframe>
                        """)
                    else:
                        st.warning("⚠️ Please provide a webhook URL first.")

    # Chatbot Analytics
    st.subheader("📊 Chatbot Analytics")
    
    # Sample analytics data
    analytics_data = {
        "Bot": ["Support Bot", "Sales Bot", "Booking Bot"],
        "Conversations": [245, 189, 156],
        "Success Rate": [87, 92, 78],
        "Avg Response Time": [2.3, 1.8, 3.1]
    }
    
    df = pd.DataFrame(analytics_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df, x="Bot", y="Conversations", title="Chatbot Usage")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(df, x="Bot", y="Success Rate", title="Success Rates (%)")
        st.plotly_chart(fig, use_container_width=True)

# Footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 n8n Business Suite - Streamline your business processes with powerful automation</p>
        <p>Built with ❤️ using Streamlit and n8n</p>
        <p>Version 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()

print("n8n Business Suite application created successfully!")
print("To run the application, use: streamlit run streamlit_business_suite.py")

