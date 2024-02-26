# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import time
import xlwt
import base64
#import io
from io import BytesIO
#import base64

import logging
_logger = logging.getLogger(__name__)

class WizardVentasCompras(models.TransientModel):
    _inherit = 'wizard.ventas.compras.sv'


    file_name = fields.Char('Nombre archivo', size=32)
    file = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        datas = {}
        datas['form'] = self.read(['company_id', 'journal_ids', 'tax_id',
                                   'base_id', 'folio_inicial', 'date_from',
                                   'date_to'])[0]
        #report_name = 'report_ventas_compras.report_purchase_book'
        if self.type_report == 'pdf' and self.type_book == 'sale':
            return self.env['report'].get_action([], 'report_ventas_compras.report_sale_book', data=datas)
        if self.type_report == 'xls' and self.type_book == 'purchase':
            #report_name = 'report_ventas_compras.purchase_book_xls'
            return True
        if self.type_report == 'xls' and self.type_book == 'sale':
            #report_name = 'report_ventas_compras.sale_book_xls'
            self.print_sale_excel()
        if self.type_report == 'pdf' and self.type_book == 'purchase':
            #report_name = 'report_ventas_compras.report_sale_book'
            return self.env['report'].get_action([], 'report_ventas_compras.report_sale_book', data=datas)
        return True
    

    def print_sale_excel(self):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for rec in self:
            if not rec.journal_ids:
                raise UserError(("No hay ningun diario seleccionado..!"))
            libro = xlwt.Workbook()
            hoja = libro.add_sheet('Libro de Ventas')

            titulos_principales_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz center; font:bold on;')
            titulos_texto_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz left;')
            titulos_numero_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz right;')
            company_tittle_style = xlwt.easyxf('align: horiz center; font:bold on;')
            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            #Tittles Styles
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
            sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz right; font:bold on;')
            text_sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz left; font:bold on;')
            #Titulos principal del Reporte
            hoja.write_merge(0, 0, 0, 9, rec.company_id.name, style=company_tittle_style)
            hoja.write_merge(1, 1, 0, 9, "Libro de Ventas a Contribuyentes", style=company_tittle_style)
            y = 4
            #Sub-titulo de datos del contribuyente
            hoja.write_merge(y, y, 0, 1, "Contibruyente:", style=company_tittle_style)
            hoja.write_merge(y, y, 2, 3, rec.company_id.name, style=company_tittle_style)
            hoja.write(y, 4, "NRC:", style=company_tittle_style)
            hoja.write(y, 5, rec.company_id.company_registry, style=company_tittle_style)
            hoja.write(y, 6, "NIT:", style=company_tittle_style)
            hoja.write(y, 7, rec.company_id.vat, style=company_tittle_style)
            month, year = self._get_date(rec.date_to)
            hoja.write(y, 8, (("MES: %s") %(month)), style=company_tittle_style)
            hoja.write(y, 9, (("AÑO: %s") %(year)), style=company_tittle_style)
            y = 6
            #Encabezados de Reporte
            hoja.col(0).width = 3000
            hoja.write(y, 0, 'No', style=titulos_principales_style)
            hoja.col(1).width = 3000
            hoja.write(y, 1, 'Emision', style=titulos_principales_style)
            hoja.col(2).width = 3000
            hoja.write(y, 2, 'Numero', style=titulos_principales_style)
            hoja.col(3).width = 3000
            hoja.write(y, 3, 'NCR', style=titulos_principales_style)
            hoja.col(4).width = 17000
            hoja.write(y, 4, 'Cliente', style=titulos_principales_style)
            hoja.col(5).width = 5000
            hoja.write(y, 5, 'Exentas', style=titulos_principales_style)
            hoja.col(6).width = 5000
            hoja.write(y, 6, 'Gravadas', style=titulos_principales_style)
            hoja.col(7).width = 5000
            hoja.write(y, 7, 'Debito Fiscal', style=titulos_principales_style)
            hoja.col(8).width = 5000
            hoja.write(y, 8, 'Ret/Per', style=titulos_principales_style)
            hoja.col(9).width = 5000
            hoja.write(y, 9, 'Total', style=titulos_principales_style)
            #Generate Records
            result, linea = rec.generate_records()
            #raise UserError((values))
            item = 0
            init_rows = y
            #Variables de Totals
            total_gravado = total_iva = total_retencion = subtotal = 0.0
            for linea in result:
                y += 1
                item += 1
                hoja.write(y, 0, item, style=titulos_texto_style)
                hoja.write(y, 1, linea.get('fecha', ''), style=titulos_texto_style)
                hoja.write(y, 2, linea.get('fac_no', ''), style=titulos_texto_style)
                hoja.write(y, 3, linea.get('nrc_cliente', ''), style=titulos_texto_style)
                hoja.write(y, 4, linea.get('cliente', ''), style=titulos_texto_style)
                hoja.write(y, 5, 0.00, style=titulos_numero_style)
                hoja.write(y, 6, (linea.get('bienes_gravados', 0.00) + linea.get('servicios_gravados', 0.00) + linea.get('bienes_e_gravados', 0.00) + linea.get('servicios_e_gravados', 0.00)), style=titulos_numero_style)
                hoja.write(y, 7, linea.get('iva', 0.00), style=titulos_numero_style)
                hoja.write(y, 8, linea.get('retencion', 0.00), style=titulos_numero_style)
                hoja.write(y, 9, linea.get('subtotal', 0.00), style=titulos_numero_style)
                total_gravado += (linea.get('bienes_gravados', 0.00) + linea.get('servicios_gravados', 0.00) + linea.get('bienes_e_gravados', 0.00) + linea.get('servicios_e_gravados', 0.00))
                total_iva += linea.get('iva', 0.00)
                total_retencion += linea.get('retencion', 0.00)
                subtotal += linea.get('subtotal', 0.00)
            #Dibujado de total de libro
            y +=1
            hoja.write_merge(y, y, 0, 4, "*TOTAL*", style=sums_style)
            hoja.write(y, 5, 0.00, style=sums_style)
            hoja.write(y, 6, total_gravado, style=sums_style)
            hoja.write(y, 7, total_iva, style=sums_style)
            hoja.write(y, 8, total_retencion, style=sums_style)
            hoja.write(y, 9, subtotal, style=sums_style)
            #Resumen de Impuestos
            #Titulos
            y += 4
            hoja.write(y, 4, 'Resumen Operaciones', style=titulos_principales_style)
            hoja.write(y, 5, 'Valor Neto', style=titulos_principales_style)
            hoja.write(y, 6, 'Débito Fiscal', style=titulos_principales_style)
            hoja.write(y, 7, 'Ret./Per.', style=titulos_principales_style)
            hoja.write(y, 8, 'Total', style=titulos_principales_style)
            y += 1
            hoja.write(y, 4, 'Ventas Netas Internas Gravadas a Contribuyentes', style=titulos_texto_style)
            hoja.write(y, 5, total_gravado, style=titulos_numero_style)
            hoja.write(y, 6, total_iva, style=titulos_numero_style)
            hoja.write(y, 7, total_retencion, style=titulos_numero_style)
            hoja.write(y, 8, subtotal, style=titulos_numero_style)
            y += 1
            hoja.write(y, 4, 'Ventas Netas Internas Gravadas a Consumidores', style=titulos_texto_style)
            hoja.write(y, 5, 0.00, style=titulos_numero_style)
            hoja.write(y, 6, 0.00, style=titulos_numero_style)
            hoja.write(y, 7, 0.00, style=titulos_numero_style)
            hoja.write(y, 8, 0.00, style=titulos_numero_style)
            y += 1
            hoja.write(y, 4, 'Total Operaciones Internas Gravadas', style=text_sums_style)
            hoja.write(y, 5, total_gravado, style=sums_style)
            hoja.write(y, 6, total_iva, style=sums_style)
            hoja.write(y, 7, total_retencion, style=sums_style)
            hoja.write(y, 8, subtotal, style=sums_style)
            y += 1
            hoja.write(y, 4, 'Ventas Netas Internas Exentas a Contribuyentes', style=titulos_texto_style)
            hoja.write(y, 5, 0.00, style=titulos_numero_style)
            hoja.write(y, 6, 0.00, style=titulos_numero_style)
            hoja.write(y, 7, 0.00, style=titulos_numero_style)
            hoja.write(y, 8, 0.00, style=titulos_numero_style)
            y += 1
            hoja.write(y, 4, 'Ventas Netas Internas Exentas a Consumidores', style=titulos_texto_style)
            hoja.write(y, 5, 0.00, style=titulos_numero_style)
            hoja.write(y, 6, 0.00, style=titulos_numero_style)
            hoja.write(y, 7, 0.00, style=titulos_numero_style)
            hoja.write(y, 8, 0.00, style=titulos_numero_style)
            y += 1
            hoja.write(y, 4, 'Total Operaciones Internas Exentas', style=text_sums_style)
            hoja.write(y, 5, 0.00, style=sums_style)
            hoja.write(y, 6, 0.00, style=sums_style)
            hoja.write(y, 7, 0.00, style=sums_style)
            hoja.write(y, 8, 0.00, style=sums_style)
            y += 1
            hoja.write(y, 4, 'Exportaciones según Facturas de Exportación', style=titulos_texto_style)
            hoja.write(y, 5, 0.00, style=titulos_numero_style)
            hoja.write(y, 6, 0.00, style=titulos_numero_style)
            hoja.write(y, 7, 0.00, style=titulos_numero_style)
            hoja.write(y, 8, 0.00, style=titulos_numero_style)
            y += 1
            hoja.write(y, 4, 'Total', style=text_sums_style)
            hoja.write(y, 5, total_gravado, style=sums_style)
            hoja.write(y, 6, total_iva, style=sums_style)
            hoja.write(y, 7, total_retencion, style=sums_style)
            hoja.write(y, 8, subtotal, style=sums_style)
            #Save Excel in Wizard
            fp = BytesIO()
            libro.save(fp)
            fp.seek(0)
            report_data_file = base64.encodestring(fp.read())
            fp.close()
            self.write({'file': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.ventas.compras.sv&field=file&download=true&id=%s&filename=libro_ventas.xls' % (rec.id),
            'target': 'new',
        }

    #Registro del Libro de Ventas de Contribuyentes
    def generate_records(self):
        result = []
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        total_iva = 0.00
        total_bienes_gravados = 0.00
        total_bienes_exentos = 0.00
        total_bienes_iva = 0.00
        total_bienes = 0.00
        total_serv_gravados = 0.00
        total_serv_exentos = 0.00
        total_serv_iva = 0.00
        total_expo_gravados = 0.00
        total_expo_exentos = 0.00
        total_expo_iva = 0.00
        total_nc_gravados = 0.00
        total_nc_exentos = 0.00
        total_nc_iva = 0.00
        total_nc = 0.00
        total_nd_gravados = 0.00
        total_nd_exentos = 0.00
        total_nd_iva = 0.00
        total_nd = 0.00
        total_ret = 0.00
        journal_ids = self.journal_ids.ids or False
        date_from = self.date_from
        date_to = self.date_to
        empresa = self.company_id or False
        folio = self.folio_inicial
        facturas = self.env['account.move'].search(
            [('state', 'in', ['posted', 'cancel']),
             ('journal_id', 'in', journal_ids),
             ('date', '>=', date_from),
             ('date', '<=', date_to),
             ('company_id', '=', empresa.id)], order='invoice_date, name')
        establecimientos = ", ".join([
            jou.name for jou in self.env['account.journal'].browse(
                journal_ids)])

        i = 1
        for inv in facturas:
            bien_local_gravado = 0.00
            servicio_local_gravado = 0.00
            bien_local_exento = 0.00
            servicio_local_exento = 0.00
            bien_expo_gravada = 0.00
            servicio_expo_gravada = 0.00
            bien_expo_exenta = 0.00
            servicio_expo_exento = 0.00
            iva_bien_l = 0.00
            iva_servicio_l = 0.00
            iva_bien_expo = 0.00
            iva_servicio_expo = 0.00
            total_iva = 0.00
            # amount_g = 0.00
            # amount_e = 0.00
            # amount_iva = 0.00
            tipo = inv.journal_id.name
            serie = inv.fel_serie
            numero = inv.fel_no
            retencion = 0.0
            fac_no = inv.name
            for tax in inv.amount_by_group:
                if 'PERCIBIDO' in str(tax[0]).upper():
                    retencion = float(tax[1])
            for tax in inv.amount_by_group:
                if 'RETENIDO' in str(tax[0]).upper():
                    retencion += float(tax[1])
            total_ret += retencion

            if inv.type == "out_refund":
                tipo = 'NC' if inv.amount_untaxed >= 0 else 'ND'

            for line in inv.invoice_line_ids:
                if inv.state != 'cancel':
                    precio = (line.quantity * line.price_unit)
                    discount = ((line.quantity * line.price_unit) * ((line.discount or 0.0) / 100.0))
                else:
                    precio = 0.00
                    discount = 0.00
                precio = (precio - discount)
                if inv.currency_id != empresa.currency_id:
                    # precio = inv.currency_id.compute(
                    #    precio, empresa.currency_id)
                    precio = inv.currency_id._convert(precio, empresa.currency_id, empresa, inv.invoice_date)
                # discount = ((line.quantity * line.price_unit) * (1 - (line.discount or 0.0) / 100.0))
                # precio = precio
                if tipo == 'NC':
                    precio = precio * -1
                # taxes = line.tax_ids.compute_all(
                #    precio, empresa.currency_id, line.quantity,
                #    line.product_id, inv.partner_id)
                taxes = line.tax_ids.compute_all(
                    precio, empresa.currency_id, 1.00,
                    line.product_id, inv.partner_id)
                aux_gravado = taxes['total_excluded']
                aux_iva = 0.00
                if line.tax_ids:
                    for tax in taxes['taxes']:
                        aux_iva += tax['amount']
                if line.product_id.tipo_gasto == "compra":
                    if 'exportación' not in inv.journal_id.name.lower():
                        if line.tax_ids:
                            bien_local_gravado += aux_gravado
                            iva_bien_l += aux_iva
                            if tipo == 'NC':
                                total_nc_gravados += aux_gravado
                                total_nc_iva += aux_iva
                            elif tipo == 'ND':
                                total_nd_gravados += aux_gravado
                                total_nd_iva += aux_iva
                            else:
                                total_bienes_gravados += aux_gravado
                                total_bienes_iva += aux_iva
                        else:
                            bien_local_exento += aux_gravado
                            if tipo == 'NC':
                                total_nc_exentos += aux_gravado
                            elif tipo == 'ND':
                                total_nd_exentos += aux_gravado
                            else:
                                total_bienes_exentos += aux_gravado
                    else:
                        if line.product_id.type == "service":
                            if line.tax_ids:
                                servicio_expo_gravada += aux_gravado
                                iva_servicio_expo += aux_iva
                            else:
                                servicio_expo_exento += aux_gravado
                        else:
                            if line.tax_ids:
                                bien_expo_gravada += aux_gravado
                                iva_bien_expo += aux_iva
                            else:
                                bien_expo_exenta += aux_gravado
                        if line.tax_ids:
                            if tipo == 'NC':
                                total_nc_gravados += aux_gravado
                                total_nc_iva += aux_iva
                            elif tipo == 'ND':
                                total_nd_gravados += aux_gravado
                                total_nd_iva += aux_iva
                            else:
                                total_expo_gravados += aux_gravado
                                total_expo_iva += aux_iva
                        else:
                            if tipo == 'NC':
                                total_nc_exentos += aux_gravado
                            elif tipo == 'ND':
                                total_nd_exentos += aux_gravado
                            else:
                                total_expo_exentos += aux_gravado
                elif line.product_id.tipo_gasto == "servicio":
                    if line.tax_ids:
                        servicio_local_gravado += aux_gravado
                        iva_servicio_l += aux_iva
                        if tipo == 'NC':
                            total_nc_gravados += aux_gravado
                            total_nc_iva += aux_iva
                        elif tipo == 'ND':
                            total_nd_gravados += aux_gravado
                            total_nd_iva += aux_iva
                        else:
                            total_serv_gravados += aux_gravado
                            total_serv_iva += aux_iva
                    else:
                        servicio_local_exento += aux_gravado
                        if tipo == 'NC':
                            total_nc_exentos += aux_gravado
                        elif tipo == 'ND':
                            total_nd_exentos += aux_gravado
                        else:
                            total_serv_exentos += aux_gravado
                elif line.product_id.tipo_gasto == "exportacion":
                    if line.product_id.type == "service":
                        if line.tax_ids:
                            servicio_expo_gravada += aux_gravado
                            iva_servicio_expo += aux_iva
                        else:
                            servicio_expo_exento += aux_gravado
                    else:
                        if line.tax_ids:
                            bien_expo_gravada += aux_gravado
                            iva_bien_expo += aux_iva
                        else:
                            bien_expo_exenta += aux_gravado
                    if line.tax_ids:
                        if tipo == 'NC':
                            total_nc_gravados += aux_gravado
                            total_nc_iva += aux_iva
                        elif tipo == 'ND':
                            total_nd_gravados += aux_gravado
                            total_nd_iva += aux_iva
                        else:
                            total_expo_gravados += aux_gravado
                            total_expo_iva += aux_iva
                    else:
                        if tipo == 'NC':
                            total_nc_exentos += aux_gravado
                        elif tipo == 'ND':
                            total_nd_exentos += aux_gravado
                        else:
                            total_expo_exentos += aux_gravado
            if tipo == 'NC':
                total_iva = sum([iva_bien_l, iva_servicio_l, iva_bien_expo,
                                 iva_servicio_expo, abs(retencion)])
            elif tipo == 'ND':
                total_iva = sum([iva_bien_l, iva_servicio_l, iva_bien_expo,
                                 iva_servicio_expo, retencion * -1])
            else:
                total_iva = sum([iva_bien_l, iva_servicio_l, iva_bien_expo,
                             iva_servicio_expo, retencion * -1])
            amount_total = sum([bien_local_gravado, servicio_local_gravado,
                                bien_local_exento, servicio_local_exento,
                                bien_expo_gravada, servicio_expo_gravada,
                                bien_expo_exenta, servicio_expo_exento,
                                total_iva, retencion])
            if inv.state == 'cancel':
                amount_total = 0.00
                bien_local_gravado = 0.00
                servicio_local_gravado = 0.00
                bien_local_exento = 0.00
                servicio_local_exento = 0.00
                bien_expo_gravada = 0.00
                servicio_expo_gravada = 0.00
                bien_expo_exenta = 0.00
                servicio_expo_exento = 0.00
                total_iva = 0.00
                retencion = 0.00

            date = inv.invoice_date if inv.invoice_date else inv.date
            linea = {
                'company': empresa.name or "",
                'nit': empresa.company_registry or "",
                'direccion': empresa.street,
                'folio_no': int(folio),
                'establecimientos': establecimientos,
                # 'mes': mes,
                'fecha': datetime.strptime(
                    str(date),
                    DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                'tipo': tipo,
                'serie': serie,
                'numero': numero if numero else inv.name,
                'nit_cliente': inv.partner_id.vat or "C/F",
                'nrc_cliente': inv.partner_id.nrc or "C/F",
                'cliente': str(inv.partner_id.name),
                'bienes_gravados': bien_local_gravado,
                'servicios_gravados': servicio_local_gravado,
                'bienes_exentos': bien_local_exento,
                'servicios_exentos': servicio_local_exento,
                'bienes_e_gravados': bien_expo_gravada,
                'servicios_e_gravados': servicio_expo_gravada,
                'bienes_e_exentos': bien_expo_exenta,
                'servicios_e_exentos': servicio_expo_exento,
                'iva': total_iva,
                'subtotal': amount_total,
                'no': i,
                'retencion': retencion if tipo != 'NC' else (retencion * -1),
                'fac_no': fac_no,
                'id': inv.id
            }
            i += 1
            result.append(linea)
        total_bienes = sum([total_bienes_gravados, total_bienes_exentos,
                            total_bienes_iva])
        total_servicios = sum([total_serv_gravados, total_serv_exentos,
                               total_serv_iva])
        total_nc = sum([total_nc_gravados, total_nc_exentos, total_nc_iva])
        total_nd = sum([total_nd_gravados, total_nd_exentos, total_nd_iva])
        total_gravado = sum([total_bienes_gravados, total_serv_gravados,
                             total_nc_gravados, total_nd_gravados,
                             total_expo_gravados])
        total_exento = sum([total_bienes_exentos, total_serv_exentos,
                            total_nc_exentos, total_nd_exentos,
                            total_expo_exentos])
        total_imp = sum([total_bienes_iva, total_serv_iva, total_nc_iva,
                         total_nd_iva, total_expo_iva])
        linea = {
            'cliente': "Totales",
            'total_bienes_gravados': total_bienes_gravados,
            'total_bienes_exentos': total_bienes_exentos,
            'total_bienes_iva': total_bienes_iva,
            'total_bienes': total_bienes,
            'total_servicios_gravados': total_serv_gravados,
            'total_servicios_exentos': total_serv_exentos,
            'total_servicios_iva': total_serv_iva,
            'total_servicios': total_servicios,
            'total_nc_gravados': total_nc_gravados,
            'total_nc_exentos': total_nc_exentos,
            'total_nc_iva': total_nc_iva,
            'total_nc': total_nc,
            'total_nd_gravados': total_nd_gravados,
            'total_nd_exentos': total_nd_exentos,
            'total_nd_iva': total_nd_iva,
            'total_nd': total_nd,
            'total_expo_gravados': total_expo_gravados,
            'total_expo_exentos': total_expo_exentos,
            'total_expo_iva': total_expo_iva,
            'total_expor': sum([total_expo_gravados, total_expo_exentos,
                                total_expo_iva]),
            'total_gravado': total_gravado,
            'total_exento': total_exento,
            'total_iva': sum([total_bienes_iva, total_serv_iva,
                              total_nc_iva, total_nd_iva, total_expo_iva]),
            'total_total': sum([total_gravado, total_exento, total_imp, total_ret]),
            'total_ret': total_ret,
        }
        #if company_id.country_id.code != 'SV' or cf:
        #    return result, linea
        #else:
        #    results = []
        #    folio = 1
        #    i = 1
        #    rows = []
        #    for row in result:
        #        rows.append(row)
        #        if i == rows_per_page:
        #            results.append([folio, rows])
        #            rows = []
        #            i = 1
        #            folio += 1
        #        else:
        #            i += 1
        #    if len(rows) > 0:
        #        results.append([folio, rows])
        return result, linea

    def print_purchase_excel(self):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for rec in self:
            if not rec.journal_ids:
                raise UserError(("No hay ningun diario seleccionado..!"))
            libro = xlwt.Workbook()
            hoja = libro.add_sheet('Libro de Ventas')

            titulos_principales_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz center; font:bold on;')
            titulos_texto_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz left;')
            titulos_numero_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz right;')
            company_tittle_style = xlwt.easyxf('align: horiz center; font:bold on;')
            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            #Tittles Styles
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
            sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz right; font:bold on;')
            text_sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz left; font:bold on;')
            #Titulos principal del Reporte
            hoja.write_merge(0, 0, 0, 9, rec.company_id.name, style=company_tittle_style)
            hoja.write_merge(1, 1, 0, 9, "Libro de Ventas a Contribuyentes", style=company_tittle_style)
            y = 4
            #Sub-titulo de datos del contribuyente
            hoja.write_merge(y, y, 0, 1, "Contibruyente:", style=company_tittle_style)
            hoja.write_merge(y, y, 2, 3, rec.company_id.name, style=company_tittle_style)
            hoja.write(y, 4, "NRC:", style=company_tittle_style)
            hoja.write(y, 5, rec.company_id.company_registry, style=company_tittle_style)
            hoja.write(y, 6, "NIT:", style=company_tittle_style)
            hoja.write(y, 7, rec.company_id.vat, style=company_tittle_style)
            month, year = self._get_date(rec.date_to)
            hoja.write(y, 8, (("MES: %s") %(month)), style=company_tittle_style)
            hoja.write(y, 9, (("AÑO: %s") %(year)), style=company_tittle_style)
            y = 6
            #Encabezados de Reporte
            hoja.col(0).width = 3000
            hoja.write(y, 0, 'No', style=titulos_principales_style)
            hoja.col(1).width = 3000
            hoja.write(y, 1, 'Emision', style=titulos_principales_style)
            hoja.col(2).width = 3000
            hoja.write(y, 2, 'NRC', style=titulos_principales_style)
            hoja.col(3).width = 3000
            hoja.write(y, 3, 'Numero', style=titulos_principales_style)
            hoja.col(4).width = 17000
            hoja.write(y, 4, 'Proveedor', style=titulos_principales_style)
            #hoja.col(4).width = 3000
            #hoja.write(y, 4, 'Numero', style=titulos_principales_style)
            hoja.col(5).width = 5000
            hoja.write(y, 5, 'Exentas Internas', style=titulos_principales_style)
            hoja.col(6).width = 5000
            hoja.write(y, 6, 'Exentas Importacion', style=titulos_principales_style)
            hoja.col(7).width = 5000
            hoja.write(y, 7, 'Gravadas Internas', style=titulos_principales_style)
            hoja.col(8).width = 5000
            hoja.write(y, 8, 'Gravadas Importacion', style=titulos_principales_style)
            hoja.col(9).width = 5000
            hoja.write(y, 9, 'Debito Fiscal', style=titulos_principales_style)
            hoja.col(10).width = 5000
            hoja.write(y, 10, 'Debito Fiscal Importaciones', style=titulos_principales_style)
            hoja.col(11).width = 5000
            hoja.write(y, 11, "Perc 1%", style=titulos_principales_style)
            hoja.col(12).width = 5000
            hoja.write(y, 12, 'Total', style=titulos_principales_style)
            hoja.col(13).width = 5000
            hoja.write(y, 13, 'Retenciones Terceros', style=titulos_principales_style)
            hoja.col(14).width = 5000
            hoja.write(y, 14, 'Compra Excluida', style=titulos_principales_style)
            #Generate Records
            result, linea = rec.generate_records_purchase()
            item = 0
            init_rows = y
            #Variables de Totals
            exentas_internas = exentas_import = gravadas_internas = gravadas_import = total_iva = total_iva_import = total_retencion = subtotal = 0.0
            for line in result:
                y += 1
                item += 1
                amount_exenta_internas = ((line.get('bienes_exentos', 0.00) + line.get('servicios_exentos', 0.00)) if line.get('importacion') == False else 0.00)
                amount_gravadas_internas = ((line.get('bienes_gravados', 0) + line.get('servicios_gravados', 0) + line.get('bienes_pc', 0)) if line.get('importacion') == False else 0.00)
                amount_gravadas_import = (line.get('bienes_i_gravados', 0) + line.get('servicios_i_gravados', 0))
                hoja.write(y, 0, item, style=titulos_texto_style)
                hoja.write(y, 1, line.get('fecha', ''), style=titulos_texto_style)
                hoja.write(y, 2, line.get('nrc_cliente', ''), style=titulos_texto_style)
                hoja.write(y, 4, line.get('cliente', ''), style=titulos_texto_style)
                hoja.write(y, 3, line.get('fac_no', ''), style=titulos_texto_style)
                hoja.write(y, 5, amount_exenta_internas, style=titulos_numero_style)
                hoja.write(y, 6, 0.00, style=titulos_numero_style)
                hoja.write(y, 7, amount_gravadas_internas, style=titulos_numero_style)
                hoja.write(y, 8, amount_gravadas_import, style=titulos_numero_style)
                hoja.write(y, 9, (line.get('iva', 0.00) if line.get('importacion') == False else 0.00), style=titulos_numero_style)
                hoja.write(y, 10, (line.get('iva', 0.00) if line.get('importacion') else 0.00), style=titulos_numero_style)
                hoja.write(y, 11, line.get('percibido', ''), style=titulos_numero_style)
                hoja.write(y, 12, line.get('subtotal', 0.00), style=titulos_numero_style)
                hoja.write(y, 13, "", style=titulos_numero_style)
                hoja.write(y, 14, 0.00, style=titulos_numero_style)
                exentas_internas += amount_exenta_internas
                gravadas_internas += amount_gravadas_internas
                gravadas_import += amount_gravadas_import
                total_iva += (line.get('iva', 0.00) if line.get('importacion') == False else 0.00)
                total_iva_import += (line.get('iva', 0.00) if line.get('importacion') else 0.00)
                total_retencion += line.get('percibdo', 0.00)
                subtotal += line.get('subtotal', 0.00)
            #Dibujado de total de libro
            y +=1
            hoja.write_merge(y, y, 0, 4, "*TOTAL*", style=sums_style)
            hoja.write(y, 5, exentas_internas, style=sums_style)
            hoja.write(y, 6, 0.00, style=sums_style)
            hoja.write(y, 7, gravadas_internas, style=sums_style)
            hoja.write(y, 8, gravadas_import, style=sums_style)
            hoja.write(y, 9, total_iva, style=sums_style)
            hoja.write(y, 10, total_iva_import, style=sums_style)
            hoja.write(y, 11, total_retencion, style=sums_style)
            hoja.write(y, 12, subtotal, style=sums_style)
            hoja.write(y, 13, "", style=sums_style)
            hoja.write(y, 14, "", style=sums_style)
            #Resumen de Impuestos
            #Titulos
            
            #Save Excel in Wizard
            fp = BytesIO()
            libro.save(fp)
            fp.seek(0)
            report_data_file = base64.encodestring(fp.read())
            fp.close()
            self.write({'file': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.ventas.compras.sv&field=file&download=true&id=%s&filename=libro_compras.xls' % (rec.id),
            'target': 'new',
        }

    #Registros del Libro de Compra de Contribuyentes
    def generate_records_purchase(self):
        result = []
        tax = self.env['account.tax']
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        tipo_doc = ""
        bienes_gravados = 0.00
        servicios_gravados = 0.00
        bienes_exentos = 0.00
        servicios_exentos = 0.00
        bienes_pc = 0.00
        servicios_pc = 0.00
        # retenciones = 0.00
        bienes_i_gravados = 0.00
        servicios_i_gravados = 0.00
        bienes_i_exentos = 0.00
        servicios_i_exentos = 0.00
        iva_bienes = 0.00
        iva_combustibles = 0.00
        iva_servicios = 0.00
        iva_impo = 0.00
        # iva_impo_s = 0.00
        # iva_impo_b = 0.00
        iva_subtotal = 0.00
        otros_impuestos = 0.00
        # idp = 0.00
        amount_g = 0.00
        amount_e = 0.00
        amount_pc = 0.00
        # amount_imp = 0.00
        amount_iva = 0.00
        subtotal = 0.00
        # total_iva = 0.00
        total_bienes_g = 0.00
        total_bienes_e = 0.00
        total_bienes_pc = 0.00
        # total_bienes = 0.00
        total_serv_g = 0.00
        total_serv_e = 0.00
        total_serv_pc = 0.00
        # total_serv= 0.00
        total_impo_g = 0.00
        total_impo_e = 0.00
        total_impo_pc = 0.00
        # total_impo = 0.00
        total_comb_g = 0.00
        total_comb_e = 0.00
        total_comb_pc = 0.00
        # total_comb = 0.00
        fac_pc = 0
        establecimientos = ""
        mes = ""
        journal_ids = self.journal_ids.ids
        date_from = self.date_from
        date_to = self.date_to
        tax_ids = tax.search(
            ['|', ('tax_group_id', '=', self.tax_id.id),
             ('tax_group_id', '=', self.tax_id.id),
             ('type_tax_use', '=', 'purchase')]).mapped('id')
        # base_id = data['form']['base_id']
        compania = self.company_id
        folio = self.folio_inicial
        total_ret = 0.00
        facturas = self.env['account.move'].search(
            [('state', 'in', ['posted']),
             ('journal_id', 'in', journal_ids),
             ('date', '>=', date_from),
             ('date', '<=', date_to),
             ('invoice_date', '!=', False),
             ('company_id', '=', compania.id)], order='invoice_date, name')
        empresa = self.company_id
        establecimientos = ", ".join([
            jou.name for jou in self.env['account.journal'].browse(
                journal_ids)])
        # for journal in self.env['account.journal'].browse(journal_ids):
        #     establecimientos += journal.name.encode(
        #         'ascii', 'ignore') + ", "
        no = 1
        for inv in facturas:
            # tipo_doc = inv.tipo_documento
            # if inv.type != 'in_invoice':
            #     tipo_doc = 'NC'
            tipo_doc = 'NC' if inv.type != 'in_invoice' else inv.tipo_documento
            bienes_gravados = 0.00
            servicios_gravados = 0.00
            bienes_exentos = 0.00
            servicios_exentos = 0.00
            bienes_pc = 0.00
            servicios_pc = 0.00
            bienes_i_gravados = 0.00
            servicios_i_gravados = 0.00
            bienes_i_exentos = 0.00
            servicios_i_exentos = 0.00
            iva_subtotal = 0.00
            # iva_subtotal_b = 0.00
            # iva_subtotal_s = 0.00
            # iva_subtotal_c = 0.00
            # iva_subtotal_i = 0.00
            otros_impuestos_b = 0.00
            otros_impuestos_s = 0.00
            retenciones_s = 0.00
            retenciones_b = 0.00
            amount_g = 0.00
            amount_e = 0.00
            amount_pc = 0.00
            # fac_pc = 0
            # amount_imp = 0.00
            amount_iva = 0.00
            # idp = 0.00
            subtotal = 0.00
            tipo_cambio = 1
            # cheque = inv.doc_origen_serie or ""
            # orden = inv.doc_origen_num or ""
            # if inv.currency_id.id != inv.company_id.currency_id.id:
            #    total = 0
            #    #for line in inv.line_ids:
            #    #    if line.account_id.id == inv.account_id.id:
            #    #        total += line.credit - line.debit
            #    tipo_cambio = 1.00
            estado = 'E'
            if inv.state == 'cancel':
                estado = 'A'
            retencion = 0.0
            retencion_terceros = 0.0
            fac_no = inv.name

            for tax in inv.amount_by_group:
                if 'RETENIDO 1%' in str(tax[0]).upper():
                    retencion = float(tax[1])
            total_ret += retencion
            fovial = 0

            for tax in inv.amount_by_group:
                if 'ISR' in str(tax[0]).upper():
                    retencion_terceros = float(tax[1])

                # Verificar si es una factura de combustible
                if 'FOVIAL' in str(tax[0]).upper():
                    fovial += tax[1]


            for line in inv.invoice_line_ids:

                precio = line.price_total if inv.state != 'cancel' else 0.0
                if inv.currency_id != empresa.currency_id:
                    precio = inv.currency_id._convert(precio, empresa.currency_id, empresa, inv.invoice_date)
                precio = precio if estado != 'A' else 0.0
                if tipo_doc == 'NC':
                    precio = precio * -1
                # taxes = line.tax_ids.compute_all(
                #    precio, empresa.currency_id, line.quantity,
                #    line.product_id, inv.partner_id)
                taxes = line.tax_ids.compute_all(
                    precio, empresa.currency_id, 1.00,
                    line.product_id, inv.partner_id)
                if line.product_id.tipo_gasto == 'compra':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                bienes_pc += i['amount']
                                total_bienes_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos_b += i['amount']
                        bienes_pc += (taxes['total_excluded'])
                        total_bienes_pc += (taxes['total_excluded'])
                        otros_impuestos_b = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += line.balance * 0.13
                                    iva_bienes += line.balance * 0.13
                                    # iva_subtotal += i['amount']
                                    # iva_bienes += i['amount']
                                elif i['amount'] > 0:
                                    otros_impuestos_b += i['amount']
                                elif i['amount'] < 0:
                                    retenciones_b += i['amount']
                                # bienes_gravados += (taxes['total_excluded'])
                                # total_bienes_g += (taxes['total_excluded'])
                            bienes_gravados += line.balance
                            total_bienes_g += line.balance
                            otros_impuestos_b = 0.00
                            retenciones_b = 0.00
                        else:
                            bienes_exentos += taxes['total_excluded']
                            total_bienes_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'servicio':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                servicios_pc += i['amount']
                                total_serv_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos_s += i['amount']
                        servicios_pc += (taxes['total_excluded'])
                        total_serv_pc += (taxes['total_excluded'])
                        otros_impuestos_s = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += i['amount']
                                    iva_servicios += i['amount']
                                elif i['amount'] > 0:
                                    otros_impuestos_s += i['amount']
                                elif i['amount'] < 0:
                                    retenciones_s += i['amount']
                                servicios_gravados += (taxes['total_excluded'])
                                total_serv_g += (taxes['total_excluded'])
                                otros_impuestos_s = 0.00
                                retenciones_s = 0.00
                        else:
                            servicios_exentos += taxes['total_excluded']
                            total_serv_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'combustibles':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                bienes_pc += i['amount']
                                total_comb_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos += i['amount']
                        bienes_pc += (taxes['total_excluded'])
                        total_comb_pc += (taxes['total_excluded'])
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += i['amount']
                                    iva_combustibles += i['amount']
                                elif i['amount'] > 0:
                                    bienes_exentos += i['amount']
                                    total_comb_e += i['amount']
                                elif i['amount'] < 0:
                                    otros_impuestos += i['amount']
                            bienes_gravados += taxes['total_excluded']
                            total_comb_g += taxes['total_excluded']
                        else:
                            bienes_exentos += taxes['total_excluded']
                            total_comb_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'importacion':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                amount_iva = i['amount']
                            # elif i['amount'] > 0:
                            #     amount_imp = i['amount']
                        amount_pc = (taxes['total_excluded'] + amount_iva)
                        amount_iva = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    amount_iva = i['amount']
                                # elif i['amount'] > 0:
                                #     amount_imp = i['amount']
                            amount_g = taxes['total_excluded']
                        else:
                            amount_e = taxes['total_excluded']
                    if line.product_id.type == "service":
                        if inv.tipo_documento == 'FPC':
                            servicios_pc += amount_pc
                            total_impo_pc += amount_pc
                        else:
                            if line.tax_ids:
                                servicios_i_gravados += amount_g
                                iva_subtotal += amount_iva
                                total_impo_g += amount_g
                                iva_impo += amount_iva
                            else:

                                servicios_i_exentos += amount_e
                                total_impo_e += amount_e
                    else:
                        if inv.tipo_documento == 'FPC':
                            bienes_pc += amount_pc
                            total_impo_pc += amount_pc
                        else:
                            if line.tax_ids:
                                bienes_i_gravados += amount_g
                                iva_subtotal += amount_iva
                                total_impo_g += amount_g
                                iva_impo += amount_iva
                            else:
                                bienes_i_exentos += amount_e
                                total_impo_e += amount_e
            # Agregar el 13% de la importacion al iva_subtotal
            if inv.DUCA:
                iva_subtotal += inv.DUCA
                bienes_i_gravados += inv.DUCA / 0.13
            bienes_exentos += fovial
            subtotal = sum([bienes_gravados, servicios_gravados,
                            bienes_exentos, servicios_exentos,
                            bienes_pc, servicios_pc, bienes_i_gravados,
                            servicios_i_gravados, bienes_i_exentos,
                            servicios_i_exentos, iva_subtotal,retencion])
            linea = {
                'nit': empresa.company_registry or "",
                'company': empresa.name.encode('ascii', 'ignore') or '',
                'direccion': empresa.street.encode(
                    'ascii', 'ignore') or '',
                'folio_no': int(folio),
                'establecimientos': establecimientos,
                'mes': mes,
                'fecha': datetime.strptime(
                    str(inv.invoice_date),
                    DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                'tipo': tipo_doc,
                'estado': estado,
                'serie': inv.serie_factura,
                'numero': inv.name,
                'origen': "N/A",
                'nit_cliente': inv.partner_id.vat or "C/F",
                'nrc_cliente': inv.partner_id.nrc or "C/F",
                'cliente': inv.partner_id.name or '',
                'bienes_gravados': bienes_gravados,
                'servicios_gravados': servicios_gravados,
                'bienes_exentos': bienes_exentos,
                'servicios_exentos': servicios_exentos,
                'bienes_pc': bienes_pc,
                'servicios_pc': servicios_pc,
                'bienes_i_gravados': bienes_i_gravados,
                'servicios_i_gravados': servicios_i_gravados,
                'bienes_i_exentos': bienes_i_exentos,
                'servicios_i_exentos': servicios_i_exentos,
                'iva': iva_subtotal,
                'subtotal': subtotal,
                'no': no,
                'retencion': retencion,
                'percibido': inv.amount_percibido,
                'retencion_terceros': retencion_terceros,
                'fac_no': fac_no,
                'importacion': inv.journal_id.importacion
            }
            no += 1
            result.append(linea)
        total_comb = sum([total_comb_g, total_comb_e, total_comb_pc,
                          iva_combustibles])
        total_g = sum([total_bienes_g, total_comb_g, total_serv_g,
                       total_impo_g])
        total_e = sum([total_bienes_e, total_comb_e, total_serv_e,
                       total_impo_e])
        total_pc = sum([total_bienes_pc, total_comb_pc, total_serv_pc,
                        total_impo_pc])
        total_iva = sum([iva_bienes, iva_servicios, iva_impo,
                         iva_combustibles])
        # total_total = sum([total_g, total_e, total_pc, total_iva])
        linea = {
            'cliente': "Totales",
            'total_bienes_g': total_bienes_g,
            'total_bienes_e': total_bienes_e,
            'total_bienes_pc': total_bienes_pc,
            'total_bienes_iva': iva_bienes,
            'total_bienes': sum([total_bienes_g, total_bienes_e,
                                 total_bienes_pc, iva_bienes]),
            'total_serv_g': total_serv_g,
            'total_serv_e': total_serv_e,
            'total_serv_pc': total_serv_pc,
            'total_serv_iva': iva_servicios,
            'total_serv': sum([total_serv_g, total_serv_e, total_serv_pc,
                               iva_servicios]),
            'total_impo_g': total_impo_g,
            'total_impo_e': total_impo_e,
            'total_impo_pc': total_impo_pc,
            'total_impo_iva': iva_impo,
            'total_impo': sum([total_impo_g, total_impo_e, total_impo_pc,
                               iva_impo]),
            'total_comb_g': total_comb_g,
            'total_comb_e': total_comb_e,
            'total_comb_pc': total_comb_pc,
            'total_comb_iva': iva_combustibles,
            'total_comb': total_comb,
            'total_g': total_g,
            'total_e': total_e,
            'total_pc': total_pc,
            'total_iva': total_iva,
            'total_total': sum([total_g, total_e, total_pc, total_iva]),
            'fac_pc': int(fac_pc),
            'fac_c': len(facturas) - fac_pc,
            'fac_total': len(facturas),
        }

        #if company_id.country_id.code != 'SV':
        #    return result, linea
        #else:
        #    results = []
        #    folio = 1
        #    i = 1
        #    rows = []
        #    for row in result:
        #        rows.append(row)
        #        if i == rows_per_page:
        #            results.append([folio, rows])
        #            rows = []
        #            i = 1
        #            folio += 1
        #        else:
        #            i += 1
        #    if len(rows) > 0:
        #        results.append([folio, rows])
        return result, linea

    def _get_date(self, date):
        month = datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT).strftime("%B")
        year = datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y")
        months = {'january': 'enero', 'february': 'febrero', 'march': 'marzo', 'april': 'abril', 'may': 'mayo',
                  'june': 'junio', 'july': 'julio', 'august': 'agosto', 'september': 'septiembre',
                  'november': 'noviembre', 'december': 'diciembre'}
        for k, v in months.items(): month = month.lower().replace(k, v)
        return month.capitalize(), year

    def print_sale_ccf(self):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for rec in self:
            if not rec.journal_ids:
                raise UserError(("No hay ningun diario seleccionado..!"))
            libro = xlwt.Workbook()
            hoja = libro.add_sheet('Libro de Ventas Consumidor Final')

            titulos_principales_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
            left thin, right thin, top thin, bottom thin; align: horiz center; font:bold on;')
            titulos_texto_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz left;')
            titulos_numero_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz right;')
            company_tittle_style = xlwt.easyxf('align: horiz center; font:bold on;')
            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            #Tittles Styles
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
            sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz right; font:bold on;')
            text_sums_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin; align: horiz left; font:bold on;')
            #Titulos principal del Reporte
            hoja.write_merge(0, 0, 0, 9, rec.company_id.name, style=company_tittle_style)
            hoja.write_merge(1, 1, 0, 9, "Libro de Ventas Consumidor Final", style=company_tittle_style)
            y = 4
            #Sub-titulo de datos del contribuyente
            hoja.write_merge(y, y, 0, 1, "Contibruyente:", style=company_tittle_style)
            hoja.write_merge(y, y, 2, 3, rec.company_id.name, style=company_tittle_style)
            hoja.write(y, 4, "NRC:", style=company_tittle_style)
            hoja.write(y, 5, rec.company_id.company_registry, style=company_tittle_style)
            hoja.write(y, 6, "NIT:", style=company_tittle_style)
            hoja.write(y, 7, rec.company_id.vat, style=company_tittle_style)
            month, year = self._get_date(rec.date_to)
            hoja.write(y, 8, (("MES: %s") %(month)), style=company_tittle_style)
            hoja.write(y, 9, (("AÑO: %s") %(year)), style=company_tittle_style)
            y = 6
            #Encabezados de Reporte
            hoja.col(0).width = 3000
            hoja.write(y, 0, 'No', style=titulos_principales_style)
            hoja.col(1).width = 3000
            hoja.write(y, 1, 'Emision', style=titulos_principales_style)
            hoja.col(2).width = 3000
            hoja.write(y, 2, 'Del', style=titulos_principales_style)
            hoja.col(3).width = 3000
            hoja.write(y, 3, 'Al', style=titulos_principales_style)
            hoja.col(4).width = 5000
            hoja.write(y, 4, 'Gravadas', style=titulos_principales_style)
            hoja.col(5).width = 5000
            hoja.write(y, 5, 'Exentas', style=titulos_principales_style)
            hoja.col(6).width = 5000
            hoja.write(y, 6, 'Exportacion', style=titulos_principales_style)
            hoja.col(7).width = 5000
            hoja.write(y, 7, 'Ret/Per', style=titulos_principales_style)
            hoja.col(8).width = 5000
            hoja.write(y, 8, 'Total', style=titulos_principales_style)
            hoja.col(9).width = 5000
            hoja.write(y, 9, 'Ventas a Terceros', style=titulos_principales_style)
            result, lineas = self.generate_records()
            vals = self.generate_records_ccf(data=result)
            #raise UserError((vals))
            row = 0
            total_amount_gravado = total_amount_exento = total_amount_export = total_amount_ret_perc = total_amount_iva = total_total = 0.00
            for key, value in vals.items():
                y += 1
                row += 1
                amount_gravado = amount_exento = amount_export = amount_ret_perc = amount_iva = total = 0.00
                number_range = []
                _logger.info(value)
                for item in value:
                    number_range.append(item.get('fac_no', ""))
                    amount_gravado += (item.get('bienes_gravados', 0.00) + item.get('servicios_gravados', 0.00))
                    amount_exento += (item.get('bienes_exentos', 0.00) + item.get('servicios_exentos', 0.00))
                    amount_export += (item.get('bienes_e_gravados', 0.00) + item.get('servicios_e_gravados', 0.00) + item.get('bienes_e_exentos', 0.00) + item.get('servicios_e_exentos', 0.00))
                    amount_ret_perc += item.get('retencion', 0.00)
                    amount_iva += item.get('iva', 0.00)
                    total += item.get('subtotal', 0.00)
                    #Totales Generales de los montos
                    total_amount_gravado += (item.get('bienes_gravados', 0.00) + item.get('servicios_gravados', 0.00))
                    total_amount_exento += (item.get('bienes_exentos', 0.00) + item.get('servicios_exentos', 0.00))
                    total_amount_export += (item.get('bienes_e_gravados', 0.00) + item.get('servicios_e_gravados', 0.00) + item.get('bienes_e_exentos', 0.00) + item.get('servicios_e_exentos', 0.00))
                    total_amount_ret_perc += item.get('retencion', 0.00)
                    total_amount_iva += item.get('iva', 0.00)
                    total_total += item.get('subtotal', 0.00)
                _logger.info("*************Number Range*****************")
                _logger.info(number_range)
                #Dibujado de las facturas
                number_from = number_range[0] if number_range and len(number_range) > 0 else ""
                number_to = number_range[len(number_range) - 1] if number_range and len(number_range) > 0 else ""
                hoja.write(y, 0, row, style=titulos_texto_style)
                hoja.write(y, 1, key, style=titulos_texto_style)
                hoja.write(y, 2, number_from, style=titulos_texto_style)
                hoja.write(y, 3, number_to, style=titulos_texto_style)
                hoja.write(y, 4, amount_gravado, style=titulos_numero_style)
                hoja.write(y, 5, amount_exento, style=titulos_numero_style)
                hoja.write(y, 6, amount_export, style=titulos_numero_style)
                hoja.write(y, 7, amount_ret_perc, style=titulos_numero_style)
                hoja.write(y, 8, (total), style=titulos_numero_style)
                hoja.write(y, 9, "", style=titulos_numero_style)
            #Dibujado de total de libro
            y +=1
            hoja.write_merge(y, y, 0, 3, "*TOTAL*", style=sums_style)
            hoja.write(y, 4, total_amount_gravado, style=sums_style)
            hoja.write(y, 5, total_amount_exento, style=sums_style)
            hoja.write(y, 6, total_amount_export, style=sums_style)
            hoja.write(y, 7, total_amount_ret_perc, style=sums_style)
            hoja.write(y, 8, total_total, style=sums_style)
            hoja.write(y, 9, '', style=sums_style)
            #Save Excel in Wizard
            fp = BytesIO()
            libro.save(fp)
            fp.seek(0)
            report_data_file = base64.encodestring(fp.read())
            fp.close()
            self.write({'file': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.ventas.compras.sv&field=file&download=true&id=%s&filename=libro_ventas_ccf.xls' % (rec.id),
            'target': 'new',
        }
        
    def generate_records_ccf(self, data=None):
        grouped_result = {}
        if data:
            grouped_result = {}
            for row in data:
                date = row.get('fecha', False)
                if date not in grouped_result:
                    grouped_result[date] = []
                grouped_result[date].append(row)
        return grouped_result

WizardVentasCompras()