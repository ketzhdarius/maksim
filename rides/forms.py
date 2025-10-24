from django import forms
from .models import Ride, RideEvent

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'destination', 'total_distance', 'price']
        widgets = {
            'total_distance': forms.NumberInput(attrs={'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make total_distance read-only as it's calculated automatically
        if 'total_distance' in self.fields:
            self.fields['total_distance'].widget.attrs['readonly'] = True
