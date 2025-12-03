# Custom HTTP/1.1 Server (Built Using Python Sockets)

This project implements a complete HTTP/1.1 server from scratch using only Python’s low-level socket module.  
No frameworks like Flask, Django, or Express were used.  
Everything — HTTP parsing, routing, JSON handling, and multithreading — is implemented manually.

The goal is to deeply understand how HTTP servers work internally.

---

## ✨ Features

---

### ⭐ Phase 1 — TCP Server
- Opens a socket on port **8080**
- Accepts client connections
- Sends raw HTTP responses manually

---

### ⭐ Phase 2 — HTTP Parsing
- Reads raw HTTP request bytes
- Extracts:
  - Request line  
  - Headers  
  - Body
- Identifies method, path, and version

---

### ⭐ Phase 3 — Routing
- `GET /` → welcome message
- `GET /echo?msg=hello` → returns `"hello"`
- Unknown paths → **404 JSON error**

---

### ⭐ Phase 4 — JSON Body Handling
- Reads JSON using **Content-Length**
- Validates **Content-Type: application/json**
- Converts JSON into a Python dictionary

---

### ⭐ Phase 5 — In-Memory CRUD API
The server uses a Python list `DATA_STORE` as an in-memory database.

#### 📌 Endpoints:
- `POST /data` → store a JSON item
- `GET /data` → return all items
- `GET /data/<id>` → return item by index
- `DELETE /data/<id>` → delete item

---

### ⭐ Phase 6 — Clean Server Architecture
- Response builder  
- JSON response helper  
- Structured routing  
- Proper `Content-Length` & `Content-Type`  
- JSON error messages

---

### ⭐ Phase 7 — Multithreading
- Each request handled in a separate **thread**
- Supports multiple clients simultaneously
- Realistic backend behaviour

---

## 🧠 How the Server Works Internally

1. Client sends an HTTP request  
2. Server reads raw bytes via TCP  
3. Request line, headers, and body are parsed  
4. Routing logic determines required action  
5. JSON body (if present) is decoded  
6. CRUD / Echo handlers process request  
7. Response builder creates valid HTTP/1.1 response  
8. Response is sent back to the client  

---

## 📂 Endpoints Overview

| Method | Route | Description |
|--------|--------|-------------|
| GET | `/` | Homepage message |
| GET | `/echo?msg=hello` | Returns message |
| POST | `/data` | Add JSON item |
| GET | `/data` | Return all items |
| GET | `/data/<id>` | Return item by index |
| DELETE | `/data/<id>` | Delete item |

---

## 🛠 How to Run

```bash
python server.py
