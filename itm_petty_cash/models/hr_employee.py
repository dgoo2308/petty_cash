# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning


class HrLocation(models.Model):
    _name = 'hr.location'
    
    name = fields.Char(string='name')


# set journal in employee 
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    journal_id = fields.Many2one('account.journal', string='Cash Journal', domain="[('type','=','cash')]")
    plant_id = fields.Many2one('hr.location', string='Plant')


    # only account manager as custodian list 
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context
        if args is None:
            args = []
        if 'set_custodian' in context:
            manager_users = self.env.ref('account.group_account_manager').users
            user_users = self.env.ref('account.group_account_user').users
            users = list(set([x.id for x in manager_users] + [y.id for y in user_users]))
            args += ([('user_id', 'in', users)])
            print("=====args===", args)
        return super(HrEmployee, self).name_search(name=name,
                                               args=args,
                                               operator=operator,
                                               limit=limit)
