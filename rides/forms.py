from django import forms
from .models import Ride, RideEvent

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'destination', 'total_distance', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # total_distance is calculated automatically and should be readonly
        if 'total_distance' in self.fields:
            self.fields['total_distance'].widget = forms.NumberInput(attrs={
                'type': 'number', 'step': '0.01', 'min': '0', 'class': 'form-control', 'readonly': 'readonly'
            })
        # price is entered by the customer
        if 'price' in self.fields:
            self.fields['price'].widget = forms.NumberInput(attrs={
                'type': 'number', 'step': '0.01', 'min': '0', 'class': 'form-control'
            })
        # add bootstrap classes to pickup/destination
        if 'pickup_location' in self.fields:
            self.fields['pickup_location'].widget.attrs.update({'class': 'form-control'})
        if 'destination' in self.fields:
            self.fields['destination'].widget.attrs.update({'class': 'form-control'})
