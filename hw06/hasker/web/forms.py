from web.models import Question
from django import forms




class QuestionCreateForm(forms.ModelForm):
    tags_str = forms.CharField(help_text='', label='tags', required=False)

    class Meta:
        model = Question
        fields = ('title','text', 'tags_str')