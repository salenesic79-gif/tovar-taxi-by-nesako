from django.contrib import admin
from .models import Profile, Vehicle, Shipment, ShipmentOffer

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'company_name', 'is_verified', 'created_at')
    list_filter = ('user_type', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'tax_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('user', 'user_type', 'is_verified')
        }),
        ('Kontakt informacije', {
            'fields': ('phone_number', 'address')
        }),
        ('Poslovne informacije', {
            'fields': ('company_name', 'tax_number')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'max_weight', 'is_active', 'created_at')
    list_filter = ('vehicle_type', 'is_active', 'created_at')
    search_fields = ('license_plate', 'owner__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('owner', 'vehicle_type', 'license_plate', 'is_active')
        }),
        ('Specifikacije', {
            'fields': ('max_weight', 'max_volume', 'length', 'width', 'height')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'shipper', 'pickup_city', 'delivery_city', 'status', 'offered_price', 'created_at')
    list_filter = ('status', 'cargo_type', 'created_at', 'pickup_country', 'delivery_country')
    search_fields = ('reference_number', 'shipper__username', 'pickup_city', 'delivery_city')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('reference_number', 'shipper', 'carrier', 'vehicle', 'status')
        }),
        ('Lokacije preuzimanja', {
            'fields': ('pickup_address', 'pickup_city', 'pickup_postal_code', 'pickup_country')
        }),
        ('Lokacije dostave', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_postal_code', 'delivery_country')
        }),
        ('Informacije o teretu', {
            'fields': ('cargo_type', 'cargo_description', 'weight', 'volume')
        }),
        ('Datumi', {
            'fields': ('pickup_date', 'delivery_date')
        }),
        ('Cene', {
            'fields': ('offered_price', 'final_price')
        }),
        ('Dodatne informacije', {
            'fields': ('special_requirements', 'contact_person', 'contact_phone')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ShipmentOffer)
class ShipmentOfferAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'carrier', 'vehicle', 'offered_price', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('shipment__reference_number', 'carrier__username', 'vehicle__license_plate')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('shipment', 'carrier', 'vehicle', 'is_accepted')
        }),
        ('Ponuda', {
            'fields': ('offered_price', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
