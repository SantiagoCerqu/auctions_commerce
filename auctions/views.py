from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q, F # Functions to work directly with the database (no python memory)

from django.views.generic import UpdateView # Update or edit the listing

from .models import User, Category, Listing, Comment
from .forms import newListingform, newCommentForm, editListingForm


def index(request):

    # List all active listings, the ones that are not already sold
    listings = Listing.objects.filter(sold=False)

    return render(request, "auctions/index.html",
                {"listings":listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html",)
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        if not username:
            messages.error(request, "Not a valid username.")
            return render(request, "auctions/register.html")
        
        try:
            # Email validation
            validate_email(request.POST["email"])
            email = request.POST["email"]
        except ValidationError:
            messages.error(request,"Not a valid email.")
            return render(request, "auctions/register.html")
            
        
        password = request.POST["password"]
        if not password:
            messages.error(request, "Not a valid password.")
            return render(request, "auctions/register.html")
        
        confirmation = request.POST["confirmation"]
        if not confirmation:
            messages.error(request, "Confirmation is empty.")
            return render(request, "auctions/register.html")
        
        # Ensure password matches confirmation
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
        
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


####
# My views 

@login_required
def add_listing(request):
    if request.method == "POST":
        form_data = newListingform(request.POST, request.FILES) # Here I am accepting an image in the form with request.FILES
        if form_data.is_valid():
            data = form_data.cleaned_data
            # * Add the current user_id to the transaction and other modifications before commit and save
            new_listing = data.save(commit=False)
            new_listing.seller_id = request.user # request.user is the current user
            # Change the title to lower
            new_listing.title = new_listing.title.lower()
            new_listing.save()
            return HttpResponseRedirect(reverse("auctions:my_listings"))
        
        else:
            # When form is not satified return the form
            return render(request, "auctions/new_listing.html",
                  {"form":form_data})

    return render(request, "auctions/new_listing.html",
                  {"form":newListingform()})


class EditListing(UpdateView):
    # User can update the fields of his post
    model = Listing
    # form_class = editListingForm
    template_name = "auctions/edit_listing_page.html"
    fields = ["title", "description", "image", "category_id"]

    # Return to the listing view
    def get_success_url(self):
        return reverse("auctions:listing_view", args=[self.object.pk])

    

@login_required
def my_listings(request):
    # Show all listings active listings
    listings = Listing.objects.filter(Q(seller_id=request.user.id)
                                      & Q(sold = False))

    return render(request, "auctions/my_listings.html", 
                  {"listings":listings})



@login_required
def place_bid(request, listing_id):

    # Get the listing
    listing = Listing.objects.get(pk = listing_id)
    # Make an offer to the current listing
    if request.method == "POST":
        # Get the data from the user, check that value is not 0 or Null
        try:
            form_data = float(request.POST["bid_amount"])

            # Check that form_data is not less or equal than the current bid
            if form_data <= listing.bid_amount:
                raise IntegrityError
            
            listing.bid_amount = form_data
            listing.bidder_id = request.user
            listing.save()
            messages.success(request, "Your bid was successfully placed!")

        except (IntegrityError, ValueError):
            messages.error(request, "Your bid must be greater than initial price and greater than current bid.")

        return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))



def listing_view(request, listing_id):

    # Get the listing with the id
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing_id=listing_id)

    # Check if user has the listing id in watchlist
    if not request.user.is_authenticated:
        in_watchlist = False
    else:
        in_watchlist = request.user.watchlist.filter(pk=listing_id)

    # Show current listing
    return render(request, "auctions/listing.html", 
                  {"listing":listing,
                   "in_watchlist":in_watchlist,
                   "comments":comments,
                   "commentForm": newCommentForm()})


def categories(request):
    # Get all the categories
    categories_list = Category.objects.all()
    return render(request, "auctions/categories.html", 
                  {"categories":categories_list})

def category_items(request, category_name):
    
    # Select the exact category, handling misspelings
    try:
        category = Category.objects.get(category=category_name.strip().lower())
        
    except Category.DoesNotExist:
        return render(request, "auctions/category_items.html", 
                      {"message": f"Category '{category_name}' do not exist."})

        
    # Get the category items and the listings that are not sold
    listings = Listing.objects.filter(Q(category_id = category.id) & Q(sold=False))

    return render(request, "auctions/category_items.html", 
                  {"category": category,
                   "listings": listings})

@login_required
def add_watchlist(request, listing_id):
    # Adding listing_id into the many to many relationship with user
    request.user.watchlist.add(listing_id)
    return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))

@login_required
def remove_watchlist(request, listing_id):
    # Remove the listing from user watchlist (removing many to many relation)
    request.user.watchlist.remove(listing_id)
    return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))
    


@login_required
def watchlist(request):
    
    listings = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html",
                  {"listings":listings})


@login_required
def shopping_history(request):
    # POST Method
    if request.method == "POST":
        # User data
        user = request.user

        # Get all purchased listings
        listings_bought = Listing.objects.filter(
            Q(bidder_id = user.id)
            & Q(sold = True)
        )

        # Get all sold listings
        listings_sold = Listing.objects.filter(
            Q(seller_id=user.id)
            & Q(sold = True)
        )

        form_data = request.POST["listing_status"]

        if form_data == "all":
            return render(request, "auctions/shopping_history.html", 
                    {"listings_bought":listings_bought,
                    "listings_sold":listings_sold})
        
        if form_data == "bought":
            return render(request, "auctions/shopping_history.html", 
                    {"listings_bought":listings_bought,
                    "listings_sold":False})
        
        if form_data == "sold":
            return render(request, "auctions/shopping_history.html", 
                    {"listings_bought":False,
                    "listings_sold":listings_sold})
        
    # GET method
    return render(request, "auctions/shopping_history.html", 
                    {"listings_bought":False,
                    "listings_sold":False})


@login_required
def sell(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # Check that bid is greater than 0 and it has bidder
    if listing.bid_amount == 0 and not listing.bidder_id:
        messages.error(request, "The listing has no bid")
        return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))
    
    # Change the sold attribute of the listing to TRUE
    listing.sold = True
    listing.save()
    return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))

@login_required
def my_bids(request):
    user_id = request.user
    listings = Listing.objects.filter(Q(bidder_id=user_id)
                                      & Q(sold=False))
    
    return render(request, "auctions/my_bids.html",
                  {"listings":listings})


def add_comments(request, listing_id):

    if not request.user.is_authenticated:
        messages.error(request, "Login to add a comment.")
        return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))

    # Get the data from the form
    form_data = newCommentForm(request.POST)
    
    if form_data.is_valid():
        
        user_comment = form_data.cleaned_data["comment"]

        # Create a new comment in the data base 
        new_comment = Comment(
            listing_id = Listing.objects.get(pk=listing_id), # Add an instance of a listing
            user_id = request.user,
            comment = user_comment
        )
        new_comment.save()

        return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))

    return HttpResponseRedirect(reverse("auctions:listing_view", args=[listing_id]))



