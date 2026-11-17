
import sys

from addon_utils import Dispatcher, sys_path_insert

#Make lib available
sys_path_insert('/src')
sys_path_insert('/src/libs/radionet_api')

from radio_de import RadioDE


radio = RadioDE()
dispatcher = Dispatcher(sys.argv, radio)
dispatcher.route()
