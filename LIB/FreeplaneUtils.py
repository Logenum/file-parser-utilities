import os, sys
import os.path
import re
import time
import datetime

from TextStoreUtils import *
from StateUtils import *

class clFreeplane(clTextStore):  # !: inheritance: https://docs.python.org/2/tutorial/classes.html
 # PURPOSE: for analyzing Feeplane mind map file(s) and producing etc. textual/graphviz outputs
	#=========================================================
	def __init__(me, sDuty, fhTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		me.fhTrace = fhTrace
		me.sDuty = sDuty
		clTextStore.__init__(me, me.sDuty, me.fhTrace)  # !: initializing parent class