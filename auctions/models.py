from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F # Functions to work directly with the database (no python memory)
from django.core.exceptions import ValidationError


class User(AbstractUser):
    # Watchlist is a table relating user and listings
    watchlist = models.ManyToManyField("Listing", null=True, blank=True)
    
    def __str__(self):
        return f"User id: {self.id}, User: {self.username}"

class Category(models.Model):
    # Category of the listings
    category = models.CharField(max_length=45)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"    

    def __str__(self):
        return f"{self.category.title()}"

class Listing(models.Model):
    # Person who is selling the poduct
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_seller", blank=True)
    # Category of the product
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="listing_category", null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder_id = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bidder", null=True, blank=True)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True) ###### Create a check constraint de > start_price
    sold = models.BooleanField(default=False, blank=True)
    image = models.ImageField(upload_to='uploads/listing/', blank=True, null=True)

    # Create constraints for some attributes
    # Check that the bid_amount is greater than start_price or equal to 0 (as the start)
    class Meta:
        constraints = [
            models.CheckConstraint(
                name="bid_amount_check",
                check=Q(bid_amount = 0) | Q(bid_amount__gt = F("start_price")),
                violation_error_message="Bid amount must be greater than the start price."
            )
        ]

    # ! CLEAN is checked when saving, so for this project this desnt work
    # def clean(self):
    #     # Ensure that bid_amount is greater than start_price and dont check when it is created (when value is 0)
    #     if self.bid_amount != 0 and self.bid_amount <= self.start_price:
    #         raise ValidationError({
    #             "bid_amount":"Bid amount must be greater than the start price."
    #         })


    #     # Check that the bid_amount is greater than current bid_amount 
    #     if self.pk is not None:
    #         original = Listing.objects.get(pk=self.pk)
    #         # Ensure that bid_amount is greater than current bid amount 
    #         if self.bid_amount <= original.bid_amount:
    #             raise ValidationError({
    #                 "bid_amount":"Bid amount must be greater than the current bid amount."
    #             })

    # ! DO NOT CHECK EVERY TIME IT IS SAVED!! ONLY WHEN THE DATA IS INTRODUCED
    # # Ensure that the clean method (before method) is invoked every time while saving
    # def save(self, *args, **kwargs):
    #     self.full_clean()  # This will call the clean method before saving
    #     super().save(*args, **kwargs)


    def __str__(self):
        return f"Listing {self.id}: {self.title.capitalize()}, initial_price:{self.start_price}, Bid:{self.bid_amount}"

class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comment")
    comment = models.TextField()

    def __str__(self) -> str:
        return f"Comment {self.id}: From {User.first_name} in Listing: {Listing.title}."
    


    

