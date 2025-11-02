# 🚀 Complex Webhook & Data Integration (FastAPI, Pydantic V2)

[![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-blue)](https://pydantic.dev)
[![CI/CD](https://github.com/stevencesario/e-commerce-integration-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/stevencesario/e-commerce-integration-demo/actions/workflows/ci.yml)

> **Portfolio Context:** This repository serves as supporting **Proof of Work** for my core Meta CAPI architecture. It demonstrates my ability to handle complex, asynchronous, high-stakes webhook data from third-party platforms.
>
> This is the *exact* skill set required to process event data from e-commerce platforms (Shopify, Skool, funnels) and securely transform it for a server-side API, just as I do for the Meta Conversions API.

---

## 🎯 Solved: A High-Pain Business Data Problem

This system solved a critical integration gap for a business, eliminating **15+ hours of weekly manual data entry** and the high risk of human error.

* **Manual Process**: 15+ hours weekly of error-prone data entry.
* **Automated Process**: Instant, error-free order flow with a full audit trail.

This project proves I don't just build scripts; I build reliable data infrastructure that solves expensive business problems.

## ✨ Core Technical Competencies (Proof of Work)

* **Webhook-Driven Automation:** Production-ready API endpoint for receiving and processing high-stakes webhooks from third-party platforms.
* **Enterprise-Grade Reliability:** Comprehensive data validation using **Pydantic V2** to define strict schemas for incoming and outgoing data.
* **Data Transformation & Mapping:** The `integration_service.py` file shows the clear, maintainable logic for mapping complex, nested JSON from one format (E-commerce) to another (Warehouse).
* **Real-World Complexity:** Demonstrates handling of real-world data problems like country code standardization, multi-currency validation, and address formatting.
* **Fully Tested:** Includes a `pytest` suite that tests the "happy path" as well as failure scenarios like API downtime and data validation errors.

## 🏗️ System Architecture (Analogous to CAPI)

This system's data flow is a direct parallel to a server-side CAPI implementation: receiving event data, transforming it, validating it, and securely forwarding it to an external API.

E-commerce Platform → Webhook → Integration Service → Warehouse API
↓                       ↓                       ↓
[Data Transformation]   [Validation & Mapping]  [Fulfillment Creation]

---

## 🔧 Technical Proof: Data Transformation (PII & Event Data)

This is tangible proof of my ability to securely map critical PII and event data from one complex JSON structure to another.

### Input (E-commerce Format)
```json
{
  "_id": "order_12345",
  "contactSnapshot": {
    "firstName": "John", "lastName": "Doe",
    "email": "john@example.com", "phone": "+1-555-0123",
    "address1": "123 Main St", "city": "New York",
    "postalCode": "10001", "country": "United States"
  },
  "items": [
    {
      "name": "Premium Widget",
      "qty": 2,
      "price": {"sku": "WIDGET-001", "amount": 29.99}
    }
  ],
  "amount": 59.98,
  "currency": "USD"
}
´´´

### Output (Warehouse Format)
```json
{
  "warehouseId": "warehouse_001",
  "orderNumber": "ECOM-order_12345",
  "deliveryDate": "2024-01-16",
  "totalValue": 59.98,
  "currency": "USD",
  "shippingAddress": {
    "customerNumber": "CUSTOMER-customer_12345",
    "name": "John Doe",
    "address1": "123 Main St",
    "postalCode": "10001",
    "city": "New York",
    "countryCode": "US",
    "emailNotification": {"enabled": true, "value": "john@example.com"}
  },
  "lineItems": [
    {
      "lineNumber": 1,
      "productSku": "WIDGET-001",
      "quantity": 2,
      "productName": "Premium Widget",
      "unitPrice": 29.99,
      "totalPrice": 59.98
    }
  ]
}
´´´
