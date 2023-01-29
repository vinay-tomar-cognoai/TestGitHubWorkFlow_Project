from django import forms
from django_ace import AceWidget


class AssignTaskProcessorForm(forms.ModelForm):
    function = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))
