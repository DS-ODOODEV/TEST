# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Financial Reports",
    "version": "13.0.1.1.1",
    "category": "Reporting",
    "summary": "Financial Reports",
    "author": "Xetechs, S.A.",
    "website": "https://www.xetechs.com/",
    "support": "Luis Aquino -> laquino@xetechs.com",
    "depends": ["account", "date_range", "report_xlsx"],
    "data": [
        "wizard/aged_partner_balance_wizard_view.xml",
        "wizard/general_ledger_wizard_view.xml",
        "wizard/journal_ledger_wizard_view.xml",
        "wizard/open_items_wizard_view.xml",
        "wizard/trial_balance_wizard_view.xml",
        "wizard/vat_report_wizard_view.xml",
        "menuitems.xml",
        "reports.xml",
        "report/templates/layouts.xml",
        "report/templates/aged_partner_balance.xml",
        "report/templates/general_ledger.xml",
        "report/templates/journal_ledger.xml",
        "report/templates/open_items.xml",
        "report/templates/trial_balance.xml",
        "report/templates/vat_report.xml",
        "view/account_view.xml",
        "view/report_template.xml",
        "view/report_general_ledger.xml",
        "view/report_journal_ledger.xml",
        "view/report_trial_balance.xml",
        "view/report_open_items.xml",
        "view/report_aged_partner_balance.xml",
        "view/report_vat_report.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}