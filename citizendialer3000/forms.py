from django.forms import ModelForm
from citizendialer3000.models import Call

class CallForm(ModelForm):
    class Meta:
        model = Call
        exclude = ('contact', 'timestamp')