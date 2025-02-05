#!/usr/bin/env python3
import requests
from django.http import JsonResponse
from django.shortcuts import render
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper


def doc_api_guide(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "API Documentation",
    })
    return render(request, 'docs/api_guide.html', context)


def yaml_api_guide(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "API Documentation",
    })
    return render(request, 'docs/api_guide.yaml', context, content_type='text/yaml')


def json_api_guide(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "API Documentation",
    })
    return render(request, 'docs/api_guide.json', context, content_type='text/json')
