from django import forms
from django_ace import AceWidget


class CampaignAPIForm(forms.ModelForm):
    api_program = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))


class CampaignVoiceBotAPIForm(forms.ModelForm):
    api_code = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))
