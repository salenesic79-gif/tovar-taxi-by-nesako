from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator
from django.utils import timezone
import json

# Cargo type choices
CARGO_TYPES = [
    ('general', 'Opšti teret'),
    ('fragile', 'Krhki teret'),
    ('hazardous', 'Opasni teret'),
    ('refrigerated', 'Rashladni teret'),
    ('oversized', 'Nadgabaritni teret'),
]

class Profile(models.Model):
    USER_TYPES = [
        ('shipper', 'Naručilac transporta'),
        ('carrier', 'Prevoznik'),
        ('forwarder', 'Špediter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='shipper')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('van', 'Kombi'),
        ('truck', 'Kamion'),
        ('trailer', 'Šleper'),
        ('mega', 'Mega trailer'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    license_plate = models.CharField(max_length=20, unique=True)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Maksimalna nosivost u kg')
    max_volume = models.DecimalField(max_digits=8, decimal_places=2, help_text='Maksimalna zapremina u m³')
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.license_plate} - {self.get_vehicle_type_display()}"

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nacrt'),
        ('published', 'Objavljeno'),
        ('assigned', 'Dodeljeno'),
        ('in_transit', 'U transportu'),
        ('delivered', 'Isporučeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    URGENCY_CHOICES = [
        ('standard', 'Standardno - spremno u naredna 3 radna dana'),
        ('today', 'Danas za danas - hitno'),
        ('asap', 'Što pre moguće - pošiljka spremna'),
        ('weekend', 'Uključiti i subotu u dostupnost'),
    ]
    
    shipper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    carrier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_shipments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Pickup location
    pickup_address = models.CharField(max_length=500, help_text='📍 Adresa preuzimanja')
    pickup_city = models.CharField(max_length=100, blank=True)
    pickup_region = models.CharField(max_length=100, blank=True, help_text='Oblast/Region')
    pickup_postal_code = models.CharField(max_length=20, blank=True)
    pickup_country = models.CharField(max_length=100, default='Srbija')
    pickup_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    pickup_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Delivery location
    delivery_address = models.CharField(max_length=500, help_text='🎯 Adresa dostave')
    delivery_city = models.CharField(max_length=100, blank=True)
    delivery_region = models.CharField(max_length=100, blank=True, help_text='Oblast/Region')
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100, default='Srbija')
    delivery_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    delivery_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Urgency and pricing
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='standard')
    pallet_count = models.PositiveIntegerField(default=1, help_text='Broj paleta')
    cargo_image = models.ImageField(upload_to='cargo_images/', null=True, blank=True, help_text='Slika tovara')
    
    cargo_type = models.CharField(max_length=20, choices=CARGO_TYPES, default='general')
    cargo_description = models.TextField()
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Težina u kg')
    volume = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Zapremina u m³')
    
    # Dates
    pickup_date = models.DateTimeField()
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Ponuđena cena u RSD')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Automatski izračunata cena')
    urgency_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    
    # Additional info
    special_requirements = models.TextField(blank=True, help_text='Posebni zahtevi')
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"TT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference_number} - {self.pickup_city} → {self.delivery_city}"

class City(models.Model):
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    population = models.IntegerField(null=True, blank=True)
    is_major = models.BooleanField(default=False, help_text='Veći grad')
    
    class Meta:
        verbose_name = 'Grad'
        verbose_name_plural = 'Gradovi'
        ordering = ['-is_major', '-population', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.postal_code}) - {self.region}"

class Highway(models.Model):
    HIGHWAY_TYPES = [
        ('highway', 'Autoput'),
        ('main_road', 'Magistralni put'),
        ('regional', 'Regionalni put'),
        ('local', 'Lokalni put'),
    ]
    
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    highway_type = models.CharField(max_length=20, choices=HIGHWAY_TYPES)
    description = models.TextField(blank=True)
    start_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='highways_start')
    end_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='highways_end')
    distance_km = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    toll_road = models.BooleanField(default=False)
    priority = models.IntegerField(default=1, help_text='1=najviša, 5=najniža važnost')
    
    class Meta:
        verbose_name = 'Put'
        verbose_name_plural = 'Putevi'
        ordering = ['priority', 'highway_type', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_highway_type_display()})"

class Route(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=200)
    highways = models.ManyToManyField(Highway, through='RouteHighway')
    total_distance = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    estimated_time = models.DurationField(null=True, blank=True)
    toll_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fuel_cost_estimate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_recommended = models.BooleanField(default=False)
    priority = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rute'
        ordering = ['priority', '-is_recommended']
    
    def __str__(self):
        return f"{self.name} - {self.shipment.reference_number}"

class RouteHighway(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    highway = models.ForeignKey(Highway, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    entry_point = models.CharField(max_length=200, blank=True)
    exit_point = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['route', 'order']

class ShipmentOffer(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='offers')
    carrier = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shipment', 'carrier']
    
    def __str__(self):
        return f"Ponuda za {self.shipment} - {self.price} RSD"


class Tour(models.Model):
    """Model za ture - kompletne transportne zadatke"""
    STATUS_CHOICES = [
        ('kreirana', 'Kreirana'),
        ('potvrdjena', 'Potvrđena'),
        ('u_toku', 'U toku'),
        ('preuzeto', 'Preuzeto'),
        ('isporuceno', 'Isporučeno'),
        ('otkazana', 'Otkazana'),
    ]
    
    id = models.AutoField(primary_key=True)
    vozac = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ture_vozac')
    narucilac = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ture_narucilac')
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='tura')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    
    pocetna_adresa = models.CharField(max_length=255)
    odredisna_adresa = models.CharField(max_length=255)
    datum_polaska = models.DateTimeField()
    kolicina_tereta = models.DecimalField(max_digits=10, decimal_places=2, help_text="u tonama ili m³")
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='kreirana')
    
    # Dodatne informacije
    tip_tereta = models.CharField(max_length=100, blank=True)
    napomene = models.TextField(blank=True)
    kontakt_narucioca = models.CharField(max_length=100, blank=True)
    
    # Potvrde
    preuzimanje_potvrdjeno = models.BooleanField(default=False)
    preuzimanje_vreme = models.DateTimeField(null=True, blank=True)
    preuzimanje_fotografija = models.ImageField(upload_to='preuzimanja/', null=True, blank=True)
    
    isporuka_potvrdjena = models.BooleanField(default=False)
    isporuka_vreme = models.DateTimeField(null=True, blank=True)
    isporuka_fotografija = models.ImageField(upload_to='isporuke/', null=True, blank=True)
    potpis_primaoca = models.TextField(blank=True)  # Base64 potpis
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tura'
        verbose_name_plural = 'Ture'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Tura #{self.id} - {self.pocetna_adresa} → {self.odredisna_adresa}"


