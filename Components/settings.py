import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, Any
import zipfile
import io

class SettingsManager:
    def __init__(self):
        self.settings_file = "data/app_settings.json"
        self.ensure_data_dir()
        self.load_settings()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_settings(self):
        """Load application settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
                self.save_settings()
        except Exception as e:
            st.error(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            st.error(f"Error saving settings: {e}")
    
    def get_default_settings(self) -> Dict:
        """Get default application settings"""
        return {
            "general": {
                "app_name": "n8n Business Suite",
                "theme": "light",
                "auto_save": True,
                "notifications": True,
                "language": "en",
                "timezone": "UTC"
            },
            "webhooks": {
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 5,
                "default_headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "n8n-business-suite/1.0"
                }
            },
            "forms": {
                "max_file_size": 10,  # MB
                "allowed_file_types": ["pdf", "jpg", "jpeg", "png", "mp3", "wav", "m4a"],
                "required_field_indicator": "*",
                "validation_enabled": True
            },
            "security": {
                "enable_csrf": True,
                "session_timeout": 3600,  # seconds
                "max_login_attempts": 5,
                "password_min_length": 8
            },
            "analytics": {
                "track_form_submissions": True,
                "track_webhook_calls": True,
                "retention_days": 90,
                "export_format": "json"
            },
            "ui": {
                "sidebar_expanded": True,
                "show_tooltips": True,
                "animation_enabled": True,
                "compact_mode": False
            },
            "integrations": {
                "n8n_base_url": "",
                "api_key": "",
                "slack_webhook": "",
                "email_service": "smtp",
                "smtp_settings": {
                    "host": "",
                    "port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                }
            }
        }
    
    def render(self):
        """Render the complete settings interface"""
        st.subheader("⚙️ Application Settings")
        
        # Settings tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔗 Webhooks", 
            "🛠️ Forms", 
            "🔐 Security", 
            "📊 Analytics", 
            "🎨 UI/UX", 
            "📱 Integrations"
        ])
        
        with tab1:
            self.render_webhook_settings()
        
        with tab2:
            self.render_form_settings()
        
        with tab3:
            self.render_security_settings()
        
        with tab4:
            self.render_analytics_settings()
        
        with tab5:
            self.render_ui_settings()
        
        with tab6:
            self.render_integration_settings()
        
        # Global actions
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Save All Settings", type="primary"):
                self.save_settings()
                st.success("✅ Settings saved successfully!")
        
        with col2:
            if st.button("🔄 Reset to Defaults"):
                if st.session_state.get('confirm_reset', False):
                    self.settings = self.get_default_settings()
                    self.save_settings()
                    st.success("✅ Settings reset to defaults!")
                    st.session_state.confirm_reset = False
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Click again to confirm reset")
        
        with col3:
            if st.button("📤 Export Settings"):
                self.export_settings()
        
        with col4:
            uploaded_file = st.file_uploader("📥 Import Settings", type=['json'], key="import_settings")
            if uploaded_file:
                self.import_settings(uploaded_file)
    
    def render_webhook_settings(self):
        """Render webhook configuration settings"""
        st.write("### 🔗 Webhook Configuration")
        
        webhook_settings = self.settings.get("webhooks", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            timeout = st.number_input(
                "Request Timeout (seconds)",
                min_value=5,
                max_value=300,
                value=webhook_settings.get("timeout", 30),
                help="Maximum time to wait for webhook response"
            )
            
            retry_attempts = st.number_input(
                "Retry Attempts",
                min_value=0,
                max_value=10,
                value=webhook_settings.get("retry_attempts", 3),
                help="Number of retry attempts for failed webhooks"
            )
        
        with col2:
            retry_delay = st.number_input(
                "Retry Delay (seconds)",
                min_value=1,
                max_value=60,
                value=webhook_settings.get("retry_delay", 5),
                help="Delay between retry attempts"
            )
        
        st.write("#### Default Headers")
        headers = webhook_settings.get("default_headers", {})
        
        # Display current headers
        for key, value in headers.items():
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.text_input(f"Header Key", value=key, disabled=True, key=f"header_key_{key}")
            with col2:
                new_value = st.text_input(f"Header Value", value=value, key=f"header_value_{key}")
                headers[key] = new_value
            with col3:
                if st.button("🗑️", key=f"delete_header_{key}"):
                    del headers[key]
                    st.rerun()
        
        # Add new header
        with st.expander("➕ Add New Header"):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                new_header_key = st.text_input("New Header Key")
            with col2:
                new_header_value = st.text_input("New Header Value")
            with col3:
                if st.button("Add") and new_header_key and new_header_value:
                    headers[new_header_key] = new_header_value
                    st.rerun()
        
        # Update settings
        self.settings["webhooks"] = {
            "timeout": timeout,
            "retry_attempts": retry_attempts,
            "retry_delay": retry_delay,
            "default_headers": headers
        }
    
    def render_form_settings(self):
        """Render form configuration settings"""
        st.write("### 🛠️ Form Configuration")
        
        form_settings = self.settings.get("forms", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_file_size = st.number_input(
                "Max File Size (MB)",
                min_value=1,
                max_value=100,
                value=form_settings.get("max_file_size", 10)
            )
            
            validation_enabled = st.checkbox(
                "Enable Form Validation",
                value=form_settings.get("validation_enabled", True)
            )
        
        with col2:
            required_indicator = st.text_input(
                "Required Field Indicator",
                value=form_settings.get("required_field_indicator", "*"),
                max_chars=5
            )
        
        st.write("#### Allowed File Types")
        current_types = form_settings.get("allowed_file_types", [])
        
        # Common file types
        file_type_options = {
            "Documents": ["pdf", "doc", "docx", "txt", "rtf"],
            "Images": ["jpg", "jpeg", "png", "gif", "bmp", "svg"],
            "Audio": ["mp3", "wav", "m4a", "ogg", "flac"],
            "Video": ["mp4", "avi", "mov", "wmv", "flv"],
            "Archives": ["zip", "rar", "7z", "tar", "gz"]
        }
        
        selected_types = []
        for category, types in file_type_options.items():
            st.write(f"**{category}:**")
            cols = st.columns(len(types))
            for i, file_type in enumerate(types):
                with cols[i]:
                    if st.checkbox(file_type, value=file_type in current_types, key=f"filetype_{file_type}"):
                        selected_types.append(file_type)
        
        # Custom file types
        custom_types = st.text_input(
            "Custom File Types (comma-separated)",
            placeholder="csv, xlsx, json"
        )
        
        if custom_types:
            selected_types.extend([t.strip() for t in custom_types.split(",") if t.strip()])
        
        # Update settings
        self.settings["forms"] = {
            "max_file_size": max_file_size,
            "allowed_file_types": list(set(selected_types)),
            "required_field_indicator": required_indicator,
            "validation_enabled": validation_enabled
        }
    
    def render_security_settings(self):
        """Render security configuration settings"""
        st.write("### 🔐 Security Settings")
        
        security_settings = self.settings.get("security", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_csrf = st.checkbox(
                "Enable CSRF Protection",
                value=security_settings.get("enable_csrf", True),
                help="Protect against Cross-Site Request Forgery attacks"
            )
            
            session_timeout = st.number_input(
                "Session Timeout (seconds)",
                min_value=300,
                max_value=86400,
                value=security_settings.get("session_timeout", 3600)
            )
        
        with col2:
            max_login_attempts = st.number_input(
                "Max Login Attempts",
                min_value=1,
                max_value=20,
                value=security_settings.get("max_login_attempts", 5)
            )
            
            password_min_length = st.number_input(
                "Minimum Password Length",
                min_value=4,
                max_value=50,
                value=security_settings.get("password_min_length", 8)
            )
        
        # Update settings
        self.settings["security"] = {
            "enable_csrf": enable_csrf,
            "session_timeout": session_timeout,
            "max_login_attempts": max_login_attempts,
            "password_min_length": password_min_length
        }
    
    def render_analytics_settings(self):
        """Render analytics configuration settings"""
        st.write("### 📊 Analytics Settings")
        
        analytics_settings = self.settings.get("analytics", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            track_submissions = st.checkbox(
                "Track Form Submissions",
                value=analytics_settings.get("track_form_submissions", True)
            )
            
            track_webhooks = st.checkbox(
                "Track Webhook Calls",
                value=analytics_settings.get("track_webhook_calls", True)
            )
        
        with col2:
            retention_days = st.number_input(
                "Data Retention (days)",
                min_value=1,
                max_value=365,
                value=analytics_settings.get("retention_days", 90)
            )
            
            export_format = st.selectbox(
                "Export Format",
                ["json", "csv", "xlsx"],
                index=["json", "csv", "xlsx"].index(analytics_settings.get("export_format", "json"))
            )
        
        # Update settings
        self.settings["analytics"] = {
            "track_form_submissions": track_submissions,
            "track_webhook_calls": track_webhooks,
            "retention_days": retention_days,
            "export_format": export_format
        }
    
    def render_ui_settings(self):
        """Render UI/UX configuration settings"""
        st.write("### 🎨 UI/UX Settings")
        
        ui_settings = self.settings.get("ui", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            sidebar_expanded = st.checkbox(
                "Sidebar Expanded by Default",
                value=ui_settings.get("sidebar_expanded", True)
            )
            
            show_tooltips = st.checkbox(
                "Show Tooltips",
                value=ui_settings.get("show_tooltips", True)
            )
        
        with col2:
            animation_enabled = st.checkbox(
                "Enable Animations",
                value=ui_settings.get("animation_enabled", True)
            )
            
            compact_mode = st.checkbox(
                "Compact Mode",
                value=ui_settings.get("compact_mode", False)
            )
        
        # Theme selection
        theme = st.selectbox(
            "Theme",
            ["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(ui_settings.get("theme", "light"))
        )
        
        # Update settings
        self.settings["ui"] = {
            "sidebar_expanded": sidebar_expanded,
            "show_tooltips": show_tooltips,
            "animation_enabled": animation_enabled,
            "compact_mode": compact_mode,
            "theme": theme
        }
    
    def render_integration_settings(self):
        """Render integration configuration settings"""
        st.write("### 📱 Integration Settings")
        
        integration_settings = self.settings.get("integrations", {})
        
        # n8n Integration
        st.write("#### n8n Integration")
        col1, col2 = st.columns(2)
        
        with col1:
            n8n_base_url = st.text_input(
                "n8n Base URL",
                value=integration_settings.get("n8n_base_url", ""),
                placeholder="https://your-n8n-instance.com"
            )
        
        with col2:
            api_key = st.text_input(
                "API Key",
                value=integration_settings.get("api_key", ""),
                type="password",
                placeholder="Your n8n API key"
            )
        
        # Slack Integration
        st.write("#### Slack Integration")
        slack_webhook = st.text_input(
            "Slack Webhook URL",
            value=integration_settings.get("slack_webhook", ""),
            placeholder="https://hooks.slack.com/services/..."
        )
        
        # Email Integration
        st.write("#### Email Integration")
        email_service = st.selectbox(
            "Email Service",
            ["smtp", "sendgrid", "mailgun", "ses"],
            index=["smtp", "sendgrid", "mailgun", "ses"].index(integration_settings.get("email_service", "smtp"))
        )
        
        if email_service == "smtp":
            smtp_settings = integration_settings.get("smtp_settings", {})
            
            col1, col2 = st.columns(2)
            with col1:
                smtp_host = st.text_input("SMTP Host", value=smtp_settings.get("host", ""))
                smtp_username = st.text_input("Username", value=smtp_settings.get("username", ""))
                smtp_use_tls = st.checkbox("Use TLS", value=smtp_settings.get("use_tls", True))
            
            with col2:
                smtp_port = st.number_input("Port", min_value=1, max_value=65535, value=smtp_settings.get("port", 587))
                smtp_password = st.text_input("Password", value=smtp_settings.get("password", ""), type="password")
            
            integration_settings["smtp_settings"] = {
                "host": smtp_host,
                "port": smtp_port,
                "username": smtp_username,
                "password": smtp_password,
                "use_tls": smtp_use_tls
            }
        
        # Update settings
        self.settings["integrations"] = {
            **integration_settings,
            "n8n_base_url": n8n_base_url,
            "api_key": api_key,
            "slack_webhook": slack_webhook,
            "email_service": email_service
        }
    
    def export_settings(self):
        """Export all settings and data"""
        try:
            # Create a zip file with all data
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add settings
                zip_file.writestr("settings.json", json.dumps(self.settings, indent=2))
                
                # Add other data files if they exist
                data_files = ["webhooks.json", "custom_forms.json", "business_models.json"]
                for file_name in data_files:
                    file_path = f"data/{file_name}"
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            zip_file.writestr(file_name, f.read())
            
            zip_buffer.seek(0)
            
            # Offer download
            st.download_button(
                label="📥 Download Settings Backup",
                data=zip_buffer.getvalue(),
                file_name=f"n8n_business_suite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
        except Exception as e:
            st.error(f"Error exporting settings: {e}")
    
    def import_settings(self, uploaded_file):
        """Import settings from uploaded file"""
        try:
            if uploaded_file.name.endswith('.json'):
                # Single JSON file
                settings_data = json.load(uploaded_file)
                self.settings = settings_data
                self.save_settings()
                st.success("✅ Settings imported successfully!")
                st.rerun()
            
            elif uploaded_file.name.endswith('.zip'):
                # Zip file with multiple data files
                with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
                    # Extract settings
                    if 'settings.json' in zip_file.namelist():
                        settings_content = zip_file.read('settings.json')
                        self.settings = json.loads(settings_content)
                        self.save_settings()
                    
                    # Extract other data files
                    for file_name in zip_file.namelist():
                        if file_name.endswith('.json') and file_name != 'settings.json':
                            content = zip_file.read(file_name)
                            with open(f"data/{file_name}", 'w') as f:
                                f.write(content.decode('utf-8'))
                
                st.success("✅ Complete backup imported successfully!")
                st.rerun()
            
            else:
                st.error("Please upload a JSON or ZIP file")
                
        except Exception as e:
            st.error(f"Error importing settings: {e}")
    
    def get_setting(self, category: str, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(category, {}).get(key, default)
    
    def update_setting(self, category: str, key: str, value: Any):
        """Update a specific setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()

