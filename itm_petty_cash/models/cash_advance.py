# -*- coding: utf-8 -*-
# Odoo, Open Source Itm advance Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning


class CashAdvance(models.Model):
    _name = 'cash.advance'
    _rec_name = 'number'

    number = fields.Char('Number')
    custodian_id = fields.Many2one('hr.employee', string='Custodian', required=True)
    custodian_journal_id = fields.Many2one('account.journal', string='Custodian Cash Journal', domain="[('type','in',['cash'])]", required=True)
    requested_employee_id = fields.Many2one('hr.employee', string='Requested By', required=True)
    requester_journal_id = fields.Many2one('account.journal', string='Requester Cash Journal', domain="[('type','in',['cash'])]", required=True)
    credit_account_id = fields.Many2one('account.account', string='Credit Account', readonly=True)
    debit_account_id = fields.Many2one('account.account', string='Debit Account', readonly=True)
    date_received = fields.Date(string='Date Received', default=date.today())
    payment_line_ids = fields.One2many('account.payment', 'cash_advance_id', string='Payment Line', readonly=True)  
    move_line_ids = fields.One2many('account.move.line', 'cash_advance_id', string='Move Line' , readonly=True)  
    amount = fields.Float(string='Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Cash Dispatched')
        ], string='Status', readonly=True, default='draft')


    @api.model
    def default_get(self, fields):
        result = super(CashAdvance, self).default_get(fields)
        user = self._uid
        requested_employee_id = self.env['hr.employee'].search([('user_id', '=', user)])[0]
        if not requested_employee_id :
            raise ValidationError(_('Logged In user is not associated with any employee!'))
        if requested_employee_id :
            if not requested_employee_id.journal_id:
                raise ValidationError(_('Please Set Cash Journal For This Employee!'))
            else:
                if not requested_employee_id.journal_id.default_debit_account_id :
                    raise ValidationError(_('Please Set  Default Accounts  For This Cash Journal!'))
                else:
                    result['requester_journal_id'] = requested_employee_id.journal_id.id
                    result['debit_account_id'] = requested_employee_id.journal_id.default_debit_account_id.id
        result['requested_employee_id'] = requested_employee_id.id
        return result

    @api.model
    def create(self, vals):
        if 'custodian_id' in vals :
            custodian_employee_id = self.env['hr.employee'].browse(vals['custodian_id'])
            if not custodian_employee_id.journal_id:
                raise ValidationError(_('Please Set Cash Journal For Custodian!'))
            journal_id = custodian_employee_id.journal_id
            vals.update({'custodian_journal_id': journal_id.id})
            if journal_id.default_credit_account_id:
                vals.update({'credit_account_id': journal_id.default_credit_account_id.id  })
            else:
                raise ValidationError(_("Please Set Default Account For This Custodian's Cash Journal!"))
        vals.update({'number':self.env['ir.sequence'].next_by_code('cash.advance') or _('New')})
        return super(CashAdvance, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'custodian_journal_id' in vals :
            journal_id = self.env['account.journal'].browse(vals.get('custodian_journal_id'))
            if journal_id:
                if journal_id.default_credit_account_id:
                    vals.update({'credit_account_id': journal_id.default_credit_account_id.id  })
                else:
                    raise ValidationError(_('Please Set  Default Account For This Payment Journal!'))
        return super(CashAdvance, self).write(vals)

    @api.multi
    @api.onchange('custodian_id')
    def onchange_custodian(self):
        for rec in self:
            if rec.custodian_id:
                if not rec.custodian_id.journal_id:
                    raise ValidationError(_('Please Set Cash Journal For Custodian!'))
                self.custodian_journal_id = rec.custodian_id.journal_id
                if not rec.custodian_id.journal_id.default_credit_account_id:
                    raise ValidationError(_("Please Set Default Account For This Custodian's Cash Journal!"))
                else:
                    rec.credit_account_id = rec.custodian_journal_id.default_credit_account_id.id 

    @api.multi
    def do_request(self):
        for advance in self:
            advance.state = 'requested'

    @api.multi
    def do_approve(self):
        for advance in self:
            advance.state = 'approved'
            payment_methods = advance.custodian_journal_id.inbound_payment_method_ids or advance.custodian_journal_id.outbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            payment_id = self.env['account.payment'].create({
                'cash_advance_id' : advance.id,
                'payment_type' : 'transfer',
                'payment_date' : advance.date_received,
                'internal_transfer_type':'journal_to_journal',
                'journal_id':advance.custodian_journal_id.id,
                'destination_journal_id' : advance.requester_journal_id.id,
                'payment_method_id': payment_method_id.id,
                'amount':advance.amount,
                'communication' :  advance.number})
            ctx = dict(self._context)
            ctx.update({'custom_payment_id':payment_id.id})
            payment_id.with_context(ctx).post()
            move_line_id = self.env['account.move.line'].search([('payment_id', '=', payment_id.id)])
            move_line_id.write({'cash_advance_id' : advance.id})
        return

