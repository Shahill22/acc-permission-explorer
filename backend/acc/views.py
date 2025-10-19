import os
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .forge import auth_url, exchange_code_for_token, with_refresh, \
    get_hubs, get_projects, get_top_folders, get_folder_contents, get_folder_permissions

@require_GET
def auth_login(request):
    url, state = auth_url()
    request.session["oauth_state"] = state
    return JsonResponse({"auth_url": url})

@require_GET
def auth_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    if not code or state != request.session.get("oauth_state"):
        return HttpResponseBadRequest("Invalid state or code")
    token = exchange_code_for_token(code)
    request.session["token"] = token
    return HttpResponseRedirect(os.getenv("FRONTEND_ORIGIN", "http://localhost:9000"))

@require_GET
def auth_logout(request):
    request.session.flush()
    return JsonResponse({"ok": True})

@require_GET
def me(request):
    authed = "token" in request.session
    return JsonResponse({"authenticated": authed})

def _require_auth(request):
    if "token" not in request.session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    return None

@api_view(["GET"])
def list_hubs(request):
    if (resp := _require_auth(request)): return resp
    data = with_refresh(request.session, lambda: get_hubs(request.session))
    return JsonResponse({"data": data})

@api_view(["GET"])
def list_projects(request, hub_id):
    if (resp := _require_auth(request)): return resp
    data = with_refresh(request.session, lambda: get_projects(request.session, hub_id))
    return JsonResponse({"data": data})

@api_view(["GET"])
def list_top_folders(request, project_id):
    if (resp := _require_auth(request)): return resp
    data = with_refresh(request.session, lambda: get_top_folders(request.session, project_id))
    return JsonResponse({"data": data})

@api_view(["GET"])
def list_folder_contents(request, project_id, folder_id):
    if (resp := _require_auth(request)): return resp
    data = with_refresh(request.session, lambda: get_folder_contents(request.session, project_id, folder_id))
    return JsonResponse({"data": data})

@api_view(["GET"])
def folder_permissions(request, project_id, folder_id):
    if (resp := _require_auth(request)): return resp
    data = with_refresh(request.session, lambda: get_folder_permissions(request.session, project_id, folder_id))
    return JsonResponse({"data": data})

