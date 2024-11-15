"""
Creator : Yann Berton
Date : 20/09/2024
Objective : Automatically generate tolm files for keithley in pymodaq
"""

# Imports
from keithleyDataClass import Keithley2700
from PyQt5.QtWidgets import QFileDialog
from utilities import getAFilesPathToSave

# The front program has a role to play here to get the Keitley and cards/modules info
INSTRUMENT01 = Keithley2700(name = "INSTRUMENT01",
                            title="Instrument in wich is plugged the switching module used for data acquisition",
                            rsrc_name_example=["ASRL1::INSTR", "TCPIP::192.168.01.01::1394::SOCKET"],
                            rsrc_name="ASRL7::INSTR",
                            model_name="2701",
                            panel="rear",
                            termination_character="Keithley must be set to LF")
#    INSTRUMENT01.add_module(name="MODULE01",
#                          number="7706",
#                         info="Channels 201 & 202 configured using thermocouple by default")"""
INSTRUMENT01.add_module(name="MODULE02", number="7702",
                        info="Channels 201 & 202 configured using thermocouple by default")


# Let's config MODULE01 channels

# List of the different sensors
Lfrtd1 = ["101"]
Ltc1 = ["102", "103", "104", "105", "106", "107"]
Lvolt1 = ["110", "109"]

Lfrtd2 = ["201"]
Ltc2 = ["213", "214", "215", "217", "218", "219", "220", "225", "226", "227", "228"]
Lvolt2 = []

# Loop to config one card (module)
#   for channel in Lfrtd1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="frtd")

for channel in Lfrtd2:
    INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="frtd")

#    for channel in Ltc1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="tc")"""

for channel in Ltc2:
    INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="tc")

#    for channel in Lvolt1:
#        INSTRUMENT01.MODULE01.config_channel(nb_channel=channel,sensor="voltage")"""

for channel in Lvolt2:
    INSTRUMENT01.MODULE02.config_channel(nb_channel=channel,sensor="voltage")

INSTRUMENT01.write_tolm(getAFilesPathToSave("Save your file", [('Tolm files', '*.tolm*')]))




