from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn, os, logging

# Import our service functions
from integration_service import (
    get_ecommerce_order_details,
    map_order_to_wms_payload,
    create_warehouse_order
)

# --- Basic Setup & Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# --- App Initialization & Documentation ---
app = FastAPI(
    title="E-commerce to Warehouse Integration",
    description="Automated webhook processor that receives e-commerce orders and creates fulfillment orders in warehouse management systems. Handles data transformation, validation, and error recovery.",
    version="1.0.0",
    docs_url="/",
)

# --- Pydantic Models ---
class EcommerceWebhook(BaseModel):
    contactId: str
    orderId: str = None  # Optional fallback identifier
    
    class Config:
        schema_extra = {
            "example": {
                "contactId": "contact_12345",
                "orderId": "order_67890"
            }
        }

class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    wmsOrderNumber: str | None = None
    processId: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Order processed and sent to warehouse successfully.",
                "wmsOrderNumber": "WMS-ORDER-12345",
                "processId": "abc123def"
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    processId: str
    error_code: str

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy", 
        "service": "E-commerce Warehouse Integration",
        "version": "1.0.0"
    }

@app.post("/webhook/order-created", response_model=SuccessResponse, tags=["Webhooks"])
async def handle_order_webhook(payload: EcommerceWebhook):
    """
    Process new order webhooks from e-commerce platforms.
    
    This endpoint:
    1. Receives webhook notification of new order
    2. Fetches complete order details from e-commerce API
    3. Transforms data for warehouse management system
    4. Creates fulfillment order in WMS
    5. Returns success confirmation with tracking ID
    """
    process_id = os.urandom(4).hex()
    
    print(f"\n--- [{process_id}] New Order Webhook Received ---")
    print(f"[{process_id}] INFO: Processing order for contact: {payload.contactId}")
    
    try:
        # Step 1: Fetch complete order details from e-commerce platform
        print(f"[{process_id}] STEP 1: Fetching order details from e-commerce platform")
        ecommerce_order_data = get_ecommerce_order_details(payload.contactId)
        
        if not ecommerce_order_data:
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to fetch order details from e-commerce platform for contact {payload.contactId}"
            )
        
        print(f"[{process_id}] SUCCESS: Retrieved order data for order ID: {ecommerce_order_data.get('orderId', 'N/A')}")
        
        # Step 2: Transform e-commerce data to warehouse format
        print(f"[{process_id}] STEP 2: Transforming order data for warehouse system")
        wms_payload_model = map_order_to_wms_payload(ecommerce_order_data, process_id)
        
        if not wms_payload_model:
            raise HTTPException(
                status_code=500, 
                detail="Failed to transform order data for warehouse processing"
            )
            
        print(f"[{process_id}] SUCCESS: Order transformed. WMS Order Number: {wms_payload_model.orderNumber}")
        
        # Step 3: Create order in warehouse management system
        print(f"[{process_id}] STEP 3: Creating fulfillment order in warehouse")
        success = create_warehouse_order(wms_payload_model, process_id)
        
        if success:
            print(f"--- [{process_id}] WORKFLOW COMPLETE: SUCCESS ---")
            return SuccessResponse(
                message="Order processed and sent to warehouse successfully.",
                wmsOrderNumber=wms_payload_model.orderNumber,
                processId=process_id
            )
        else:
            raise HTTPException(
                status_code=502, 
                detail="Failed to create fulfillment order in warehouse system"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error during order processing: {str(e)}"
        print(f"[{process_id}] ERROR: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": error_msg,
                "processId": process_id,
                "error_type": "internal_error"
            }
        )

@app.post("/webhook/order-updated", tags=["Webhooks"])
async def handle_order_update_webhook(payload: EcommerceWebhook):
    """
    Handle order update notifications (cancellations, modifications, etc.)
    """
    process_id = os.urandom(4).hex()
    print(f"[{process_id}] INFO: Order update webhook received for contact: {payload.contactId}")
    
    # In a real implementation, this would handle order modifications
    # For demo purposes, we'll return a simple acknowledgment
    return {
        "status": "acknowledged",
        "message": "Order update webhook received and queued for processing",
        "processId": process_id
    }

@app.get("/orders/{order_id}/status", tags=["Orders"])
async def get_order_status(order_id: str):
    """
    Get the current processing status of an order.
    Useful for debugging and customer service.
    """
    # In a real implementation, this would query a database
    # For demo purposes, return a mock status
    return {
        "orderId": order_id,
        "status": "processed",
        "wmsOrderNumber": f"WMS-{order_id}",
        "lastUpdated": "2024-01-15T10:30:00Z",
        "steps": [
            {"step": "webhook_received", "status": "completed", "timestamp": "2024-01-15T10:25:00Z"},
            {"step": "order_fetched", "status": "completed", "timestamp": "2024-01-15T10:26:00Z"},
            {"step": "data_transformed", "status": "completed", "timestamp": "2024-01-15T10:27:00Z"},
            {"step": "wms_order_created", "status": "completed", "timestamp": "2024-01-15T10:30:00Z"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)