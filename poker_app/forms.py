from django import forms
from .models import Hero, GameConfig


class GameConfigForm(forms.ModelForm):
    class Meta:
        model = GameConfig
        fields = ['initial_stack', 'small_blind', 'ante']
        widgets = {
        'initial_stack': forms.NumberInput(),
        'small_blind': forms.NumberInput(),
        'ante': forms.NumberInput(),
        }

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['name']
