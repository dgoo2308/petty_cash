# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning

import logging
_logger = logging.getLogger(__name__)

#  petty cash    
class PettyCash(models.Model):
    _name = 'petty.cash'
    _rec_name = 'number'

    number = fields.Char('Number')
    custodian_id = fields.Many2one('hr.employee', string='Custodian', required=True)
    requested_employee_id = fields.Many2one('hr.employee', string='Requested By', required=True)
    requester_journal_id = fields.Many2one('account.journal', string='Requester Cash Journal', domain="[('type','in',['bank','cash'])]", required=True)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', domain="[('type','in',['bank','cash'])]", readonly=True)
    credit_account_id = fields.Many2one('account.account', string='Credit Account', readonly=True)
    debit_account_id = fields.Many2one('account.account', string='Debit Account', readonly=True)
    date_requested = fields.Date(string='Date Requested', default=date.today(), readonly=True)
    date_received = fields.Date(string='Date Received', readonly=True)
    payment_line_ids = fields.One2many('account.payment', 'petty_cash_id', string='Payment Line', readonly=True)  
    move_line_ids = fields.One2many('account.move.line', 'petty_cash_id', string='Move Line' , readonly=True)  
    amount = fields.Float(string='Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'approved')
        ], string='Status', readonly=True, default='draft')

    @api.model
    def default_get(self, fields):
        result = super(PettyCash, self).default_get(fields)
        user = self._uid
        _logger.error("================================")
        _logger.error(user)
        requested_employee_id = self.env['hr.employee'].search([('user_id', '=', user)])[0]
        if not requested_employee_id :
            raise ValidationError(_('Logged In user is not associated with any employee!'))
        if requested_employee_id :
            if not requested_employee_id.journal_id:
                raise ValidationError(_('Please Set Account Journal For This Employee!'))
            else:
                if not requested_employee_id.journal_id.default_debit_account_id :
                    raise ValidationError(_('Please Set  Default Accounts  For This Petty Cash Journal!'))
                else:
                    result['debit_account_id'] = requested_employee_id.journal_id.default_debit_account_id.id
                    result['requester_journal_id'] = requested_employee_id.journal_id.id 
        result['requested_employee_id'] = requested_employee_id.id
        return result

    @api.model
    def create(self, vals):
        if 'payment_journal_id' in vals :
            journal_id = self.env['account.journal'].browse(vals.get('payment_journal_id'))
            if journal_id:
                if journal_id.default_credit_account_id:
                    vals.update({'credit_account_id': journal_id.default_credit_account_id.id  })
                else:
                    raise ValidationError(_('Please Set Default Account For This Payment Journal!'))
        vals.update({'number':self.env['ir.sequence'].next_by_code('petty.cash') or _('New')})
        return super(PettyCash, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'payment_journal_id' in vals :
            journal_id = self.env['account.journal'].browse(vals.get('payment_journal_id'))
            if journal_id:
                if journal_id.default_credit_account_id:
                    vals.update({'credit_account_id': journal_id.default_credit_account_id.id  })
                else:
                    raise ValidationError(_('Please Set  Default Account For This Payment Journal!'))
        return super(PettyCash, self).write(vals)

    @api.multi
    @api.onchange('payment_journal_id')
    def onchange_defualt_account(self):
        if self.payment_journal_id:
            if not self.payment_journal_id.default_credit_account_id:
                raise ValidationError(_('Please Set Default Account For This Payment Journal!'))
            else:
                self.credit_account_id = self.payment_journal_id.default_credit_account_id.id 
    
    @api.multi
    @api.onchange('requested_employee_id')
    def onchange_requester_employee(self):
        if self.requested_employee_id:
            if not self.requested_employee_id.journal_id:
                raise ValidationError(_('Please Set Account Journal For This Employee!'))
            else:
                self.requester_journal_id = self.requested_employee_id.journal_id.id

    @api.multi
    def do_request(self):
        for petty in self:
            petty.state = 'requested'
