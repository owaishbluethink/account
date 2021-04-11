from django.shortcuts import render,get_object_or_404
from django .http import HttpResponse
import requests,datetime


def login(request):
    return render(request, 'account/login.html')

def register(request):
    return render(request,'account/register.html')


