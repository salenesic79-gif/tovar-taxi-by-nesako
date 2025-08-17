from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Dobrodošao u Taxi projekat!</h1><p>Server radi!</p>")
from django.http import HttpResponse

def lista_tovara(request):
    return HttpResponse("Ovo je lista svih tovarnih jedinica.")

def detalji_tovara(request, tovar_id):
    return HttpResponse(f"Detalji tovara sa ID-jem: {tovar_id}")
