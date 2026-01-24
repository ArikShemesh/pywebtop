# pywebtop

An unofficial async Python API wrapper for **Webtop** (SmartSchool educational platform). This library provides easy access to Webtop's student portal API endpoints for retrieving grades, homework, schedules, messages, notifications, and more.

## Features

- 🔐 **Async/Await Support** - Built on `httpx` for modern async Python
- 📚 **Student Portal Access** - Login and retrieve student information
- 📖 **Homework & Assignments** - Get homework details by class
- 📅 **Schedule/Timetable** - Retrieve pupil schedules for any week
- 💬 **Messaging System** - Access message inbox with filtering
- 🔔 **Notifications** - Get unread notifications and notification settings
- 📊 **Discipline Events** - Retrieve behavior/discipline records
- ⚙️ **Configurable** - Custom base URL, timeout, and auto-login support

## Installation

Install via pip:

```bash
pip install pywebtop
```

Or from source:

```bash
git clone https://github.com/t0mer/pywebtop.git
cd pywebtop
pip install -e .
```

### Requirements

- Python 3.8+
- `httpx>=0.25,<1.0`

## Quick Start

### Basic Usage

```python
import asyncio
from webtop import WebtopClient

async def main():
    # Create client and login
    async with WebtopClient(username="your_username", password="your_password") as client:
        # Login automatically happens on first API call
        session = await client.login()
        print(f"Logged in as: {session.first_name} {session.last_name}")
        
        # Get students dashboard
        dashboard = await client.get_students()
        print(dashboard)

asyncio.run(main())
```

### Without Auto-Login

If you prefer to control login manually:

```python
async with WebtopClient(
    username="your_username",
    password="your_password",
    auto_login=False
) as client:
    # Manually call login
    session = await client.login()
    
    # Now make requests
    dashboard = await client.get_students()
```

## API Reference

### Client Initialization

```python
WebtopClient(
    username: str,
    password: str,
    *,
    data: str = "+Aabe7FAdVluG6Lu+0ibrA==",
    remember_me: bool = False,
    biometric_login: str = "",
    base_url: str = "https://webtopserver.smartschool.co.il",
    timeout: float = 20.0,
    auto_login: bool = True,
)
```

**Parameters:**
- `username` - Webtop username
- `password` - Webtop password
- `data` - Encryption data (default value works for SmartSchool)
- `remember_me` - Whether to remember login (boolean)
- `biometric_login` - Biometric login token (if available)
- `base_url` - Webtop server URL (defaults to SmartSchool Israel)
- `timeout` - Request timeout in seconds
- `auto_login` - Automatically login before requests (default: True)

### Methods

#### Authentication

##### `login()`
Perform login and establish session.

```python
session = await client.login()
# session.token - auth token
# session.user_id - user ID
# session.student_id - student ID
# session.school_name - school name
# session.first_name, session.last_name - user names
```

#### Dashboard & Students

##### `get_students()`
Get student dashboard data with list of students.

```python
dashboard = await client.get_students()
```

#### Homework & Assignments

##### `get_homework()`
Get homework for a specific class.

```python
homework = await client.get_homework(
    encrypted_student_id="rgIuvaSjTq1Iizmx8TyS/kVbqExiqaKN+HMmES/FcEoTjO1W4c5lY96Ca0/fef3I+++qdhjhoN7aLAqTStKx9AX8C2pLhUJBAZzXH3rEC+w=",
    class_code=3,
    class_number=3,
)
```

**Parameters:**
- `encrypted_student_id` - Student ID from login response
- `class_code` - Class code
- `class_number` - Class number

#### Schedule & Timetable

##### `get_pupil_schedule()`
Get student schedule/timetable for a specific week.

```python
schedule = await client.get_pupil_schedule(
    week_index=0,           # 0 = current week
    view_type=0,            # schedule view type
    study_year=2026,        # school year
    encrypted_student_id="...",
    class_code=3,
    module_id=10,
)
```

**Parameters:**
- `week_index` - Week offset (0 = current week, 1 = next week, etc.)
- `view_type` - Schedule view type (usually 0)
- `study_year` - School year (e.g., 2026)
- `encrypted_student_id` - Student ID from login response
- `class_code` - Class code
- `module_id` - Module ID (default: 10)

#### Messaging

##### `get_messages_inbox()`
Get messages from inbox with pagination and filtering.

```python
messages = await client.get_messages_inbox(
    page_id=1,
    label_id=0,
    has_read=None,          # None, True, or False to filter
    search_query="",
)
```

**Parameters:**
- `page_id` - Page number (1-based, default: 1)
- `label_id` - Message label/category (default: 0)
- `has_read` - Filter by read status (None for all, default: None)
- `search_query` - Free-text search (default: "")

#### Notifications

##### `get_preview_unread_notifications()`
Get preview of unread notifications.

```python
notifications = await client.get_preview_unread_notifications()
```

##### `get_notification_settings()`
Get notification settings for the user.

```python
settings = await client.get_notification_settings(
    encrypted_student_id="...",
)
```

**Parameters:**
- `encrypted_student_id` - Student ID from login response

#### Discipline & Behavior

##### `get_discipline_events()`
Get student behavior/discipline events.

