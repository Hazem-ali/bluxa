from rest_framework.response import Response
from .models import ItemCart


class CustomResponse(Response):

    def __init__(self, data=None, status_code=None, **kwargs):
        
        _id = data['id']
        owner = data['owner']
        total_price = data['total_price']
        keyed_items = data['items']

        new_items = []
        for item_id in keyed_items:
            item_cart = ItemCart.objects.get(cart__id=_id,item__id=item_id)
            new_items.append({
                'item_id':item_id,
                'quantity': item_cart.qty
            })


        data['items'] = new_items
        
        
        
        
        
        
        
        super().__init__(data, **kwargs)