from rest_framework import generics, mixins, filters, exceptions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner


from . import models
from .serializers import (
    ItemSerializer,
    CategorySerializer,
    OrderDetailSerializer,
    WishlistSerializer,
    CartSerializer,
    CartDetailsSerializer,
)


# Item (CRUD)
class ItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.Item.objects.all()
    serializer_class = ItemSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields =["title","qty","sell_price"]


class ItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Item.objects.all()
    serializer_class = ItemSerializer


# Category (Add, Remove " Admin Only ")
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.Category.objects.all()
    serializer_class = CategorySerializer


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Category.objects.all()
    serializer_class = CategorySerializer


# Add/Remove item from wishlist (user)
class WishlistRetrieveCreateUpdateAPIView(
    generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView
):
    queryset = models.Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return models.Wishlist.objects.get(owner=self.request.user.id)

    def get_owner_wishlist(self, owner_id):
        try:
            wishlist = models.Wishlist.objects.get(owner=owner_id)
        except:
            raise exceptions.ErrorDetail("You do not have a wishlist yet")
        return wishlist

    def post(self, request, *args, **kwargs):
        # Add the items only in the request into wishlist (ignore old items if user has items in wishlist)
        owner = self.request.user.id
        self.request.data["owner"] = owner
        wishlist = models.Wishlist.objects.filter(owner=owner)
        if wishlist.exists():
            return self.update(request, *args, **kwargs)
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Add the items to the current wishlist
        owner = self.request.user.id
        self.request.data["owner"] = owner

        wishlist = self.get_owner_wishlist(owner)
        current_items = list(wishlist.items.values_list("id", flat=True))
        new_items = [*self.request.data.get("items", []), *current_items]
        self.request.data["items"] = new_items

        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Delete items from wishlist
        owner = self.request.user.id
        self.request.data["owner"] = owner
        wishlist = self.get_owner_wishlist(owner)
        current_items = list(wishlist.items.values_list("id", flat=True))
        items_to_delete = self.request.data["items"]
        remaining_items = [
            item for item in current_items if item not in items_to_delete
        ]

        self.request.data["items"] = remaining_items
        
        return self.update(request, *args, **kwargs)


# Add/Remove item to cart (user)
class CartRetrieveCreateUpdateAPIView(
    # generics.GenericAPIView,
    # mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    generics.RetrieveUpdateAPIView,
):
    queryset = models.Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return models.Cart.objects.get(owner=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        cart = models.Cart.objects.get(owner=request.user.id)
        cart_serializer = CartDetailsSerializer(cart)
        return Response(cart_serializer.data)

    def create(self, request, *args, **kwargs):
        # Getting the items list
        items_data = request.data["items"]

        # Setting new list containing item_objects instead of ids
        items = []

        total_price = 0.0
        for item_data in items_data:
            item_id = item_data.get("item_id")
            quantity = item_data.get("quantity", 1)

            try:
                item = models.Item.objects.get(pk=item_id)

                if quantity > item.qty:
                    raise exceptions.ValidationError(
                        {"error": "Quantity higher than item inventory"}
                    )

                items.append({"item": item, "quantity": quantity})
                total_price += float(item.sell_price * quantity)
            except models.Item.DoesNotExist:
                return Response(
                    {"error": f"Item with id {item_id} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Create a data object with the same structure as Cart model
        cart_data = {
            "owner": request.user.id,
            "total_price": total_price,
        }

        # Use the serializer to validate and save the data
        cart_serializer = self.get_serializer(data=cart_data)
        cart_serializer.is_valid(raise_exception=True)
        cart = cart_serializer.save()

        # Add items to the cart after the cart has been saved
        for item_info in items:
            models.ItemCart.objects.create(
                cart=cart, item=item_info["item"], qty=item_info["quantity"]
            )

        headers = self.get_success_headers(cart_serializer.data)
        return Response(
            cart_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        # Getting user cart
        cart = models.Cart.objects.get(owner=self.request.user.id)

        # Getting new items to be in the cart
        items_in_request = request.data["items"]
        items_list = []

        total_price = 0.0

        # Adding items into items_list as objects
        for item_data in items_in_request:
            item_id = item_data.get("item_id")
            quantity = item_data.get("quantity", 1)

            try:
                item = models.Item.objects.get(pk=item_id)

                if quantity > item.qty:
                    raise exceptions.ValidationError(
                        {"error": "Quantity higher than item inventory"}
                    )
                items_list.append({"item": item, "quantity": quantity})
                total_price += float(item.sell_price * quantity)

            except models.Item.DoesNotExist:
                return Response(
                    {"error": f"Item with id {item_id} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cart.items.clear()
        cart.total_price = total_price
        for item_info in items_list:
            models.ItemCart.objects.create(
                cart=cart, item=item_info["item"], qty=item_info["quantity"]
            )

        cart.save()

        serialized_cart = CartSerializer(cart)
        return Response(serialized_cart.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# Place Order ( add order ) (user)
class OrderListCreateAPIView(
    generics.ListCreateAPIView,
):

    def get_queryset(self):
        return models.Order.objects.filter(owner=self.request.user.id)

    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        cart = models.Cart.objects.get(owner=self.request.user.id)
        order = models.Order.objects.create(
            owner=cart.owner,
            total_price=cart.total_price,
            status="placed",
        )

        cart_items = cart.items.all()

        for item in cart_items:
            item_cart = models.ItemCart.objects.get(item=item.id, cart=cart.id)
            models.ItemOrder.objects.create(order=order, item=item, qty=item_cart.qty)

        order.save()

        return Response(OrderDetailSerializer(order).data)


class OrderRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView,
):

    queryset = models.Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def update(self, request, *args, **kwargs):
        status = request.data.get("status", None)
        if not status:
            raise exceptions.NotAcceptable("You can only update order status only")

        order = models.Order.objects.get(pk=self.kwargs.get("pk"))

        order.status = status

        order.save()

        return Response(self.get_serializer(order).data)
