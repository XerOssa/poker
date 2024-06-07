from django import forms
from .models import Player

class GameConfigForm(forms.Form):
    initial_stack = forms.IntegerField(label='Initial Stack', initial=100, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
    small_blind = forms.IntegerField(label='Small Blind', initial=5, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
    ante = forms.IntegerField(label='Ante', initial=0, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name']

