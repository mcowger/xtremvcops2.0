__author__ = 'mcowger'

import logging
import time

from docopt import docopt

from hammock.hammock import Hammock as XtremIO
from hammock.hammock import Hammock as Vcops


__doc__ = """
Usage: xtremvcops2.py [-h] XMS_IP XMS_USER XMS_PASS VCOPS_IP [--interval=<interval>] [--vcops_user=<user>] [--vcops_pass=<pass>] [--quiet] [--debug_level=<level>] [--protocol=<proto>] [--xms_base_path=<base_path>]

Collect Performance Statistics from an XtremIO array and push them to vCenter Operations

Arguments:
    XMS_IP       IP of XMS (required)
    XMS_USER    Username for XMS
    XMS_PASS    PAssword for XMS
    VCOPS_IP    IP of VCOPS instance


Options:
    -h --help    show this
    --quiet      print less text
    --debug_level=<level>    Very verbose debugging [default: WARN]
    --protocol=<proto>   [http | https] [default: https]
    --xms_base_path=<base_path>  base_path for API operations [default: /api/json/types]
    --vcops_user=<user>  VC Ops User [default: admin]
    --vcops_pass=<pass>  VC Ops Password [default: P@ssword1!]
    --interval=<interval>   Sleep interval between collections [default: 60]
"""


class XtremIO_Connection(object):
    def __init__(self, options):
        try:
            self.xtremio = XtremIO(options['--protocol']+ "://" + options['XMS_IP'] + options['--xms_base_path'],verify=False, auth=(options['XMS_USER'], options['XMS_PASS']))
        except Exception as exp:
            raise
        self.options = options

    def get_volumes(self):
        logging.info("Retrieving list of all volumes from XMS")
        try:
            volumes =  self.xtremio.volumes.GET().json()['volumes']
        except Exception as exp:
            raise
        logging.info("Got %d volumes from XMS" % len(volumes))
        return volumes

    def get_volume(self,volume_record):
        logging.info("Retrieving info for volume: " + volume_record['name'])
        volume_number = volume_record['href'].rsplit('/',1)[-1]
        try:
            return self.xtremio.volumes(volume_number).GET().json()
        except Exception as exp:
            raise

    def get_brick_list(self):
        """
        Gets the list of bricks available in an XMS.

        """
        try:
            return self.xtremio.bricks.GET().json()['bricks']
        except Exception as exp:
            raise

    def collect_and_submit(self):
        vcops_connection = Vcops_Connection(vcops_ip=options['VCOPS_IP'])
        for volume in self.get_volumes():
            volume_info = self.get_volume(volume)
            brick_name = volume_info['content']['sys-id'][1]

            vcops_info = Vcops_Record_Keeper(resourceName='XMS-'+brick_name+"-"+volume['name'],resourceKindKey='XtremeIO-Array',resourceDescription='XtremeIO Array')
            for metric in volume_info['content'].items():
                if type(metric[1]) in [type(1),type("")]: #Did we find a str or int?
                    logging.debug("Metric found: brick:volume:metric:value %s:%s:%s:%s" % (brick_name,volume['name'],metric[0],metric[1]))
                    vcops_info.add_metric_observation(entity_name=volume['name'],metric_name=metric[0],value=str(metric[1]))
            response = vcops_connection.submit_set(vcops_info.first_line,vcops_info.metric_lines)
            logging.info(response)

class Vcops_Connection(object):
    def __init__(self,vcops_ip=""):
        self.vcops_ip = vcops_ip
        try:
            self.vcops = Vcops(options['--protocol']+ "://" + self.vcops_ip + '/HttpPostAdapter/OpenAPIServlet',verify=False,auth=(options['--vcops_user'],options['--vcops_pass']))
        except Exception as exp:
            raise
        logging.info("Logging into vcops @ %s as %s" % (self.vcops_ip,options['--vcops_user']))

    def submit_set(self,first_line,metric_lines):
        logging.debug("Submitting metrics as user: %s:\n %s" % (options['--vcops_user'],first_line+'\n'+metric_lines[0:500]))
        response = self.vcops.POST(data=first_line+'\n'+metric_lines)
        return response

class Vcops_Record_Keeper(object):
    def __init__(self,resourceName,resourceKindKey="",identifiers="",resourceDescription=""):

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
        logging.debug("Returning first line: %s" % first_line)
        return first_line

    def add_metric_observation(self,entity_name,metric_name,alarm_level=0,alarm_message="",value=''):
        metric_string = ','.join((metric_name,'','',str(self.current_time_millis),value,str(alarm_level)))
        self.metrics.append(metric_string)
        logging.debug("Added metric: %s" % metric_string)


    @property
    def current_time_millis(self):
        import time
        return int(round(time.time() * 1000))



if __name__ == "__main__":
    options = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    numeric_level = getattr(logging, options['--debug_level'].upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level,format='%(asctime)s|%(name)s|%(levelname)s|%(module)s:%(lineno)d|%(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Printing received options:")
    logger.info(options)

    while True:
        logger.warn("Starting Collection Run")
        xtremeio_conn = XtremIO_Connection(options)
        xtremeio_conn.collect_and_submit()
        logger.warn("Sleeping for %d seconds until next run" % int(options['--interval']))
        time.sleep(int(options['--interval']))