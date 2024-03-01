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
