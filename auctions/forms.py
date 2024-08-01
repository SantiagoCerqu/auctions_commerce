from django import forms
from django.forms import ModelForm
from .models import Listing, Comment, Category

class newListingform(ModelForm):
    class Meta:
        model = Listing
        fields = ["title","category_id","image","description","start_price"]

        widgets = {
            "title":forms.TextInput(attrs={
                "class":"form-control",
                "placeholder": "Listing Title ..."
            }),

            "category_id": forms.Select(attrs={
                "class": "form-select"
            }),

            "image": forms.FileInput(attrs={
                "class": "form-control",
                "type": "file"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the product ..."
            }),

            "start_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder":"Digit the start price ...",
                "step":"0.01",
                "min":"0"    
            })

        }

    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the initial "Open this select menu" option
        self.fields['category_id'].choices = [('open', 'Open this select menu')] + [(cat.id, cat.category.title()) for cat in Category.objects.all()]

    def clean_category(self):
        category_id = self.cleaned_data['category']
        if category_id == 'open':
            raise forms.ValidationError("Please select a valid category.")
        return category_id


class newCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        # exclude = ["user_id", "listing_id"]

        labels = {
            "comment" : ""            
        }

        widgets = {
            # input type="text" name="comment_text" id="addComment" class="form-control" placeholder="Type comment..." /> -->
            "comment":forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Type comment...",
                "id": "addComment"
            })
        }



class editListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title","category_id","image","description"]