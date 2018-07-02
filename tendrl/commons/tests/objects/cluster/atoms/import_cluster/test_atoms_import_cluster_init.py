import __builtin__
import maps
from mock import patch
import mock
import subprocess
import uuid

from tendrl.commons.flows import utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.tests import test_init


from tendrl.commons.objects.cluster.atoms.import_cluster import ImportCluster

class MockClusterObject(object):
    def __init__(self, integration_id = 1):
        self.short_name = "9"

    def load(self):
        return self

class MockTendrlContext(object):
    def __init__(self):
        self.node_id = 0
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

class MockCompiledDefinitions(object):
    def __init__(self):
        pass
    def get_parsed_defs(self):
        mock_return = maps.NamedDict()
        nested_return = maps.NamedDict(min_reqd_gluster_ver = "1.2.3")
        mock_return["namespace.tendrl"] = nested_return
        return mock_return


@mock.patch('subprocess.Popen')
@patch.object(utils, 'release_node_lock')
@patch.object(utils, 'acquire_node_lock')
def test_import_cluster(patch_acquire_node_lock, patch_release_node_lock, mock_subproc_popen):

    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())
    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.config.data["logging_socket_path"] = "/tmp"
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = MockClusterObject
    NS.tendrl_context = MockTendrlContext()
    NS.tendrl.objects.Job = MockJob

    process_mock = mock.Mock()



    test = ImportCluster()
    test.parameters = maps.NamedDict()
    attrs = {'communicate.return_value': ('glusterfs-server-test.dev.more\n 1.2\n 1', '')}
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock

    #tendrlNS = test_init()
    #NS["compiled_definitions"] = tendrlNS.current_ns.definitions

    NS.compiled_definitions = MockCompiledDefinitions()
    #NS.compiled_definitions = mock.MagicMock()


    test.parameters["TendrlContext.integration_id"] = '94ac63ba-de73-4e7f-8dfa-9010d9554084'
    test.parameters['Node[]'] = [0,1]
    test.parameters['job_id'] = [20]
    test.parameters['flow_id'] = 1
    test.run()
    NS.compiled_definitions = None
    #test_init()