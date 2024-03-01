# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _

from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    TextInput,
    Tuple
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupEnforcedServicesApplications,
)


def _item_valuespec_mssql_log_shipping():
    return TextInput(
        title="Instance and database name",
        help="Insert the instance and database name here"
    )


def _parameter_valuespec_mssql_log_shipping():
    return Dictionary(
        elements=[
            (
                "gap_upper",
                Tuple(
                    title = _("Gap"),
                    elements = [
                        Integer(
                            title=_("Warning"),
                            default_value = 900
                        ),
                        Integer(
                            title=_("Critical"),
                            default_value = 1800
                        ),
                    ],
                    help = _('Represents the time in seconds between the last backup log in the primary database and the last restore in the secondary database.')
                )
            ),
            (
                "time_since_last_restore_upper",
                Tuple(
                    title = _("Time Since Last Restore"),
                    elements = [
                        Integer(
                            title=_("Warning"),
                            default_value = 3600
                        ),
                        Integer(
                            title=_("Critical"),
                            default_value = 7200
                        ),
                    ],
                    help = _('Represents the time in seconds since the last restore in the secondary database.')
                )
            ),
            (
                "time_since_last_backup_upper",
                Tuple(
                    title = _("Time Since Last Backup"),
                    elements = [
                        Integer(
                            title=_("Warning"),
                            default_value = 3600
                        ),
                        Integer(
                            title=_("Critical"),
                            default_value = 7200
                        ),
                    ],
                    help = _('Represents the time in seconds since the last Log backup in the primary database.')
                )
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="mssql_log_shipping",
        group=RulespecGroupEnforcedServicesApplications,
        match_type="dict",
        item_spec=_item_valuespec_mssql_log_shipping,
        parameter_valuespec=_parameter_valuespec_mssql_log_shipping,
        title=lambda: _("MSSQL Log Shipping"),
    )
)
