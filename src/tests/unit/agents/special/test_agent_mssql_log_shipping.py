#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# Checkmk special agent for MSSQL Log Shipping (https://github.com/Fyotta/checkmk-mssql-log-shipping) - Francisco Fernandes <franciscoyotta@gmail.com>
# This code is distributed under the terms of the GNU General Public License, version 3 (GPLv3).
# See the LICENSE file for details on the license terms.
import datetime
from unittest.mock import MagicMock
from uuid import UUID
import pytest

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

spec = spec_from_loader('agent_mssql_log_shipping', SourceFileLoader('agent_mssql_log_shipping', 'agents/special/agent_mssql_log_shipping'))
agent_mssql_log_shipping = module_from_spec(spec)
spec.loader.exec_module(agent_mssql_log_shipping)


class TestAPI:
    @pytest.mark.parametrize(
        'args, expected_result, expected_exception',
        [
            # Valid args:
            (
                ['-u', 'db_user', '-p', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:1234', 'localhost:5678'],
                {'user': 'db_user', 'password': 'mypass123', 'timeout': 10, 'login_timeout': 30, 'primary': ('localhost', 1234), 'secondary': ('localhost', 5678)},
                None
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:1234', 'localhost:5678'],
                {'user': 'db_user', 'password': 'mypass123', 'timeout': 10, 'login_timeout': 30, 'primary': ('localhost', 1234), 'secondary': ('localhost', 5678)},
                None
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', '127.0.0.1', 'localhost:5678'],
                {'user': 'db_user', 'password': 'mypass123', 'timeout': 10, 'login_timeout': 30, 'primary': ('127.0.0.1', 1433), 'secondary': ('localhost', 5678)},
                None
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:1234', '192.168.1.2:1010'],
                {'user': 'db_user', 'password': 'mypass123', 'timeout': 10, 'login_timeout': 30, 'primary': ('localhost', 1234), 'secondary': ('192.168.1.2', 1010)},
                None
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', 'localhost:1234', 'localhost:5678'],
                {'user': 'db_user', 'password': 'mypass123', 'timeout': 0, 'login_timeout': 60, 'primary': ('localhost', 1234), 'secondary': ('localhost', 5678)},
                None
            ),
            # Invalid args:
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', '', 'localhost:5678'],
                None,
                SystemExit
            ),
            (
                ['--invalid_param', 'value', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:1234', 'localhost:5678'],
                None,
                SystemExit
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:-1234', 'localhost:5678'],
                None,
                SystemExit
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '10', '--login-timeout', '30', 'localhost:1234', 'localhost:99999'],
                None,
                SystemExit
            ),
            (
                ['--user', 'db_user', '--password', 'mypass123', '--timeout', '-10', '--login-timeout', '30', 'localhost:1234', 'localhost:5678'],
                None,
                SystemExit
            ),
        ]
    )
    def test_parse_args(self, args, expected_result, expected_exception):
        if expected_exception is not None:
            with pytest.raises(expected_exception):
                agent_mssql_log_shipping.parse_arguments(args)
        else:
            parsed_args = agent_mssql_log_shipping.parse_arguments(args)
            assert parsed_args.user == expected_result['user']
            assert parsed_args.password == expected_result['password']
            assert parsed_args.timeout == expected_result['timeout']
            assert parsed_args.login_timeout == expected_result['login_timeout']
            assert parsed_args.primary == expected_result['primary']
            assert parsed_args.secondary == expected_result['secondary']


