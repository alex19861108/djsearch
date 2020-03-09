from django.shortcuts import render

# Create your views here.
from djsearch.utils import JsonResponse


def build(request):
    from builder.build_resource import Builder
    Builder.build()
    return JsonResponse({"status": 0, "message": "success", "data": []})
