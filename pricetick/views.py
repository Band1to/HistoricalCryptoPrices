import json

from django.http import HttpResponse
import arrow
from models import PriceTick

# Create your views here.
def price_for_date(request):
    currency = request.GET['crypto']
    fiat = request.GET['fiat']
    date = arrow.get(request.GET['date']).datetime

    tick = PriceTick.objects.filter(
        date__gt=date,
        currency=currency.upper(),
    ).order_by('date')[0]

    j = json.dumps([tick.price, tick.exchange])
    return HttpResponse(j, content_type="application/json")
