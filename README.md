# Task Control Center

A modern FastAPI-based server for task and resource management with real-time monitoring.

## Features

- **Task Management**: Create, start, pause, cancel, and monitor tasks
- **Resource Management**: Manage proxies, cards, emails, and accounts
- **Real-time Monitoring**: WebSocket-based live updates
- **Beautiful UI**: Modern, responsive dark-themed interface
- **API Documentation**: Auto-generated Swagger/ReDoc docs

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

**Access:**

- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
python server/
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── app/
│   ├── core/            # Configuration
│   ├── models/          # Data models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── static/          # Frontend (HTML/CSS/JS)
```

## API Endpoints

### Tasks

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| GET    | `/api/tasks/`              | List all tasks    |
| POST   | `/api/tasks/`              | Create a new task |
| GET    | `/api/tasks/{id}`          | Get task by ID    |
| PUT    | `/api/tasks/{id}`          | Update task       |
| DELETE | `/api/tasks/{id}`          | Delete task       |
| POST   | `/api/tasks/{id}/start`    | Start task        |
| POST   | `/api/tasks/{id}/pause`    | Pause task        |
| POST   | `/api/tasks/{id}/cancel`   | Cancel task       |
| POST   | `/api/tasks/{id}/complete` | Complete task     |

### Resources

#### Proxies

| Method | Endpoint                      | Description      |
| ------ | ----------------------------- | ---------------- |
| GET    | `/api/resources/proxies/`     | List proxies     |
| POST   | `/api/resources/proxies/`     | Add proxy        |
| POST   | `/api/resources/proxies/bulk` | Bulk add proxies |
| PUT    | `/api/resources/proxies/{id}` | Update proxy     |
| DELETE | `/api/resources/proxies/{id}` | Delete proxy     |

#### Cards, Emails, Accounts

Similar CRUD endpoints available for cards, emails, and accounts.

### Monitoring

| Method | Endpoint                 | Description          |
| ------ | ------------------------ | -------------------- |
| GET    | `/api/monitor/dashboard` | Dashboard data       |
| GET    | `/api/monitor/health`    | Health check         |
| GET    | `/api/monitor/events`    | SSE stream           |
| WS     | `/api/monitor/ws`        | WebSocket connection |

## Configuration

All settings have sensible defaults. No configuration needed for development.

Settings can be customized in `app/core/config.py` if needed.
