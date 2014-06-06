__author__ = 'mcowger'

from pprint import pprint
from hammock import Hammock as XtremIO
from docopt import docopt
import json
import logging



__doc__ = """
Usage: xtremevcops-rest.py [-h] XMS_IP XMS_USER XMS_PASS VCOPS_IP [--vcops_user] [--vcops_pass] [--quiet] [--debug_level=<level>] [--protocol=<proto>] [--xms_base_path=<base_path>]

Collect Performance Statistics from an XtremIO array and push them to vCenter Operations

Arguments:
    XMS_IP       IP of XMS (required)
    XMS_USER    Username for XMS
    XMS_PASS    PAssword for XMS
    VCOPS_IP    IP of VCOPS instance


Options:
    -h --help    show this
    --quiet      print less text
    --debug_level=<level>    Very verbose debugging [default: INFO]
    --protocol=<proto>   [http | https] [default: https]
    --xms_base_path=<base_path>  base_path for API operations [default: /api/json/types]
    --vcops_user  VC Ops User [default: admin]
    --vcops_pass    VC Ops Password [default: P@ssword1!]
"""
options = docopt(__doc__, argv=None, help=True, version=None, options_first=False)

if options['--debug_level'] == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

xtremio = XtremIO(options['--protocol']+ "://" + options['XMS_IP'] + options['--xms_base_path'],verify=False, auth=(options['XMS_USER'], options['XMS_PASS']))



def get_volumes():
    logger.info("Retrieving list of all volumes from XMS")
    return xtremio.volumes.GET().json()['volumes']

def get_volume(volume_record):
    logger.info("Retrieving info for volume: " + volume_record['name'])
    volume_number = volume_record['href'].rsplit('/',1)[-1]
    return xtremio.volumes(volume_number).GET().json()

def get_brick_list():
    """
    Gets the list of bricks available in an XMS.

    """
    return xtremio.bricks.GET().json()['bricks']

class Vcops_Connection(object):
    def __init__(self,vcops_ip="",vcops_user=options['--vcops_user'],vcops_pass=options['--vcops_pass']):
        super().__init__()



class Vcops_Record(object):
    def __init__(self,resourceName,resourceKindKey="",identifiers="",resourceDescription=""):
        super().__init__()
        self.resource_name = resourceName
        self.resource_kind_key = resourceKindKey
        self.identifiers = identifiers
        self.resource_description = resourceDescription
        self.metrics = []

    @property
    def metric_lines(self):
        return '\n'.join(self.metrics)

    @property
    def first_line(self):

        first_line = ",".join( ( self.resource_name,'HTTP Post',self.resource_kind_key,self.identifiers,self.resource_description,'','')  )
        logger.debug("Returning first line: %s" % first_line)
        return first_line

    def add_metric_observation(self,entity_name,metric_name,alarm_level=0,alarm_message="",value=''):
        metric_string = ','.join((entity_name + '|' + metric_name,str(alarm_level),alarm_message,str(self.current_time_millis),value))
        self.metrics.append(metric_string)
        logger.debug("Added metric: %s" % metric_string)


    @property
    def current_time_millis(self):
        import time
        return int(round(time.time() * 1000))

if __name__ == "__main__":
    vcops_info = Vcops_Record(resourceName='XMS-'+ options['XMS_IP'],resourceKindKey='XtremeIO-Array',resourceDescription='XtremeIO Array')
    for volume in get_volumes():
        volume_info = get_volume(volume)
        brick_name = volume_info['content']['sys-id'][1]
        for metric in volume_info['content'].items():
            if type(metric[1]) in [type(1),type("")]: #Did we find a str or int?
                logger.debug("Metric found: brick:volume:metric:value %s:%s:%s:%s" % (brick_name,volume['name'],metric[0],metric[1]))
                vcops_info.add_metric_observation(entity_name=volume['name'],metric_name=metric[0],value=str(metric[1]))

