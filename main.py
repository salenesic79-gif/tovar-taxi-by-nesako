<!-- driver_terms.html -->
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <div>
    <input type="checkbox" id="terms_checkbox" required>
    <label for="terms_checkbox">Prihvatam uslove korišćenja.</label>
  </div>
  <button type="submit" class="btn btn-primary">Potvrdi</button>
</form>
# views.py
@login_required
def driver_terms(request):
    if request.method == 'POST':
        form = DriverTermsForm(request.POST)
        if form.is_valid():
            terms = form.save(commit=False)
            terms.user = request.user
            terms.terms_accepted = True
            terms.save()
            return redirect('driver_dashboard')
    else:
        form = DriverTermsForm()
    return render(request, 'driver_terms.html', {'form': form})
# forms.py
from django import forms
from .models import DriverTerms

class DriverTermsForm(forms.ModelForm):
    class Meta:
        model = DriverTerms
        fields = ['full_name', 'vehicle_type', 'capacity', 'cargo_height', 'cargo_dimensions', 'location_tracking']
        widgets = {
            'vehicle_type': forms.Select(choices=[
                ('truck', 'Kamion'),
                ('van', 'Kombi'),
                ('trailer', 'Prikolica'),
            ]),
        }
# views.py
def home(request):
    return render(request, 'home.html')

# home.html
<div style="margin-top: 80px; text-align: center;">
  <h2>Da li ste vozač ili tražite transport?</h2>
  <a href="{% url 'driver_register' %}" class="btn btn-primary">Vozač</a>
  <a href="{% url 'customer_order' %}" class="btn btn-success">Tražim transport</a>
</div>
<!-- base.html -->
<header style="background: #ff6600; color: white; padding: 10px; position: fixed; top: 0; width: 100%; z-index: 1000;">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
      <img src="{% static 'images/ttaxi_logo.png' %}" alt="TTaxi Logo" style="height: 50px;">
    </div>
    <div style="font-size: 18px;">
      Dobrodošli, {{ user.get_full_name|default:user.username }}!
    </div>
  </div>
</header>
settings.py
