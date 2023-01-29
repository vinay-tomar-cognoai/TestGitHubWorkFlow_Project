from django import forms
from django_ace import AceWidget


class LiveChatBotChannelWebhookForm(forms.ModelForm):
    function = forms.CharField(initial="Please select bot, channel. And click on 'save' and Open same object to get sample code", widget=AceWidget(
        wordwrap=False, width="1100px", height="500px", showprintmargin=True, mode='python', theme='twilight'))


class ApiTreeEditorForm(forms.ModelForm):

    api_caller = forms.CharField(widget=AceWidget(
        wordwrap=False, width="1100px", height="500px", showprintmargin=True, mode='python', theme='twilight'))


class ProcessorEditorForm(forms.ModelForm):
    function = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))


class WhatsAppWebhookForm(forms.ModelForm):
    function = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))
    extra_function = forms.CharField(widget=AceWidget(
        wordwrap=False, width="900px", height="500px", showprintmargin=True, mode='python', theme='twilight'))


class BotResponseEditorForm(forms.ModelForm):
    sentence = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    recommendations = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    cards = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    images = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    videos = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    modes = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    modes_param = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))

    table = forms.CharField(widget=AceWidget(
        wordwrap=False, width="700px", height="200px", showprintmargin=True, mode='json', theme='twilight'))
