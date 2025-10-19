# acc/forge.py
import os, time, math
from typing import Dict, Any, Optional, Tuple
import requests
from requests_oauthlib import OAuth2Session

AUTH_BASE = "https://developer.api.autodesk.com/authentication/v2/authorize"
TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"
BASE_URL  = "https://developer.api.autodesk.com"
SCOPES = os.getenv("ACC_SCOPES", "data:read").split()

CLIENT_ID = os.getenv("ACC_CLIENT_ID")
CLIENT_SECRET = os.getenv("ACC_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ACC_REDIRECT_URI")

def oauth_client(state: Optional[str]=None) -> OAuth2Session:
    return OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        state=state
    )

def auth_url() -> Tuple[str, str]:
    oauth = oauth_client()
    authorization_url, state = oauth.authorization_url(AUTH_BASE)
    return authorization_url, state

def exchange_code_for_token(code: str) -> Dict[str, Any]:
    oauth = oauth_client()
    token = oauth.fetch_token(
        token_url=TOKEN_URL,
        client_secret=CLIENT_SECRET,
        code=code,
        include_client_id=True,
    )
    return token

def refresh_token(refresh_token: str) -> Dict[str, Any]:
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    resp = requests.post(TOKEN_URL, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def _bearer(session) -> Dict[str, str]:
    return {"Authorization": f"Bearer {session['token']['access_token']}"}

def with_refresh(session, fn):
    
    try:
        return fn()
    except requests.HTTPError as e:
        if e.response.status_code == 401 and "token" in session and "refresh_token" in session["token"]:
            newtok = refresh_token(session["token"]["refresh_token"])
            session["token"] = newtok
            return fn()
        raise

def backoff_request(method, url, headers=None, params=None):
   
    attempt = 0
    while True:
        resp = requests.request(method, url, headers=headers, params=params, timeout=60)
        if resp.status_code != 429:
            resp.raise_for_status()
            return resp
        attempt += 1
        wait = min(60, (2 ** attempt) + (math.floor(1000 * time.time()) % 1000) / 1000)
        time.sleep(wait)

def paginated_get(session, url, params=None):
    
    params = params or {}
    headers = _bearer(session)
    results = []
    while True:
        resp = backoff_request("GET", url, headers=headers, params=params)
        data = resp.json()
        if isinstance(data, dict) and "data" in data:
            results.extend(data["data"])
            
            links = data.get("links", {})
            next_url = (links.get("next") or {}).get("href")
            if next_url:
                url, params = next_url, {}
                continue
        else:
            results.extend(data if isinstance(data, list) else [data])
        break
    return results

def get_hubs(session):
    return paginated_get(session, f"{BASE_URL}/project/v2/hubs")

def get_projects(session, hub_id: str):
    return paginated_get(session, f"{BASE_URL}/project/v2/hubs/{hub_id}/projects")

def get_top_folders(session, project_id: str):
    return paginated_get(session, f"{BASE_URL}/data/v1/projects/{project_id}/topFolders")

def get_folder_contents(session, project_id: str, folder_id: str):
    return paginated_get(session, f"{BASE_URL}/data/v1/projects/{project_id}/folders/{folder_id}/contents")

def get_folder_permissions(session, project_id: str, folder_id: str):
   
    return paginated_get(session, f"{BASE_URL}/construction/admin/v1/projects/{project_id}/folders/{folder_id}/permissions")
