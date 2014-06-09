__author__ = 'mcowger'

from nose import SkipTest
from xtremvcops2.xtremvcops2 import XtremIO_Connection
import vcr

class Test_XtremIO_Connection:

    def __init__(self):
        self.options = {'--debug_level': 'INFO',
         '--help': False,
         '--interval': '60',
         '--protocol': 'https',
         '--quiet': False,
         '--vcops_pass': 'P@ssword1!',
         '--vcops_user': 'admin',
         '--xms_base_path': '/api/json/types',
         'VCOPS_IP': '10.5.132.130',
         'XMS_IP': '10.28.79.100',
         'XMS_PASS': 'demo',
         'XMS_USER': 'demo'}


    @vcr.use_cassette('fixtures/vcr_cassettes/init.yaml')
    def test__init__(self):

        xtremeio_conn = XtremIO_Connection(self.options)
        assert xtremeio_conn.options == self.options

