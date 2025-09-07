from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    ROLE_CHOICES = [
        ('naručilac', 'Naručilac transporta'),
        ('prevoznik', 'Prevoznik'),
        ('vozač', 'Vozač'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    pib = models.CharField(max_length=20, blank=True, verbose_name='PIB')
    maticni_broj = models.CharField(max_length=20, blank=True, verbose_name='Matični broj')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('kombi', 'Kombi'),
        ('kamion', 'Kamion'),
        ('šleper', 'Šleper'),
        ('mega_trailer', 'Mega trailer'),
    ]
    
    VEHICLE_BRANDS = [
        ('mercedes', 'Mercedes-Benz'),
        ('volvo', 'Volvo'),
        ('scania', 'Scania'),
        ('man', 'MAN'),
        ('daf', 'DAF'),
        ('iveco', 'Iveco'),
        ('renault', 'Renault Trucks'),
        ('ford', 'Ford'),
        ('isuzu', 'Isuzu'),
        ('fiat', 'Fiat'),
    ]
    
    VEHICLE_COLORS = [
        ('bela', 'Bela'),
        ('crna', 'Crna'),
        ('siva', 'Siva'),
        ('plava', 'Plava'),
        ('crvena', 'Crvena'),
        ('zelena', 'Zelena'),
        ('zuta', 'Žuta'),
        ('narandzasta', 'Narandžasta'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_brand = models.CharField(max_length=20, choices=VEHICLE_BRANDS, default='mercedes')
    vehicle_color = models.CharField(max_length=20, choices=VEHICLE_COLORS, default='bela')
    license_plate = models.CharField(max_length=20, unique=True)
    transport_license = models.CharField(max_length=50, blank=True, help_text="Broj dozvole za prevoz tereta")
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Kapacitet u tonama")
    volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Zapremina u m³")
    loading_height = models.IntegerField(default=250, help_text="Visina utovarnog dela u cm")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.license_plate} - {self.get_vehicle_type_display()}"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nacrt'),
        ('published', 'Objavljeno'),
        ('in_progress', 'U toku'),
        ('completed', 'Završeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shipments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Lokacije
    pickup_address = models.CharField(max_length=300)
    delivery_address = models.CharField(max_length=300)
    pickup_city = models.CharField(max_length=100)
    delivery_city = models.CharField(max_length=100)
    
    # Teret
    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Težina u tonama")
    cargo_volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Zapremina u m³")
    cargo_type = models.CharField(max_length=100)
    
    # Cena i status
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Datumi
    pickup_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.pickup_city} → {self.delivery_city}"


class ShipmentOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('accepted', 'Prihvaćena'),
        ('rejected', 'Odbijena'),
    ]
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='offers')
    carrier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ponuda za {self.shipment.title} - {self.price} RSD"


