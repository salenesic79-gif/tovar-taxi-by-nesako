from django.http import HttpResponse

def pocetna_strana(request):
    return HttpResponse("Dobrodošli u Tovar Taksi aplikaciju NESAKO!")

def lista_tovara(request):
    return HttpResponse("Ovo je lista svih tovarnih jedinica.")

def detalji_tovara(request, tovar_id):
    return HttpResponse(f"Detalji tovara sa ID-jem: {tovar_id}")
