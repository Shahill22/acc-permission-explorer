# acc/tests/test_routes.py
import json
from django.urls import reverse

def test_me_unauth(client):
    r = client.get(reverse("me"))
    assert r.status_code == 200
    assert r.json()["authenticated"] is False

def test_hubs_unauth(client):
    r = client.get(reverse("list_hubs"))
    assert r.status_code == 401
