# -*- coding: utf-8 -*-
{
    'name': "logmath_reports",
    'version': '1.0.1',
    'category': 'Tools',
    'license': 'OPL-1',
    'summary': 'Custom Report Template for Quotation/SO/Sales, Invoice, Picking/Delivery Order,RFQ/PO/Purchases',
    'description': """
		Custom Report Template for Quotation/SO/Sales, Invoice, Picking/Delivery Order,RFQ/PO/Purchases
    """,
    'license': 'OPL-1',
    'author': 'Inventions Technologies Ltd',
    'website': 'https://www.it.co.tz',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','purchase','account','stock','mail'],

    # always loaded
    'data': [
        'views/views.xml',
        'data/sales_quotation_email.xml',
        'reports/sales_quotation.xml',
        'reports/purchase_order.xml',
        'reports/invoice.xml',
        'reports/delivery.xml',
        'reports/purchase_quotation.xml',
        'reports/credit_note.xml',
        'views/report_menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': True,
    'sequence': 0,
}
