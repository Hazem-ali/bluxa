from django.db import models


# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    target_gender = models.CharField(max_length=50)
    qty = models.IntegerField()
    buy_price = models.DecimalField(max_digits=9, decimal_places=2)
    sell_price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self) -> str:
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Item, related_name="categories", null=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Wishlist(models.Model):
    owner = models.OneToOneField("user_app.User", on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, related_name="wishlists")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wishlist of {self.owner}"


class Cart(models.Model):
    owner = models.OneToOneField("user_app.User", on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through="ItemCart", related_name="carts")
    total_price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self) -> str:
        return f"Cart of {self.owner}"


class Order(models.Model):
    owner = models.ForeignKey("user_app.User", on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through="ItemOrder", related_name="orders")

    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"Order of {self.owner}"


class ItemCart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    qty = models.IntegerField()


class ItemOrder(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    qty = models.IntegerField()
