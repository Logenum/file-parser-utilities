import os, sys
import os.path
import re
import time
import datetime
import sqlite3
from ParamUtils import *
from TraceOtlUtils import *
from StateUtils import *
from TrickUtils import *


class clDatabase(clParams):
    
    # TBD: add SQLite accessibility
    # =========================================================
    def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
    # =========================================================
        # trace file opens/closes are handled by main script, not in objects
        # TBD: buffer type setting in constructor to reduce accidental writing to input files

    
        me.oTrace = oTrace
        me.sDuty = sDuty  # means the "task" or "role" of the object. Mainly used to improve Trace Log
        me.sDatabaseFileNameWholeName = ""
        me.oSqlConn = 0

    #=========================================================
    def connectToDatabase(me, sDatabaseName, sDbType):  #
    #=========================================================
        # TBD: add assuring an absolute path name
        sType = ""
        bStatus = False

        if os.path.isfile(sDatabaseName):
            sType =  " existing "
        else:
            sType = " new "

        if sDbType == "SQLITE":
            try:
                me.oSqlConn = sqlite3.connect(sDatabaseName)
                me.bThisObjectIsOperable = True
                me.oTrace.INFO("connected to"+sType+"SQLITE database: '" + sDatabaseName + "' at object '" + me.sDuty + "'")
                bStatus = True
                
            except: # TBD...
                exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
                sErrorText = str(exctype) + " " + str(value)
                me.oTrace.INFO("'" + sErrorText + "' when trying to connect to" + sType + "SQLITE to database: '" + sDatabaseName + "' at object '" + me.sDuty + "'")
            finally:
                pass

        else:
            me.oTrace.INFO("unknown database type: '" + sDbType + "' at object '" + me.sDuty + "'")
            
        return bStatus

    #=========================================================
    def Do(me):  #
    #=========================================================
        oCursor = 0
        if me.bThisObjectIsOperable == True:
            oCursor = me.oSqlConn.cursor

        return oCursor


