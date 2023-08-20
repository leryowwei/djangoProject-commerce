from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from .models import Listing, Bid, Comment


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price', 'bidder', 'listing']

    def clean(self):
        cleaned_data = super().clean()
        listing = cleaned_data.get("listing")
        price = cleaned_data.get("price")
        bidder = cleaned_data.get("bidder")

        # make sure that price submission is higher that current highest bid
        if price <= listing.get_highest_bid_price():
            raise ValidationError("Bidding price needs to be higher than the current bid price!")

        # make sure that bidder cannot be originator
        if bidder == listing.originator:
            raise ValidationError("Originator of this listing cannot bid on the item!")


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ('name', 'description', 'image', 'starting_bid', 'category', 'originator', 'active')
        widgets = {'originator': forms.HiddenInput(), 'active': forms.HiddenInput()}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'listing', 'body')
        widgets = {'author': forms.HiddenInput(), 'listing': forms.HiddenInput()}
