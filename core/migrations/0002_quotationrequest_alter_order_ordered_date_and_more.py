# Generated by Django 4.2.23 on 2025-07-16 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('SUBMITTED', 'Submitted'), ('ANSWERED', 'Answered'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], default='SUBMITTED', max_length=10)),
                ('user_notes', models.TextField(blank=True, help_text='Any details from the user.', null=True)),
                ('admin_notes', models.TextField(blank=True, help_text='Notes from the admin about the quote.', null=True)),
                ('proposed_total', models.FloatField(blank=True, help_text='The price quoted by the admin.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answered_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='QuotationRequestItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.item')),
                ('quotation_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.quotationrequest')),
            ],
        ),
        migrations.AddField(
            model_name='quotationrequest',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.order'),
        ),
        migrations.AddField(
            model_name='quotationrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
