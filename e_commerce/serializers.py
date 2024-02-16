from rest_framework import serializers

from .models import Item, Category, Wishlist, Cart, ItemCart, Order, ItemOrder


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"
        # depth = 1


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        # depth = 1


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        # depth = 1


class CartDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

    def to_representation(self, instance):
        # instance here is a queryset object that has direct access to data

        data = {
            "id": instance.id,
            "total_price": instance.total_price,
            "owner": instance.owner.id,
        }
        new_items = []
        items = instance.items.all()
        for item in items:
            item_cart = ItemCart.objects.get(cart__id=instance.id, item=item)
            new_items.append({"item_id": item.id, "quantity": item_cart.qty})
        data["items"] = new_items

        return data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        # depth = 1


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        # depth = 1

    def to_representation(self, instance):

        data = {
            "id": instance.id,
            "total_price": instance.total_price,
            "owner": instance.owner.id,
            "ordered_at": instance.ordered_at,
            "last_updated": instance.last_updated,
            "status": instance.status,
        }
        detailed_items =[ ]
        items = instance.items.all()
        
        for item in items:
            item_order = ItemOrder.objects.get(order__id=instance.id, item=item)
            detailed_items.append({"item_id": item.id, "quantity": item_order.qty})

        data['items']=detailed_items

        
        return data