```python
discipline = await client.get_discipline_events(
    encrypted_student_id="...",
    class_code=3,
)
```

**Parameters:**
- `encrypted_student_id` - Student ID from login response
- `class_code` - Class code

### Session Properties

After login, access session information via `client.session`:

```python
session = client.session
print(session.token)           # Auth token
print(session.user_id)         # User ID
print(session.student_id)      # Student ID
print(session.school_id)       # School ID
print(session.school_name)     # School name
print(session.first_name)      # First name
print(session.last_name)       # Last name
print(session.raw_login_data)  # Raw login response data
```

### Connection Management

#### Check Login Status

```python
if client.is_logged_in:
    print("Already logged in")
```

#### Manual Close

```python
await client.close()  # or use 'async with' for auto-close
```

## Examples

### Complete Example: Get Homework

```python
import asyncio
from webtop import WebtopClient

async def get_homework_example():
    async with WebtopClient(
        username="",
        password=""
    ) as client:
        # Get students to find IDs
        dashboard = await client.get_students()
        student = dashboard['data'][0]  # Get first student
        encrypted_id = student['id']
        
        # Get homework
        homework = await client.get_homework(
            encrypted_student_id=encrypted_id,
            class_code=3,
            class_number=3,
        )
        print(homework)

asyncio.run(get_homework_example())
```

### Complete Example: Check Schedule

```python
import asyncio
from webtop import WebtopClient
from datetime import datetime

async def check_schedule():
    async with WebtopClient(
        username="",
        password=""
    ) as client:
        dashboard = await client.get_students()
        student = dashboard['data'][0]
        
        # Get this week's schedule
        schedule = await client.get_pupil_schedule(
            week_index=0,
            study_year=2026,
            encrypted_student_id=student['id'],
            class_code=student['classCode'],
        )
        
        print(f"Schedule for week {datetime.now().isocalendar()[1]}:")
        print(schedule)

asyncio.run(check_schedule())
```

### Complete Example: Get Messages

```python
import asyncio
from webtop import WebtopClient

async def check_messages():
    async with WebtopClient(
        username="",
        password=""
    ) as client:
        # Get unread messages
        messages = await client.get_messages_inbox(
            page_id=1,
            has_read=False,  # Only unread
        )
        
        print(f"Found {len(messages.get('data', []))} unread messages")
        for msg in messages.get('data', []):
            print(f"  - {msg['sender']}: {msg['subject']}")

asyncio.run(check_messages())
```

## Error Handling

The library provides specific exceptions for error handling:

```python
from webtop import WebtopClient, WebtopLoginError, WebtopRequestError

try:
    async with WebtopClient(username="user", password="pass") as client:
        dashboard = await client.get_students()
except WebtopLoginError as e:
    print(f"Login failed: {e}")
except WebtopRequestError as e:
    print(f"API request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**Exception Types:**
- `WebtopError` - Base exception class
- `WebtopLoginError` - Raised when login fails or not logged in
- `WebtopRequestError` - Raised when API request fails

## Authentication Details

### How Authentication Works

1. **Login Request** - Send username/password to `/server/api/user/LoginByUserNameAndPassword`
2. **Token Response** - Server returns `data.token` in the response
3. **Cookie-Based Auth** - Token is set as cookie: `webToken=<token>`
4. **Subsequent Requests** - All API calls automatically include the `webToken` cookie

### Cookie Management

Authentication is handled automatically via httpx's cookie jar. The token is stored as a cookie and included in all subsequent requests.

## Configuration

### Custom Base URL

If you use a custom Webtop server:

```python
async with WebtopClient(
    username="user",
    password="pass",
    base_url="https://custom-webtop-server.example.com"
) as client:
    # Use custom server
    dashboard = await client.get_students()
```

### Timeout Configuration

Adjust request timeout:

```python
async with WebtopClient(
    username="user",
    password="pass",
    timeout=30.0  # 30 seconds
) as client:
    dashboard = await client.get_students()
```

### Remember Me

Enable remember-me login:

```python
async with WebtopClient(
    username="user",
    password="pass",
    remember_me=True
) as client:
    await client.login()
```

## Project Structure

```
pywebtop/
├── webtop/
│   ├── __init__.py           # Package exports
│   ├── client.py             # Main WebtopClient class
│   ├── models.py             # Data models (WebtopSession)
│   └── exceptions.py         # Custom exceptions
├── test.py                   # Test script
├── setup.py                  # Package setup
└── README.md                 # This file
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/t0mer/pywebtop.git
cd pywebtop

# Install in development mode with dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
python test.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

**Tomer Klein** - [GitHub](https://github.com/t0mer) - tomer.klein@gmail.com

## Disclaimer

This is an **unofficial** wrapper for the Webtop API. It is not affiliated with or endorsed by SmartSchool. Use at your own risk and ensure compliance with Webtop's Terms of Service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub Issues](https://github.com/t0mer/pywebtop/issues)
- Contact the author

## Changelog

### Version 0.0.1
- Initial release
- Login functionality
- Dashboard access
- Homework retrieval
- Schedule/timetable access
- Messaging system
- Notifications
- Discipline events tracking

## Related Projects

- [pymashov](https://github.com/t0mer/pymashov) - Another Mashov wrapper

---

**Last Updated:** January 2026