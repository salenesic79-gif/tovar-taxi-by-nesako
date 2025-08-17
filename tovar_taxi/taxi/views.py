from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Dobrodošao u Taxi projekat!</h1><p>Server radi!</p>")
