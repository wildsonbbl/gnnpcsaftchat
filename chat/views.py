"request handler."

import json
import os.path as osp

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import ChatSession

file_dir = osp.dirname(__file__)


def about(request):
    "handle request for about page"
    return render(request, "about.html")


def chat(request):
    "handle request for chat"
    return render(
        request,
        "chat.html",
    )


@require_http_methods(["GET"])
def get_sessions(request):  # pylint: disable=unused-argument
    """Get all sessions"""
    sessions = list(
        ChatSession.objects.values("session_id", "name", "created_at", "updated_at")
    )
    return JsonResponse({"sessions": sessions})


@require_http_methods(["POST"])
def create_session(request):
    """Create a new session"""
    data = json.loads(request.body)
    name = data.get("name", "New Session")
    session = ChatSession.objects.create(name=name)
    return JsonResponse({"session_id": str(session.session_id), "name": session.name})


@require_http_methods(["DELETE"])
def delete_session(request, session_id):  # pylint: disable=unused-argument
    """Delete a session"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        session.delete()
        return JsonResponse({"success": True})
    except ChatSession.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Session not found"}, status=404
        )


def service_worker(request):  # pylint: disable=unused-argument
    "serve root service worker"
    with open(
        settings.STATIC_ROOT / "js/serviceworker.js", encoding="utf-8"
    ) as serviceworker_file:
        return HttpResponse(
            serviceworker_file.read(),
            content_type="application/javascript",
        )
