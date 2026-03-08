# Simple Messaging SDK

A Python SDK for interacting with a simplified version of the Sinch Messaging API.
Supports sending and managing messages over **SMS** and **WhatsApp** with a single client interface.

## Installation

```bash
pip install simple-messaging-sdk
```

Requires Python 3.10+.

---

## Usage

### Initializing a client
```python
from sinch import SinchClient

client = SinchClient(auth_token="your-token")

# A custom base URL may also be provided
client = SinchClient(auth_token="your-token", base_url="http://localhost:8080")
```

### Sending messages

```python
from sinch import SMS, WhatsApp

# Send an SMS
msg = client.messages.send(
    to=SMS(phone_number="+50212345678"),
    text="Hello from SMS!",
)

# Send a WhatsApp message
msg = client.messages.send(
    to=WhatsApp(phone_number="+50287654321"),
    text="Hello from WhatsApp!",
)
```

### Getting a message
```python
msg = client.messages.get("msg_abc123")
print(msg.status)      # MessageStatus.DELIVERED
print(msg.channel)     # "sms"
print(msg.created_at)  # datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
```

### Listing messages
```python
page = client.messages.list(page_size=50)

for msg in page.items:
    print(msg.id)

# Fetch the next page when current is exhausted
if page.has_next_page():
    next_page = page.next_page()
```

### Recalling a message
```python
client.messages.recall("msg_abc123")
```

## Design Choices

### Exposing resources:
The client interacts with a single resource (messages, via `client.messages`), but does so in a way that extending it with more resources can happen in a similar fashion. This allows for a clear path to interact with the different concerns that may be involved when adding more resources in the future.

### HTTP layer:
The client uses a self-contained http client (with httpx) to handle communication with the API. This client acts as the layer that translates API errors with various shapes into SDK specific exceptions.

### Exceptions:
Care has been taken to define and provide specific exceptions for expected exceptional situations for developers to be able to handle their specific occurrences.

### Naming and conventions:
The SDK uses `snake_case` both for input and output models. It handles any inconsistencies by switching to other conventions such as `camelCase` under the hood, providing a consistent naming experience for consumers.

---

### Walkthrough
🎬 [Video]()