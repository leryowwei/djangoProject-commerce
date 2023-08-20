from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, WatchList, Category
from .form import BidForm, CommentForm, ListingForm


def index(request):
    """ get all active listings """
    listings = Listing.objects.filter(active=True).order_by('-created_on')

    return render(request, "auctions/index.html", {
        'listings': listings,
    })


def categories(request):
    """ Show All Categories"""
    return render(request, "auctions/category.html", {
        'categories': Category.objects.all(),
    })


def get_listings_in_category(request, category_name):
    """ Get listings in the category"""
    if Category.objects.filter(category=category_name).exists():
        return render(request, "auctions/listing_category.html", {
            'listings': Listing.objects.filter(category=Category.objects.get(category=category_name), active=True).order_by('-created_on'),
            'category_name': category_name,
        })

    return render(request, "auctions/page_error.html", {
        'error_message': 'Category "{}" does not exist. Please visit "Categories" page for all available categories.'
                  .format(category_name),
    })


def listing(request, listing_name):
    """ Check if listing exists then return listing details otherwise return listing not found """

    if Listing.objects.filter(name=listing_name).exists():
        listing_obj = Listing.objects.get(name=listing_name)

        # get form and comment for listing
        initial_form = BidForm(initial={'listing': listing_obj, 'bidder': request.user})

        # check if user who is authenticated is watching the item
        watching = None
        if request.user.is_authenticated:
            if WatchList.objects.filter(originator=request.user, listing=listing_obj).exists():
                # get first obj - should only have one per user per listing
                watching = WatchList.objects.filter(originator=request.user, listing=listing_obj)[0]

        if request.method == "POST":
            form = BidForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, "auctions/listing.html", {
                    'listing': listing_obj,
                    'form': initial_form,
                    'watch': watching,
                })
            else:
                return render(request, "auctions/listing.html", {
                    'listing': listing_obj,
                    'form': form,
                    'watch': watching,
                })
        return render(request, "auctions/listing.html", {
            'listing': listing_obj,
            'form': initial_form,
            'watch': watching,
        })
    else:
        return render(request, "auctions/page_error.html", {
            'error_message': 'Listing "{}" does not exist. Please visit "Active Listing" page to search for all '
                             'active listings.'.format(listing_name),
        })


def create_listing(request):
    """Create listing"""
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("listing", args=(form.cleaned_data['name'],)))
        else:
            return render(request, "auctions/create.html", {
                'form': form,
            })

    return render(request, "auctions/create.html", {
        'form': ListingForm(initial={'active': True, 'originator': request.user}),
    })


@login_required
def add_comment(request, listing_name):
    """Add comment for a listing"""

    # make sure that the listing actually exists
    if Listing.objects.filter(name=listing_name).exists():
        listing_obj = Listing.objects.get(name=listing_name)

        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_name,)))
            else:
                return render(request, "auctions/comment.html", {
                    'form': form,
                    'listing': listing_obj,
                })

        return render(request, "auctions/comment.html", {
            'form': CommentForm(initial={'listing': listing_obj, 'author': request.user}),
            'listing': listing_obj,
        })

    else:
        return render(request, "auctions/listing_not_found.html", {
            'listing_name': listing_name,
        })


@login_required
def close_bid(request, listing_name):
    """Close bid if object exists and user is originator"""
    # close bid all requirements fulfilled
    if Listing.objects.filter(name=listing_name).exists():
        listing_obj = Listing.objects.get(name=listing_name)
        if listing_obj.originator == request.user:
            listing_obj.active = False
            listing_obj.save()

    return listing(request, listing_name)


@login_required
def access_my_watchlist(request):
    """Access user's watchlist """
    # get all listings watched by user
    if request.user.is_authenticated:
        watchlist = WatchList.objects.filter(originator=request.user).order_by('-created_on')
    else:
        watchlist = None

    return render(request, "auctions/my_watchlist.html", {
        'watchlist': watchlist,
    })


@login_required
def access_my_listings(request):
    """Access listings posted by user """
    # get all listings by user
    if request.user.is_authenticated:
        listings = Listing.objects.filter(originator=request.user).order_by('-created_on')
    else:
        listings = None

    return render(request, "auctions/my_listings.html", {
        'listings': listings,
    })


@login_required
def add_to_watchlist(request, listing_name):
    """Add listing to watchlist"""

    # only save to database if listing object actually exists
    if Listing.objects.filter(name=listing_name).exists():
        watchlist = WatchList()
        watchlist.listing = Listing.objects.get(name=listing_name)
        watchlist.originator = request.user
        watchlist.save()

    return redirect(request.META['HTTP_REFERER'])


@login_required
def remove_from_watchlist(request, listing_name):
    """Remove from watchlist"""
    # only delete when objects exist
    if Listing.objects.filter(name=listing_name).exists():
        listing_obj = Listing.objects.get(name=listing_name)
        if WatchList.objects.filter(originator=request.user, listing=listing_obj).exists():
            watching = WatchList.objects.get(originator=request.user, listing=listing_obj)
            watching.delete()

    return redirect(request.META['HTTP_REFERER'])


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
