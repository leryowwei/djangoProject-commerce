from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    """Class for user"""
    pass


class Category(models.Model):
    """Class for categories - does not allow same category to occur twice"""
    category = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return '{}'.format(self.category)


class Bid(models.Model):
    """Class for bids"""
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name='listing')

    def __str__(self):
        return 'Bid: {} for {}, by {}'.format(self.listing.name, self.price, self.bidder.username)


class Comment(models.Model):
    """Class for comment"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'author',)

    def __str__(self):
        return 'Comment on {} by {}'.format(self.listing.name, self.author.username)


class WatchList(models.Model):
    """Class for watchlist

       Does not allow same user to watch the same thing twice
    """
    originator = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('originator', 'listing',)

    def __str__(self):
        return 'Watching: {}, by {}'.format(self.listing.name, self.originator.username)


class Listing(models.Model):
    """Class for listing"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(blank=True)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    originator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="originator")
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'category',)

    def __str__(self):
        return '{} in {}, Starting Bid: {},  by {}'.format(self.name, self.category, self.starting_bid,
                                                           self.originator)

    def get_highest_bid_price(self):
        """Find out highest bid price for the item otherwise return the starting bid price"""
        if Bid.objects.filter(listing=self):
            return Bid.objects.filter(listing=self).order_by('-price')[0].price
        else:
            return self.starting_bid

    def get_no_of_bids(self):
        """Find out how many bids has been made"""
        return len(Bid.objects.filter(listing=self))

    def get_highest_bidder(self):
        """Find out user profile of highest bidder> If no bid, return none"""
        if Bid.objects.filter(listing=self):
            return Bid.objects.filter(listing=self).order_by('-price')[0].bidder
        else:
            return None

    def get_all_bidders(self):
        """Find out all bidders> If no bid, return none"""
        if Bid.objects.filter(listing=self):
            bidders = []
            for bid in Bid.objects.filter(listing=self):
                bidders.append(bid.bidder)
            return bidders
        else:
            return None

    def get_comments(self):
        """Get comments related to the listing and sort by date"""
        if Comment.objects.filter(listing=self):
            return Comment.objects.filter(listing=self).order_by('-created_on')
        else:
            return None