import __builtin__
import maps
from mock import patch
import mock

import uuid
import pytest

from tendrl.commons.utils import ansible_module_runner

from tendrl.commons.flows import utils

from tendrl.commons.flows.import_cluster import gluster_help

from tendrl.commons.objects.cluster.atoms.import_cluster import ImportCluster


class MockClusterObject(object):

    def __init__(self, integration_id = 1):
        self.short_name = "test_uuid"

    def load(self):
        return self


class MockTendrlContext(object):

    def __init__(self, sds_version=1):
        self.node_id = 0
        self.sds_version = 1

    def load(self):
        return self


class MockJob(object):

    def __init__(self, job_id=None, status="new", payload=None):
        pass

    def load(self):
        self.payload = {}
        return self

    def save(self):
        return self


def get_bad_parsed_defs():
    mock_return = maps.NamedDict()
    nested_return = maps.NamedDict(min_reqd_gluster_ver="3.2.1")
    mock_return["namespace.tendrl"] = nested_return
    return mock_return


def get_good_parsed_defs():
    mock_return = maps.NamedDict()
    nested_return = maps.NamedDict(min_reqd_gluster_ver="1.2.3")
    mock_return["namespace.tendrl"] = nested_return
    return mock_return


@mock.patch('subprocess.Popen')
@patch.object(utils, 'release_node_lock')
@patch.object(utils, 'acquire_node_lock')
@patch.object(gluster_help, 'import_gluster')
def test_import_cluster(patch_import_gluster, patch_acquire_node_lock, patch_release_node_lock, mock_subproc_popen):

    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())
    NS.node_context["fqdn"] = "localhost"

    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.config.data["logging_socket_path"] = "/tmp"
    NS.config.data['package_source_type'] = 'rpm'
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = MockClusterObject
    NS.tendrl_context = MockTendrlContext()
    NS.tendrl.objects.Job = MockJob


    test = ImportCluster()
    test.parameters = maps.NamedDict()

    process_mock = mock.Mock()
    Popen_attrs = {'communicate.return_value': ('glusterfs-server-1.2.3', '')}
    process_mock.configure_mock(**Popen_attrs)
    mock_subproc_popen.return_value = process_mock

    test.parameters["TendrlContext.integration_id"] = '94ac63ba-de73-4e7f-8dfa-9010d9554084'
    test.parameters['Node[]'] = ['test_node_0', 'test_node_1']
    test.parameters['job_id'] = 'test_id'
    test.parameters['flow_id'] = 'test_flow_id'

    NS.compiled_definitions = mock.MagicMock()

    patch_import_gluster.return_value = (True, '')

    # gluster version incompatible
    with patch.object(NS.compiled_definitions, 'get_parsed_defs', get_bad_parsed_defs):
        with pytest.raises(Exception):
            test.run()

    # succeed
    with patch.object(NS.compiled_definitions, 'get_parsed_defs', get_good_parsed_defs):
        with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                          return_value=({"rc": 1, "msg": None}, None)):
            with pytest.raises(Exception):
                test.run()

#with patch.object(gluster_help, 'import_gluster',
#                              return_value=(True, True)):