class Tour(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Potvrđena'),
        ('in_progress', 'U toku'),
        ('pickup_confirmed', 'Preuzeto'),
        ('delivered', 'Isporučeno'),
        ('completed', 'Završena'),
        ('cancelled', 'Otkazana'),
    ]
    
    CARGO_TYPE_CHOICES = [
        ('paleta', 'Paleta 120x80'),
        ('paketna_roba', 'Paketna roba'),
        ('paleta_paketna_roba', 'Paleta ili paketna roba'),
        ('rasuti_teret', 'Rasuti teret'),
        ('tečni_teret', 'Tečni teret'),
    ]
    
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    offer = models.OneToOneField(ShipmentOffer, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    # Geolokacija i ruta
    polaziste = models.CharField(max_length=255, help_text="Polazište ture")
    odrediste = models.CharField(max_length=255, help_text="Odredište ture")
    planirana_putanja = models.CharField(max_length=100, blank=True, help_text="Planirana putanja/autoput")
    
    # Dotovar informacije
    dostupno_za_dotovar = models.CharField(max_length=50, choices=CARGO_TYPE_CHOICES, help_text="Tip tereta dostupan za dotovar")
    kapacitet = models.DecimalField(max_digits=10, decimal_places=2, help_text="Dostupan kapacitet u tonama")
    slobodna_kilaza = models.DecimalField(max_digits=10, decimal_places=2, help_text="Slobodna kilaža u kg")
    
    # Koordinate
    polaziste_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    polaziste_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    odrediste_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    odrediste_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    pickup_confirmed_at = models.DateTimeField(null=True, blank=True)
    delivery_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.shipment:
            return f"Tura: {self.shipment.title}"
        return f"Tura: {self.polaziste} → {self.odrediste}"


class ChatMessage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_offer', 'Nova ponuda'),
        ('offer_accepted', 'Ponuda prihvaćena'),
        ('offer_rejected', 'Ponuda odbijena'),
        ('tour_confirmed', 'Tura potvrđena'),
        ('pickup_confirmed', 'Preuzimanje potvrđeno'),
        ('delivery_confirmed', 'Isporuka potvrđena'),
        ('new_message', 'Nova poruka'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Opciono povezivanje sa objektima
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Location(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lokacija za {self.tour} - {self.timestamp}"


class PaymentReservation(models.Model):
    """Model za rezervaciju sredstava - B2B funkcionalnost"""
    PAYMENT_STATUS_CHOICES = [
        ('reserved', 'Rezervisano'),
        ('captured', 'Naplaćeno'),
        ('released', 'Oslobođeno'),
        ('failed', 'Neuspešno'),
    ]
    
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='payment_reservation')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RSD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='reserved')
    reserved_at = models.DateTimeField(auto_now_add=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='card')
    transaction_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"Rezervacija {self.amount} {self.currency} za {self.shipment}"


class InstantDelivery(models.Model):
    """Model za instant dostavu - Uber/Glovo funkcionalnost"""
    DELIVERY_TYPE_CHOICES = [
        ('express', 'Express (do 1h)'),
        ('same_day', 'Isti dan'),
        ('scheduled', 'Zakazano'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('accepted', 'Prihvaćeno'),
        ('pickup', 'Preuzimanje'),
        ('in_transit', 'U tranzitu'),
        ('delivered', 'Dostavljeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instant_deliveries')
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    pickup_coordinates = models.CharField(max_length=50, blank=True)
    delivery_coordinates = models.CharField(max_length=50, blank=True)
    
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    item_description = models.TextField()
    estimated_weight = models.DecimalField(max_digits=5, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    
    assigned_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries')
    
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField()
    
    def __str__(self):
        return f"Instant dostava #{self.id} - {self.status}"


class FoodDelivery(models.Model):
    """Model za dostavu hrane - Donesi funkcionalnost"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('confirmed', 'Potvrđeno'),
        ('preparing', 'Priprema se'),
        ('ready', 'Spremno za preuzimanje'),
        ('pickup', 'Preuzeto'),
        ('delivered', 'Dostavljeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_orders')
    restaurant_name = models.CharField(max_length=200)
    restaurant_address = models.TextField()
    
    delivery_address = models.TextField()
    customer_phone = models.CharField(max_length=20)
    
    items = models.JSONField()  # Lista stavki narudžbine
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=200.00)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    assigned_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='food_deliveries')
    
    ordered_at = models.DateTimeField(auto_now_add=True)
    estimated_preparation = models.IntegerField(default=30)  # minuti
    estimated_delivery = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"Narudžbina #{self.id} - {self.restaurant_name}"


class DriverLocation(models.Model):
    """Model za praćenje lokacije vozača - GPS tracking"""
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(default=0.0)
    speed = models.FloatField(default=0.0)
    heading = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.driver.username} - {self.latitude}, {self.longitude}"


class DeliveryRating(models.Model):
    """Model za ocenjivanje dostave"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    delivery = models.OneToOneField(InstantDelivery, on_delete=models.CASCADE, related_name='rating', null=True, blank=True)
    food_delivery = models.OneToOneField(FoodDelivery, on_delete=models.CASCADE, related_name='rating', null=True, blank=True)
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ocena {self.rating}/5 za {self.driver.username}"


class PremiumSubscription(models.Model):
    """Model za premium pretplate - B2B funkcionalnost"""
    SUBSCRIPTION_TYPES = [
        ('basic', 'Basic - 5% popust'),
        ('premium', 'Premium - 10% popust + odloženo plaćanje'),
        ('enterprise', 'Enterprise - 15% popust + mesečna faktura'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='premium_subscription')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    
    deferred_payment_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sound_file = models.CharField(max_length=50, default='ping.mp3')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"


class Cargo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('reserved', 'Rezervisano'),
        ('assigned', 'Dodeljeno prevozniku'),
        ('in_transit', 'U transportu'),
        ('delivered', 'Isporučeno'),
        ('paid', 'Plaćeno'),
    ]
    
    # Povezivanje sa postojećim sistemom
    posiljilac = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posiljke')
    prevoznik = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teretni_poslovi')
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True, related_name='tereti')
    
    # Informacije o teretu
    tezina = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.1)])
    broj_paleta = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opis_tereta = models.TextField(blank=True)
    
    # Lokacije
    polazna_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    polazna_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    polazna_adresa = models.CharField(max_length=255)
    
    odredisna_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    odredisna_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    odredisna_adresa = models.CharField(max_length=255)
    
    # Cene i plaćanje
    udaljenost_km = models.DecimalField(max_digits=8, decimal_places=2)
    cena_za_posiljaoce = models.DecimalField(max_digits=10, decimal_places=2)
    cena_za_prevoznika = models.DecimalField(max_digits=10, decimal_places=2)  # minus 15%
    app_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 15% fee
    payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Eko-ambalaža
    eko_ambalaza = models.TextField(blank=True)
    
    # Status i vreme
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    kreiran = models.DateTimeField(auto_now_add=True)
    isporucen = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Automatski izračunaj cene
        if self.cena_za_posiljaoce and not self.cena_za_prevoznika:
            self.app_fee = self.cena_za_posiljaoce * 0.15  # 15% fee
            self.cena_za_prevoznika = self.cena_za_posiljaoce - self.app_fee
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Teret {self.id} - {self.broj_paleta} paleta - {self.status}"


class CenaPoKilometrazi(models.Model):
    """Tabela cena za palete po udaljenosti"""
    broj_paleta = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    cena_do_200km = models.DecimalField(max_digits=10, decimal_places=2)
    cena_preko_200km = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['broj_paleta']
        verbose_name = 'Cena po kilometraži'
        verbose_name_plural = 'Cene po kilometraži'
    
    def __str__(self):
        return f"{self.broj_paleta} paleta: {self.cena_do_200km}/{self.cena_preko_200km} RSD"
