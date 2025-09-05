# Generated migration for Tour model updates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0004_premiumsubscription_paymentreservation_and_more'),
    ]

    operations = [
        # Make shipment and offer fields nullable
        migrations.AlterField(
            model_name='tour',
            name='shipment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.shipment'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='offer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.shipmentoffer'),
        ),
        
        # Add vehicle field
        migrations.AddField(
            model_name='tour',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.vehicle'),
        ),
        
        # Add geolocation and route fields
        migrations.AddField(
            model_name='tour',
            name='polaziste',
            field=models.CharField(default='', help_text='Polazište ture', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tour',
            name='odrediste',
            field=models.CharField(default='', help_text='Odredište ture', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tour',
            name='planirana_putanja',
            field=models.CharField(blank=True, help_text='Planirana putanja/autoput', max_length=100),
        ),
        
        # Add cargo information fields
        migrations.AddField(
            model_name='tour',
            name='dostupno_za_dotovar',
            field=models.CharField(choices=[('paleta', 'Paleta 120x80'), ('paketna_roba', 'Paketna roba'), ('paleta_paketna_roba', 'Paleta ili paketna roba'), ('rasuti_teret', 'Rasuti teret'), ('tečni_teret', 'Tečni teret')], default='paleta', help_text='Tip tereta dostupan za dotovar', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tour',
            name='kapacitet',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Dostupan kapacitet u tonama', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tour',
            name='slobodna_kilaza',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Slobodna kilaža u kg', max_digits=10),
            preserve_default=False,
        ),
        
        # Add coordinate fields
        migrations.AddField(
            model_name='tour',
            name='polaziste_lat',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='polaziste_lng',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='odrediste_lat',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='odrediste_lng',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
    ]