class TestCore:
    @pytest.fixture
    def mock_mssql(self):
        mssql_mock = MagicMock(spec=agent_mssql_log_shipping.Mssql)
        mssql_mock.execute.side_effect = [
            [(1, 'Status 1'), (2, 'Status 2')],
            [(3, 'Status 3'), (4, 'Status 4')]
        ]
        return mssql_mock

    def test_querying(self, mock_mssql):
        args_namespace = MagicMock()
        result_info = agent_mssql_log_shipping.querying(args_namespace, agent_mssql_log_shipping.DbType.PRIMARY, mock_mssql)
        result_jobs = agent_mssql_log_shipping.querying(args_namespace, agent_mssql_log_shipping.DbType.SECONDARY, mock_mssql)
        assert result_info, result_jobs == ([(1, 'Status 1'), (2, 'Status 2')], [(3, 'Status 3'), (4, 'Status 4')])

    @pytest.mark.parametrize(
        'raw_query_results, expected_result, columns, cast',
        [
            (
                (b'MSSQLSERVER', 'MYDB', 'C:\\MYDBLOG\\MYDB_20240226133001.trn', datetime.datetime(2024, 2, 26, 10, 30, 1, 340000), datetime.datetime(2024, 2, 26, 13, 30, 1, 340000)),
                {
                    'instance_name': 'MSSQLSERVER',
                    'primary_database': 'MYDB',
                    'last_backup_file': 'C:\\MYDBLOG\\MYDB_20240226133001.trn',
                    'last_backup_date': '2024-02-26T10:30:01.340000',
                    'last_backup_date_utc': '2024-02-26T13:30:01.340000'
                },
                agent_mssql_log_shipping.QUERY['get_primary_status']['columns'],
                agent_mssql_log_shipping.map_one_result
            ),
            (
                [
                    (UUID('295ea804-8d8d-440d-a18b-170342c7d3be'), 'LSAlert_NOCMSSQLREP03', 1, 20240226, 102800, 1, 'The job succeeded.  The Job was invoked by Schedule 11 (Log shipping alert job schedule.).  The last step to run was step 1 (Log shipping alert job step.).', 20240226, 104400, 0, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 500000)),
                    (UUID('7ee36c8b-e64d-4f00-8c06-0d493631c890'), 'LSBackup_MYDB', 1, 20240226, 103000, 1, 'The job succeeded.  The Job was invoked by Schedule 12 (LSBackupSchedule_NOCMSSQLREP031).  The last step to run was step 1 (Log shipping backup log job step.).', 20240226, 103000, 1, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 500000)),
                    (UUID('42f5572f-23b5-4e20-8459-63b3d3428f74'), 'syspolicy_purge_history', 1, 20240227, 20000, 1, 'The job succeeded.  The Job was invoked by Schedule 8 (syspolicy_purge_history_schedule).  The last step to run was step 3 (Erase Phantom System Health Records.).', 20240226, 20000, 2, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 500000))
                ],
                [
                    {
                        'id': '295ea804-8d8d-440d-a18b-170342c7d3be',
                        'name': 'LSAlert_NOCMSSQLREP03',
                        'enabled': 1,
                        'next_run_date': 20240226,
                        'next_run_time': 102800,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 11 (Log shipping alert job schedule.).  The last step to run was step 1 (Log shipping alert job step.).',
                        'last_run_date': 20240226,
                        'last_run_time': 104400,
                        'last_run_duration': 0,
                        'schedule_enabled': 1,
                    },
                    {
                        'id': '7ee36c8b-e64d-4f00-8c06-0d493631c890',
                        'name': 'LSBackup_MYDB',
                        'enabled': 1,
                        'next_run_date': 20240226,
                        'next_run_time': 103000,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 12 (LSBackupSchedule_NOCMSSQLREP031).  The last step to run was step 1 (Log shipping backup log job step.).',
                        'last_run_date': 20240226,
                        'last_run_time': 103000,
                        'last_run_duration': 1,
                        'schedule_enabled': 1,
                    },
                    {
                        'id': '42f5572f-23b5-4e20-8459-63b3d3428f74',
                        'name': 'syspolicy_purge_history',
                        'enabled': 1,
                        'next_run_date': 20240227,
                        'next_run_time': 20000,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 8 (syspolicy_purge_history_schedule).  The last step to run was step 3 (Erase Phantom System Health Records.).',
                        'last_run_date': 20240226,
                        'last_run_time': 20000,
                        'last_run_duration': 2,
                        'schedule_enabled': 1,
                    },
                ],
                agent_mssql_log_shipping.QUERY['get_jobs']['columns'],
                agent_mssql_log_shipping.map_many_results
            ),
            (
                (b'MSSQLSERVER', 'MYDB', 'C:\\log_shipping\\MYDB_20240226133001.trn', datetime.datetime(2024, 2, 26, 10, 30, 1, 390000), datetime.datetime(2024, 2, 26, 13, 30, 1, 390000), 'C:\\log_shipping\\MYDB_20240226130000.trn', datetime.datetime(2024, 2, 26, 10, 15, 1, 313000), datetime.datetime(2024, 2, 26, 13, 30, 1, 390000)),
                {
                    'instance_name': 'MSSQLSERVER',
                    'secondary_database': 'MYDB',
                    'last_copied_file': 'C:\\log_shipping\\MYDB_20240226133001.trn',
                    'last_copied_date': '2024-02-26T10:30:01.390000',
                    'last_copied_date_utc': '2024-02-26T13:30:01.390000',
                    'last_restored_file': 'C:\\log_shipping\\MYDB_20240226130000.trn',
                    'last_restored_date': '2024-02-26T10:15:01.313000',
                    'last_restored_date_utc': '2024-02-26T13:30:01.390000'
                },
                agent_mssql_log_shipping.QUERY['get_secondary_status']['columns'],
                agent_mssql_log_shipping.map_one_result
            ),
            (
                [
                    (UUID('3c77e655-1503-4df9-bed4-90c614dab32b'), 'LSAlert_NOCMSSQLREP04', 1, 20240226, 103600, 1, 'The job succeeded.  The Job was invoked by Schedule 11 (Log shipping alert job schedule.).  The last step to run was step 1 (Log shipping alert job step.).', 20240226, 104400, 0, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 487000)),
                    (UUID('b5640351-801f-41aa-901e-39178c094a5d'), 'LSCopy_NOCMSSQLREP03_MYDB', 0, 20240209, 94500, 0, 'The job failed.  The Job was invoked by Schedule 9 (DefaultCopyJobSchedule).  The last step to run was step 1 (Log shipping copy job step.).', 20240209, 93000, 1, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 487000)),
                    (UUID('909fe951-e1f8-45e1-bc30-17e6f0a25f4d'), 'LSRestore_NOCMSSQLREP03_MYDB', 1, 20240226, 104500, 1, 'The job succeeded.  The Job was invoked by Schedule 10 (DefaultRestoreJobSchedule).  The last step to run was step 1 (Log shipping restore log job step.).', 20240226, 103000, 0, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 487000)),
                    (UUID('2302f1ae-9471-4725-ac8a-2583cdef4406'), 'syspolicy_purge_history', 1, 20240227, 20000, 1, 'The job succeeded.  The Job was invoked by Schedule 8 (syspolicy_purge_history_schedule).  The last step to run was step 3 (Erase Phantom System Health Records.).', 20240226, 20000, 3, 1, datetime.datetime(2024, 2, 26, 10, 44, 14, 487000))
                ],
                [
                    {
                        'id': '3c77e655-1503-4df9-bed4-90c614dab32b',
                        'name': 'LSAlert_NOCMSSQLREP04',
                        'enabled': 1,
                        'next_run_date': 20240226,
                        'next_run_time': 103600,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 11 (Log shipping alert job schedule.).  The last step to run was step 1 (Log shipping alert job step.).',
                        'last_run_date': 20240226,
                        'last_run_time': 104400,
                        'last_run_duration': 0,
                        'schedule_enabled': 1,
                    },
                    {
                        'id': 'b5640351-801f-41aa-901e-39178c094a5d',
                        'name': 'LSCopy_NOCMSSQLREP03_MYDB',
                        'enabled': 0,
                        'next_run_date': 20240209,
                        'next_run_time': 94500,
                        'last_run_outcome': 0,
                        'last_outcome_message': 'The job failed.  The Job was invoked by Schedule 9 (DefaultCopyJobSchedule).  The last step to run was step 1 (Log shipping copy job step.).',
                        'last_run_date': 20240209,
                        'last_run_time': 93000,
                        'last_run_duration': 1,
                        'schedule_enabled': 1,
                    },
                    {
                        'id': '909fe951-e1f8-45e1-bc30-17e6f0a25f4d',
                        'name': 'LSRestore_NOCMSSQLREP03_MYDB',
                        'enabled': 1,
                        'next_run_date': 20240226,
                        'next_run_time': 104500,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 10 (DefaultRestoreJobSchedule).  The last step to run was step 1 (Log shipping restore log job step.).',
                        'last_run_date': 20240226,
                        'last_run_time': 103000,
                        'last_run_duration': 0,
                        'schedule_enabled': 1,
                    },
                    {
                        'id': '2302f1ae-9471-4725-ac8a-2583cdef4406',
                        'name': 'syspolicy_purge_history',
                        'enabled': 1,
                        'next_run_date': 20240227,
                        'next_run_time': 20000,
                        'last_run_outcome': 1,
                        'last_outcome_message': 'The job succeeded.  The Job was invoked by Schedule 8 (syspolicy_purge_history_schedule).  The last step to run was step 3 (Erase Phantom System Health Records.).',
                        'last_run_date': 20240226,
                        'last_run_time': 20000,
                        'last_run_duration': 3,
                        'schedule_enabled': 1,
                    },
                ],
                agent_mssql_log_shipping.QUERY['get_jobs']['columns'],
                agent_mssql_log_shipping.map_many_results
            ),
        ]
    )
    def test_result_to_dict(self, raw_query_results, expected_result, columns, cast):
        data = cast(columns, raw_query_results)
        assert data == expected_result
