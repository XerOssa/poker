from django import forms
from .models import Hero, GameConfig


class GameConfigForm(forms.ModelForm):
    class Meta:
        model = GameConfig  # Replace with your actual model name
        fields = ['initial_stack', 'small_blind', 'ante']



class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['name']
        widgets = {  # Optional: customize widget for name field
            'name': forms.TextInput(attrs={'required': True}),
        }
# class GameConfigForm(forms.ModelForm):
#     class Meta:
#         initial_stack = forms.IntegerField(label='Initial Stack', initial=150, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
#         small_blind = forms.IntegerField(label='Small Blind', initial=5, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
#         ante = forms.IntegerField(label='Ante', initial=0, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))