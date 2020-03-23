from django.shortcuts import render

# Create your views here.
import logging
from django.views.generic import View
from builder.index_builder import IndexBuilder
from builder.tasks import add
from djsearch.utils import JsonResponse

log = logging.getLogger(__name__)


def add_delay(request):
    add.delay(2, 3)
    return JsonResponse({"status": 0, "message": "success", "data": []})


class ReIndexView(View):
    def get(self, request):
        index = request.get("index", None)
        if not index:
            return JsonResponse({
                "status": -1,
                "message": "param index is required",
                "data": []
            })

        if IndexBuilder().reindex(index):
            return JsonResponse({
                "status": 0,
                "message": "reindex success",
                "data": []
            })
        else:
            return JsonResponse({
                "status": 1,
                "message": "reindex failed",
                "data": []
            })
