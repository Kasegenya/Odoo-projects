from odoo import models, fields, api, _


class stockPicking(models.Model):
    _inherit = "stock.picking"


    order_ref = fields.Char('Order Reference')

class hrExpense(models.Model):
    _inherit = "hr.expense"

    purchase_order_no = fields.Many2one('purchase.order', string='Purchase Order')
    po_ref = fields.Char('Order reference', compute='_get_po_number')

    @api.depends('purchase_order_no')
    def _get_po_number(self):
       for rec in self:
           rec.po_ref = rec.purchase_order_no.customer_po_ref

class accountMove(models.Model):
    _inherit = "account.move"


    purchase_order_ref = fields.Char('Purchase Order Reference')
    other_comments = fields.Char('Comments')
    delivery_term = fields.Char('Delivery Term')
    internal_reference = fields.Char('Internal Reference')
    validity = fields.Char('Validity', tracking=True)
    xlsx_file = fields.Binary('XLSX Report')
    contact_person_id  = fields.Many2one('res.partner', string='Contact Person')
    child_ids = fields.Many2many('res.partner', string='Child Contacts', compute='_compute_child_ids')
    @api.depends('partner_id')
    def _compute_child_ids(self):
        for rec in self:
            rec.child_ids = rec.partner_id.child_ids




    def action_print_xlsx(self):
        from io import BytesIO
        import xlsxwriter
        import base64
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()

        # formating the whole sheet not to have any gridlines
        sheet.hide_gridlines(2)
        # enforce contents to fit in A4 paper
        sheet.set_paper(9)
        sheet.center_vertically()

        totals = workbook.add_format()
        totals.set_font_size(10)

        to_info = workbook.add_format({
            'bold': True
            })
        to_info.set_font_size(10)

        comment_info = workbook.add_format({
            'border': 1,
            })
        comment_info.set_font_size(10)

        date_field = workbook.add_format({
            'border': 1,
            'align': 'start'
            })
        date_field.set_font_size(10)
        date_field.set_num_format(15)

        
        total_amount = workbook.add_format({
            'font_size': '12',
            'bold': True
            })
        total_amount.set_font_size(10)
        total_amount.set_num_format(4)

        cell_format = workbook.add_format({
            'font_size': '11',
             'border': 1,
             'align': 'start'
             })
        cell_format.set_font_size(10)

        head = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '20px',
            'color': '#3464ab'
            })
        table_heads = workbook.add_format({
            'align': 'center',
            'bg_color': '#3464ab',
            'bold': True,
            'color': 'white'
            })
        table_heads.set_font_size(10)

        serial_number = workbook.add_format({
            'align': 'left',
            'bg_color': '#3464ab',
            'bold': True,
            'color': 'white'
            })
        serial_number.set_font_size(10)         
        company_logo = BytesIO(base64.b64decode(self.company_id.logo))
        sheet.merge_range('A1:B2', '')
        if self.company_id == 1:
            sheet.insert_image('A1', 'company_logo.png', {'image_data': company_logo, 'x_scale': 0.07, 'y_scale': 0.1})
        else:
            sheet.insert_image('A1', 'company_logo.png', {'image_data': company_logo, 'x_scale': 0.9, 'y_scale': 0.6})


        sheet.merge_range('B1:E1', '')
        sheet.merge_range('F1:G1', 'TAX INVOICE', head)
        sheet.write('A4', 'To', table_heads)
        sheet.write('A5', ' [Attn]: '+ self.partner_id.name or '', to_info)
        sheet.write('A6', ' [Company]: '+ self.partner_id.name or '', to_info)
        sheet.write('A7', ' [Street Address]: '+ self.partner_id.street or '', to_info)
        sheet.write('A8', ' [Phone]: '+ self.partner_id.phone or '', to_info)

        sheet.write('F5', 'Date', cell_format)
        sheet.write('G5', self.invoice_date, date_field)
        sheet.write('F6', 'TI #', cell_format)
        sheet.write('G6', self.purchase_order_ref, cell_format)
        sheet.write('F7', 'Customer Id', cell_format)
        sheet.write('G7', self.partner_id.id, cell_format)
        sheet.write('F8', 'Validity', cell_format)
        sheet.write('G8', self.validity, cell_format)
        sheet.write('F9', 'TIN', cell_format)
        sheet.write('G9', self.company_id.vat, cell_format)
        sheet.write('F10', 'VRN', cell_format)
        sheet.write('G10', self.company_id.company_vrn, cell_format)
        sheet.write('F11', 'REF', cell_format)
        sheet.write('G11', self.name, cell_format)

        # now table for order lines
        sheet.write('A13', 'S.No', serial_number)
        sheet.write('B13', 'Part Number', table_heads)
        sheet.write('C13', 'Description', table_heads)
        sheet.write('D13', 'Quantity', table_heads)
        sheet.write('E13', 'UOM', table_heads)
        sheet.write('F13', 'Unit Price', table_heads)
        sheet.write('G13', 'Total', table_heads)

        row = 13   
        for line in self.invoice_line_ids:
            sheet.write(row, 0, row-12, cell_format)
            sheet.write(row, 1, line.product_id.default_code, cell_format)
            sheet.write(row, 2, line.product_id.name, cell_format)
            sheet.write(row, 3, line.quantity, cell_format)
            sheet.write(row, 4, line.product_uom_id.name, cell_format)
            currency_symbol = self.currency_id.symbol or ''
            formatted_unit = f"{currency_symbol}  {line.price_unit:,.2f}"
            sheet.write(row, 5, formatted_unit, cell_format)
            formated_total = f"{currency_symbol}  {line.price_subtotal:,.2f}"
            sheet.write(row, 6, formated_total, cell_format)
            row += 1

            # now total, tax and discount each on new row
        sheet.write(row, 5, 'Total', totals)
        sheet.write(row, 6, self.amount_untaxed, totals)
        row += 1
        sheet.write(row, 5, 'Taxable', totals)
        sheet.write(row, 6, self.amount_untaxed, totals)
        row += 1
        sheet.write(row, 5, 'Tax Rate (VAT)', totals)
        sheet.write(row, 6, '18%', totals)
        row += 1
        sheet.write(row, 5, 'Taxes Due', totals)
        sheet.write(row, 6, self.amount_tax, totals)
        row += 1
        sheet.write(row, 5, 'Discount', totals)
        currency_symbol = self.currency_id.symbol or ''
        discount_percentage = sum([(l.discount*line.price_unit)/100 for l in self.invoice_line_ids if l.discount])
        formated_discount = f"{currency_symbol}  {discount_percentage:,.2f}"
        sheet.write(row, 6, formated_discount, totals)
        row += 1
        sheet.write(row, 5, 'Total', total_amount)
        formatted_amount = f"{currency_symbol}  {self.amount_total:,.2f}"
        sheet.write(row, 6,formatted_amount, total_amount)

        


        # merge range column 1 up to 2
        sheet.merge_range('A'+str(row+2)+':B'+str(row+2), 'Other Comments', table_heads)
        sheet.merge_range('A'+str(row+3)+':B'+str(row+3), 'Delivery Time: '+ str(self.delivery_date), comment_info)
        sheet.merge_range('A'+str(row+4)+':B'+str(row+4), 'Condition of the Parts: Original and New' , comment_info)
        sheet.merge_range('A'+str(row+5)+':B'+str(row+5), 'Delivery Term: '+ str(self.delivery_term), comment_info)


        workbook.close()
        output.seek(0)
        xlsx_data = base64.b64encode(output.read())
        self.write({'xlsx_file': xlsx_data})

        attachment = self.env['ir.attachment'].create({
            'name': self.name+'-'+'report.xlsx',
            'type': 'binary',
            'datas': self.xlsx_file,
            'store_fname': self.name +'_'+'report.xlsx',
            'res_model': 'documents.document',
            'res_id': self.id,  # Will be linked to document in next step
        })

        # Create document record in the Documents module
        document = self.env['documents.document'].create({
            'name': self.name+'-'+'report.xlsx',
            'folder_id': 1,
            'attachment_id': attachment.id,
        })
        return document

