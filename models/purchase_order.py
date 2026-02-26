from odoo import models, fields, api
from datetime import datetime 
from markupsafe import Markup

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

            project_ref = "NA"

            if order.project_id:
                full_project_name = order.project_id.name or ""

                project_ref = full_project_name.split('/')[0].strip()

                project_ref = project_ref.upper()


            current_year = datetime.now().strftime('%y')

            user_name = self.env.user.name or "Admin"

            user_initials = "".join([x[0].upper() for x in user_name.split() if x])

            new_name = f"{base_name}-{project_ref}-{current_year}-{user_initials}"

            order.name = new_name

        return orders 
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # 1. Cuando se AGREGA un producto nuevo a la orden
    @api.model_create_multi
    def create(self, vals_list):
        lines = super(PurchaseOrderLine, self).create(vals_list)
        for line in lines:
            if line.product_id:
                mensaje = Markup(f"<p>🟢 <b>Producto agregado:</b> {line.product_id.display_name} (Cantidad: {line.product_qty})</p>")
                line.order_id.message_post(body=mensaje)
        return lines

    # 2. Cuando se EDITA un producto o su cantidad
    def write(self, vals):
        for line in self:
            cambios = []
            
            # Guardamos el nombre actual del producto
            nombre_producto = line.product_id.display_name

            # Si cambiaron el producto
            if 'product_id' in vals and vals['product_id'] != line.product_id.id:
                nuevo_producto = self.env['product.product'].browse(vals['product_id'])
                cambios.append(f"<li><b>Producto:</b> {nombre_producto} ➔ {nuevo_producto.display_name}</li>")
                
                # Si cambiaron el producto, actualizamos la variable para que la cantidad muestre el nombre nuevo
                nombre_producto = nuevo_producto.display_name
            
            # Si cambiaron la cantidad, ahora especificamos de qué producto es
            if 'product_qty' in vals and vals['product_qty'] != line.product_qty:
                cambios.append(f"<li><b>Cantidad de '{nombre_producto}':</b> {line.product_qty} ➔ {vals['product_qty']}</li>")
            
            # Publicamos la nota si hubo cambios
            if cambios:
                mensaje = Markup("<p>🟠 <b>Línea modificada:</b></p><ul>" + "".join(cambios) + "</ul>")
                line.order_id.message_post(body=mensaje)

        return super(PurchaseOrderLine, self).write(vals)

    # 3. Cuando se ELIMINA un producto de la orden
    def unlink(self):
        for line in self:
            if line.product_id:
                mensaje = Markup(f"<p>🔴 <b>Producto eliminado:</b> {line.product_id.display_name} (Cantidad: {line.product_qty})</p>")
                line.order_id.message_post(body=mensaje)
        return super(PurchaseOrderLine, self).unlink()