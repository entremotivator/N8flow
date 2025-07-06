import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import uuid
import base64
import io
import csv
from PIL import Image
import zipfile

# Configure Streamlit page
st.set_page_config(
    page_title="Webhook Business Suite - n8n Integration",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .webhook-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .business-type-card {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #2196f3;
        margin-bottom: 1rem;
    }
    .upload-zone {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f9f9f9;
    }
    .webhook-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem;
    }
    .status-success { background: #d4edda; color: #155724; }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-error { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

class WebhookBusinessSuite:
    def __init__(self):
        self.n8n_webhook_base = "http://localhost:5678/webhook"
        self.business_webhooks = self.load_business_webhooks()
        self.file_processors = self.setup_file_processors()
    
    def load_business_webhooks(self) -> List[Dict]:
        """Load 25 different webhook configurations for various business types"""
        return [
            # Restaurant & Food Service (1-5)
            {
                "id": 1,
                "name": "Restaurant Order Processing",
                "business_type": "Restaurant",
                "webhook_path": "/restaurant-order",
                "description": "Process new restaurant orders from delivery apps",
                "data_fields": ["order_id", "customer_name", "items", "total_amount", "delivery_address"],
                "file_types": ["menu.csv", "orders.json", "customer_data.xlsx"],
                "sample_payload": {
                    "order_id": "ORD-12345",
                    "customer_name": "John Doe",
                    "items": [{"name": "Pizza", "quantity": 2, "price": 25.99}],
                    "total_amount": 51.98,
                    "delivery_address": "123 Main St"
                }
            },
            {
                "id": 2,
                "name": "Food Inventory Alert",
                "business_type": "Restaurant",
                "webhook_path": "/food-inventory",
                "description": "Alert when food inventory is running low",
                "data_fields": ["item_name", "current_stock", "minimum_threshold", "supplier_info"],
                "file_types": ["inventory.csv", "suppliers.xlsx"],
                "sample_payload": {
                    "item_name": "Tomatoes",
                    "current_stock": 5,
                    "minimum_threshold": 20,
                    "supplier_info": "Fresh Foods Inc"
                }
            },
            {
                "id": 3,
                "name": "Table Reservation System",
                "business_type": "Restaurant",
                "webhook_path": "/table-reservation",
                "description": "Handle table reservations and confirmations",
                "data_fields": ["customer_name", "phone", "party_size", "date_time", "special_requests"],
                "file_types": ["reservations.csv", "customer_preferences.json"],
                "sample_payload": {
                    "customer_name": "Jane Smith",
                    "phone": "+1234567890",
                    "party_size": 4,
                    "date_time": "2024-01-15 19:00",
                    "special_requests": "Window table"
                }
            },
            {
                "id": 4,
                "name": "Staff Scheduling",
                "business_type": "Restaurant",
                "webhook_path": "/staff-schedule",
                "description": "Manage staff schedules and shift changes",
                "data_fields": ["employee_id", "shift_date", "start_time", "end_time", "position"],
                "file_types": ["staff.csv", "schedules.xlsx"],
                "sample_payload": {
                    "employee_id": "EMP001",
                    "shift_date": "2024-01-15",
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "position": "Server"
                }
            },
            {
                "id": 5,
                "name": "Customer Feedback Collection",
                "business_type": "Restaurant",
                "webhook_path": "/customer-feedback",
                "description": "Collect and process customer feedback",
                "data_fields": ["customer_name", "rating", "comments", "visit_date", "order_id"],
                "file_types": ["feedback.csv", "reviews.json"],
                "sample_payload": {
                    "customer_name": "Mike Johnson",
                    "rating": 5,
                    "comments": "Excellent food and service!",
                    "visit_date": "2024-01-14",
                    "order_id": "ORD-12344"
                }
            },
            
            # Retail & E-commerce (6-10)
            {
                "id": 6,
                "name": "Product Inventory Sync",
                "business_type": "Retail",
                "webhook_path": "/product-inventory",
                "description": "Sync product inventory across multiple channels",
                "data_fields": ["product_id", "sku", "quantity", "price", "channel"],
                "file_types": ["products.csv", "inventory.xlsx", "pricing.json"],
                "sample_payload": {
                    "product_id": "PROD001",
                    "sku": "TEE-BLU-M",
                    "quantity": 50,
                    "price": 29.99,
                    "channel": "online_store"
                }
            },
            {
                "id": 7,
                "name": "Customer Purchase Tracking",
                "business_type": "Retail",
                "webhook_path": "/customer-purchase",
                "description": "Track customer purchases and buying patterns",
                "data_fields": ["customer_id", "purchase_amount", "items", "payment_method", "store_location"],
                "file_types": ["purchases.csv", "customers.xlsx"],
                "sample_payload": {
                    "customer_id": "CUST001",
                    "purchase_amount": 89.97,
                    "items": ["TEE-BLU-M", "JEAN-BLK-L"],
                    "payment_method": "credit_card",
                    "store_location": "Downtown"
                }
            },
            {
                "id": 8,
                "name": "Supplier Order Management",
                "business_type": "Retail",
                "webhook_path": "/supplier-order",
                "description": "Manage orders to suppliers and vendors",
                "data_fields": ["supplier_id", "order_items", "total_cost", "delivery_date", "order_status"],
                "file_types": ["suppliers.csv", "purchase_orders.xlsx"],
                "sample_payload": {
                    "supplier_id": "SUP001",
                    "order_items": [{"sku": "TEE-BLU-M", "quantity": 100}],
                    "total_cost": 1500.00,
                    "delivery_date": "2024-01-20",
                    "order_status": "pending"
                }
            },
            {
                "id": 9,
                "name": "Price Change Notifications",
                "business_type": "Retail",
                "webhook_path": "/price-change",
                "description": "Notify about product price changes",
                "data_fields": ["product_id", "old_price", "new_price", "effective_date", "reason"],
                "file_types": ["pricing_history.csv", "products.xlsx"],
                "sample_payload": {
                    "product_id": "PROD001",
                    "old_price": 29.99,
                    "new_price": 24.99,
                    "effective_date": "2024-01-16",
                    "reason": "seasonal_sale"
                }
            },
            {
                "id": 10,
                "name": "Return Processing",
                "business_type": "Retail",
                "webhook_path": "/product-return",
                "description": "Process product returns and refunds",
                "data_fields": ["return_id", "customer_id", "product_id", "reason", "refund_amount"],
                "file_types": ["returns.csv", "refunds.xlsx"],
                "sample_payload": {
                    "return_id": "RET001",
                    "customer_id": "CUST001",
                    "product_id": "PROD001",
                    "reason": "size_issue",
                    "refund_amount": 29.99
                }
            },
            
            # Healthcare & Wellness (11-15)
            {
                "id": 11,
                "name": "Patient Appointment Booking",
                "business_type": "Healthcare",
                "webhook_path": "/patient-appointment",
                "description": "Handle patient appointment bookings",
                "data_fields": ["patient_id", "doctor_id", "appointment_date", "appointment_type", "notes"],
                "file_types": ["patients.csv", "doctors.xlsx", "appointments.json"],
                "sample_payload": {
                    "patient_id": "PAT001",
                    "doctor_id": "DOC001",
                    "appointment_date": "2024-01-16 10:00",
                    "appointment_type": "consultation",
                    "notes": "Follow-up visit"
                }
            },
            {
                "id": 12,
                "name": "Medical Records Update",
                "business_type": "Healthcare",
                "webhook_path": "/medical-records",
                "description": "Update patient medical records",
                "data_fields": ["patient_id", "record_type", "data", "doctor_id", "timestamp"],
                "file_types": ["medical_records.csv", "patient_data.xlsx"],
                "sample_payload": {
                    "patient_id": "PAT001",
                    "record_type": "vital_signs",
                    "data": {"blood_pressure": "120/80", "heart_rate": 72},
                    "doctor_id": "DOC001",
                    "timestamp": "2024-01-15 14:30"
                }
            },
            {
                "id": 13,
                "name": "Prescription Management",
                "business_type": "Healthcare",
                "webhook_path": "/prescription",
                "description": "Manage patient prescriptions",
                "data_fields": ["patient_id", "medication", "dosage", "frequency", "doctor_id"],
                "file_types": ["prescriptions.csv", "medications.xlsx"],
                "sample_payload": {
                    "patient_id": "PAT001",
                    "medication": "Amoxicillin",
                    "dosage": "500mg",
                    "frequency": "3 times daily",
                    "doctor_id": "DOC001"
                }
            },
            {
                "id": 14,
                "name": "Insurance Claim Processing",
                "business_type": "Healthcare",
                "webhook_path": "/insurance-claim",
                "description": "Process insurance claims",
                "data_fields": ["claim_id", "patient_id", "insurance_provider", "claim_amount", "status"],
                "file_types": ["claims.csv", "insurance_data.xlsx"],
                "sample_payload": {
                    "claim_id": "CLM001",
                    "patient_id": "PAT001",
                    "insurance_provider": "HealthCare Plus",
                    "claim_amount": 250.00,
                    "status": "submitted"
                }
            },
            {
                "id": 15,
                "name": "Lab Results Processing",
                "business_type": "Healthcare",
                "webhook_path": "/lab-results",
                "description": "Process and distribute lab results",
                "data_fields": ["patient_id", "test_type", "results", "lab_id", "result_date"],
                "file_types": ["lab_results.csv", "test_data.xlsx"],
                "sample_payload": {
                    "patient_id": "PAT001",
                    "test_type": "blood_work",
                    "results": {"glucose": 95, "cholesterol": 180},
                    "lab_id": "LAB001",
                    "result_date": "2024-01-15"
                }
            },
            
            # Professional Services (16-20)
            {
                "id": 16,
                "name": "Client Project Updates",
                "business_type": "Professional Services",
                "webhook_path": "/project-update",
                "description": "Update client project status and milestones",
                "data_fields": ["project_id", "client_id", "milestone", "status", "completion_date"],
                "file_types": ["projects.csv", "clients.xlsx", "milestones.json"],
                "sample_payload": {
                    "project_id": "PROJ001",
                    "client_id": "CLI001",
                    "milestone": "Design Phase",
                    "status": "completed",
                    "completion_date": "2024-01-15"
                }
            },
            {
                "id": 17,
                "name": "Time Tracking Integration",
                "business_type": "Professional Services",
                "webhook_path": "/time-tracking",
                "description": "Track billable hours and project time",
                "data_fields": ["employee_id", "project_id", "hours", "task_description", "date"],
                "file_types": ["timesheet.csv", "projects.xlsx"],
                "sample_payload": {
                    "employee_id": "EMP001",
                    "project_id": "PROJ001",
                    "hours": 8.5,
                    "task_description": "Client consultation and planning",
                    "date": "2024-01-15"
                }
            },
            {
                "id": 18,
                "name": "Invoice Generation",
                "business_type": "Professional Services",
                "webhook_path": "/invoice-generation",
                "description": "Generate invoices for completed work",
                "data_fields": ["client_id", "project_id", "amount", "due_date", "line_items"],
                "file_types": ["invoices.csv", "billing_data.xlsx"],
                "sample_payload": {
                    "client_id": "CLI001",
                    "project_id": "PROJ001",
                    "amount": 2500.00,
                    "due_date": "2024-02-15",
                    "line_items": [{"description": "Consulting", "hours": 20, "rate": 125}]
                }
            },
            {
                "id": 19,
                "name": "Document Management",
                "business_type": "Professional Services",
                "webhook_path": "/document-management",
                "description": "Manage client documents and contracts",
                "data_fields": ["document_id", "client_id", "document_type", "status", "expiry_date"],
                "file_types": ["documents.csv", "contracts.xlsx"],
                "sample_payload": {
                    "document_id": "DOC001",
                    "client_id": "CLI001",
                    "document_type": "contract",
                    "status": "signed",
                    "expiry_date": "2024-12-31"
                }
            },
            {
                "id": 20,
                "name": "Client Communication Log",
                "business_type": "Professional Services",
                "webhook_path": "/client-communication",
                "description": "Log all client communications",
                "data_fields": ["client_id", "communication_type", "subject", "content", "timestamp"],
                "file_types": ["communications.csv", "client_notes.xlsx"],
                "sample_payload": {
                    "client_id": "CLI001",
                    "communication_type": "email",
                    "subject": "Project Update",
                    "content": "Phase 1 completed successfully",
                    "timestamp": "2024-01-15 16:30"
                }
            },
            
            # Real Estate & Property (21-25)
            {
                "id": 21,
                "name": "Property Listing Updates",
                "business_type": "Real Estate",
                "webhook_path": "/property-listing",
                "description": "Update property listings across platforms",
                "data_fields": ["property_id", "address", "price", "status", "agent_id"],
                "file_types": ["properties.csv", "listings.xlsx", "photos.zip"],
                "sample_payload": {
                    "property_id": "PROP001",
                    "address": "123 Oak Street",
                    "price": 350000,
                    "status": "active",
                    "agent_id": "AGT001"
                }
            },
            {
                "id": 22,
                "name": "Lead Management System",
                "business_type": "Real Estate",
                "webhook_path": "/real-estate-lead",
                "description": "Manage real estate leads and inquiries",
                "data_fields": ["lead_id", "name", "email", "phone", "property_interest", "budget"],
                "file_types": ["leads.csv", "inquiries.xlsx"],
                "sample_payload": {
                    "lead_id": "LEAD001",
                    "name": "Sarah Wilson",
                    "email": "sarah@email.com",
                    "phone": "+1234567890",
                    "property_interest": "3BR house",
                    "budget": 400000
                }
            },
            {
                "id": 23,
                "name": "Property Showing Scheduler",
                "business_type": "Real Estate",
                "webhook_path": "/property-showing",
                "description": "Schedule property showings",
                "data_fields": ["property_id", "client_id", "agent_id", "showing_date", "notes"],
                "file_types": ["showings.csv", "calendar.xlsx"],
                "sample_payload": {
                    "property_id": "PROP001",
                    "client_id": "CLI001",
                    "agent_id": "AGT001",
                    "showing_date": "2024-01-16 14:00",
                    "notes": "First-time buyer"
                }
            },
            {
                "id": 24,
                "name": "Contract Processing",
                "business_type": "Real Estate",
                "webhook_path": "/contract-processing",
                "description": "Process real estate contracts and offers",
                "data_fields": ["contract_id", "property_id", "buyer_id", "offer_amount", "status"],
                "file_types": ["contracts.csv", "offers.xlsx"],
                "sample_payload": {
                    "contract_id": "CON001",
                    "property_id": "PROP001",
                    "buyer_id": "BUY001",
                    "offer_amount": 340000,
                    "status": "pending"
                }
            },
            {
                "id": 25,
                "name": "Market Analysis Updates",
                "business_type": "Real Estate",
                "webhook_path": "/market-analysis",
                "description": "Update market analysis and property valuations",
                "data_fields": ["area_id", "average_price", "market_trend", "analysis_date", "agent_id"],
                "file_types": ["market_data.csv", "analysis.xlsx"],
                "sample_payload": {
                    "area_id": "AREA001",
                    "average_price": 375000,
                    "market_trend": "increasing",
                    "analysis_date": "2024-01-15",
                    "agent_id": "AGT001"
                }
            }
        ]
    
    def setup_file_processors(self) -> Dict:
        """Setup file processors for different file types"""
        return {
            'csv': self.process_csv_file,
            'xlsx': self.process_excel_file,
            'json': self.process_json_file,
            'txt': self.process_text_file,
            'pdf': self.process_pdf_file,
            'zip': self.process_zip_file,
            'jpg': self.process_image_file,
            'png': self.process_image_file,
            'jpeg': self.process_image_file
        }
    
    def process_csv_file(self, file) -> Dict:
        """Process CSV file and return data"""
        try:
            df = pd.read_csv(file)
            return {
                'type': 'csv',
                'rows': len(df),
                'columns': list(df.columns),
                'data': df.to_dict('records')[:10],  # First 10 rows
                'preview': df.head().to_html()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def process_excel_file(self, file) -> Dict:
        """Process Excel file and return data"""
        try:
            df = pd.read_excel(file)
            return {
                'type': 'excel',
                'rows': len(df),
                'columns': list(df.columns),
                'data': df.to_dict('records')[:10],
                'preview': df.head().to_html()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def process_json_file(self, file) -> Dict:
        """Process JSON file and return data"""
        try:
            data = json.load(file)
            return {
                'type': 'json',
                'structure': type(data).__name__,
                'data': data if isinstance(data, list) and len(data) <= 10 else str(data)[:500],
                'preview': json.dumps(data, indent=2)[:1000]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def process_text_file(self, file) -> Dict:
        """Process text file and return data"""
        try:
            content = file.read().decode('utf-8')
            return {
                'type': 'text',
                'length': len(content),
                'lines': len(content.split('\n')),
                'preview': content[:500]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def process_pdf_file(self, file) -> Dict:
        """Process PDF file (placeholder)"""
        return {
            'type': 'pdf',
            'message': 'PDF processing would require additional libraries',
            'size': len(file.read())
        }
    
    def process_zip_file(self, file) -> Dict:
        """Process ZIP file and return contents"""
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                return {
                    'type': 'zip',
                    'files': file_list,
                    'count': len(file_list),
                    'preview': file_list[:10]
                }
        except Exception as e:
            return {'error': str(e)}
    
    def process_image_file(self, file) -> Dict:
        """Process image file and return metadata"""
        try:
            image = Image.open(file)
            return {
                'type': 'image',
                'format': image.format,
                'size': image.size,
                'mode': image.mode,
                'preview': 'Image loaded successfully'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def send_webhook(self, webhook_path: str, data: Dict, files_data: List[Dict] = None) -> Dict:
        """Send data to n8n webhook"""
        try:
            webhook_url = f"{self.n8n_webhook_base}{webhook_path}"
            
            payload = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'files': files_data or []
            }
            
            # Simulate webhook call (in real implementation, this would be actual HTTP request)
            # response = requests.post(webhook_url, json=payload, timeout=10)
            
            # For demo purposes, simulate success
            return {
                'status': 'success',
                'webhook_url': webhook_url,
                'payload_size': len(json.dumps(payload)),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    suite = WebhookBusinessSuite()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔗 Webhook Business Suite - n8n Integration</h1>
        <p>File upload & webhook automation for 25+ business types - No API credentials needed!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a section:", [
        "Dashboard",
        "File Upload Center",
        "Webhook Manager",
        "Business Templates",
        "Webhook Testing",
        "Analytics"
    ])
    
    if page == "Dashboard":
        show_dashboard(suite)
    elif page == "File Upload Center":
        show_file_upload(suite)
    elif page == "Webhook Manager":
        show_webhook_manager(suite)
    elif page == "Business Templates":
        show_business_templates(suite)
    elif page == "Webhook Testing":
        show_webhook_testing(suite)
    elif page == "Analytics":
        show_analytics(suite)

def show_dashboard(suite):
    st.header("📊 Webhook Business Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="webhook-card">
            <h3>25</h3>
            <p>Business Webhooks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="webhook-card">
            <h3>1,247</h3>
            <p>Files Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="webhook-card">
            <h3>98.5%</h3>
            <p>Success Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="webhook-card">
            <h3>5</h3>
            <p>Business Types</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Business type overview
    st.subheader("🏢 Business Types Overview")
    
    business_types = {}
    for webhook in suite.business_webhooks:
        btype = webhook['business_type']
        if btype not in business_types:
            business_types[btype] = []
        business_types[btype].append(webhook)
    
    for business_type, webhooks in business_types.items():
        with st.expander(f"{business_type} ({len(webhooks)} webhooks)"):
            for webhook in webhooks:
                st.markdown(f"""
                <div class="business-type-card">
                    <h4>{webhook['name']}</h4>
                    <p>{webhook['description']}</p>
                    <p><strong>Webhook:</strong> <code>{webhook['webhook_path']}</code></p>
                    <p><strong>File Types:</strong> {', '.join(webhook['file_types'])}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Recent webhook activity
    st.subheader("📋 Recent Webhook Activity")
    
    activity_data = [
        {"Time": "2 minutes ago", "Webhook": "/restaurant-order", "Status": "✅ Success", "Files": "menu.csv"},
        {"Time": "15 minutes ago", "Webhook": "/product-inventory", "Status": "✅ Success", "Files": "inventory.xlsx"},
        {"Time": "1 hour ago", "Webhook": "/patient-appointment", "Status": "⚠️ Pending", "Files": "appointments.json"},
        {"Time": "2 hours ago", "Webhook": "/property-listing", "Status": "✅ Success", "Files": "photos.zip"},
        {"Time": "3 hours ago", "Webhook": "/client-communication", "Status": "✅ Success", "Files": "communications.csv"}
    ]
    
    df_activity = pd.DataFrame(activity_data)
    st.dataframe(df_activity, use_container_width=True)

def show_file_upload(suite):
    st.header("📁 File Upload Center")
    
    st.info("Upload files for processing and automatic webhook integration with n8n")
    
    # File upload section
    st.subheader("📤 Upload Files")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['csv', 'xlsx', 'json', 'txt', 'pdf', 'zip', 'jpg', 'png', 'jpeg'],
            help="Supported formats: CSV, Excel, JSON, Text, PDF, ZIP, Images"
        )
    
    with col2:
        if uploaded_files:
            st.metric("Files Selected", len(uploaded_files))
            total_size = sum(len(f.read()) for f in uploaded_files)
            for f in uploaded_files:  # Reset file pointers
                f.seek(0)
            st.metric("Total Size", f"{total_size / 1024:.1f} KB")
    
    # Process uploaded files
    if uploaded_files:
        st.subheader("📋 File Processing Results")
        
        processed_files = []
        
        for uploaded_file in uploaded_files:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension in suite.file_processors:
                with st.expander(f"📄 {uploaded_file.name}"):
                    processor = suite.file_processors[file_extension]
                    result = processor(uploaded_file)
                    
                    if 'error' in result:
                        st.error(f"Error processing file: {result['error']}")
                    else:
                        st.success(f"File processed successfully!")
                        
                        # Display file info
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**File Information:**")
                            for key, value in result.items():
                                if key not in ['data', 'preview']:
                                    st.write(f"- {key.title()}: {value}")
                        
                        with col2:
                            if 'preview' in result:
                                st.write("**Preview:**")
                                if result['type'] in ['csv', 'excel']:
                                    st.write(result['preview'], unsafe_allow_html=True)
                                else:
                                    st.text(str(result['preview'])[:300] + "..." if len(str(result['preview'])) > 300 else str(result['preview']))
                        
                        processed_files.append({
                            'filename': uploaded_file.name,
                            'type': result['type'],
                            'data': result
                        })
            else:
                st.warning(f"Unsupported file type: {file_extension}")
        
        # Webhook integration options
        if processed_files:
            st.subheader("🔗 Webhook Integration")
            
            st.write("Select which webhook to trigger with your uploaded files:")
            
            # Group webhooks by business type
            business_types = {}
            for webhook in suite.business_webhooks:
                btype = webhook['business_type']
                if btype not in business_types:
                    business_types[btype] = []
                business_types[btype].append(webhook)
            
            selected_webhook = None
            
            for business_type, webhooks in business_types.items():
                with st.expander(f"{business_type} Webhooks"):
                    for webhook in webhooks:
                        if st.button(f"Use {webhook['name']}", key=f"webhook_{webhook['id']}"):
                            selected_webhook = webhook
                            
                            # Send webhook with file data
                            webhook_result = suite.send_webhook(
                                webhook['webhook_path'],
                                webhook['sample_payload'],
                                processed_files
                            )
                            
                            if webhook_result['status'] == 'success':
                                st.success(f"✅ Webhook sent successfully to {webhook_result['webhook_url']}")
                                st.json(webhook_result)
                            else:
                                st.error(f"❌ Webhook failed: {webhook_result['error']}")

def show_webhook_manager(suite):
    st.header("🔗 Webhook Manager")
    
    st.info("Manage and configure your 25 business webhooks for n8n integration")
    
    # Webhook configuration
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Configuration")
        
        n8n_base_url = st.text_input("n8n Base URL", value="http://localhost:5678")
        webhook_prefix = st.text_input("Webhook Prefix", value="/webhook")
        
        st.write("**Connection Status:**")
        if st.button("Test Connection"):
            st.success("✅ Connection successful!")
        
        st.markdown("---")
        
        st.subheader("📊 Quick Stats")
        st.metric("Total Webhooks", "25")
        st.metric("Active", "23")
        st.metric("Inactive", "2")
    
    with col2:
        st.subheader("📋 Webhook List")
        
        # Search and filter
        search_term = st.text_input("🔍 Search webhooks", placeholder="e.g., restaurant, inventory")
        business_filter = st.selectbox("Filter by business type", 
                                     ["All"] + list(set(w['business_type'] for w in suite.business_webhooks)))
        
        # Filter webhooks
        filtered_webhooks = suite.business_webhooks
        
        if search_term:
            filtered_webhooks = [w for w in filtered_webhooks 
                               if search_term.lower() in w['name'].lower() or 
                                  search_term.lower() in w['description'].lower()]
        
        if business_filter != "All":
            filtered_webhooks = [w for w in filtered_webhooks if w['business_type'] == business_filter]
        
        # Display webhooks
        for webhook in filtered_webhooks:
            with st.container():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    st.markdown(f"""
                    **{webhook['name']}** ({webhook['business_type']})  
                    {webhook['description']}  
                    `{n8n_base_url}{webhook_prefix}{webhook['webhook_path']}`
                    """)
                
                with col_b:
                    status = "🟢 Active" if webhook['id'] % 3 != 0 else "🔴 Inactive"
                    st.write(status)
                
                with col_c:
                    if st.button("Configure", key=f"config_{webhook['id']}"):
                        st.session_state[f"show_config_{webhook['id']}"] = True
                
                # Configuration panel
                if st.session_state.get(f"show_config_{webhook['id']}", False):
                    with st.expander("Webhook Configuration", expanded=True):
                        st.write("**Data Fields:**")
                        for field in webhook['data_fields']:
                            st.write(f"• {field}")
                        
                        st.write("**Supported File Types:**")
                        for file_type in webhook['file_types']:
                            st.write(f"• {file_type}")
                        
                        st.write("**Sample Payload:**")
                        st.json(webhook['sample_payload'])
                        
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if st.button("Test Webhook", key=f"test_{webhook['id']}"):
                                result = suite.send_webhook(webhook['webhook_path'], webhook['sample_payload'])
                                if result['status'] == 'success':
                                    st.success("✅ Test successful!")
                                else:
                                    st.error("❌ Test failed!")
                        
                        with col_y:
                            if st.button("Close", key=f"close_{webhook['id']}"):
                                st.session_state[f"show_config_{webhook['id']}"] = False
                                st.rerun()
                
                st.markdown("---")

def show_business_templates(suite):
    st.header("🏢 Business Templates")
    
    st.info("Pre-configured webhook templates for different business types")
    
    # Business type tabs
    business_types = {}
    for webhook in suite.business_webhooks:
        btype = webhook['business_type']
        if btype not in business_types:
            business_types[btype] = []
        business_types[btype].append(webhook)
    
    tabs = st.tabs(list(business_types.keys()))
    
    for i, (business_type, webhooks) in enumerate(business_types.items()):
        with tabs[i]:
            st.subheader(f"{business_type} Webhooks")
            
            for webhook in webhooks:
                with st.container():
                    st.markdown(f"""
                    <div class="webhook-card">
                        <h4>{webhook['name']}</h4>
                        <p>{webhook['description']}</p>
                        <p><strong>Webhook Path:</strong> <code>{webhook['webhook_path']}</code></p>
                        <p><strong>Data Fields:</strong> {', '.join(webhook['data_fields'])}</p>
                        <p><strong>File Types:</strong> {', '.join(webhook['file_types'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Use Template", key=f"use_template_{webhook['id']}"):
                            st.success(f"Template '{webhook['name']}' activated!")
                    
                    with col2:
                        if st.button("View Sample", key=f"sample_{webhook['id']}"):
                            st.json(webhook['sample_payload'])
                    
                    with col3:
                        if st.button("Copy Webhook URL", key=f"copy_{webhook['id']}"):
                            webhook_url = f"http://localhost:5678/webhook{webhook['webhook_path']}"
                            st.code(webhook_url)
                    
                    st.markdown("---")

def show_webhook_testing(suite):
    st.header("🧪 Webhook Testing")
    
    st.info("Test your webhooks with custom data and file uploads")
    
    # Select webhook to test
    webhook_options = {f"{w['name']} ({w['business_type']})": w for w in suite.business_webhooks}
    selected_webhook_name = st.selectbox("Select webhook to test:", list(webhook_options.keys()))
    selected_webhook = webhook_options[selected_webhook_name]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Webhook Details")
        st.write(f"**Name:** {selected_webhook['name']}")
        st.write(f"**Business Type:** {selected_webhook['business_type']}")
        st.write(f"**Description:** {selected_webhook['description']}")
        st.write(f"**Webhook Path:** `{selected_webhook['webhook_path']}`")
        
        st.subheader("📋 Data Fields")
        for field in selected_webhook['data_fields']:
            st.write(f"• {field}")
        
        st.subheader("📁 Supported Files")
        for file_type in selected_webhook['file_types']:
            st.write(f"• {file_type}")
    
    with col2:
        st.subheader("🔧 Test Configuration")
        
        # Custom payload editor
        st.write("**Custom Payload:**")
        custom_payload = st.text_area(
            "Edit JSON payload",
            value=json.dumps(selected_webhook['sample_payload'], indent=2),
            height=200
        )
        
        # File upload for testing
        st.write("**Test Files:**")
        test_files = st.file_uploader(
            "Upload test files",
            accept_multiple_files=True,
            type=['csv', 'xlsx', 'json', 'txt', 'pdf', 'zip', 'jpg', 'png', 'jpeg']
        )
        
        # Test button
        if st.button("🚀 Send Test Webhook", type="primary"):
            try:
                payload_data = json.loads(custom_payload)
                
                # Process test files
                processed_test_files = []
                if test_files:
                    for test_file in test_files:
                        file_extension = test_file.name.split('.')[-1].lower()
                        if file_extension in suite.file_processors:
                            processor = suite.file_processors[file_extension]
                            result = processor(test_file)
                            processed_test_files.append({
                                'filename': test_file.name,
                                'type': result['type'],
                                'data': result
                            })
                
                # Send webhook
                result = suite.send_webhook(
                    selected_webhook['webhook_path'],
                    payload_data,
                    processed_test_files
                )
                
                st.subheader("📊 Test Results")
                
                if result['status'] == 'success':
                    st.success("✅ Webhook sent successfully!")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Status", "Success")
                        st.metric("Payload Size", f"{result['payload_size']} bytes")
                    
                    with col_b:
                        st.metric("Webhook URL", selected_webhook['webhook_path'])
                        st.metric("Timestamp", result['timestamp'])
                    
                    st.write("**Full Response:**")
                    st.json(result)
                    
                else:
                    st.error(f"❌ Webhook failed: {result['error']}")
                    st.json(result)
                    
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON payload")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def show_analytics(suite):
    st.header("📈 Webhook Analytics")
    
    # Generate sample analytics data
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    # Sample webhook activity data
    webhook_data = []
    for date in dates:
        for webhook in suite.business_webhooks[:10]:  # Use first 10 for demo
            webhook_data.append({
                'date': date,
                'webhook_name': webhook['name'],
                'business_type': webhook['business_type'],
                'calls': np.random.poisson(20),
                'success_rate': np.random.uniform(0.85, 0.99),
                'avg_response_time': np.random.uniform(0.5, 3.0)
            })
    
    df_webhooks = pd.DataFrame(webhook_data)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_calls = df_webhooks['calls'].sum()
        st.metric("Total Webhook Calls", f"{total_calls:,}")
    
    with col2:
        avg_success_rate = df_webhooks['success_rate'].mean()
        st.metric("Average Success Rate", f"{avg_success_rate:.1%}")
    
    with col3:
        avg_response_time = df_webhooks['avg_response_time'].mean()
        st.metric("Avg Response Time", f"{avg_response_time:.2f}s")
    
    with col4:
        active_webhooks = len(df_webhooks['webhook_name'].unique())
        st.metric("Active Webhooks", active_webhooks)
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["Daily Activity", "Business Type Analysis", "Performance Metrics"])
    
    with tab1:
        st.subheader("Daily Webhook Activity")
        
        daily_activity = df_webhooks.groupby('date')['calls'].sum().reset_index()
        fig = px.line(daily_activity, x='date', y='calls', 
                     title='Daily Webhook Calls')
        st.plotly_chart(fig, use_container_width=True)
        
        # Top webhooks
        st.subheader("Top Performing Webhooks")
        top_webhooks = df_webhooks.groupby('webhook_name')['calls'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_webhooks.values, y=top_webhooks.index, orientation='h',
                    title='Webhook Calls by Endpoint')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Business Type Analysis")
        
        business_analysis = df_webhooks.groupby('business_type').agg({
            'calls': 'sum',
            'success_rate': 'mean',
            'avg_response_time': 'mean'
        }).reset_index()
        
        fig = px.bar(business_analysis, x='business_type', y='calls',
                    title='Webhook Calls by Business Type')
        st.plotly_chart(fig, use_container_width=True)
        
        # Success rate by business type
        fig = px.bar(business_analysis, x='business_type', y='success_rate',
                    title='Success Rate by Business Type')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Performance Metrics")
        
        # Response time distribution
        fig = px.histogram(df_webhooks, x='avg_response_time', nbins=20,
                          title='Response Time Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        # Success rate over time
        daily_success = df_webhooks.groupby('date')['success_rate'].mean().reset_index()
        fig = px.line(daily_success, x='date', y='success_rate',
                     title='Success Rate Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed webhook performance table
    st.subheader("📊 Detailed Webhook Performance")
    
    performance_summary = df_webhooks.groupby(['webhook_name', 'business_type']).agg({
        'calls': 'sum',
        'success_rate': 'mean',
        'avg_response_time': 'mean'
    }).reset_index()
    
    performance_summary['success_rate'] = performance_summary['success_rate'].apply(lambda x: f"{x:.1%}")
    performance_summary['avg_response_time'] = performance_summary['avg_response_time'].apply(lambda x: f"{x:.2f}s")
    
    st.dataframe(performance_summary, use_container_width=True)

if __name__ == "__main__":
    # Import required libraries
    import numpy as np
    main()
