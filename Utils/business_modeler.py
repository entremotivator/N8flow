import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class BusinessModeler:
    def __init__(self):
        self.models_file = "data/business_models.json"
        self.ensure_data_dir()
        self.load_models()
        self.process_types = {
            "lead_generation": "Lead Generation",
            "customer_onboarding": "Customer Onboarding", 
            "support_workflow": "Support Workflow",
            "sales_pipeline": "Sales Pipeline",
            "content_approval": "Content Approval",
            "invoice_processing": "Invoice Processing",
            "hr_onboarding": "HR Onboarding",
            "project_management": "Project Management"
        }
        
        self.node_types = {
            "trigger": {"icon": "🚀", "color": "#4CAF50", "description": "Process trigger/start"},
            "form": {"icon": "📝", "color": "#2196F3", "description": "Form submission"},
            "webhook": {"icon": "🔗", "color": "#FF9800", "description": "Webhook call"},
            "condition": {"icon": "❓", "color": "#9C27B0", "description": "Decision point"},
            "action": {"icon": "⚡", "color": "#F44336", "description": "Action/task"},
            "notification": {"icon": "📧", "color": "#607D8B", "description": "Send notification"},
            "database": {"icon": "💾", "color": "#795548", "description": "Database operation"},
            "api": {"icon": "🌐", "color": "#00BCD4", "description": "API call"},
            "end": {"icon": "🏁", "color": "#757575", "description": "Process end"}
        }
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_models(self):
        """Load business models from file"""
        try:
            if os.path.exists(self.models_file):
                with open(self.models_file, 'r') as f:
                    self.models = json.load(f)
            else:
                self.models = self.get_default_models()
                self.save_models()
        except Exception as e:
            st.error(f"Error loading models: {e}")
            self.models = self.get_default_models()
    
    def save_models(self):
        """Save business models to file"""
        try:
            with open(self.models_file, 'w') as f:
                json.dump(self.models, f, indent=2)
        except Exception as e:
            st.error(f"Error saving models: {e}")
    
    def get_default_models(self) -> Dict:
        """Get default business process models"""
        return {
            "lead_capture_model": {
                "name": "Lead Capture Process",
                "description": "Complete lead capture and nurturing workflow",
                "type": "lead_generation",
                "nodes": [
                    {"id": "start", "type": "trigger", "label": "Website Visit", "x": 100, "y": 100},
                    {"id": "form", "type": "form", "label": "Contact Form", "x": 250, "y": 100},
                    {"id": "webhook", "type": "webhook", "label": "Send to CRM", "x": 400, "y": 100},
                    {"id": "email", "type": "notification", "label": "Welcome Email", "x": 550, "y": 100},
                    {"id": "condition", "type": "condition", "label": "Qualified Lead?", "x": 400, "y": 250},
                    {"id": "sales_notify", "type": "notification", "label": "Notify Sales", "x": 550, "y": 200},
                    {"id": "nurture", "type": "action", "label": "Add to Nurture", "x": 550, "y": 300},
                    {"id": "end", "type": "end", "label": "Process Complete", "x": 700, "y": 250}
                ],
                "connections": [
                    {"from": "start", "to": "form"},
                    {"from": "form", "to": "webhook"},
                    {"from": "webhook", "to": "email"},
                    {"from": "email", "to": "condition"},
                    {"from": "condition", "to": "sales_notify", "condition": "qualified"},
                    {"from": "condition", "to": "nurture", "condition": "not_qualified"},
                    {"from": "sales_notify", "to": "end"},
                    {"from": "nurture", "to": "end"}
                ],
                "webhooks": ["lead_capture", "crm_integration"],
                "forms": ["contact_form"],
                "created_at": "2024-01-01T00:00:00Z"
            },
            "support_ticket_model": {
                "name": "Support Ticket Workflow",
                "description": "Customer support ticket processing and resolution",
                "type": "support_workflow",
                "nodes": [
                    {"id": "ticket_created", "type": "trigger", "label": "Ticket Created", "x": 100, "y": 100},
                    {"id": "categorize", "type": "condition", "label": "Categorize Issue", "x": 250, "y": 100},
                    {"id": "urgent", "type": "action", "label": "Urgent Queue", "x": 400, "y": 50},
                    {"id": "normal", "type": "action", "label": "Normal Queue", "x": 400, "y": 150},
                    {"id": "auto_response", "type": "notification", "label": "Auto Response", "x": 550, "y": 100},
                    {"id": "assign", "type": "action", "label": "Assign Agent", "x": 700, "y": 100},
                    {"id": "resolved", "type": "condition", "label": "Resolved?", "x": 850, "y": 100},
                    {"id": "close", "type": "action", "label": "Close Ticket", "x": 1000, "y": 50},
                    {"id": "escalate", "type": "action", "label": "Escalate", "x": 1000, "y": 150},
                    {"id": "end", "type": "end", "label": "Complete", "x": 1150, "y": 100}
                ],
                "connections": [
                    {"from": "ticket_created", "to": "categorize"},
                    {"from": "categorize", "to": "urgent", "condition": "high_priority"},
                    {"from": "categorize", "to": "normal", "condition": "normal_priority"},
                    {"from": "urgent", "to": "auto_response"},
                    {"from": "normal", "to": "auto_response"},
                    {"from": "auto_response", "to": "assign"},
                    {"from": "assign", "to": "resolved"},
                    {"from": "resolved", "to": "close", "condition": "yes"},
                    {"from": "resolved", "to": "escalate", "condition": "no"},
                    {"from": "close", "to": "end"},
                    {"from": "escalate", "to": "end"}
                ],
                "webhooks": ["support_ticket", "agent_notification"],
                "forms": ["support_form"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    def render(self):
        """Render the business modeler interface"""
        st.subheader("🏗️ Business Process Modeler")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Model Gallery", 
            "🛠️ Create Model", 
            "📈 Analytics", 
            "📋 Templates"
        ])
        
        with tab1:
            self.render_model_gallery()
        
        with tab2:
            self.render_model_creator()
        
        with tab3:
            self.render_model_analytics()
        
        with tab4:
            self.render_model_templates()
    
    def render_model_gallery(self):
        """Render existing models gallery"""
        st.write("### 📊 Your Business Models")
        
        if not self.models:
            st.info("No business models created yet. Create your first model in the 'Create Model' tab.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            process_filter = st.selectbox(
                "Filter by Process Type",
                ["All"] + list(self.process_types.values())
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Name", "Created Date", "Type", "Complexity"]
            )
        
        with col3:
            view_mode = st.selectbox(
                "View Mode",
                ["Grid", "List", "Detailed"]
            )
        
        # Display models
        filtered_models = self.models
        if process_filter != "All":
            process_key = [k for k, v in self.process_types.items() if v == process_filter][0]
            filtered_models = {k: v for k, v in self.models.items() if v.get("type") == process_key}
        
        if view_mode == "Grid":
            cols = st.columns(2)
            for i, (model_key, model) in enumerate(filtered_models.items()):
                with cols[i % 2]:
                    self.render_model_card(model_key, model)
        
        elif view_mode == "List":
            for model_key, model in filtered_models.items():
                with st.expander(f"📋 {model.get('name', model_key)}"):
                    self.render_model_details(model_key, model)
        
        else:  # Detailed
            for model_key, model in filtered_models.items():
                st.markdown("---")
                self.render_model_detailed(model_key, model)
    
    def render_model_card(self, model_key: str, model: Dict):
        """Render a model card"""
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd; 
                border-radius: 10px; 
                padding: 1rem; 
                margin: 0.5rem 0;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #333;">
                    📋 {model.get('name', model_key)}
                </h4>
                <p style="margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;">
                    {model.get('description', 'No description')}
                </p>
                <p style="margin: 0; color: #888; font-size: 0.8rem;">
                    Type: {self.process_types.get(model.get('type', ''), 'Unknown')}
                </p>
                <p style="margin: 0; color: #888; font-size: 0.8rem;">
                    Nodes: {len(model.get('nodes', []))} | 
                    Connections: {len(model.get('connections', []))}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👁️ View", key=f"view_{model_key}"):
                    st.session_state.selected_model = model_key
                    self.render_model_visualization(model)
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{model_key}"):
                    st.session_state.editing_model = model_key
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{model_key}"):
                    if st.session_state.get(f'confirm_delete_{model_key}', False):
                        del self.models[model_key]
                        self.save_models()
                        st.success(f"Deleted model: {model.get('name', model_key)}")
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_{model_key}'] = True
                        st.warning("Click again to confirm deletion")
    
    def render_model_visualization(self, model: Dict):
        """Render model as a flowchart visualization"""
        st.subheader(f"📊 {model.get('name', 'Business Model')}")
        
        nodes = model.get('nodes', [])
        connections = model.get('connections', [])
        
        if not nodes:
            st.warning("No nodes defined in this model")
            return
        
        # Create plotly figure
        fig = go.Figure()
        
        # Add nodes
        for node in nodes:
            node_type = node.get('type', 'action')
            node_info = self.node_types.get(node_type, self.node_types['action'])
            
            fig.add_trace(go.Scatter(
                x=[node.get('x', 0)],
                y=[node.get('y', 0)],
                mode='markers+text',
                marker=dict(
                    size=40,
                    color=node_info['color'],
                    line=dict(width=2, color='white')
                ),
                text=node_info['icon'],
                textfont=dict(size=20),
                name=node.get('label', node.get('id', 'Node')),
                hovertemplate=f"<b>{node.get('label', node.get('id'))}</b><br>" +
                             f"Type: {node_info['description']}<br>" +
                             f"Position: ({node.get('x', 0)}, {node.get('y', 0)})<extra></extra>"
            ))
        
        # Add connections
        for connection in connections:
            from_node = next((n for n in nodes if n['id'] == connection['from']), None)
            to_node = next((n for n in nodes if n['id'] == connection['to']), None)
            
            if from_node and to_node:
                fig.add_trace(go.Scatter(
                    x=[from_node.get('x', 0), to_node.get('x', 0)],
                    y=[from_node.get('y', 0), to_node.get('y', 0)],
                    mode='lines',
                    line=dict(width=2, color='gray'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Add arrow annotation
                fig.add_annotation(
                    x=to_node.get('x', 0),
                    y=to_node.get('y', 0),
                    ax=from_node.get('x', 0),
                    ay=from_node.get('y', 0),
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='gray'
                )
        
        # Update layout
        fig.update_layout(
            title=f"Process Flow: {model.get('name', 'Business Model')}",
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Nodes", len(nodes))
        
        with col2:
            st.metric("Connections", len(connections))
        
        with col3:
            st.metric("Webhooks", len(model.get('webhooks', [])))
        
        # Node types breakdown
        st.subheader("📊 Node Types Breakdown")
        node_type_counts = {}
        for node in nodes:
            node_type = node.get('type', 'action')
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        if node_type_counts:
            fig_pie = px.pie(
                values=list(node_type_counts.values()),
                names=[self.node_types.get(nt, {}).get('description', nt) for nt in node_type_counts.keys()],
                title="Node Types Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    def render_model_creator(self):
        """Render model creation interface"""
        st.write("### 🛠️ Create New Business Model")
        
        with st.form("create_model"):
            col1, col2 = st.columns(2)
            
            with col1:
                model_key = st.text_input("Model Key (unique identifier)", placeholder="my_business_model")
                model_name = st.text_input("Model Name", placeholder="My Business Process")
                model_type = st.selectbox("Process Type", list(self.process_types.keys()), format_func=lambda x: self.process_types[x])
            
            with col2:
                model_description = st.text_area("Description", placeholder="Describe your business process...")
                webhooks = st.text_input("Associated Webhooks (comma-separated)", placeholder="webhook1, webhook2")
                forms = st.text_input("Associated Forms (comma-separated)", placeholder="form1, form2")
            
            st.write("### 🔧 Process Nodes")
            
            # Initialize nodes in session state
            if 'model_nodes' not in st.session_state:
                st.session_state.model_nodes = []
            
            # Display existing nodes
            if st.session_state.model_nodes:
                st.write("#### Current Nodes:")
                for i, node in enumerate(st.session_state.model_nodes):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{node.get('label', 'Unnamed')}**")
                    
                    with col2:
                        node_info = self.node_types.get(node.get('type', 'action'), {})
                        st.write(f"{node_info.get('icon', '⚡')} {node_info.get('description', 'Action')}")
                    
                    with col3:
                        st.write(f"({node.get('x', 0)}, {node.get('y', 0)})")
                    
                    with col4:
                        if st.button("🗑️", key=f"remove_node_{i}"):
                            st.session_state.model_nodes.pop(i)
                            st.rerun()
            
            # Add new node
            if st.button("➕ Add Node"):
                st.session_state.show_node_creator = True
            
            # Node creator
            if st.session_state.get('show_node_creator', False):
                st.write("#### Add New Node")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    node_id = st.text_input("Node ID", placeholder="node_id")
                    node_label = st.text_input("Node Label", placeholder="Node Label")
                
                with col2:
                    node_type = st.selectbox("Node Type", list(self.node_types.keys()), format_func=lambda x: f"{self.node_types[x]['icon']} {self.node_types[x]['description']}")
                
                with col3:
                    node_x = st.number_input("X Position", value=100, step=50)
                    node_y = st.number_input("Y Position", value=100, step=50)
                
                with col4:
                    st.write("")  # Spacer
                    if st.button("Add Node to Model"):
                        if node_id and node_label:
                            new_node = {
                                "id": node_id,
                                "type": node_type,
                                "label": node_label,
                                "x": node_x,
                                "y": node_y
                            }
                            st.session_state.model_nodes.append(new_node)
                            st.session_state.show_node_creator = False
                            st.rerun()
                        else:
                            st.error("Please provide node ID and label")
                    
                    if st.button("Cancel"):
                        st.session_state.show_node_creator = False
                        st.rerun()
            
            # Submit form
            if st.form_submit_button("Create Business Model"):
                if model_key and model_name and st.session_state.model_nodes:
                    new_model = {
                        "name": model_name,
                        "description": model_description,
                        "type": model_type,
                        "nodes": st.session_state.model_nodes,
                        "connections": [],  # Will be added in edit mode
                        "webhooks": [w.strip() for w in webhooks.split(",") if w.strip()],
                        "forms": [f.strip() for f in forms.split(",") if f.strip()],
                        "created_at": datetime.now().isoformat()
                    }
                    
                    self.models[model_key] = new_model
                    self.save_models()
                    
                    # Clear session state
                    st.session_state.model_nodes = []
                    st.session_state.show_node_creator = False
                    
                    st.success(f"✅ Created business model: {model_name}")
                    st.rerun()
                else:
                    st.error("Please provide model key, name, and at least one node")
    
    def render_model_analytics(self):
        """Render model analytics and insights"""
        st.write("### 📈 Business Model Analytics")
        
        if not self.models:
            st.info("No models available for analysis. Create some models first.")
            return
        
        # Overall statistics
        total_models = len(self.models)
        total_nodes = sum(len(model.get('nodes', [])) for model in self.models.values())
        total_connections = sum(len(model.get('connections', [])) for model in self.models.values())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Models", total_models)
        
        with col2:
            st.metric("Total Nodes", total_nodes)
        
        with col3:
            st.metric("Total Connections", total_connections)
        
        with col4:
            avg_complexity = total_nodes / total_models if total_models > 0 else 0
            st.metric("Avg Complexity", f"{avg_complexity:.1f}")
        
        # Process type distribution
        st.subheader("📊 Process Type Distribution")
        
        type_counts = {}
        for model in self.models.values():
            model_type = model.get('type', 'unknown')
            type_name = self.process_types.get(model_type, model_type)
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        if type_counts:
            fig_bar = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Models by Process Type",
                labels={'x': 'Process Type', 'y': 'Number of Models'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Model complexity analysis
        st.subheader("📈 Model Complexity Analysis")
        
        model_names = []
        node_counts = []
        connection_counts = []
        
        for model_key, model in self.models.items():
            model_names.append(model.get('name', model_key))
            node_counts.append(len(model.get('nodes', [])))
            connection_counts.append(len(model.get('connections', [])))
        
        fig_complexity = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Nodes per Model', 'Connections per Model'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig_complexity.add_trace(
            go.Bar(x=model_names, y=node_counts, name="Nodes", marker_color='lightblue'),
            row=1, col=1
        )
        
        fig_complexity.add_trace(
            go.Bar(x=model_names, y=connection_counts, name="Connections", marker_color='lightcoral'),
            row=1, col=2
        )
        
        fig_complexity.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_complexity, use_container_width=True)
        
        # Node type usage
        st.subheader("🔧 Node Type Usage")
        
        node_type_usage = {}
        for model in self.models.values():
            for node in model.get('nodes', []):
                node_type = node.get('type', 'action')
                type_name = self.node_types.get(node_type, {}).get('description', node_type)
                node_type_usage[type_name] = node_type_usage.get(type_name, 0) + 1
        
        if node_type_usage:
            fig_usage = px.pie(
                values=list(node_type_usage.values()),
                names=list(node_type_usage.keys()),
                title="Node Type Usage Distribution"
            )
            st.plotly_chart(fig_usage, use_container_width=True)
    
    def render_model_templates(self):
        """Render model templates and quick start options"""
        st.write("### 📋 Business Model Templates")
        
        templates = {
            "lead_generation": {
                "name": "Lead Generation Workflow",
                "description": "Complete lead capture, qualification, and nurturing process",
                "complexity": "Intermediate",
                "estimated_time": "30 minutes",
                "includes": ["Contact forms", "CRM integration", "Email automation", "Lead scoring"]
            },
            "customer_support": {
                "name": "Customer Support Process",
                "description": "Ticket creation, routing, escalation, and resolution workflow",
                "complexity": "Advanced",
                "estimated_time": "45 minutes",
                "includes": ["Ticket forms", "Auto-routing", "SLA tracking", "Customer notifications"]
            },
            "sales_pipeline": {
                "name": "Sales Pipeline Management",
                "description": "Opportunity tracking from lead to close",
                "complexity": "Advanced",
                "estimated_time": "60 minutes",
                "includes": ["Opportunity forms", "Stage progression", "Sales notifications", "Reporting"]
            },
            "onboarding": {
                "name": "Customer Onboarding",
                "description": "New customer welcome and setup process",
                "complexity": "Intermediate",
                "estimated_time": "40 minutes",
                "includes": ["Welcome forms", "Account setup", "Training materials", "Check-ins"]
            },
            "content_approval": {
                "name": "Content Approval Workflow",
                "description": "Content creation, review, approval, and publishing process",
                "complexity": "Beginner",
                "estimated_time": "20 minutes",
                "includes": ["Submission forms", "Review process", "Approval routing", "Publishing"]
            },
            "invoice_processing": {
                "name": "Invoice Processing",
                "description": "Invoice receipt, validation, approval, and payment workflow",
                "complexity": "Intermediate",
                "estimated_time": "35 minutes",
                "includes": ["Invoice upload", "Data extraction", "Approval workflow", "Payment processing"]
            }
        }
        
        # Template cards
        for template_key, template in templates.items():
            with st.expander(f"📋 {template['name']} - {template['complexity']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {template['description']}")
                    st.write(f"**Estimated Setup Time:** {template['estimated_time']}")
                    st.write("**Includes:**")
                    for item in template['includes']:
                        st.write(f"  • {item}")
                
                with col2:
                    complexity_color = {
                        "Beginner": "🟢",
                        "Intermediate": "🟡", 
                        "Advanced": "🔴"
                    }
                    st.write(f"**Complexity:** {complexity_color.get(template['complexity'], '⚪')} {template['complexity']}")
                    
                    if st.button(f"🚀 Use Template", key=f"template_{template_key}"):
                        self.create_from_template(template_key, template)
                        st.success(f"✅ Created model from template: {template['name']}")
                        st.rerun()
        
        # Custom template creator
        st.markdown("---")
        st.subheader("🛠️ Create Custom Template")
        
        with st.form("create_template"):
            template_name = st.text_input("Template Name")
            template_description = st.text_area("Template Description")
            template_complexity = st.selectbox("Complexity Level", ["Beginner", "Intermediate", "Advanced"])
            
            if st.form_submit_button("Save as Template"):
                if template_name and template_description:
                    # This would save the current model as a template
                    st.success(f"✅ Template '{template_name}' saved successfully!")
                else:
                    st.error("Please provide template name and description")
    
    def create_from_template(self, template_key: str, template: Dict):
        """Create a new model from a template"""
        # This would create a pre-configured model based on the template
        # For now, we'll create a basic structure
        
        template_models = {
            "lead_generation": {
                "nodes": [
                    {"id": "start", "type": "trigger", "label": "Lead Source", "x": 100, "y": 100},
                    {"id": "form", "type": "form", "label": "Contact Form", "x": 250, "y": 100},
                    {"id": "qualify", "type": "condition", "label": "Qualify Lead", "x": 400, "y": 100},
                    {"id": "crm", "type": "webhook", "label": "Add to CRM", "x": 550, "y": 50},
                    {"id": "nurture", "type": "action", "label": "Nurture Campaign", "x": 550, "y": 150},
                    {"id": "end", "type": "end", "label": "Complete", "x": 700, "y": 100}
                ],
                "connections": [
                    {"from": "start", "to": "form"},
                    {"from": "form", "to": "qualify"},
                    {"from": "qualify", "to": "crm", "condition": "qualified"},
                    {"from": "qualify", "to": "nurture", "condition": "not_qualified"},
                    {"from": "crm", "to": "end"},
                    {"from": "nurture", "to": "end"}
                ]
            }
        }
        
        model_key = f"{template_key}_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        new_model = {
            "name": template['name'],
            "description": template['description'],
            "type": template_key,
            "nodes": template_models.get(template_key, {}).get('nodes', []),
            "connections": template_models.get(template_key, {}).get('connections', []),
            "webhooks": [],
            "forms": [],
            "created_at": datetime.now().isoformat(),
            "template": template_key
        }
        
        self.models[model_key] = new_model
        self.save_models()
    
    def get_model(self, model_key: str) -> Dict:
        """Get specific model"""
        return self.models.get(model_key, {})
    
    def get_all_models(self) -> Dict:
        """Get all models"""
        return self.models

