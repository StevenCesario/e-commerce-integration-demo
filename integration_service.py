import requests
import base64
import json
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import time

load_dotenv()

# --- Environment Configuration ---
ECOMMERCE_API_TOKEN = os.getenv("ECOMMERCE_API_TOKEN", "demo_token_12345")
ECOMMERCE_LOCATION_ID = os.getenv("ECOMMERCE_LOCATION_ID", "demo_location_67890")
ECOMMERCE_API_BASE_URL = os.getenv("ECOMMERCE_API_BASE_URL", "https://api.ecommerce-platform.com")

WMS_USERNAME = os.getenv("WMS_USERNAME", "demo_wms_user")
WMS_PASSWORD = os.getenv("WMS_PASSWORD", "demo_wms_password")
WMS_WAREHOUSE_ID = os.getenv("WMS_WAREHOUSE_ID", "warehouse_001")
WMS_API_BASE_URL = os.getenv("WMS_API_BASE_URL", "https://api.warehouse-system.com")

# --- Country Code Mapping for International Orders ---
COUNTRY_CODE_MAP = {
    "sweden": "SE", "united states": "US", "united kingdom": "GB",
    "norway": "NO", "denmark": "DK", "finland": "FI", "germany": "DE",
    "france": "FR", "spain": "ES", "italy": "IT", "netherlands": "NL",
    "canada": "CA", "australia": "AU", "japan": "JP", "singapore": "SG"
}

def get_country_code(country_name: str | None) -> str:
    """Convert country names to ISO 3166-1 alpha-2 codes."""
    if not country_name: 
        return "US"  # Default fallback
    if len(country_name) == 2 and country_name.isalpha(): 
        return country_name.upper()
    return COUNTRY_CODE_MAP.get(country_name.lower(), "US")

# --- Pydantic Models for Data Validation ---
class CustomerNotification(BaseModel):
    """Customer notification preferences."""
    enabled: bool = True
    value: Optional[str] = None

class ShippingAddress(BaseModel):
    """Standardized shipping address format."""
    customerNumber: str
    name: str
    address1: Optional[str] = None
    address2: Optional[str] = None
    postalCode: str
    city: str
    countryCode: str
    phoneNotification: CustomerNotification
    emailNotification: CustomerNotification

class OrderLineItem(BaseModel):
    """Individual product line item in an order."""
    lineNumber: int
    productSku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    productName: str
    unitPrice: float = Field(ge=0, description="Unit price must be non-negative")
    totalPrice: float = Field(ge=0, description="Total price must be non-negative")
    
    @field_validator('totalPrice', mode='after')
    @classmethod
    def validate_total_price(cls, v, info):
        """Ensure total price matches quantity * unit price."""
        if 'quantity' in info.data and 'unitPrice' in info.data:
            expected_total = info.data['quantity'] * info.data['unitPrice']
            if abs(v - expected_total) > 0.01:  # Allow for small rounding differences
                raise ValueError(f"Total price {v} doesn't match quantity * unit price {expected_total}")
        return v

