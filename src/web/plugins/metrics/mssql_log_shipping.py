# -*- encoding: utf-8; py-indent-offset: 4 -*-
# Checkmk special agent for MSSQL Log Shipping (https://github.com/Fyotta/checkmk-mssql-log-shipping) - Francisco Fernandes <franciscoyotta@gmail.com>
# This code is distributed under the terms of the GNU General Public License, version 3 (GPLv3).
# See the LICENSE file for details on the license terms.
from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info


metric_info['mssql_log_shipping_gap'] = {
    'title': _('Replication Gap'),
    'unit': 's',
    'color': '34/a',
}

metric_info['mssql_log_shipping_time_since_last_restore'] = {
    'title': _('Time Since Last Restore'),
    'unit': 's',
    'color': '14/a',
}

metric_info['mssql_log_shipping_time_since_last_backup'] = {
    'title': _('Time Since Last Backup'),
    'unit': 's',
    'color': '16/a',
}
