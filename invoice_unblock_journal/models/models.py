# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        for move in self:
            # evil hack to allow change the journal
            name = ''
            if move.company_id.id in [8, 9] and move.name != '/' and 'journal_id' in vals and move.journal_id.id != \
                    vals['journal_id'] and move.state != 'posted':
                name = move.name
                journal_id = vals['journal_id']
                vals['journal_id'] = move.journal_id.id
                move.name = '/'
                vals['journal_id'] = journal_id

            if (move.restrict_mode_hash_table and move.state == "posted" and set(vals).intersection(
                    INTEGRITY_HASH_MOVE_FIELDS)):
                raise UserError(
                    _("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(
                        INTEGRITY_HASH_MOVE_FIELDS))
            if (move.restrict_mode_hash_table and move.inalterable_hash and 'inalterable_hash' in vals) or (
                    move.secure_sequence_number and 'secure_sequence_number' in vals):
                raise UserError(_('You cannot overwrite the values ensuring the inalterability of the accounting.'))
            if (move.name != '/' and 'journal_id' in vals and move.journal_id.id != vals['journal_id']):
                raise UserError(_('You cannot edit the journal of an account move if it has been posted once.'))

            # You can't change the date of a move being inside a locked period.
            if 'date' in vals and move.date != vals['date']:
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            # You can't post subtract a move to a locked period.
            if 'state' in vals and move.state == 'posted' and vals['state'] != 'posted':
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

        if self._move_autocomplete_invoice_lines_write(vals):
            res = True
        else:
            vals.pop('invoice_line_ids', None)
            res = super(AccountMove, self.with_context(check_move_validity=False)).write(vals)

        # You can't change the date of a not-locked move to a locked period.
        # You can't post a new journal entry inside a locked period.
        if 'date' in vals or 'state' in vals:
            self._check_fiscalyear_lock_date()
            self.mapped('line_ids')._check_tax_lock_date()

        if ('state' in vals and vals.get('state') == 'posted') and self.restrict_mode_hash_table:
            for move in self.filtered(lambda m: not (m.secure_sequence_number or m.inalterable_hash)):
                new_number = move.journal_id.secure_sequence_id.next_by_id()
                vals_hashing = {'secure_sequence_number': new_number,
                                'inalterable_hash': move._get_new_hash(new_number)}
                res |= super(AccountMove, move).write(vals_hashing)

        # Ensure the move is still well balanced.
        if 'line_ids' in vals:
            if self._context.get('check_move_validity', True):
                self._check_balanced()
            self.update_lines_tax_exigibility()
        
        # Return original name
        #if name:
        #    move.name = name

        return res



    def unlink(self):
        for move in self:
            if move.name != '/' and move.company_id.id in [8, 9] and move.state != 'posted':
                move.name = '/'
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted once."))
            move.line_ids.unlink()
        return super(AccountMove, self).unlink()