class quotationSales(models.Model):
    _inherit = "sale.order"

    delivery_term = fields.Char('Delivery Term')
    other_comments = fields.Char('Comments')
    delivery_period = fields.Char('Delivery Period')
    purchase_enquiry_ref = fields.Char('Purchase Enquiry Reference')
    purchase_order_reference = fields.Char('Purchase Order Reference')
    validity = fields.Char('Validity', tracking=True)
    contact_person_id  = fields.Many2one('res.partner', string='Contact Person')
    child_ids = fields.Many2many('res.partner', string='Child Contacts', compute='_compute_child_ids')
    @api.depends('partner_id')
    def _compute_child_ids(self):
        for rec in self:
            rec.child_ids = rec.partner_id.child_ids

    xlsx_file = fields.Binary('XLSX Report')

    def action_print_xlsx(self):
        from io import BytesIO
        import xlsxwriter
        import base64
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()

        # formating the whole sheet not to have any gridlines
        sheet.hide_gridlines(2)
        # enforce contents to fit in A4 paper
        sheet.set_paper(9)
        sheet.center_vertically()

        totals = workbook.add_format()
        totals.set_font_size(10)

        to_info = workbook.add_format({
            'bold': True
            })
        to_info.set_font_size(10)

        comment_info = workbook.add_format({
            'border': 1,
            })
        comment_info.set_font_size(10)

        date_field = workbook.add_format({
            'border': 1,
            'align': 'start'
            })
        date_field.set_font_size(10)
        date_field.set_num_format(15)

        
        total_amount = workbook.add_format({
            'font_size': '12',
            'bold': True
            })
        total_amount.set_font_size(10)
        total_amount.set_num_format(4)

        cell_format = workbook.add_format({
            'font_size': '11',
             'border': 1,
             'align': 'start'
             })
        cell_format.set_font_size(10)

        head = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '20px'
            })
        table_heads = workbook.add_format({
            'align': 'center',
            'bg_color': '#3464ab',
            'bold': True,
            'color': 'white'
            })
        table_heads.set_font_size(10)

        serial_number = workbook.add_format({
            'align': 'left',
            'bg_color': '#3464ab',
            'bold': True,
            'color': 'white'
            })
        serial_number.set_font_size(10)         
        company_logo = BytesIO(base64.b64decode(self.company_id.logo))
        sheet.merge_range('A1:B2', '')
        if self.company_id == 1:
            sheet.insert_image('A1', 'company_logo.png', {'image_data': company_logo, 'x_scale': 0.07, 'y_scale': 0.1})
        else:
            sheet.insert_image('A1', 'company_logo.png', {'image_data': company_logo, 'x_scale': 0.9, 'y_scale': 0.6})



        sheet.merge_range('B1:E1', '')
        sheet.merge_range('F1:G1', 'PROFOMA INVOICE', head)
        sheet.write('A4', 'To', table_heads)
        sheet.write('A5', ' [Attn]: '+ self.contact_person_id.name, to_info)
        sheet.write('A6', ' [Company]: '+ self.partner_id.name, to_info)
        sheet.write('A7', ' [Street Address]: '+ self.partner_id.street, to_info)
        sheet.write('A8', ' [Phone]: '+ self.partner_id.phone, to_info)

        sheet.write('F5', 'Date', cell_format)
        sheet.write('G5', self.date_order, date_field)
        sheet.write('F6', 'PI #', cell_format)
        sheet.write('G6', self.name, cell_format)
        sheet.write('F7', 'Customer Id', cell_format)
        sheet.write('G7', self.partner_id.id, cell_format)
        sheet.write('F8', 'Validity', cell_format)
        sheet.write('G8', str(self.payment_term_id.name), cell_format)
        sheet.write('F9', 'TIN', cell_format)
        sheet.write('G9', self.company_id.vat, cell_format)
        sheet.write('F10', 'VRN', cell_format)
        sheet.write('G10', self.company_id.company_vrn, cell_format)
        sheet.write('F11', 'REF', cell_format)
        sheet.write('G11', self.purchase_enquiry_ref, cell_format)

        # now table for order lines
        sheet.write('A13', 'S.No', serial_number)
        sheet.write('B13', 'Part Number', table_heads)
        sheet.write('C13', 'Description', table_heads)
        sheet.write('D13', 'Quantity', table_heads)
        sheet.write('E13', 'UOM', table_heads)
        sheet.write('F13', 'Unit Price'+'('+self.pricelist_id.currency_id.symbol+')', table_heads)
        sheet.write('G13', 'Total'+'('+self.pricelist_id.currency_id.symbol+')', table_heads)

        row = 14    
        for line in self.order_line:
            sheet.write(row, 0, row-13, cell_format)
            sheet.write(row, 1, line.product_template_id.default_code, cell_format)
            sheet.write(row, 2, line.product_id.name, cell_format)
            sheet.write(row, 3, line.product_uom_qty, cell_format)
            sheet.write(row, 4, line.product_uom.name, cell_format)
            currency_symbol = self.currency_id.symbol or ''
            formatted_unit = f"{currency_symbol}  {line.price_unit:,.2f}"
            sheet.write(row, 5, formatted_unit, cell_format)
            formated_total = f"{currency_symbol}  {line.price_subtotal:,.2f}"
            sheet.write(row, 6, formated_total, cell_format)
            row += 1

            # now total, tax and discount each on new row
        sheet.write(row, 5, 'Total', totals)
        sheet.write(row, 6, self.amount_untaxed, totals)
        row += 1
        sheet.write(row, 5, 'Taxable', totals)
        sheet.write(row, 6, self.amount_untaxed, totals)
        row += 1
        sheet.write(row, 5, 'Tax Rate (VAT)', totals)
        sheet.write(row, 6, '18%', totals)
        row += 1
        sheet.write(row, 5, 'Taxes Due', totals)
        sheet.write(row, 6, self.amount_tax, totals)
        row += 1
        sheet.write(row, 5, 'Others', totals)
        sheet.write(row, 6, '', totals)
        row += 1
        sheet.write(row, 5, 'Total', total_amount)
        currency_symbol = self.currency_id.symbol or ''
        formatted_amount = f"{currency_symbol}  {self.amount_total:,.2f}"
        sheet.write(row, 6,formatted_amount, total_amount)

        


        # merge range column 1 up to 2
        sheet.merge_range('A'+str(row+2)+':B'+str(row+2), 'Other Comments', table_heads)
        sheet.merge_range('A'+str(row+3)+':B'+str(row+3), 'Delivery Period: '+ str(self.delivery_period) or '', comment_info)
        sheet.merge_range('A'+str(row+4)+':B'+str(row+4), 'Condition of the Parts: Original and New' , comment_info)
        sheet.merge_range('A'+str(row+5)+':B'+str(row+5), 'Delivery Term: '+str(self.delivery_term) or '', comment_info)
        sheet.merge_range('A'+str(row+5)+':B'+str(row+5), 'Others: '+str(self.other_comments) or '', comment_info)

       


        workbook.close()
        output.seek(0)
        xlsx_data = base64.b64encode(output.read())
        self.write({'xlsx_file': xlsx_data})

        attachment = self.env['ir.attachment'].create({
            'name': self.name+'-'+'report.xlsx',
            'type': 'binary',
            'datas': self.xlsx_file,
            'store_fname': self.name +'_'+'report.xlsx',
            'res_model': 'documents.document',
            'res_id': self.id,  # Will be linked to document in next step
        })

        # Create document record in the Documents module
        document = self.env['documents.document'].create({
            'name': self.name+'-'+'report.xlsx',
            'folder_id': 10,
            'attachment_id': attachment.id,
        })
        return document
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': '/web#action=595&model=documents.document&view_type=kanban&menu_id=394&folder_id=1',
        #     'target': 'self',
        # }
    


