import streamlit as st
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import os

class WebhookManager:
    def __init__(self):
        self.webhooks_file = "data/webhooks.json"
        self.ensure_data_dir()
        self.load_webhooks()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_webhooks(self):
        """Load webhooks from file"""
        try:
            if os.path.exists(self.webhooks_file):
                with open(self.webhooks_file, 'r') as f:
                    self.webhooks = json.load(f)
            else:
                self.webhooks = self.get_default_webhooks()
                self.save_webhooks()
        except Exception as e:
            st.error(f"Error loading webhooks: {e}")
            self.webhooks = self.get_default_webhooks()
    
    def save_webhooks(self):
        """Save webhooks to file"""
        try:
            with open(self.webhooks_file, 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            st.error(f"Error saving webhooks: {e}")
    
    def get_default_webhooks(self) -> Dict:
        """Get default webhook configurations"""
        return {
            "lead_capture": {
                "name": "Lead Capture",
                "url": "https://your-n8n-instance.com/webhook/lead-capture",
                "description": "Captures leads from contact forms",
                "fields": ["name", "email", "phone", "company", "message"],
                "active": True
            },
            "customer_feedback": {
                "name": "Customer Feedback",
                "url": "https://your-n8n-instance.com/webhook/feedback",
                "description": "Collects customer feedback and reviews",
                "fields": ["name", "email", "rating", "feedback", "product"],
                "active": True
            },
            "appointment_booking": {
                "name": "Appointment Booking",
                "url": "https://your-n8n-instance.com/webhook/booking",
                "description": "Handles appointment scheduling",
                "fields": ["name", "email", "phone", "service", "date", "time"],
                "active": True
            },
            "support_ticket": {
                "name": "Support Ticket",
                "url": "https://your-n8n-instance.com/webhook/support",
                "description": "Creates support tickets",
                "fields": ["name", "email", "priority", "category", "description"],
                "active": True
            },
            "newsletter_signup": {
                "name": "Newsletter Signup",
                "url": "https://your-n8n-instance.com/webhook/newsletter",
                "description": "Newsletter subscription management",
                "fields": ["email", "name", "preferences", "source"],
                "active": True
            }
        }
    
    def add_webhook(self, key: str, webhook_data: Dict):
        """Add a new webhook configuration"""
        self.webhooks[key] = webhook_data
        self.save_webhooks()
    
    def update_webhook(self, key: str, webhook_data: Dict):
        """Update existing webhook configuration"""
        if key in self.webhooks:
            self.webhooks[key].update(webhook_data)
            self.save_webhooks()
    
    def delete_webhook(self, key: str):
        """Delete webhook configuration"""
        if key in self.webhooks:
            del self.webhooks[key]
            self.save_webhooks()
    
    def get_webhook(self, key: str) -> Dict:
        """Get specific webhook configuration"""
        return self.webhooks.get(key, {})
    
    def get_all_webhooks(self) -> Dict:
        """Get all webhook configurations"""
        return self.webhooks
    
    def test_webhook(self, webhook_url: str, test_data: Dict = None) -> Dict:
        """Test webhook connectivity"""
        if not test_data:
            test_data = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "Test webhook from n8n Business Suite"
            }
        
        try:
            response = requests.post(
                webhook_url, 
                json=test_data, 
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text[:500] if response.text else "No response",
                "error": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }
    
    def send_to_webhook(self, webhook_key: str, data: Dict, files: Dict = None) -> Dict:
        """Send data to specific webhook"""
        webhook = self.get_webhook(webhook_key)
        
        if not webhook or not webhook.get('active', False):
            return {
                "success": False,
                "error": "Webhook not found or inactive"
            }
        
        webhook_url = webhook.get('url')
        if not webhook_url:
            return {
                "success": False,
                "error": "Webhook URL not configured"
            }
        
        try:
            # Add metadata
            payload = {
                **data,
                "webhook_key": webhook_key,
                "timestamp": datetime.now().isoformat(),
                "source": "n8n_business_suite"
            }
            
            if files:
                response = requests.post(webhook_url, data=payload, files=files, timeout=30)
            else:
                response = requests.post(
                    webhook_url, 
                    json=payload, 
                    timeout=30,
                    headers={"Content-Type": "application/json"}
                )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text[:500] if response.text else "No response",
                "error": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }
    
    def render_webhook_selector(self, key: str = "webhook_selector") -> str:
        """Render webhook selector in Streamlit"""
        webhook_options = {k: v['name'] for k, v in self.webhooks.items() if v.get('active', False)}
        
        if not webhook_options:
            st.warning("No active webhooks configured. Please add webhooks in Settings.")
            return None
        
        selected = st.selectbox(
            "Select Webhook",
            options=list(webhook_options.keys()),
            format_func=lambda x: webhook_options[x],
            key=key
        )
        
        if selected:
            webhook = self.get_webhook(selected)
            st.info(f"📝 {webhook.get('description', 'No description')}")
            
            # Show webhook URL (masked for security)
            url = webhook.get('url', '')
            masked_url = url[:20] + "..." + url[-10:] if len(url) > 30 else url
            st.caption(f"🔗 {masked_url}")
        
        return selected
    
    def render_webhook_manager(self):
        """Render full webhook management interface"""
        st.subheader("🔗 Webhook Management")
        
        tab1, tab2, tab3 = st.tabs(["View Webhooks", "Add/Edit", "Test"])
        
        with tab1:
            st.write("### Current Webhooks")
            for key, webhook in self.webhooks.items():
                with st.expander(f"{'✅' if webhook.get('active') else '❌'} {webhook.get('name', key)}"):
                    st.write(f"**Description:** {webhook.get('description', 'No description')}")
                    st.write(f"**URL:** {webhook.get('url', 'Not configured')}")
                    st.write(f"**Fields:** {', '.join(webhook.get('fields', []))}")
                    st.write(f"**Status:** {'Active' if webhook.get('active') else 'Inactive'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit {key}", key=f"edit_{key}"):
                            st.session_state[f"editing_{key}"] = True
                    with col2:
                        if st.button(f"Delete {key}", key=f"delete_{key}"):
                            self.delete_webhook(key)
                            st.success(f"Deleted webhook: {key}")
                            st.rerun()
        
        with tab2:
            st.write("### Add New Webhook")
            with st.form("add_webhook"):
                new_key = st.text_input("Webhook Key (unique identifier)")
                new_name = st.text_input("Webhook Name")
                new_url = st.text_input("Webhook URL")
                new_description = st.text_area("Description")
                new_fields = st.text_input("Fields (comma-separated)", value="name,email")
                new_active = st.checkbox("Active", value=True)
                
                if st.form_submit_button("Add Webhook"):
                    if new_key and new_name and new_url:
                        webhook_data = {
                            "name": new_name,
                            "url": new_url,
                            "description": new_description,
                            "fields": [f.strip() for f in new_fields.split(",") if f.strip()],
                            "active": new_active
                        }
                        self.add_webhook(new_key, webhook_data)
                        st.success(f"Added webhook: {new_name}")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")
        
        with tab3:
            st.write("### Test Webhooks")
            webhook_to_test = st.selectbox(
                "Select webhook to test",
                options=list(self.webhooks.keys()),
                format_func=lambda x: self.webhooks[x].get('name', x)
            )
            
            if webhook_to_test:
                webhook = self.get_webhook(webhook_to_test)
                test_url = st.text_input("Test URL", value=webhook.get('url', ''))
                
                if st.button("Test Webhook"):
                    if test_url:
                        result = self.test_webhook(test_url)
                        if result['success']:
                            st.success("✅ Webhook test successful!")
                            st.json(result)
                        else:
                            st.error("❌ Webhook test failed!")
                            st.json(result)
                    else:
                        st.error("Please enter a webhook URL to test")

