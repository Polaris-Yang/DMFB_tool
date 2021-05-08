from django.shortcuts import render
from django.http import HttpResponse
import json
import os


benchmark_name = ['benchmark1', 'benchmark2', 'in_vitro_1', 'protein_1']


# Create your views here.
def index(request):
    return render(request, 'mytool/index.html')


def verify(request):
    paths = request.POST.get('paths')
    if paths is None:
        paths = ''
    return render(request, 'mytool/verification.html', {'paths': paths})


# POST
def get1(request):
    a = request.GET.get('a')
    b = request.GET['b']
    print('a = ' + a + ', b = ' + b)
    return HttpResponse('a = ' + a + ', b = ' + b)


def get2(request):
    a = request.GET.getlist('a')
    a1 = a[0]
    a2 = a[1]
    b = request.GET['b']
    print('a1 = ' + a1 + ', a2 = ' + a2 + ', b = ' + b)
    return HttpResponse('a1 = ' + a1 + ', a2 = ' + a2 + ', b = ' + b)


def learn_temp(request):
    return render(request, 'mytool/tmp.html', {'num': 10})



