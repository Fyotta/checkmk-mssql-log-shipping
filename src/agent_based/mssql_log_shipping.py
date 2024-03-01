# -*- encoding: utf-8; py-indent-offset: 4 -*-
# import cmk.base.plugins.agent_based.agent_based_api.v1
from .agent_based_api.v1 import (
    render,
    check_levels,
    register,
    Result,
    Service,
    State,
)
import zlib
import json
import base64
from typing import List, Any
from datetime import datetime, timezone


def _join_section(section: List[List[str]]) -> str:
    return '\n'.join([' '.join(line) for line in section])


def _decode_data(compressed_base64: str) -> str:
    compressed_data = base64.b64decode(compressed_base64)
    decompressed_base64 = zlib.decompress(compressed_data)
    return decompressed_base64.decode('utf-8')


def parse_mssql_log_shipping(string_table: List[List[str]]) -> any:
    base64_data = _join_section(string_table)
    json_str = _decode_data(base64_data)
    return json.loads(json_str)


def discover_mssql_log_shipping_plugin(section):
    instance_name = section['primary']['status']['instance_name'] if section['primary']['status']['instance_name'] == section['secondary']['status']['instance_name'] else f"{section['primary']['status']['instance_name']}_{section['secondary']['status']['instance_name']}"
    database_name = section['primary']['status']['primary_database'] if section['primary']['status']['primary_database'] == section['secondary']['status']['secondary_database'] else f"{section['primary']['status']['primary_database']}_{section['secondary']['status']['secondary_database']}"
    item_name = f"{instance_name}_{database_name}"
    yield Service(item=item_name)


def _agregate_results(state_list: List[State], **kwargs: Any):
    result, metric = check_levels(**kwargs)
    state_list.append(result.state)
    yield result
    yield metric


def check_mssql_log_shipping_plugin(item, params, section):
    primary = section.get('primary')
    secondary = section.get('secondary')
    if not primary or not secondary:
        if not primary:
            yield Result(state=State.CRIT, summary='Primary data not found')
        if not secondary:
            yield Result(state=State.CRIT, summary='Secondary data not found')
        return

    last_backup_date_utc = datetime.fromisoformat(primary['status']['last_backup_date_utc']).replace(tzinfo=timezone.utc)
    last_restored_date_utc = datetime.fromisoformat(secondary['status']['last_restored_date_utc']).replace(tzinfo=timezone.utc)

    primary_server_current_time = datetime.fromisoformat(primary['server_current_time']['server_current_time']).replace(tzinfo=timezone.utc)
    secondary_server_current_time = datetime.fromisoformat(secondary['server_current_time']['server_current_time']).replace(tzinfo=timezone.utc)
    diff_current_time = abs(primary_server_current_time - secondary_server_current_time)

    diff = abs(last_restored_date_utc - last_backup_date_utc) - diff_current_time
    diff_seconds = diff.total_seconds()

    time_since_last_restore = abs(datetime.now(timezone.utc) - last_restored_date_utc)
    time_since_last_backup = abs(datetime.now(timezone.utc) - last_backup_date_utc)

    state_list = []
    yield from _agregate_results(
        state_list,
        value = diff_seconds,
        levels_upper = params['gap_upper'],
        metric_name = 'mssql_log_shipping_gap',
        label = 'Gap',
        render_func = lambda v: render.timespan(v),
        notice_only = True,
    )

    yield from _agregate_results(
        state_list,
        value = time_since_last_restore.total_seconds(),
        levels_upper = params['time_since_last_restore_upper'],
        metric_name = 'mssql_log_shipping_time_since_last_restore',
        label = 'Time Since Last Restore',
        render_func = lambda v: render.timespan(v),
        notice_only = True,
    )

    yield from _agregate_results(
        state_list,
        value = time_since_last_backup.total_seconds(),
        levels_upper = params['time_since_last_backup_upper'],
        metric_name = 'mssql_log_shipping_time_since_last_backup',
        label = 'Time Since Last Log Backup',
        render_func = lambda v: render.timespan(v),
        notice_only = True,
    )

    details = f"\nLast Backup File: {primary['status']['last_backup_file']}\nLast Copied File: {secondary['status']['last_copied_file']}\nLast Restored File: {secondary['status']['last_restored_file']}"
    if State.worst(*state_list) == State.OK:
        yield Result(state=State.OK, summary='Synchronized databases', details=details)
    elif State.worst(*state_list) == State.CRIT:
        yield Result(state=State.CRIT, summary='Desynchronized databases', details=details)


register.agent_section(
    name = 'mssql_log_shipping',
    parse_function = parse_mssql_log_shipping,
)


register.check_plugin(
    name = 'mssql_log_shipping',
    service_name = 'MSSQL %s Log Shipping',
    discovery_function = discover_mssql_log_shipping_plugin,
    check_function = check_mssql_log_shipping_plugin,
    check_default_parameters={
        'gap_upper': (900, 1800),
        'time_since_last_restore_upper': (3600, 7200),
        'time_since_last_backup_upper': (3600, 7200),
    },
    check_ruleset_name='mssql_log_shipping'
)
