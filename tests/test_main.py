from fastapi.testclient import TestClient
from unittest.mock import patch
import integration_service # Import the service to mock its functions

# Test 1: The "Happy Path" - A successful end-to-end order process
def test_handle_order_webhook_success(client: TestClient):
    """
    Tests the entire successful workflow from webhook to WMS creation.
    - Asserts a 200 OK status.
    - Verifies the success response structure and message.
    - Confirms the WMS order number is correctly formatted.
    """
    # Arrange: Define a valid webhook payload
    webhook_payload = {"contactId": "customer_12345", "orderId": "order_abcde"}

    # Act: Send the payload to the webhook endpoint
    response = client.post("/webhook/order-created", json=webhook_payload)

    # Assert: Check for a successful response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Order processed and sent to warehouse successfully" in data["message"]
    # The simulated order ID is based on contactId and a timestamp
    assert data["wmsOrderNumber"].startswith("ECOM-order_customer_12345_")


# Test 2: External Dependency Failure - E-commerce API is down
def test_handle_order_webhook_ecommerce_fetch_fails(client: TestClient, monkeypatch):
    """
    Tests the failure scenario where the e-commerce platform API is unavailable.
    - Mocks the get_ecommerce_order_details function to simulate a failure (returns None).
    - Asserts that the endpoint returns a 502 Bad Gateway status.
    - Verifies the error message correctly identifies the point of failure.
    """
    # Arrange: Mock the service function to simulate a failure
    monkeypatch.setattr("main.get_ecommerce_order_details", lambda contact_id: None)
    webhook_payload = {"contactId": "customer_failed_fetch"}

    # Act: Send the payload
    response = client.post("/webhook/order-created", json=webhook_payload)

    # Assert: Check for the specific 502 error
    assert response.status_code == 502
    data = response.json()
    assert "Failed to fetch order details from e-commerce platform" in data["detail"]


# Test 3: Data Validation Failure - Order contains no items
def test_handle_order_webhook_no_items_in_order(client: TestClient, monkeypatch):
    """
    Tests the data validation logic when an order has no line items.
    - Mocks the e-commerce response to return an order with an empty 'items' list.
    - Asserts that the data transformation fails and returns a 500 Internal Server Error.
    - Verifies the error message indicates a data transformation problem.
    """
    # Arrange: Create a mock response with no items
    mock_order_data_with_no_items = {
        "_id": "order_no_items",
        "contactSnapshot": {"id": "contact_no_items"},
        "items": [] # The critical part: an empty list of items
    }
    # Mock the service function to return this specific data
    monkeypatch.setattr(
    "main.get_ecommerce_order_details", 
    lambda contact_id: mock_order_data_with_no_items
    )
    webhook_payload = {"contactId": "customer_no_items"}

    # Act: Send the payload
    response = client.post("/webhook/order-created", json=webhook_payload)

    # Assert: Check that our internal validation catches the error
    assert response.status_code == 500
    data = response.json()
    assert "Failed to transform order data" in data["detail"]