class Transaction(models.Model):
    """Model za transakcije i plaćanja"""
    STATUS_CHOICES = [
        ('rezervisano', 'Rezervisano'),
        ('naplaceno', 'Naplaćeno'),
        ('isplaceno', 'Isplaćeno'),
        ('refundirano', 'Refundirano'),
        ('otkazano', 'Otkazano'),
    ]
    
    id = models.AutoField(primary_key=True)
    tura = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='transakcije')
    iznos = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rezervisano')
    
    # Detalji plaćanja
    payment_method = models.CharField(max_length=50, blank=True)  # 'card', 'bank_transfer', 'monthly_invoice'
    payment_id = models.CharField(max_length=100, blank=True)  # ID od payment providera
    
    # Provizija platforme
    provizija_procenat = models.DecimalField(max_digits=5, decimal_places=2, default=12.50)
    provizija_iznos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    datum_transakcije = models.DateTimeField(auto_now_add=True)
    datum_isplate = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transakcija'
        verbose_name_plural = 'Transakcije'
        ordering = ['-datum_transakcije']
    
    def save(self, *args, **kwargs):
        # Automatski izračunaj proviziju
        if not self.provizija_iznos:
            self.provizija_iznos = (self.iznos * self.provizija_procenat) / 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Transakcija #{self.id} - {self.iznos} RSD ({self.status})"


class ChatMessage(models.Model):
    """Model za chat poruke između vozača i naručioca"""
    MESSAGE_TYPES = [
        ('text', 'Tekst'),
        ('image', 'Slika'),
        ('document', 'Dokument'),
        ('location', 'Lokacija'),
        ('system', 'Sistemska poruka'),
    ]
    
    tura = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='chat_poruke')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Sadržaj poruke
    text_content = models.TextField(blank=True)
    image_content = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    document_content = models.FileField(upload_to='chat_documents/', null=True, blank=True)
    location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Chat poruka'
        verbose_name_plural = 'Chat poruke'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Poruka od {self.sender.username} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class TourNotification(models.Model):
    """Model za notifikacije vezane za ture"""
    NOTIFICATION_TYPES = [
        ('nova_tura', 'Nova tura kreirana'),
        ('tura_potvrdjena', 'Tura potvrđena'),
        ('tura_odbijena', 'Tura odbijena'),
        ('preuzimanje_potvrdjeno', 'Preuzimanje potvrđeno'),
        ('isporuka_potvrdjena', 'Isporuka potvrđena'),
        ('nova_poruka', 'Nova chat poruka'),
        ('payment_processed', 'Plaćanje obrađeno'),
    ]
    
    ACTION_TYPES = [
        ('potvrdi_turu', 'Potvrdi turu'),
        ('odbij_turu', 'Odbij turu'),
        ('detalji_ture', 'Detalji ture'),
        ('otvori_chat', 'Otvori chat'),
        ('pozovi', 'Pozovi'),
        ('potvrdi_preuzimanje', 'Potvrdi preuzimanje'),
        ('potvrdi_isporuku', 'Potvrdi isporuku'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tour_notifications')
    tura = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='notifikacije')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, blank=True)
    action_url = models.CharField(max_length=200, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_acted = models.BooleanField(default=False)  # Da li je korisnik reagovao na akciju
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notifikacija ture'
        verbose_name_plural = 'Notifikacije tura'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class Notification(models.Model):
    """Model za čuvanje notifikacija"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    data = models.TextField(blank=True, help_text='JSON data')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Označava notifikaciju kao pročitanu"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])


class Rating(models.Model):
    """Sistem ocenjivanja vozača i naručilaca"""
    RATING_TYPES = [
        ('shipper_to_carrier', 'Naručilac ocenjuje vozača'),
        ('carrier_to_shipper', 'Vozač ocenjuje naručioca'),
    ]
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rating_type = models.CharField(max_length=20, choices=RATING_TYPES)
    stars = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], help_text='Ocena od 1 do 5 zvezda')
    comment = models.TextField(blank=True, help_text='Komentar')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shipment', 'rater', 'rated_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.stars}★ - {self.rater.username} → {self.rated_user.username}"


class LocationTracking(models.Model):
    """GPS tracking vozača tokom transporta"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='location_updates')
    carrier = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    accuracy = models.FloatField(null=True, blank=True, help_text='GPS tačnost u metrima')
    speed = models.FloatField(null=True, blank=True, help_text='Brzina u km/h')
    heading = models.FloatField(null=True, blank=True, help_text='Smer kretanja u stepenima')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['shipment', '-timestamp']),
            models.Index(fields=['carrier', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.shipment.reference_number} - {self.timestamp}"
