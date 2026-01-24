from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .exceptions import WebtopLoginError, WebtopRequestError
from .models import WebtopSession

DEFAULT_BASE_URL = "https://webtopserver.smartschool.co.il"


class WebtopClient:
    """
    Async client for Webtop (SmartSchool).

    Auth model:
      - Login returns JSON with data.token
      - Token must be sent as cookie: webToken=<token>
    """

    def __init__(
        self,
        username: str,
        password: str,
        *,
        data: str = "+Aabe7FAdVluG6Lu+0ibrA==",
        remember_me: bool = False,
        biometric_login: str = "",
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
        auto_login: bool = True,
    ):
        self._username = username
        self._password = password
        self._data = data
        self._remember_me = remember_me
        self._biometric_login = biometric_login

        self._base_url = base_url.rstrip("/")
        self._auto_login = auto_login

        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json; charset=utf-8"},
            follow_redirects=True,
        )

        self._session: Optional[WebtopSession] = None

    async def __aenter__(self) -> "WebtopClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._http.aclose()

    @property
    def is_logged_in(self) -> bool:
        return self._session is not None

    @property
    def session(self) -> WebtopSession:
        if not self._session:
            raise WebtopLoginError("Not logged in. Call await client.login() first.")
        return self._session

    async def login(self) -> WebtopSession:
        """
        Perform ONLY the login call.
        """
        resp = await self._http.post(
            "/server/api/user/LoginByUserNameAndPassword",
            json={
                "UserName": self._username,
                "Password": self._password,
                "Data": self._data,
                "RememberMe": self._remember_me,
                "BiometricLogin": self._biometric_login,
            },
        )

        if resp.status_code >= 400:
            raise WebtopLoginError(f"Login failed ({resp.status_code}): {resp.text}")

        try:
            body = resp.json()
        except Exception as e:
            raise WebtopLoginError(f"Login response is not JSON: {e}") from e

        if body.get("status") is not True:
            raise WebtopLoginError(
                f"Login returned status=false. "
                f"errorDescription={body.get('errorDescription')!r}, errorId={body.get('errorId')!r}"
            )

        data = body.get("data") or {}
        token = data.get("token")
        if not token:
            raise WebtopLoginError("Login succeeded but data.token is missing")

        # ✅ Webtop requires token as cookie: webToken=<token>
        self._http.cookies.set("webToken", token)

        self._session = WebtopSession(
            token=token,
            user_id=data.get("userId"),
            student_id=data.get("studentId"),
            school_id=data.get("schoolId"),
            school_name=data.get("schoolName"),
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            raw_login_data=data,
        )
        return self._session

    async def ensure_logged_in(self) -> None:
        if self._session:
            return
        if not self._auto_login:
            raise WebtopLoginError("Not logged in and auto_login=False. Call await client.login().")
        await self.login()

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Authenticated request helper.
        Since auth is cookie-based (webToken), we only ensure login here.
        """
        await self.ensure_logged_in()

        final_headers: Dict[str, str] = {}
        if headers:
            final_headers.update(headers)

        resp = await self._http.request(method, path, headers=final_headers, **kwargs)

        if resp.status_code >= 400:
            raise WebtopRequestError(f"{method} {path} failed ({resp.status_code}): {resp.text}")

        return resp

    # -----------------------------
    # Endpoints
    # -----------------------------
    async def get_students(self) -> Any:
        """
        POST /server/api/dashboard/InitDashboard
        Body: {}
        Auth: cookie webToken
        """
        resp = await self.request(
            "POST",
            "/server/api/dashboard/InitDashboard",
            json={},
        )
        return resp.json()

    async def get_homework(
        self,
        *,
        encrypted_student_id: str,
        class_code: int,
        class_number: int,
    ) -> Any:
        """
        Get homework from Webtop.

        POST /server/api/dashboard/GetHomeWork

        Auth:
          - Cookie: webToken=<token>

        Params:
          encrypted_student_id: value from login data['id']
          class_code: ClassCode
          class_number: ClassNumber
        """
        resp = await self.request(
            "POST",
            "/server/api/dashboard/GetHomeWork",
            json={
                "id": encrypted_student_id,
                "ClassCode": class_code,
                "ClassNumber": class_number,
            },
        )
        return resp.json()

    async def get_discipline_events(
        self,
        *,
        encrypted_student_id: str,
        class_code: int,
    ) -> Any:
        """
        Get pupil discipline (behavior) events.

        POST /server/api/dashboard/GetPupilDiciplineEvents

        Auth:
          - Cookie: webToken=<token>

        Params:
          encrypted_student_id: value from login data['id']
          class_code: ClassCode
        """
        resp = await self.request(
            "POST",
            "/server/api/dashboard/GetPupilDiciplineEvents",
            json={
                "id": encrypted_student_id,
                "ClassCode": class_code,
            },
        )
        return resp.json()
    
    async def get_preview_unread_notifications(self) -> Any:
        """
        Get preview of unread notifications.

        POST /server/api/Menu/GetPreviewUnreadNotifications

        Auth:
          - Cookie: webToken=<token>
        """
        resp = await self.request(
            "POST",
            "/server/api/Menu/GetPreviewUnreadNotifications",
            json={},  # empty body
        )
        return resp.json()
    
    async def get_notification_settings(
        self,
        *,
        encrypted_student_id: str,
    ) -> Any:
        """
        Get notification settings for the user.

        POST /server/api/Notification/GetNotificationsSettings

        Auth:
          - Cookie: webToken=<token>

        Params:
          encrypted_student_id: value from login data['id']
        """
        resp = await self.request(
            "POST",
            "/server/api/Notification/GetNotificationsSettings",
            json={
                "id": encrypted_student_id,
            },
        )
        return resp.json()

    async def get_messages_inbox(
        self,
        *,
        page_id: int = 1,
        label_id: int = 0,
        has_read: Optional[bool] = None,
        search_query: str = "",
    ) -> Any:
        """
        Get messages inbox.

        POST /server/api/messageBox/GetMessagesInbox

        Auth:
          - Cookie: webToken=<token>

        Params:
          page_id: page number (1-based)
          label_id: message label/category
          has_read: filter by read status (True / False / None)
          search_query: free-text search
        """
        resp = await self.request(
            "POST",
            "/server/api/messageBox/GetMessagesInbox",
            json={
                "PageId": page_id,
                "LabelId": label_id,
                "HasRead": has_read,
                "SearchQuery": search_query,
            },
        )
        return resp.json()

    async def get_pupil_schedule(
        self,
        *,
        week_index: int = 0,
        view_type: int = 0,
        study_year: int,
        encrypted_student_id: str,
        class_code: int,
        module_id: int = 10,
    ) -> Any:
        """
        Get pupil schedule (timetable).

        POST /server/api/PupilCard/GetPupilScheduale

        Auth:
          - Cookie: webToken=<token>

        Params:
          week_index: week offset (0 = current week)
          view_type: schedule view type (usually 0)
          study_year: school year (e.g. 2026)
          encrypted_student_id: value from login data['id']
          class_code: ClassCode
          module_id: module identifier (usually 10)
        """
        resp = await self.request(
            "POST",
            "/server/api/PupilCard/GetPupilScheduale",
            json={
                "weekIndex": week_index,
                "viewType": view_type,
                "studyYear": study_year,
                "studentID": encrypted_student_id,
                "classCode": class_code,
                "moduleID": module_id,
            },
        )
        return resp.json()
