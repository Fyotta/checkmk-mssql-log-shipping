# -*- encoding: utf-8; py-indent-offset: 4 -*-
# Checkmk special agent for MSSQL Log Shipping (https://github.com/Fyotta/checkmk-mssql-log-shipping) - Francisco Fernandes <franciscoyotta@gmail.com>
# This code is distributed under the terms of the GNU General Public License, version 3 (GPLv3).
# See the LICENSE file for details on the license terms.
"""Checkmk special agent for MSSQL Log Shipping"""
from cmk.gui.plugins.wato.utils import IndividualOrStoredPassword
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    TextAscii,
    HostAddress,
    Tuple
)

from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupVMCloudContainer


def _valuespec_special_agents_mssql_log_shipping():
    return Dictionary(
        title=_('Agent MSSQL Log Shipping'),
        help=_('This agent connects to the primary and secondary instances of the MSSQL database and gathers information regarding Log Shipping replication.'),
        required_keys=['user', 'password', 'primary', 'secondary'],
        elements=[
            (
                "user",
                TextAscii(
                    title=_("User"),
                    allow_empty=False,
                    help=_('Database user to connect as'),
                ),
            ),
            (
                "password",
                IndividualOrStoredPassword(
                    title=_("Password"),
                    allow_empty=False,
                    help=_("User's password"),
                ),
            ),
            (
                "timeout",
                Integer(
                    title=_("Timeout"),
                    help=_('Query timeout in seconds, default 0 (no timeout)'),
                ),
            ),
            (
                "login-timeout",
                Integer(
                    title=_("Login Timeout"),
                    help=_('Timeout for connection and login in seconds, default 60'),
                ),
            ),
            (
                "primary",
                Tuple(
                    title=_("Primary Database"),
                    help=_('Hostname or IP-Address and port(Optional) where the primary databases lives'),
                    elements=[
                        HostAddress(
                            title=_('Address'),
                            allow_empty=False
                        ),
                        Integer(
                            title=_("TCP Port"),
                            default_value=1433,
                        ),
                    ],
                ),
            ),
            (
                "secondary",
                Tuple(
                    title=_("Secondary Database"),
                    help=_('Hostname or IP-Address and port(Optional) where the secondary databases lives'),
                    elements=[
                        HostAddress(
                            title=_('Address'),
                            allow_empty=False
                        ),
                        Integer(
                            title=_("TCP Port"),
                            default_value=1433,
                        ),
                    ],
                ),
            ),
        ]
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupVMCloudContainer,
        name="special_agents:mssql_log_shipping",
        valuespec=_valuespec_special_agents_mssql_log_shipping,
    )
)
