# -*- encoding: UTF-8 -*-
##############################################################################

from odoo import fields, models, api, _

tipo_documento_es = [
		('CCF', 'CCF'),
		('FACT', 'FACTURA'),
		('FAEX', 'FAEX'),
		('TICKET', 'TICKET'),
		('INV', 'INVOICE')
	]
class AccountInvoice(models.Model):
	_inherit = "account.move"

	@api.onchange('tipo_documento_es')
	def _tipo_documento_es(self):
		for data in self:
			data.tipo_documento = data.tipo_documento_es

	#pruebas
	serie_factura = fields.Char(string="Serie Factura", required=False, help="Serie de la factura de proveedor")
	num_factura = fields.Char(string="Numero Factura", required=False, help="Numero de la factura de proveedor")
	tipo_documento = fields.Selection([
		('FC', 'Factura Cambiaria'),
		('FE', 'Factura Especial'),
		('FCE', 'Factura Electronica'),
		('FAC', 'Factura'),
		('FEL', 'FEL'),
		('NC', 'Nota de Credito'),
		('ND', 'Nota de Debito'),
		('FPC', 'Factura Peq. Contribuyente'),
		('DA', 'Declaracion Unica Aduanera'),
		('FA', 'FAUCA'),
		('FO', 'Formulario SAT'),
		('ONAF', 'Otros No Afectos'),
		('EP', 'Escritura Publica'),
		('RC', 'RECIBO'),
		('CCF', 'CCF'),
		('FACT', 'FACTURA'),
		('FAEX', 'FAEX'),
		('TICKET', 'TICKET'),
		('INV', 'INVOICE')],'Tipo Documento', default='FC', required=False, help="Tipo de documento de gasto que se reflejara en el libro de Ventas/Compras del IVA")

	tipo_documento_es = fields.Selection(tipo_documento_es, 'Tipo Documento')

AccountInvoice()
