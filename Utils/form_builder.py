import streamlit as st
import json
from datetime import datetime, date
from typing import Dict, List, Any, Union
import os

class FormBuilder:
    def __init__(self):
        self.forms_file = "data/custom_forms.json"
        self.ensure_data_dir()
        self.load_forms()
        self.field_types = {
            "text": "Text Input",
            "email": "Email Input",
            "number": "Number Input",
            "textarea": "Text Area",
            "select": "Select Dropdown",
            "multiselect": "Multi-Select",
            "checkbox": "Checkbox",
            "radio": "Radio Buttons",
            "date": "Date Picker",
            "time": "Time Picker",
            "file": "File Upload",
            "slider": "Slider",
            "color": "Color Picker"
        }
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_forms(self):
        """Load custom forms from file"""
        try:
            if os.path.exists(self.forms_file):
                with open(self.forms_file, 'r') as f:
                    self.custom_forms = json.load(f)
            else:
                self.custom_forms = self.get_default_forms()
                self.save_forms()
        except Exception as e:
            st.error(f"Error loading forms: {e}")
            self.custom_forms = self.get_default_forms()
    
    def save_forms(self):
        """Save custom forms to file"""
        try:
            with open(self.forms_file, 'w') as f:
                json.dump(self.custom_forms, f, indent=2)
        except Exception as e:
            st.error(f"Error saving forms: {e}")
    
    def get_default_forms(self) -> Dict:
        """Get default form templates"""
        return {
            "contact_form": {
                "name": "Contact Form",
                "description": "Basic contact form for lead capture",
                "fields": [
                    {"name": "full_name", "label": "Full Name", "type": "text", "required": True},
                    {"name": "email", "label": "Email Address", "type": "email", "required": True},
                    {"name": "phone", "label": "Phone Number", "type": "text", "required": False},
                    {"name": "company", "label": "Company", "type": "text", "required": False},
                    {"name": "message", "label": "Message", "type": "textarea", "required": True}
                ],
                "webhook_key": "lead_capture"
            },
            "feedback_form": {
                "name": "Customer Feedback Form",
                "description": "Collect customer feedback and ratings",
                "fields": [
                    {"name": "customer_name", "label": "Your Name", "type": "text", "required": True},
                    {"name": "email", "label": "Email", "type": "email", "required": True},
                    {"name": "rating", "label": "Overall Rating", "type": "slider", "min_value": 1, "max_value": 5, "required": True},
                    {"name": "product", "label": "Product/Service", "type": "select", "options": ["Product A", "Product B", "Service X", "Service Y"], "required": True},
                    {"name": "feedback", "label": "Your Feedback", "type": "textarea", "required": True},
                    {"name": "recommend", "label": "Would you recommend us?", "type": "radio", "options": ["Yes", "No", "Maybe"], "required": True}
                ],
                "webhook_key": "customer_feedback"
            },
            "booking_form": {
                "name": "Appointment Booking Form",
                "description": "Schedule appointments and consultations",
                "fields": [
                    {"name": "client_name", "label": "Full Name", "type": "text", "required": True},
                    {"name": "email", "label": "Email", "type": "email", "required": True},
                    {"name": "phone", "label": "Phone Number", "type": "text", "required": True},
                    {"name": "service", "label": "Service Type", "type": "select", "options": ["Consultation", "Meeting", "Demo", "Support"], "required": True},
                    {"name": "preferred_date", "label": "Preferred Date", "type": "date", "required": True},
                    {"name": "preferred_time", "label": "Preferred Time", "type": "time", "required": True},
                    {"name": "notes", "label": "Additional Notes", "type": "textarea", "required": False}
                ],
                "webhook_key": "appointment_booking"
            }
        }
    
    def create_field(self, field_config: Dict, form_key: str) -> Any:
        """Create a form field based on configuration"""
        field_name = field_config.get("name", "field")
        field_label = field_config.get("label", "Field")
        field_type = field_config.get("type", "text")
        required = field_config.get("required", False)
        key = f"{form_key}_{field_name}"
        
        # Add required indicator to label
        if required:
            field_label += " *"
        
        try:
            if field_type == "text":
                return st.text_input(field_label, key=key)
            
            elif field_type == "email":
                return st.text_input(field_label, key=key, placeholder="example@email.com")
            
            elif field_type == "number":
                min_val = field_config.get("min_value", 0)
                max_val = field_config.get("max_value", 100)
                return st.number_input(field_label, min_value=min_val, max_value=max_val, key=key)
            
            elif field_type == "textarea":
                return st.text_area(field_label, key=key)
            
            elif field_type == "select":
                options = field_config.get("options", ["Option 1", "Option 2"])
                return st.selectbox(field_label, options, key=key)
            
            elif field_type == "multiselect":
                options = field_config.get("options", ["Option 1", "Option 2"])
                return st.multiselect(field_label, options, key=key)
            
            elif field_type == "checkbox":
                return st.checkbox(field_label, key=key)
            
            elif field_type == "radio":
                options = field_config.get("options", ["Yes", "No"])
                return st.radio(field_label, options, key=key)
            
            elif field_type == "date":
                return st.date_input(field_label, key=key)
            
            elif field_type == "time":
                return st.time_input(field_label, key=key)
            
            elif field_type == "file":
                file_types = field_config.get("file_types", ["pdf", "jpg", "png"])
                return st.file_uploader(field_label, type=file_types, key=key)
            
            elif field_type == "slider":
                min_val = field_config.get("min_value", 0)
                max_val = field_config.get("max_value", 100)
                return st.slider(field_label, min_value=min_val, max_value=max_val, key=key)
            
            elif field_type == "color":
                return st.color_picker(field_label, key=key)
            
            else:
                return st.text_input(field_label, key=key)
                
        except Exception as e:
            st.error(f"Error creating field {field_name}: {e}")
            return None
    
    def render_form(self, form_key: str, webhook_manager=None) -> Dict:
        """Render a complete form"""
        if form_key not in self.custom_forms:
            st.error(f"Form '{form_key}' not found")
            return {}
        
        form_config = self.custom_forms[form_key]
        form_name = form_config.get("name", "Custom Form")
        form_description = form_config.get("description", "")
        fields = form_config.get("fields", [])
        webhook_key = form_config.get("webhook_key", "")
        
        st.subheader(f"📝 {form_name}")
        if form_description:
            st.write(form_description)
        
        # Create form
        with st.form(f"form_{form_key}"):
            form_data = {}
            files_data = {}
            
            # Create columns for better layout
            if len(fields) > 4:
                col1, col2 = st.columns(2)
                for i, field in enumerate(fields):
                    with col1 if i % 2 == 0 else col2:
                        value = self.create_field(field, form_key)
                        field_name = field.get("name", f"field_{i}")
                        
                        if field.get("type") == "file" and value:
                            files_data[field_name] = value
                        else:
                            form_data[field_name] = value
            else:
                for field in fields:
                    value = self.create_field(field, form_key)
                    field_name = field.get("name", f"field_{len(form_data)}")
                    
                    if field.get("type") == "file" and value:
                        files_data[field_name] = value
                    else:
                        form_data[field_name] = value
            
            # Submit button
            submitted = st.form_submit_button(f"Submit {form_name}")
            
            if submitted:
                # Validate required fields
                validation_errors = []
                for field in fields:
                    if field.get("required", False):
                        field_name = field.get("name")
                        if field_name in form_data:
                            value = form_data[field_name]
                            if not value or (isinstance(value, str) and not value.strip()):
                                validation_errors.append(f"{field.get('label', field_name)} is required")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return {}
                
                # Add metadata
                form_data.update({
                    "form_key": form_key,
                    "form_name": form_name,
                    "timestamp": datetime.now().isoformat(),
                    "source": "n8n_business_suite"
                })
                
                # Send to webhook if configured
                if webhook_manager and webhook_key:
                    # Prepare files for webhook
                    webhook_files = {}
                    for field_name, file_obj in files_data.items():
                        if file_obj:
                            webhook_files[field_name] = (file_obj.name, file_obj.getvalue(), file_obj.type)
                    
                    result = webhook_manager.send_to_webhook(webhook_key, form_data, webhook_files)
                    
                    if result.get("success"):
                        st.success("✅ Form submitted successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Failed to submit form: {result.get('error', 'Unknown error')}")
                else:
                    st.success("✅ Form data collected successfully!")
                    st.json(form_data)
                
                return form_data
        
        return {}
    
    def render_form_builder(self):
        """Render the form builder interface"""
        st.subheader("🛠️ Form Builder")
        
        tab1, tab2, tab3 = st.tabs(["Existing Forms", "Create New", "Edit Form"])
        
        with tab1:
            st.write("### Your Forms")
            for form_key, form_config in self.custom_forms.items():
                with st.expander(f"📝 {form_config.get('name', form_key)}"):
                    st.write(f"**Description:** {form_config.get('description', 'No description')}")
                    st.write(f"**Fields:** {len(form_config.get('fields', []))}")
                    st.write(f"**Webhook:** {form_config.get('webhook_key', 'None')}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"Preview {form_key}", key=f"preview_{form_key}"):
                            st.session_state[f"preview_form"] = form_key
                    with col2:
                        if st.button(f"Edit {form_key}", key=f"edit_form_{form_key}"):
                            st.session_state[f"edit_form"] = form_key
                    with col3:
                        if st.button(f"Delete {form_key}", key=f"delete_form_{form_key}"):
                            del self.custom_forms[form_key]
                            self.save_forms()
                            st.success(f"Deleted form: {form_key}")
                            st.rerun()
        
        with tab2:
            st.write("### Create New Form")
            self.render_form_creator()
        
        with tab3:
            st.write("### Edit Existing Form")
            if self.custom_forms:
                form_to_edit = st.selectbox(
                    "Select form to edit",
                    options=list(self.custom_forms.keys()),
                    format_func=lambda x: self.custom_forms[x].get('name', x)
                )
                if form_to_edit:
                    self.render_form_editor(form_to_edit)
            else:
                st.info("No forms available to edit. Create a new form first.")
    
    def render_form_creator(self):
        """Render form creation interface"""
        with st.form("create_new_form"):
            form_key = st.text_input("Form Key (unique identifier)", placeholder="my_custom_form")
            form_name = st.text_input("Form Name", placeholder="My Custom Form")
            form_description = st.text_area("Form Description")
            webhook_key = st.text_input("Webhook Key (optional)", placeholder="lead_capture")
            
            st.write("### Form Fields")
            
            # Initialize fields in session state
            if 'new_form_fields' not in st.session_state:
                st.session_state.new_form_fields = []
            
            # Display existing fields
            for i, field in enumerate(st.session_state.new_form_fields):
                with st.expander(f"Field {i+1}: {field.get('label', 'Unnamed')}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Type:** {self.field_types.get(field.get('type', 'text'), 'Text Input')}")
                        st.write(f"**Required:** {'Yes' if field.get('required') else 'No'}")
                    with col2:
                        if st.button(f"Remove", key=f"remove_field_{i}"):
                            st.session_state.new_form_fields.pop(i)
                            st.rerun()
            
            # Add new field button
            if st.button("➕ Add Field"):
                st.session_state.show_field_creator = True
            
            # Field creator
            if st.session_state.get('show_field_creator', False):
                st.write("#### Add New Field")
                field_name = st.text_input("Field Name", placeholder="field_name")
                field_label = st.text_input("Field Label", placeholder="Field Label")
                field_type = st.selectbox("Field Type", options=list(self.field_types.keys()), format_func=lambda x: self.field_types[x])
                field_required = st.checkbox("Required Field")
                
                # Additional options based on field type
                field_options = {}
                if field_type in ["select", "multiselect", "radio"]:
                    options_text = st.text_input("Options (comma-separated)", placeholder="Option 1, Option 2, Option 3")
                    if options_text:
                        field_options["options"] = [opt.strip() for opt in options_text.split(",")]
                
                elif field_type in ["number", "slider"]:
                    col1, col2 = st.columns(2)
                    with col1:
                        field_options["min_value"] = st.number_input("Min Value", value=0)
                    with col2:
                        field_options["max_value"] = st.number_input("Max Value", value=100)
                
                elif field_type == "file":
                    file_types_text = st.text_input("Allowed File Types (comma-separated)", placeholder="pdf, jpg, png")
                    if file_types_text:
                        field_options["file_types"] = [ft.strip() for ft in file_types_text.split(",")]
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Add Field to Form"):
                        if field_name and field_label:
                            new_field = {
                                "name": field_name,
                                "label": field_label,
                                "type": field_type,
                                "required": field_required,
                                **field_options
                            }
                            st.session_state.new_form_fields.append(new_field)
                            st.session_state.show_field_creator = False
                            st.rerun()
                        else:
                            st.error("Please provide field name and label")
                
                with col2:
                    if st.button("Cancel"):
                        st.session_state.show_field_creator = False
                        st.rerun()
            
            # Submit form
            if st.form_submit_button("Create Form"):
                if form_key and form_name and st.session_state.new_form_fields:
                    new_form = {
                        "name": form_name,
                        "description": form_description,
                        "fields": st.session_state.new_form_fields,
                        "webhook_key": webhook_key if webhook_key else ""
                    }
                    
                    self.custom_forms[form_key] = new_form
                    self.save_forms()
                    
                    # Clear session state
                    st.session_state.new_form_fields = []
                    st.session_state.show_field_creator = False
                    
                    st.success(f"✅ Created form: {form_name}")
                    st.rerun()
                else:
                    st.error("Please provide form key, name, and at least one field")
    
    def render_form_editor(self, form_key: str):
        """Render form editing interface"""
        if form_key not in self.custom_forms:
            st.error("Form not found")
            return
        
        form_config = self.custom_forms[form_key]
        
        with st.form(f"edit_form_{form_key}"):
            form_name = st.text_input("Form Name", value=form_config.get('name', ''))
            form_description = st.text_area("Form Description", value=form_config.get('description', ''))
            webhook_key = st.text_input("Webhook Key", value=form_config.get('webhook_key', ''))
            
            st.write("### Current Fields")
            for i, field in enumerate(form_config.get('fields', [])):
                st.write(f"**{i+1}.** {field.get('label', 'Unnamed')} ({self.field_types.get(field.get('type', 'text'), 'Text')})")
            
            if st.form_submit_button("Update Form"):
                self.custom_forms[form_key].update({
                    "name": form_name,
                    "description": form_description,
                    "webhook_key": webhook_key
                })
                self.save_forms()
                st.success("✅ Form updated successfully!")
                st.rerun()

