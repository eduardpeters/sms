# Simple Messaging SDK

A Python SDK for interacting with a simplified version of the Sinch Messaging API.
Supports sending and managing messages over **SMS** and **WhatsApp** with a single client interface.

## Installation

```bash
pip install simple-messaging-sdk
```

Requires Python 3.10+.

---

## Design Choices

### HTTP:
The client uses a self-contained http client (with httpx) to handle communication with the API. This client acts as the layer that translates API errors with various shapes into SDK specific exceptions.