class resPartner(models.Model):
    _inherit = "res.partner"

    vrn_number = fields.Char('VRN')







class purchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_requisition_ref = fields.Char('Purchase Requisition Reference')
    customer_po_ref = fields.Char('Purchase Order Reference')
    validity = fields.Char('Validity', tracking=True)
    contact_person_id  = fields.Many2one('res.partner', string='Contact Person')
    child_ids = fields.Many2many('res.partner', string='Child Contacts', compute='_compute_child_ids')
    xlsx_file = fields.Binary('XLSX Report')
    @api.depends('partner_id')
    def _compute_child_ids(self):
        for rec in self:
            rec.child_ids = rec.partner_id.child_ids

    def action_generate_xlxs(self):
        from io import BytesIO
        import xlsxwriter
        import base64
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()

        # formating the whole sheet not to have any gridlines
        sheet.hide_gridlines(2)
        # enforce contents to fit in A4 paper
        sheet.set_paper(9)
        sheet.center_vertically()

        totals = workbook.add_format()
        totals.set_font_size(10)

        to_info = workbook.add_format({
            'bold': True
            })
        to_info.set_font_size(10)

        comment_info = workbook.add_format({
            'border': 1,
            })
        comment_info.set_font_size(10)

        
        total_amount = workbook.add_format({
            'font_size': '12',
            'bold': True
            })
        total_amount.set_font_size(10)
        total_amount.set_num_format('#,##0.00')
        cell_format = workbook.add_format({
            'font_size': '11',
             'border': 1,
             'align': 'start'
             })
        cell_format.set_font_size(10)

        head = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '20px'
            })
        table_heads = workbook.add_format({
            'align': 'center',
            'bg_color': '#3464ab',
            'bold': True,
            'color': 'white'
            })
        table_heads.set_font_size(10)
        company_logo = BytesIO(base64.b64decode(self.company_id.logo))
        sheet.merge_range('A1:B2', '')
        sheet.insert_image('A1', 'company_logo.png', {'image_data': company_logo, 'x_scale': 0.07, 'y_scale': 0.1})


        sheet.merge_range('B1:E1', '')
        sheet.merge_range('F1:G1', 'PURCHASE ORDER', head)
        sheet.write('A4', 'To', table_heads)
        sheet.write('A5', ' [Attn]: '+ self.partner_id.name, to_info)
        sheet.write('A6', ' [Company]: '+ self.partner_id.name, to_info)
        sheet.write('A7', ' [Street Address]: '+ str(self.partner_id.street) or '', to_info)
        sheet.write('A8', ' [Phone]: '+ str(self.partner_id.phone) or '', to_info)

        sheet.write('F5', 'Date', cell_format) 
        sheet.write('G5', self.date_order, cell_format)
        sheet.write('F6', 'PO #', cell_format)
        sheet.write('G6', self.purchase_requisition_ref, cell_format)
        sheet.write('F7', 'Vendor Id', cell_format)
        sheet.write('G7', self.partner_id.id, cell_format)
        sheet.write('F8', 'Validity', cell_format)
        sheet.write('G8', str(self.payment_term_id.name), cell_format)
        sheet.write('F9', 'TIN', cell_format)
        sheet.write('G9', self.company_id.vat, cell_format)
        sheet.write('F10', 'VRN', cell_format)
        sheet.write('G10', self.company_id.company_vrn, cell_format)
        sheet.write('F11', 'REF', cell_format)
        sheet.write('G11', self.name, cell_format)

        # now table for order lines
        sheet.write('A13', 'S.No', table_heads)
        sheet.write('B13', 'Part Number', table_heads)
        sheet.write('C13', 'Description', table_heads)
        sheet.write('D13', 'Quantity', table_heads)
        sheet.write('E13', 'UOM', table_heads)
        sheet.write('F13', 'Unit Price', table_heads)
        sheet.write('G13', 'Amount', table_heads)

        row = 13
        if self.state in ['draft','sent']:
            for line in self.order_line:
                sheet.write(row, 0, row-12, cell_format)
                sheet.write(row, 1, line.product_id.default_code, cell_format)
                sheet.write(row, 2, line.product_id.name, cell_format)
                sheet.write(row, 3, line.product_qty, cell_format)
                sheet.write(row, 4, line.product_uom.name, cell_format)
                sheet.write(row, 5, '', cell_format)
                sheet.write(row, 6, '', cell_format)
                row += 1
        else:
            for line in self.order_line:
                sheet.write(row, 0, row-12, cell_format)
                sheet.write(row, 1, line.product_id.default_code, cell_format)
                sheet.write(row, 2, line.product_id.name, cell_format)
                sheet.write(row, 3, line.product_qty, cell_format)
                sheet.write(row, 4, line.product_uom.name, cell_format)
                sheet.write(row, 5, line.price_unit, cell_format)
                sheet.write(row, 6, line.price_subtotal, cell_format)
                row += 1


        workbook.close()
        output.seek(0)
        xlsx_data = base64.b64encode(output.read())
        self.write({'xlsx_file': xlsx_data})

        # attaching the report to the documents module
        attachment = self.env['ir.attachment'].create({
            'name': self.name+'-'+'report.xlsx',
            'type': 'binary',
            'datas': self.xlsx_file,
            'store_fname': self.name +'_'+'report.xlsx',
            'res_model': 'documents.document',
            'res_id': self.id,  # Will be linked to document in next step
        })

        # Create document record in the Documents module
        document = self.env['documents.document'].create({
            'name': 'report.xlsx',
            'folder_id': 10,
            'attachment_id': attachment.id,
        })
        return document
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': '/web#action=595&model=documents.document&view_type=kanban&menu_id=394&folder_id=1',
        #     'target': 'self',
        # }




class resCompany(models.Model):
    _inherit = "res.company"

    company_vrn = fields.Char('VRN')
    company_stamp = fields.Binary('Stamp')
    company_bank_footer = fields.Html('Bank Footer')

class productTemplate(models.Model):
    _inherit = "product.template"

    product_description = fields.Text('Description')

