# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning


# set petty cash in move line
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash')
    cash_advance_id = fields.Many2one('cash.advance', string='Cash Advance')


# set petty cash in payment
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash')
    cash_advance_id = fields.Many2one('cash.advance', string='Cash Advance')