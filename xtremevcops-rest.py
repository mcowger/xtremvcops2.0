__author__ = 'mcowger'

from pprint import pprint
from hammock import Hammock as XtremIO
from docopt import docopt
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__doc__ = """
Usage: xtremevcops-rest.py [-h] XMS_IP [--quiet | --verbose] [--protocol=<proto>] [--base_path=<base_path>]

Collect Performance Statistics from an XtremIO array and push them to vCenter Operations

Arguments:
    XMS_IP       IP of XMS (required)

Options:
    -h --help    show this
    --quiet      print less text
    --verbose    print more text
    --protocol=proto   [http | https] [default: https]
    --base_path=base_path  base_path for API operations [default: /api/json/types]
"""
options = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
xtremio = XtremIO(options['--protocol']+ "://" + options['XMS_IP'] + options['--base_path'],verify=False, auth=('demo', 'demo'))



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

if __name__ == "__main__":
    for volume in get_volumes():
        volume_info = get_volume(volume)
        brick_name = volume_info['content']['sys-id'][1]
        for metric in volume_info['content'].items():
            if type(metric[1]) in [type(1),type("")]:
                logger.info("Metric found: brick:volume:metric:value %s:%s:%s:%s" % (brick_name,volume['name'],metric[0],metric[1]))
