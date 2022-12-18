# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import api, fields, models, _
from datetime import datetime as date
from odoo.exceptions import UserError
    
class ApprovePettyCashRequestWizard(models.TransientModel):
    _name = 'approve.pettycash.wizard'
    
    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True)


    @api.multi
    def do_approve(self):
        petty = self.env['petty.cash'].browse(self._context.get('active_id'))
        petty.state = 'approved'
        petty.payment_journal_id = self.journal_id.id
        petty.date_received = date.today()
        payment_methods = self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        payment_id = self.env['account.payment'].create({
            'petty_cash_id' : petty.id,
            'payment_type' : 'transfer',
            'payment_date' : petty.date_received,
            'internal_transfer_type':'journal_to_journal',
            'journal_id':self.journal_id.id,
            'destination_journal_id' : petty.requester_journal_id.id,
            'payment_method_id': payment_method_id.id,
            'amount':petty.amount,
            'communication' :  petty.number})
        ctx = dict(self._context)
        ctx.update({'custom_payment_id':payment_id.id})
        payment_id.with_context(ctx).post()
        move_line_id = self.env['account.move.line'].search([('payment_id', '=', payment_id.id)])
        move_line_id.write({'petty_cash_id' : petty.id})
        return {'type': 'ir.actions.act_window_close'}

