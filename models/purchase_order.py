from odoo import models, fields, api
from datetime import datetime 

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_term = fields.Char(string='Plazo de entrega')
    delivery_place = fields.Char(string='Lugar de entrega')
    delivery_address = fields.Char(string='Dirección')

    @api.model_create_multi
    def create(self, vals_list):
        orders = super(PurchaseOrder, self).create(vals_list)

        for order in orders:
            base_name = order.name 

            first_product_ref = "NA"
            if order.order_line:
                first_line = order.order_line[0]
                if first_line.product_id and first_line.product_id.default_code:
                    first_product_ref = first_line.product_id.default_code
                
            current_year = datetime.now().strftime('%y')

            user_name = self.env.user.name or "Admin"

            user_initials = "".join([x[0].upper() for x in user_name.split() if x])

            new_name = f"{base_name}-{first_product_ref}-{current_year}-{user_initials}"

            order.name = new_name

        return orders 
    
