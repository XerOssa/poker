from django import forms
from .models import Hero, GameConfig


class GameConfigForm(forms.ModelForm):
       class Meta:
           model = GameConfig
           fields = ['initial_stack', 'small_blind', 'ante']
           widgets = {
            'initial_stack': forms.NumberInput(attrs={'value': 200}),  # Set default value
            'small_blind': forms.NumberInput(attrs={'value': 5}),
            'ante': forms.NumberInput(attrs={'value': 0}),
            }

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['name']
