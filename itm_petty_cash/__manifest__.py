# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Petty Cash Management',
    'category': 'Account',
    'author': 'Odoowikia - Bhavik Vyas',
    'website': 'http://odoowikia.com/',
    'description': """
================================================================================

1. Petty Cash Management .

================================================================================
""",
    'depends': [ 'itm_payment_analytic', 'hr', 'base', 'web', 'analytic', 'account', 'hr_expense'],
     'summary': 'Manage Petty Cash Funds',
    'data': [
        'security/security.xml',
        'wizard/approve_pettycash_request_wizard.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/petty_cash_view.xml',
        'views/cash_advance_view.xml',
        'views/expense_view.xml',
        'views/employee_view.xml',
        'views/menu.xml'
        ],
    'installable': True,

}