class WarehouseOrder(BaseModel):
    """Complete warehouse fulfillment order."""
    warehouseId: str
    orderNumber: str
    deliveryDate: date
    orderNotes: Optional[str] = None
    totalValue: Optional[float] = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    shippingAddress: ShippingAddress
    lineItems: List[OrderLineItem] = Field(min_length=1, description="Order must have at least one item")
    shippingMethod: str = "standard"
    priority: str = "normal"
    
    @field_validator('deliveryDate', mode='before')
    @classmethod
    def parse_delivery_date(cls, v):
        """Parse delivery date from various formats."""
        if isinstance(v, str): 
            return date.fromisoformat(v)
        return v
    
    @field_validator('currency', mode='after')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase."""
        return v.upper()

# --- Service Functions ---

def get_warehouse_auth_header(username: str, password: str) -> str | None:
    """Generate Basic Auth header for warehouse API."""
    if not username or not password:
        print("ERROR: Warehouse credentials not provided")
        return None
    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded_credentials}"

def get_ecommerce_order_details(contact_id: str, retries: int = 3, delay_seconds: int = 2) -> dict | None:
    """
    Fetch complete order details from e-commerce platform.
    
    This simulates the two-step process many e-commerce platforms use:
    1. Find the latest transaction for a contact
    2. Fetch complete order details using the transaction ID
    """
    if not ECOMMERCE_API_TOKEN:
        print("ERROR: E-commerce API token not configured")
        return None
    
    headers = {
        "Authorization": f"Bearer {ECOMMERCE_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"INFO: Step 1/2 - Searching for recent transaction for contact: {contact_id}")
    
    # Step 1: Find the latest transaction for this contact
    transactions_endpoint = f"{ECOMMERCE_API_BASE_URL}/payments/transactions"
    transaction_params = {
        "contactId": contact_id,
        "locationId": ECOMMERCE_LOCATION_ID,
        "limit": 1,
        "sortBy": "createdAt",
        "order": "desc"
    }
    
    order_id = None
    for attempt in range(retries):
        try:
            # In a real implementation, this would make an actual API call
            # For demo purposes, we'll simulate a successful response
            print(f"INFO: Attempt {attempt + 1} - Fetching transactions...")
            
            # Simulate API delay
            time.sleep(0.1)
            
            # Mock successful transaction lookup
            order_id = f"order_{contact_id}_{int(time.time())}"
            print(f"INFO: Step 1/2 - Success: Found Order ID: {order_id}")
            break
            
        except Exception as e:
            print(f"ERROR: Transaction lookup attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay_seconds)
    
    if not order_id:
        print("ERROR: Could not find order for contact")
        return None
    
    # Step 2: Fetch complete order details
    print(f"INFO: Step 2/2 - Fetching complete order details for Order ID: {order_id}")
    
    try:
        # Simulate fetching complete order data
        # In production, this would be a real API call to the e-commerce platform
        mock_order_data = {
            "_id": order_id,
            "contactSnapshot": {
                "id": contact_id,
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "address1": "123 Main Street",
                "address2": "Apt 4B",
                "city": "New York",
                "postalCode": "10001",
                "country": "United States"
            },
            "items": [
                {
                    "name": "Premium Widget",
                    "qty": 2,
                    "price": {
                        "sku": "WIDGET-001",
                        "amount": 29.99
                    }
                },
                {
                    "name": "Deluxe Gadget",
                    "qty": 1,
                    "price": {
                        "sku": "GADGET-002", 
                        "amount": 49.99
                    }
                }
            ],
            "amount": 109.97,
            "currency": "USD",
            "notes": f"Order from e-commerce platform: {order_id}",
            "createdAt": "2024-01-15T10:25:00Z"
        }
        
        print("INFO: Step 2/2 - Successfully fetched order data")
        return mock_order_data
        
    except Exception as e:
        print(f"ERROR: Failed to fetch order details: {e}")
        return None

def map_order_to_wms_payload(ecommerce_order_data: dict, process_id: str) -> Optional[WarehouseOrder]:
    """
    Transform e-commerce order data into warehouse management system format.
    
    This function handles:
    - Data structure transformation
    - Field mapping between systems
    - Data validation and cleaning
    - Currency and pricing calculations
    """
    print(f"[{process_id}] INFO: Mapping e-commerce order to warehouse format...")
    
    if not ecommerce_order_data or not ecommerce_order_data.get("_id"):
        print(f"[{process_id}] ERROR: Invalid order data provided")
        return None
    
    order_id = ecommerce_order_data.get("_id")
    customer_info = ecommerce_order_data.get("contactSnapshot", {})
    contact_id = customer_info.get("id")
    items = ecommerce_order_data.get("items", [])
    
    if not items:
        print(f"[{process_id}] ERROR: No items found in order")
        return None
    
    # Transform line items
    line_items = []
    for index, item in enumerate(items):
        sku = item.get("price", {}).get("sku")
        if not sku:
            print(f"[{process_id}] WARNING: Skipping item without SKU: {item.get('name', 'Unknown')}")
            continue
            
        quantity = int(item.get("qty", 1))
        unit_price = float(item.get("price", {}).get("amount", 0))
        total_price = round(unit_price * quantity, 2)
        
        line_items.append({
            "lineNumber": index + 1,
            "productSku": sku,
            "quantity": quantity,
            "productName": item.get("name", "Unknown Product"),
            "unitPrice": unit_price,
            "totalPrice": total_price
        })
    
    if not line_items:
        print(f"[{process_id}] ERROR: No valid line items after processing")
        return None
    
    # Build shipping address
    try:
        country_code = get_country_code(customer_info.get("country"))
        
        payload_data = {
            "warehouseId": WMS_WAREHOUSE_ID,
            "orderNumber": f"ECOM-{order_id}",
            "deliveryDate": date.today() + timedelta(days=1),  # Next business day
            "orderNotes": ecommerce_order_data.get("notes", f"E-commerce order: {order_id}"),
            "totalValue": ecommerce_order_data.get("amount"),
            "currency": ecommerce_order_data.get("currency", "USD").upper(),
            "shippingAddress": {
                "customerNumber": f"CUSTOMER-{contact_id}",
                "name": f"{customer_info.get('firstName', '')} {customer_info.get('lastName', '')}".strip(),
                "address1": customer_info.get("address1"),
                "address2": customer_info.get("address2"),
                "postalCode": customer_info.get("postalCode", "00000"),
                "city": customer_info.get("city", "Unknown City"),
                "countryCode": country_code,
                "phoneNotification": {
                    "enabled": bool(customer_info.get("phone")),
                    "value": customer_info.get("phone")
                },
                "emailNotification": {
                    "enabled": bool(customer_info.get("email")),
                    "value": customer_info.get("email")
                }
            },
            "lineItems": line_items,
            "shippingMethod": "standard",
            "priority": "normal"
        }
        
        # Validate the data using Pydantic
        warehouse_order = WarehouseOrder(**payload_data)
        print(f"[{process_id}] SUCCESS: Order mapped and validated")
        return warehouse_order
        
    except Exception as e:
        print(f"[{process_id}] ERROR: Failed to map order data: {e}")
        return None

def create_warehouse_order(warehouse_order: WarehouseOrder, process_id: str) -> bool:
    """
    Create a fulfillment order in the warehouse management system.
    
    This function:
    - Authenticates with the warehouse API
    - Sends the formatted order data
    - Handles responses and errors
    - Provides detailed logging for debugging
    """
    print(f"[{process_id}] INFO: Creating warehouse order: {warehouse_order.orderNumber}")
    
    # Get authentication header
    auth_header = get_warehouse_auth_header(WMS_USERNAME, WMS_PASSWORD)
    if not auth_header:
        print(f"[{process_id}] ERROR: Failed to generate warehouse authentication")
        return False
    
    # Prepare API request
    orders_endpoint = f"{WMS_API_BASE_URL}/orders"
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # Convert Pydantic model to JSON
    order_json = warehouse_order.model_dump_json(exclude_none=True)
    print(f"[{process_id}] DEBUG: Sending warehouse order payload")
    
    try:
        # In a real implementation, this would make an actual API call
        # For demo purposes, we'll simulate a successful response
        print(f"[{process_id}] INFO: Sending order to warehouse system...")
        
        # Simulate API processing time
        time.sleep(0.2)
        
        # Mock successful response
        print(f"[{process_id}] SUCCESS: Order {warehouse_order.orderNumber} created in warehouse system")
        return True
        
    except requests.exceptions.HTTPError as http_err:
        print(f"[{process_id}] ERROR: Warehouse API HTTP error: {http_err}")
        return False
    except requests.exceptions.RequestException as req_err:
        print(f"[{process_id}] ERROR: Warehouse API request failed: {req_err}")
        return False
    except Exception as e:
        print(f"[{process_id}] ERROR: Unexpected error creating warehouse order: {e}")
        return False