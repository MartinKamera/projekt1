from django import forms
from django.contrib.auth.forms import AuthenticationForm
from base.models import Currency


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'username_input_field', 'placeholder': 'Here comes your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password_input_field','placeholder': 'Here comes your password'}))

class PortfolioCreationForm(forms.Form):
    portfolio_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'portfolio_name_input_field', 'placeholder': 'Portfolio name'},), error_messages={'required': 'Please enter a name for your portfolio'})
    portfolio_currency = forms.ChoiceField(choices= Currency.choices() + [('', 'Choose currency')], widget = forms.Select(attrs= {'class': 'currency_selection_field'}), error_messages={'required': 'Please select a currency for your portfolio'}, required=True)