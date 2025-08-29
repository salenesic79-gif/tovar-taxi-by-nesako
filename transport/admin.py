from django.contrib import admin
from .models import Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'phone_number', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('user', 'role')
        }),
        ('Kontakt informacije', {
            'fields': ('phone_number', 'address')
        }),
        ('Poslovne informacije', {
            'fields': ('company_name',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'capacity', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'is_available', 'created_at')
    search_fields = ('license_plate', 'owner__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('owner', 'vehicle_type', 'license_plate', 'is_available')
        }),
        ('Specifikacije', {
            'fields': ('capacity', 'volume')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'pickup_city', 'delivery_city', 'status', 'budget', 'created_at')
    list_filter = ('status', 'cargo_type', 'created_at')
    search_fields = ('title', 'sender__username', 'pickup_city', 'delivery_city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('title', 'sender', 'description', 'status')
        }),
        ('Lokacije preuzimanja', {
            'fields': ('pickup_address', 'pickup_city')
        }),
        ('Lokacije dostave', {
            'fields': ('delivery_address', 'delivery_city')
        }),
        ('Informacije o teretu', {
            'fields': ('cargo_type', 'cargo_weight', 'cargo_volume')
        }),
        ('Datumi', {
            'fields': ('pickup_date', 'delivery_date')
        }),
        ('Cena', {
            'fields': ('budget',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ShipmentOffer)
class ShipmentOfferAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'carrier', 'vehicle', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipment__title', 'carrier__username', 'vehicle__license_plate')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('shipment', 'carrier', 'vehicle', 'status')
        }),
        ('Ponuda', {
            'fields': ('price', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'driver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipment__title', 'driver__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('tour', 'sender', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'message')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('tour', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('tour__shipment__title',)
    readonly_fields = ('timestamp',)
