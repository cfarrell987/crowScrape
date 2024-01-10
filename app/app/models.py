from django.db import models


# Create your models here.
class Item(models.Model):
    item_name = models.CharField(max_length=100)
    item_url = models.URLField()
    category = models.CharField(max_length=100)  # Add the category field

    def __str__(self):
        return self.item_name


class Price(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.item_name}"
