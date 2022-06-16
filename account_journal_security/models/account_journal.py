##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    user_ids = fields.Many2many('res.users', 'journal_security_journal_users', 'journal_id','user_id', string='Users with Access',
        help='If choose some users, then this journal and the information related to it will be only visible for those users.',
        copy=False)

    modification_user_ids = fields.Many2many('res.users', 'journal_security_journal_modification_users', 'journal_id',
                                             'user_id', string='Modifications restricted to',
        help='If choose some users, then only this users will be allow to  create, write or delete accounting data related of this journal. '
             'Information will still be visible for other users.', copy=False )

    journal_restriction = fields.Selection([('none', 'None'), ('modification', 'Modification'), ('total', 'Access')],
                                          string="Restriction Type", compute='_compute_journal_restriction', readonly=False)

    def _compute_journal_restriction(self):
        for rec in self:
            if rec.user_ids:
                rec.journal_restriction = 'total'
            elif rec.modification_user_ids:
                rec.journal_restriction = 'modification'
            else:
                rec.journal_restriction = 'none'

    @api.constrains('user_ids')
    def check_restrict_users(self):
        self._check_journal_users_restriction('user_ids')

    @api.constrains('modification_user_ids')
    def check_modification_users(self):
        self._check_journal_users_restriction('modification_user_ids')

    def _check_journal_users_restriction(self, field):
        self.env['ir.rule'].clear_caches()
        if self.modification_user_ids and self.user_ids:
            raise ValidationError(_(
                'You cannot set values ​​in "Fully restricted to:" and '
                '"Modifications restricted to:" simultaneously. The options '
                'are exclusive!'))
        env_user = self.env.user
        if env_user.id == SUPERUSER_ID:
            # if superadmin no need to check
            return True
        for rec in self.sudo():
            journal_users = rec[field]
            if journal_users and env_user not in journal_users:
                raise ValidationError(_(
                    'You cannot restrict the "Customer Invoices" journal to users without including yourself as you will no longer see this journal.') % (rec.name))
        self.env.user.context_get.clear_cache(self)

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user
        # if superadmin, do not apply
        if not self.env.is_superuser():
            args += [
                '|', ('modification_user_ids', '=', False),
                ('id', 'in', user.modification_journal_ids.ids)]

        return super()._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

    @api.onchange('journal_restriction')
    def unset_modification_user_ids(self):
        if self.journal_restriction == 'modification':
            self.modification_user_ids = self.user_ids
            self.user_ids = None
        elif self.journal_restriction == 'total':
            self.user_ids = self.modification_user_ids
            self.modification_user_ids = None
        else:
            self.user_ids = None
            self.modification_user_ids = None
