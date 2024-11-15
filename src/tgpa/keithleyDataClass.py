"""
Creator : Yann Berton
Date : 20/09/2024
Objective : Get user's keithley information
"""
# Imports
import toml

# Classes definitions


class Channel:

    """Channel data object"""

    def __init__(self,number:str, mode:str, transducer=None, type=None, ref_junc = None, resolution=None, nplc=None):
        self.number = number
        self.mode = mode
        self.transducer = transducer
        self.type = type
        self.ref_junc = ref_junc
        self.resolution = resolution
        self.nplc = nplc


class ModuleKeithley:

    """Module data object"""

    def __init__(self, name: str, number:str,info: str, sensors_settings : dict):
        self.name = name  # Module name
        self.number = number  # Card number
        self.info = info  # Module info
        self.channels = []  # Initialization of the module's used channel
        self.sensors_settings = sensors_settings

    def config_channel(self, nb_channel: str, sensor: str):

        """Config a module's channel"""

        match sensor:
            case "frtd":
                self.channels.append(Channel(nb_channel,self.sensors_settings['Frtd']['mode'], self.sensors_settings['Frtd']['transducer'],
                                             self.sensors_settings['Frtd']['type'], resolution=int(self.sensors_settings['Frtd']['resolution']),
                                             nplc=int(self.sensors_settings['Frtd']['nplc'])))
                self.__setattr__("c" + nb_channel, self.channels[-1])

            case "tc":
                self.channels.append(Channel(nb_channel,self.sensors_settings['Tc']['mode'], self.sensors_settings['Tc']['transducer'],
                                             self.sensors_settings['Tc']['type'], ref_junc = self.sensors_settings['Tc']['ref_junc'],
                                             resolution=int(self.sensors_settings['Tc']['resolution'])))
                                             
                self.__setattr__("c" + nb_channel, self.channels[-1])

            case "Volt":
                self.channels.append(Channel(nb_channel,self.sensors_settings['Volt']['mode']))
                self.__setattr__("c" + nb_channel, self.channels[-1])

    def config_all_channels(self, Lfrtd:list, Ltc:list, LVolt:list):

        """Config all the modules channels"""

        [self.config_channel(nb_channel=chan, sensor="frtd")
         for chan in Lfrtd
         if len(Lfrtd) > 0]
        [self.config_channel(nb_channel=chan, sensor="tc")
         for chan in Ltc
         if len(Ltc) > 0]
        [self.config_channel(nb_channel=chan, sensor="Volt")
         for chan in LVolt
         if len(LVolt) > 0]


class Keithley2700:

    """Keithley data object"""

    def __init__(self, name, title, rsrc_name_example, rsrc_name,
                 model_name, panel, termination_character, sensors_settings):
        self.tolm = f""""""
        self.name = name
        self.title = title
        self.rsrc_name_example = rsrc_name_example
        self.rsrc_name = rsrc_name
        self.model_name = model_name
        self.panel = panel
        self.termination_character = termination_character
        self.sensors_settings = sensors_settings
        self.modules = []

    def add_module(self, name, number, info):

        """Add a module to the object Keithley"""

        self.modules.append(ModuleKeithley(name, number, info, self.sensors_settings))  # Get the new module in a list
        self.__setattr__(name, self.modules[-1])  # Give the module as a attribute to the Keithley

    def write_tolm(self, output_path):

        """Generate a tolm file with the info input from the user"""
        
        self.tolm = f""""""  # Wiping self.tolm
        self.tolm += f"""
title = "this is the configuration file of the Keithley plugin"

[Keithley.27XX]
title = "Configuration entry for a Keithley 27XX Multimeter/Switch System"

[Keithley.27XX.{self.name}]
title = \"{self.title}\"
rsrc_name_example = \"{self.rsrc_name_example}\"
rsrc_name = \"{self.rsrc_name}\"
model_name = \"{self.model_name}\"
panel = \"{self.panel}\"
termination_character = \"{self.termination_character}\"
"""

        for module in self.modules:
            self.tolm += f"""
[Keithley.27XX.{self.name}.{module.name}]
module_name = \"{module.number}\"
info = \"{module.info}\"

[Keithley.27XX.INSTRUMENT01.{module.name}.CHANNELS]
"""

        for module in self.modules:
            for chan in module.channels:
                match chan.transducer:
                    case "tc":
                        self.tolm += f"""
[Keithley.27XX.{self.name}.{module.name}.CHANNELS.{chan.number}]
mode = \"{chan.mode}\"
transducer = \"{chan.transducer}\"
type = \"{chan.type}\"
ref_junc = \"{chan.ref_junc}\"
resolution = \"{chan.resolution}\"
nplc = \"{chan.nplc}\"
"""
                    case "frtd":
                        self.tolm += f"""
[Keithley.27XX.{self.name}.{module.name}.CHANNELS.{chan.number}]                        
mode = \"{chan.mode}\"
transducer = \"{chan.transducer}\"
type = \"{chan.type}\"
resolution = \"{chan.resolution}\"
nplc = \"{chan.nplc}\"
"""
                    case _:
                        self.tolm += f"""
[Keithley.27XX.{self.name}.{module.name}.CHANNELS.{chan.number}]
mode = \"{chan.mode}\"
"""
        self.tolm = toml.loads(self.tolm)
        with open(output_path,"w") as f:
            toml.dump(self.tolm,f)
        print("Your tolm file has been successfully generated")


if __name__ == "__main__":
    INSTRUMENT01 = Keithley2700(name = "INSTRUMENT01",
                                title="Instrument in wich is plugged the switching module used for data acquisition",
                                rsrc_name_example=["ASRL1::INSTR", "TCPIP::192.168.01.01::1394::SOCKET"],
                                rsrc_name="ASRL7::INSTR",
                                model_name="2701",
                                panel="rear",
                                termination_character="Keithley must be set to LF",
                                sensors_settings={'Frtd': {'mode': 'temp',
                                                           'transducer': 'frtd',
                                                           'type': 'pt100',
                                                           'resolution': '6',
                                                           'nplc': '5'},
                                                  'Tc': {'mode': 'temp',
                                                         'transducer': 'tc',
                                                         'type': 'K',
                                                         'ref_junc': 'ext',
                                                         'resolution': '6',
                                                         'nplc': '5'},
                                                  'Volt': {'mode': 'Volt:dc'}})
#    INSTRUMENT01.add_module(name="MODULE01",
#                          number="7706",
#                          info="Channels 201 & 202 configured using thermocouple by default")"""
    INSTRUMENT01.add_module(name="MODULE02", number="7702",
                            info="Channels 201 & 202 configured using thermocouple by default")

    # Let's config MODULE01 channels

    # List of the different sensors
    Lfrtd1 = ["101"]
    Ltc1 = ["102", "103", "104", "105", "106", "107"]
    LVolt1 = ["110", "109"]

    Lfrtd2 = ["201"]
    Ltc2 = ["213", "214", "215", "217", "218", "219", "220", "225", "226", "227", "228"]
    LVolt2 = ["110", "109"]

    # Loop to config one card (module)
#   for channel in Lfrtd1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="frtd")

    for channel in Lfrtd2:
        INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="frtd")

#    for channel in Ltc1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="tc")"""

    for channel in Ltc2:
        INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="tc")

#    for channel in LVolt1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="Voltage")"""

    for channel in LVolt2:
        INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="Volt")

    INSTRUMENT01.write_tolm("config_keitley_test.tolm")



