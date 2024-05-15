


#!/usr/bin/env python
#coding=utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException

import time, unittest, re, os, sys
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil, errno  # for file copying
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains #move_to_element
import glob # removes all non-stored logfiles and screenshots
import os.path
import base64


# Library

class SeleniumUtils:
    nTIMEOUT = -1   # common with all objects of this class (= a CLASS VARIABLE)
    #=========================================================
    def __init__(me,
                 NEobjId,
                 useCaseName,
                 browserProfilePath,
                 browserWaitSec,
                 dGlobalVars,
                 nCallerTime,
                 nTextWaitTimeMax,
                 nTextChecksPerSec,
                 objDocDir,
                 bStoreScreenshots):  # python constructor
    #=========================================================
    
        # TODO: add ignoring profile usage, if "browserProfilePath" is string "DEFAULT"
        oProfile = webdriver.FirefoxProfile(browserProfilePath)
        #oProfile = webdriver.FirefoxProfile()
        oProfile.set_preference("webdriver.load.strategy", "unstable")
        #oProfile.set_preference("dom.event.contextmenu.enabled", False)
        # -from http://rostislav-matl.blogspot.fi/2011/09/setting-firefox-preferences-via.html
        # -from https://code.google.com/p/selenium/issues/detail?id=6168
        oProfile.set_preference("webdriver.log.file", "/" + useCaseName + "_webdriver.log")
        # - from http://stackoverflow.com/questions/10752122/how-to-save-the-logs-generated-using-selenium-with-python
        #oProfile.set_preference("http.response.timeout", browserWaitSec)
        #oProfile.set_preference("dom.max_script_run_time", browserWaitSec)
        # http://stackoverflow.com/questions/17533024/how-to-set-selenium-python-webdriver-default-timeout
        #me.DRIVER = webdriver.Firefox(firefox_profile=oProfile)  # TODO: activate finally
        me.DRIVER = webdriver.Firefox()  # for trying to pass by Authorization prompt
        me.DRIVER.implicitly_wait(browserWaitSec)

        #me.DRIVER.manage().timeouts().implicitlyWait(60, TimeUnit.SECONDS); # added 150928
        #me.DRIVER.set_page_load_timeout(browserWaitSec)

        me.OBJ_ID = NEobjId
        me.nTEXT_WAIT_MAX_SECONDS = nTextWaitTimeMax
        me.nTEXT_CHECKS_PER_SECOND = nTextChecksPerSec
        me.fTEXT_WAIT_CHECK_SECONDS =  1 /float( nTextChecksPerSec)
        fLoopCnt =  float(me.nTEXT_WAIT_MAX_SECONDS) / me.fTEXT_WAIT_CHECK_SECONDS
        me.nTEXT_WAIT_LOOP_CNT_MAX = int(fLoopCnt)

       # me.fTEXT_WAIT_CHECK_SECONDS =  nTextWaitTimeMax / nTextChecksPerSec
        me.prevTime = nCallerTime
        me.startTime = nCallerTime
        me.logTimePrev = nCallerTime
        me.traceFileNamesList=[]
        me.initTime=0.0
        today = datetime.now()
        me.focusMonthName = today.strftime("%B")
        me.OBJ_DOC_DIR = objDocDir
        me.latestStepName = "step0"
        me.nextStepName = "step0"

        me.dCALLER_GLOBALS = dGlobalVars
        me.USE_CASE_NAME = useCaseName
        me.LOG_FILE = "./"+me.USE_CASE_NAME+"-LATEST.log"
        #me.SCREENSHOT_STORE_DIR = objDocDir+"/"+useCaseName
        me.SCREENSHOT_STORE_DIR = objDocDir+"/"+useCaseName+"/"+me.focusMonthName
        # added monthly -based subdirectory (according to Samlink)
        me.bSTORE_SCREENSHOTS = bStoreScreenshots
        me.screenshotOrderNbr = 0
        me.LOG_INIT(nCallerTime, NEobjId)
        me.bExecutionStoppingStarted = False

        me.LOG("text wait: frequency/wait/total/maxloops = "+str(nTextChecksPerSec)+"/"+str(me.fTEXT_WAIT_CHECK_SECONDS)+"/"+ str(nTextWaitTimeMax)+"/"+str(me.nTEXT_WAIT_LOOP_CNT_MAX))

        try:
            if not os.path.exists(me.SCREENSHOT_STORE_DIR):
                os.makedirs(me.SCREENSHOT_STORE_DIR)
                me.LOG("new directory '" + me.SCREENSHOT_STORE_DIR+ "' is created")
            else:
                a=1
                ## me.LOG("directory '" + me.SCREENSHOT_STORE_DIR+ "' exists already")
        except:
            me.LOG("directory '" + me.SCREENSHOT_STORE_DIR+ "' creation failed")
            print "directory '" + me.SCREENSHOT_STORE_DIR+ "' creation failed"
            sys.exit(0)
        me.cleanRemainings()

    #==============================================================================
    def getDriver(me):
    #==============================================================================
        return me.DRIVER

    #==============================================================================
    def goURL(me, sURL):
    #==============================================================================
        sURLvarName = me.getVarAsStr(sURL)

        me.LOG("try go to URL '"+ sURLvarName+"'  '"+sURL+"'")
        try:
            me.DRIVER.get(sURL)
            me.LOG("succeeded to go to URL '"+ sURLvarName+"'  '"+sURL+"'")

        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.LOG("failed to go to URL: "+errorText)
            me.stopExecution("go URL: ", errorText) # 150902 commented to allow false url just to go out of page

    #==============================================================================
    def setStep(me, stepName, stepLabel=""):
    #==============================================================================
        if me.bExecutionStoppingStarted == True:
            return
        stepDescr=""
        stepLogText = ""
        if (stepLabel == ""):
            stepDescr = stepName
            stepLogText = "  step '"+stepName+"' passed"
        else:
            stepDescr = stepLabel
            stepLogText = "  step '"+stepName+"'/'"+stepLabel +"' passed"

        me.latestStepName = stepName

        me.nextStepName = me.getNextStepNameByStepName(stepName)

        nowTime = time.time()
        diffTime = nowTime - me.prevTime
        print (stepName + " " + str(diffTime))
        me.prevTime = nowTime
        me.LOG(str(diffTime) +  stepLogText)
        me.saveNamedScreenshot(stepDescr)   # decommented 151216 due to missing modal prompt error screenshot
        ##    log_text = str(driver.get_log)
        ##    LOG("step '" + stepName + "' driver log: "+ log_text)  # non-error

    # little helper to get the ok dialog
    def scrollDownPage(me):
        sHeight = .1
        while sHeight < 9.9:
            me.DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % sHeight)
            sHeight += .01
        return True
    #=========================================
    def switchToDefaultFrameContent(me):
        me.LOG("switch to default frame content")
        me.DRIVER.switch_to_default_content()
    #=====================================================
    def waitForTextAtPage(me,searchText,stepGoal):
        me.checkWaitForEitherTextAtPage(searchText,"THIS STRING IS NOT USED",stepGoal)

    #=====================================================
    def checkWaitForEitherTextAtPage(me,searchText1, searchText2, stepGoal):

        cnt=""
        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX

        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt = str(x)
            pageSourceRaw = me.DRIVER.page_source
            pageSource = pageSourceRaw.encode('utf-8')
            if searchText1 in pageSource:
                me.LOG("found '"+searchText1+"' at page, cnt="+cnt)
                return True
            elif  searchText2 in pageSource:
                me.LOG("found '"+searchText2+"' at page, cnt="+cnt)
                return True
            else:
                a=1 # do nothing
        me.LOG("NEITHER '"+searchText1 + "' NOR '" + searchText2 + "' found at page at '"+stepGoal+"', cnt="+cnt)
        me.setError("error: "+stepGoal+" failed")
        return False

    #===============================
    # check if texts are found and act accordingly
    def checkAndDeleteIfExists(me,sWaitText,sWaitText2):

        employeeField = "/html/body/div/div/div/div/aside/div/div[3]/table/tbody/tr[1]/td[3]"
        deleteEmployeeButton_xpath = "html/body/div/div/div/div/aside/div/div[2]/div/div[5]/div[2]/button[3]"
        confirmDeleteAction_xpath = "/html/body/div[3]/div[3]/div/button[1]"

        if sWaitText != "":
            pageSourceRaw = me.DRIVER.page_source
            pageSource = pageSourceRaw.encode('utf-8')
            if sWaitText in pageSource:
                me.LOG("text '"+sWaitText+ "' detected")
            else:
                if sWaitText2 in pageSource:
                    me.LOG("text '"+sWaitText2+ "' detected, cleaning up")
                    me.clickAndWaitFor(employeeField)
                    me.clickAndWaitFor(deleteEmployeeButton_xpath)
                    me.waitForElementByCssVisible("span.ui-dialog-title")
                    me.clickAndWaitFor(confirmDeleteAction_xpath)
                    me.LOG("deleted employee")
        else:
            me.LOG("nothing to wait for..")

    #===============================
    # compare attributes value
    def verifyAttributeValue(me,elemXpath,searchText):

        cnt=""
        nStepsMax = 20

        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            content = me.DRIVER.find_element_by_xpath(elemXpath).get_attribute('value')
            me.LOG("content: "+str(content))
            me.LOG("search: "+searchText)
            if str(content) == searchText:
                me.LOG("attribute value '"+searchText+"' matches, cnt="+cnt)
                return True

        me.LOG(searchText+" not found on page, cnt="+cnt)
        me.setError("error, attribute value mismatch, content: "+str(content))
        return False

    def verifyAttributeValueIsNot(me,elemXpath,searchText):

        cnt=""
        nStepsMax = 20

        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            #time.sleep(1)
            content = me.DRIVER.find_element_by_xpath(elemXpath).get_attribute('value')
            #content2 = me.DRIVER.find_element_by_xpath(elemXpath).text
            #me.LOG("content2: "+str(content2))
            me.LOG("content: "+str(content))
            me.LOG("search: "+searchText)
            if str(content) != searchText:
                me.LOG("attribute value '"+searchText+"' differs, cnt="+cnt)
                return True

        me.LOG(searchText+" matched on page, cnt="+cnt)
        me.setError("error, attribute value already exists, content: "+str(content))
        return False

    #==============================
    # return false if text found on elem
    def verifyNoElementTxtPresent(me,elemXpath,searchText):

        cnt=""
        nStepsMax = 5

        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            content = me.DRIVER.find_element_by_xpath(elemXpath).text
            me.LOG("content: "+str(content))
            me.LOG("search: "+searchText)
            if str(content) == searchText:
                me.LOG("found '"+searchText+"' at page, cnt="+cnt)
                me.setError("error, content present on page, content: "+str(content))
                return False

        me.LOG(searchText+" not found on page, cnt="+cnt)
        return True

    #==============================
    # return false if text found on elem
    def verifyElementTxtPresent(me,elemXpath,searchText):

        cnt=""
        nStepsMax = 20
        sElementName = me.getVarAsStr(elemXpath)

        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            element = me.DRIVER.find_element_by_xpath(elemXpath)
            if element.is_displayed():
                me.LOG("element "+sElementName+" located, count: "+cnt)
                content = me.DRIVER.find_element_by_xpath(elemXpath).text
                me.LOG("content: "+str(content))
                me.LOG("search: "+searchText)
                if str(content) == searchText:
                    me.LOG(searchText+" found on page, cnt="+cnt)
                    return True
            else:
                me.LOG("element "+sElementName+" not found, count: "+cnt)

        me.LOG(searchText+"' not found on page, cnt="+cnt)
        me.setError("error, content not present on page, content: "+str(content))
        return False

    #================================
    def waitForElementByXpathVisible(me, xpathSelector):

        element=None
        cnt=""
        sElementName = me.getVarAsStr(xpathSelector)
        nameAndVal = "name/val = '"+sElementName+"'/'"+ xpathSelector+"'"
        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX
        me.LOG("Waiting for an element "+nameAndVal+" to become visible")
        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
             #LOG("cnt="+str(cnt))
            element = me.DRIVER.find_element_by_xpath(xpathSelector)
            if element.is_displayed():
                me.LOG("element '"+nameAndVal+"' IS visible, count="+cnt)
                return True
        me.LOG("element '"+nameAndVal+"' IS NOT visible, count="+cnt)
        me.setError("error: '"+nameAndVal+"' is not visible,count="+cnt)
        return False

    #=================================
    def waitForElementByCssVisible(me, cssSelector):
        element=None
        cnt=""
        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX
        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            element = me.DRIVER.find_element_by_css_selector(cssSelector)
            if element.is_displayed():
                me.LOG("element '"+cssSelector+"' IS visible, count="+cnt)
                return True
        me.LOG("element '"+cssSelector+"' IS NOT visible, count="+cnt)
        #stopExecution("element '"+elementName+"' is NOT displayed, count="+cnt)
        return False

    #=====================================================
    def waitForElementByNameVisible(me, elementName):

        element=None
        cnt=""

        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX
        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            element = me.DRIVER.find_element_by_name(elementName)
            if element.is_displayed():
                me.LOG("element '"+elementName+"' IS visible, count="+cnt)
                return element
        me.LOG("element '"+elementName+"' IS NOT visible, count="+cnt)
        #stopExecution("element '"+elementName+"' is NOT displayed, count="+cnt)
        return None

    #=====================================================
    def waitForElementByIdVisible(me, elementId):

        element=None
        cnt=""
        me.LOG("Waiting for a element with id: '"+elementId+"' to become visible")
        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX
        for x in range(1, nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            cnt=str(x)
            #LOG("cnt="+str(cnt))
            element = me.DRIVER.find_element_by_id(elementId)
            if element.is_displayed():
                me.LOG("element '"+elementId+"' IS visible, count="+cnt)
                return element
        me.LOG("element '"+elementId+"' IS NOT visible, count="+cnt)
        me.setError("error: '"+sElementId+"' is not visible,count="+cnt)
        #stopExecution("element '"+elementName+"' is NOT displayed, count="+cnt)
        return None

    #====================================================
    def setError(me, comment):

        if me.bExecutionStoppingStarted == False:
            me.setStoppingState(True,"setError")
            print "available 0"
            me.LOG("available = 0")
            me.saveNamedScreenshot("Ended By Error")
            me.LOG("time "+str(me.startTime)+ " error: "+comment) # for error cases
            ### me.SAVE_LOG()
            comment = me.tidyRawErrorText(comment)
            print "error in "+me.nextStepName +" "+ comment
            print me.startTime
            me.storeTraceFilesWithUniqueNames(comment)
            me.DRIVER.quit()
            sys.exit(0)    # terminates whole script

    #===================================================
    def stopExecution(me, comment, errorText):

        if me.bExecutionStoppingStarted == False:
            errorText = me.tidyRawErrorText(errorText)

            me.setStoppingState(True,"Stop Execution: '"+errorText+"'")
            print "error in "+me.nextStepName+" "+errorText
            print "available 0"
            print me.startTime
            me.LOG("available = 0")
            me.LOG("stop caused by "+comment+", error:"+errorText)
            me.saveNamedScreenshot("Stopped By Execution")
            ### me.SAVE_LOG()
            me.storeTraceFilesWithUniqueNames(comment)
            me.DRIVER.quit()
            sys.exit(0)
 #   print startTime

    #==================================================================
    def LOG_INIT(me, callerTime, objId):

        me.initTime = time.time()
        me.traceFileNamesList.append(me.LOG_FILE)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fhl=open(me.LOG_FILE, 'w')  # 'w'= write
        fhl.write("time="+now+", objectId="+str(objId)+"\n")
        fhl.close()   # syntax required by Web Browsers

    #==================================================================
    def LOG(me, text):

        now = time.time()
        logTimeRel = now - me.initTime
        logTimeRel = "%3.1f" % logTimeRel
        fhl=open(me.LOG_FILE, 'a')
        fhl.write("***** "+str(logTimeRel)+"  "+text+"\n")  # 140407: for simplified logs
        fhl.close()   # syntax required by Web Browsers
    #=====================================================================================
    # http://stackoverflow.com/questions/9823272/python-selenium-waiting-for-frame-element-lookups
    def frame_available_cb(me,frame_reference):
        """Return a callback that checks whether the frame is available."""
        def callback(browser):
            try:
                browser.switch_to_frame(frame_reference)
            except NoSuchFrameException:
                return False
            else:
                me.LOG("Succeeded to switch to IFRAME '"+frame_reference+"'")
                return True
        return callback


    # http://stackoverflow.com/questions/9823272/python-selenium-waiting-for-frame-element-lookups
    #============================================================================
    def switchToIframe(me,iframeName):
        me.LOG("Try to switch to IFRAME '"+iframeName+"'")
        WebDriverWait(me.DRIVER, timeout=180).until(me.frame_available_cb(iframeName))

    #===========================================
    def moveMouseOverElement(me,sElementVal):
        sElementName = me.getVarAsStr(sElementVal)
        me.LOG("Try to move mouse over element '"+sElementName+"' = '"+sElementVal+"'" )
        try:
            if "_xpath" in sElementName:
                element = me.DRIVER.find_element_by_xpath(sElementVal)
                hov = ActionChains(me.DRIVER).move_to_element(element)
                hov.perform()
            elif "_name" in sElementName:
                element = me.DRIVER.find_element_by_name(sElementVal)
                hov = ActionChains(me.DRIVER).move_to_element(element)
                hov.perform()
            elif "_id" in sElementName:
                element = me.DRIVER.find_element_by_id(sElementVal).click()
                hov = ActionChains(me.DRIVER).move_to_element(element)
                hov.perform()
            elif "_css" in sElementName:
                element = me.DRIVER.find_element_by_css_selector(sElementVal).click()
                hov = ActionChains(me.DRIVER).move_to_element(element)
                hov.perform()
            elif "_text" in sElementName:
                element = me.DRIVER.find_element_by_link_text(sElementVal).click()
                hov = ActionChains(me.DRIVER).move_to_element(element)
                hov.perform()
            else:
                me.LOG("element name '"+sElementName + "' does not contain proper postfix to indicate element type")
                me.setError("element name error") # shall terminate script
                me.saveNamedScreenshot("MouseMoveDone")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("mouse move", errorText)
    #===========================================
    def Sleep(me,nSec):
    #===========================================
        if me.bExecutionStoppingStarted == True:
            return
        me.LOG("Sleep "+str(nSec)+" seconds")
        time.sleep(nSec)

    #===========================================
    def selectOption(me,sElementId,sOption):
         try:
            #sElementName = me.getVarAsStr(sElementId)
            #sOptionName = me.getVarAsStr(sOption)
            me.LOG("Try click element '"+sElementId+"' = '"+sOption+"'" )
            me.DRIVER.find_element_by_xpath("//select[@id='"+sElementId+"']/option[text()='"+sOption+"']").click()
            me.LOG("click succeeded")
         except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("element click: ", errorText)
    #================================
    def closeSuccessDialog(me,sButton):
        me.LOG("trying to locate ui-dialog success popup")
        # handles "sometimes" hidden success popup dialog
        #parent_h = me.DRIVER.current_window_handle

        element = None
        cnt = ""
        #button_path = '//span[contains(text(), "Close")]'
        #button_path = '//button[\@type='button'])[2]'
        button_name = me.getVarAsStr(sButton)

        try:
            # try to find the success dialog and press ok
            for x in range(1, 3):
                element = me.DRIVER.find_element_by_xpath(sButton)
                time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
                cnt=str(x)
                if element.is_displayed():
                    me.LOG("found element "+button_name+" count: "+cnt)
                    me.DRIVER.find_element_by_xpath(sButton).click()
                    return True
                else:
                    me.LOG("success dialog not found, trying to swith to alert, count: "+cnt)
                    #handles = me.DRIVER.window_handles
                    #me.LOG('handles: '+str(handles))
                    #handles.remove(parent_h)
                    #me.LOG('handles: '+str(handles))
                    #me.DRIVER.switch_to_window(handles.pop())
                    me.DRIVER.switch_to_alert()
                    element = me.DRIVER.find_element_by_xpath(sButton)
                    if element.is_displayed():
                        me.LOG("found element "+button_name+" count: "+cnt)
                        me.DRIVER.find_element_by_xpath(sButton).click()
                        #me.DRIVER.switch_to_window(parent_h)
                        return True
                    else:
                        me.LOG("warning: element "+button_name+" not found, proceeding anyway")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("element click: ", errorText)

    #=======================================
    def clickAndWaitFor(me, sElementVal, sWaitText=""):
    #=======================================
        if me.bExecutionStoppingStarted == True:
            me.LOG("clickAndWaitFor() interrupted, because stopping has started")
            #return
        sElementName=""
        nTime=0;
        try:
            sElementName = me.getVarAsStr(sElementVal)
            me.LOG("Try click element '"+sElementName+"' = '"+sElementVal+"'" )
            if "_xpath" in sElementName:
                me.DRIVER.find_element_by_xpath(sElementVal).click()

                #  driver.find_element_by_xpath(sElementVal).click()
            elif "_name" in sElementName:
                me.DRIVER.find_element_by_name(sElementVal).click()

                #  driver.find_element_by_name(sElementVal).click()
            elif "_id" in sElementName:
                me.DRIVER.find_element_by_id(sElementVal).click()

                #  driver.find_element_by_id(sElementVal).click()
            elif "_text" in sElementName:
                me.DRIVER.find_element_by_link_text(sElementVal).click()

                #  driver.find_element_by_id(sElementVal).click()
            elif "_css" in sElementName:
                me.DRIVER.find_element_by_css_selector(sElementVal).click()

            elif "_class" in sElementName:
                me.DRIVER.find_element_by_class_name(sElementVal).click()

                #  driver.find_element_by_id(sElementVal).click()
            else:
                me.LOG("element name '"+sElementName + "' does not contain proper postfix to indicate element type")
                me.setError("element name error") # shall terminate script
                me.saveNamedScreenshot("ElementClickDone")
            if sWaitText != "":
                nTime = me.waitForText(sWaitText)
                sTime = str(nTime)
                if nTime < me.nTEXT_WAIT_MAX_SECONDS:
                    me.LOG("element click succeeded: text '"+sWaitText+ "' detected after "+sTime+" seconds")
                else:
                    me.LOG("element '"+sElementName+"': text '"+sWaitText+ "' NOT detected after "+sTime+" seconds")
                    me.setError("element not detected") # shall terminate script '''
            else:
                me.LOG("click succeeded")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("element click: ", errorText)
        #    return nTime
        #===========================================================================================================



    #=======================================
    def doubleClickAndWaitFor(me, sElementVal, sWaitText=""):
    #=======================================
        if me.bExecutionStoppingStarted == True:
            me.LOG("doubleClickAndWaitFor() interrupted, because stopping has started")
            #return
        sElementName=""
        nTime=0;

        try:
            sElementName = me.getVarAsStr(sElementVal)
            me.LOG("Try doubleclick element '"+sElementName+"' = '"+sElementVal+"'" )
            if "_xpath" in sElementName:

                me.DRIVER.find_element_by_xpath(sElementVal).click()
                me.DRIVER.find_element_by_xpath(sElementVal).click()
                me.DRIVER.find_element_by_xpath(sElementVal).click()
                #  driver.find_element_by_xpath(sElementVal).click()
            elif "_name" in sElementName:
                me.DRIVER.find_element_by_name(sElementVal).click()
                me.DRIVER.find_element_by_name(sElementVal).click()

                #  driver.find_element_by_name(sElementVal).click()
            elif "_id" in sElementName:
                me.DRIVER.find_element_by_id(sElementVal).click()
                me.DRIVER.find_element_by_id(sElementVal).click()
                #  driver.find_element_by_id(sElementVal).click()
            elif "_text" in sElementName:
                me.DRIVER.find_element_by_link_text(sElementVal).click()
                me.DRIVER.find_element_by_link_text(sElementVal).click()

                #  driver.find_element_by_id(sElementV).click()
            elif "_css" in sElementName:
                me.DRIVER.find_element_by_css_selector(sElementVal).click()
                me.DRIVER.find_element_by_css_selector(sElementVal).click()

                #  driver.find_element_by_id(sElementVal).click()
            else:
                me.LOG("element name '"+sElementName + "' does not contain proper postfix to indicate element type")
                me.setError("element name error") # shall terminate script
                me.saveNamedScreenshot("ElementDoubleclickDone")
            if sWaitText != "":
                nTime = me.waitForText(sWaitText)
                sTime = str(nTime)
                if nTime < me.nTEXT_WAIT_MAX_SECONDS:
                    me.LOG("element doubleclick succeeded: text '"+sWaitText+ "' detected after "+sTime+" seconds")
                else:
                    me.LOG("element '"+sElementName+"': text '"+sWaitText+ "' NOT detected after "+sTime+" seconds")
                    me.setError("element not detected") # shall terminate script '''
            else:
                me.LOG("doubleclick succeeded")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("element doubleclick: ", errorText)
        #    return nTime

    #==========================
    def writeWithJs(me, sElementVal, sWriteText):

        if me.bExecutionStoppingStarted == True:
            return

        try:
            me.LOG("trying execute_script(): write '"+  sWriteText+"' to element id '"+sElementVal+"'")
            me.DRIVER.execute_script("document.getElementById('"+sElementVal+"').value='"+sWriteText+"'")
            me.LOG("execute_script() succeeded")

            #time.sleep(1)
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            print "error '" + errorText + "' when writing text to element id "+sElementVal

    #==========================
    def clickWithJs(me, sElementVal):

        if me.bExecutionStoppingStarted == True:
            return
        try:
            me.LOG("execute_script() to element id '"+sElementVal+"'")
            me.DRIVER.execute_script("document.getElementByXpath('"+sElementVal+"').click()")
            #time.sleep(1)
            me.LOG("excecute_script() succeeded")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            wholeErrorText = "error '" + errorText + "' when clicking to element id "+sElementVal
            me.LOG(wholeErrorText)
            print wholeErrorText

    #=======================================
    def writeAndWaitFor(me, sElementVal, sWriteText, sWaitText=""):
    #=======================================
        # global driver
        sElementName=""

        if me.bExecutionStoppingStarted == True:
            me.LOG("doubleClickAndWaitFor() interrupted, because stopping has started")
            return

        try:
            sElementName = me.getVarAsStr(sElementVal)
            me.LOG("try write '"+  sWriteText+"' to element '"+sElementName+"' = '"+sElementVal+"'" )
            if "_xpath" in sElementName:
                me.DRIVER.find_element_by_xpath(sElementVal).clear()
                me.DRIVER.find_element_by_xpath(sElementVal).send_keys(sWriteText)

            elif "_name" in sElementName:
                me.DRIVER.find_element_by_name(sElementVal).clear()
                me.DRIVER.find_element_by_name(sElementVal).send_keys(sWriteText)

            elif "_id" in sElementName:
                me.DRIVER.find_element_by_id(sElementVal).clear()
                me.DRIVER.find_element_by_id(sElementVal).send_keys(sWriteText)
            elif "_text" in sElementName:
                me.DRIVER.find_element_by_link_text(sElementVal).clear()
                me.DRIVER.find_element_by_link_text(sElementVal).send_keys(sWriteText)
            elif "_css" in sElementName:
                me.DRIVER.find_element_by_css_selector(sElementVal).clear()
                me.DRIVER.find_element_by_css_selector(sElementVal).send_keys(sWriteText)
            else:
                me.LOG("element name '"+sElementName + "' does not contain proper postfix to indicate element type")
                me.setError("element name error") # shall terminate script
                me.saveNamedScreenshot("ElementWriteDone")
            if sWaitText != "":
                nTime = me.waitForText(sWaitText)
                sTime = str(nTime)
                if nTime < me.nTEXT_WAIT_MAX_SECONDS:
                    me.LOG("element write succeeded: text '"+sWaitText+ "' detected after "+sTime+" seconds")
                else:
                    me.LOG("element '"+sElementName+"': text '"+sWaitText+ "' NOT detected after "+sTime+" seconds")
                    me.setError("element not detected") # shall terminate script
            else:
                me.LOG("element write succeeded")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("element write: ", errorText)

        #    return nTime



    #=============================================================
    def getVarAsStr(me, variable):
    #=============================================================
        # me.LOG("try get variable of value'"+str(variable)+"'")
        try:
            for key in me.dCALLER_GLOBALS:
                val =  me.dCALLER_GLOBALS[key]
                if val == variable:
                  ##  me.LOG("variable '"+str(key)+"' contains value '"+str(val)+"'")
                    return key
            me.LOG("variable '"+str(key)+"' contains no value")
            return ""
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.stopExecution("global variables dictionary usage failed: ", errorText)



    #=====================================================
    def waitForText(me, searchText):

        #me.LOG("start wait for text '"+searchText+"' (max steps count ="+")
        fSecs=0.0
        nSteps=0
        nStepsMax = me.nTEXT_WAIT_LOOP_CNT_MAX
        sStepsMax = str(nStepsMax)
        sSleepSecs = str(me.fTEXT_WAIT_CHECK_SECONDS)
        me.LOG("start wait for text '"+searchText+"' (max steps count = "+sStepsMax+", sleep secs = "+sSleepSecs+")")

        for nSteps in range(1,nStepsMax):  # changed from 3000 due to fails
            # me.LOG("nSteps = "+str(nSteps))
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            pageSourceRaw = me.DRIVER.page_source
            pageSource = pageSourceRaw.encode('utf-8')
            if searchText.lower() in pageSource.lower():   # case insensitive comparison edited
                fSecs = float(nSteps *  me.fTEXT_WAIT_CHECK_SECONDS)
                #me.LOG("loops: "+str(nSteps))
                me.LOG("text wait succeeded")
                return fSecs
            else:
                a=1 # do nothing

        me.setError("text wait failed")
    #=====================================================
    def waitForTextToDisappear(me, searchText):
        me.LOG("wait for possible text '"+searchText+"' to disappear")
        fSecs=0
        nSteps=0
        nStepsMax =  me.nTEXT_WAIT_LOOP_CNT_MAX
        for nSteps in range(1,nStepsMax):
            time.sleep(me.fTEXT_WAIT_CHECK_SECONDS)
            pageSourceRaw = me.DRIVER.page_source
            pageSource = pageSourceRaw.encode('utf-8')
            if searchText.lower() in pageSource.lower(): # case insensitive to increase robustness
                a=1 # do nothing
            else:
                #fSecs = float(nSteps *  me.fTEXT_WAIT_CHECK_SECONDS)
                me.LOG("text not detected after "+str(fSecs)+ " seconds")
                return;
            fSecs = float(nSteps *  me.fTEXT_WAIT_CHECK_SECONDS)
        me.setError("text '"+searchText+"' on screen still after "+str(fSecs)+ " seconds")

    #=============================================================
    def saveNamedScreenshot(me, name):
    #=============================================================
        me.screenshotOrderNbr += 1
        sOrder = str(me.screenshotOrderNbr)

        if me.DRIVER != None:
            name = me.assureValidSymbolName(name)
       # screenshotFileFullWorkName = "./"+USE_CASE_NAME+"-LATEST-"+sOrder+'.'+name+'.png'
            fileName = sOrder+'.'+name+'-LATEST.png'
            screenshotFileFullWorkName =  me.SCREENSHOT_STORE_DIR + "/" + fileName

        if (me.bSTORE_SCREENSHOTS == 1):
            me.LOG("save screenshot '"+screenshotFileFullWorkName+"'")
            me.DRIVER.get_screenshot_as_file(screenshotFileFullWorkName)
        else:
            me.LOG("screenshot '"+screenshotFileFullWorkName+"' is NOT saved")

        me.traceFileNamesList.append(screenshotFileFullWorkName)

    #=============================================================
    def   storeTraceFilesWithUniqueNames(me,comment):   # for error case usage
    #=============================================================
        me.LOG("================ store screenshots: "+comment+" (object="+str(me.OBJ_ID)+" ===========================")

    ###time.sleep(3)
        nowTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   # LOG("start to store screenshots and log files")

        fullLogLame = me.traceFileNamesList.pop(0)
        try:
            for fullWorkName in me.traceFileNamesList:
                workPathPart, workFilePart  = os.path.split(fullWorkName)
                storeFilePart = workFilePart.replace("LATEST", nowTime)
                fullStoreName =  me.SCREENSHOT_STORE_DIR+"/"+ storeFilePart
                if (me.bSTORE_SCREENSHOTS == 1):
                    # me.LOG("copy file '"+fullWorkName+"' to '"+fullStoreName+"'")
                    me.LOG("store file '"+fullStoreName+"'")
                    shutil.copyfile(fullWorkName, fullStoreName)
                else:
                    me.LOG("file '"+fullWorkName+"' is NOT strored to '"+fullStoreName+"'")
            workPathPart, workFilePart  = os.path.split(fullLogLame)
            storeFilePart = workFilePart.replace("LATEST", nowTime)
            fullStoreName =  me.SCREENSHOT_STORE_DIR+"/"+ storeFilePart
            if (me.bSTORE_SCREENSHOTS == 1):
                shutil.copyfile(fullLogLame, fullStoreName)
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            print "error '" + errorText + "' when storing files"
        # os.remove(defaultName)
    #==============================
    def cleanRemainings(me):
    #==============================
        sFileSelection =  me.SCREENSHOT_STORE_DIR+'/*LATEST*.*'
        me.LOG("============ start removing files '"+sFileSelection+"'")
        fileName=""
        try:
            for fileName in glob.glob(sFileSelection):
                   #  if os.filePath.isfile(fileName):
                if (me.bSTORE_SCREENSHOTS == 1):
                    me.LOG("removes file '"+fileName+"'")
                    os.remove(fileName)
                else:
                    me.LOG("file '"+fileName+"' is NOT removed")
            me.LOG("=========================================================")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.LOG("error '" + errorText + "' when removing files")


    #==============================
    def isAlreadyStopping(me):
    #==============================
        return me.bExecutionStoppingStarted
    #==============================
    def setStoppingState(me, status, comment):
    #==============================
        me.LOG("stopping state set to '"+str(status)+"' due to '"+comment+"'")
        me.bExecutionStoppingStarted = status;

    #==============================
    def assureValidSymbolName(me, sText):
    #==============================
        sName = re.sub(r'\W','_',sText)
        ### me.LOG("'"+sText+"' was converted to '"+sName+"'")
        return sName
    #==============================
    def handleFatalException(me, comment):
    #==============================
        exctype, value = sys.exc_info()[:2]
        errorText = str(exctype)+" "+str(value)
        me.stopExecution(comment, errorText)
    #=============================
    def testPassed(me):
    #============================
        if me.isAlreadyStopping() == False:
            me.setStoppingState(True,"test passed")
            me.LOG("available = 1")
            me.LOG("test passed successfully")
            print "available 1"
            print me.startTime
            me.DRIVER.quit()
            sys.exit(0)
    #=============================
    def testEnd(me,availability):
    #========================
        if me.isAlreadyStopping() == False:
            me.setStoppingState(True,"test ended")
            sAvail = str(availablity)
            sResult = "avalable "+sAvail
            me.LOG(sResult)
            me.LOG("start time = " + str(me.startTime))
            me.LOG("===== use case ended =======")
            print sResult
            print me.startTime
    #=============================
    def TERMINATE(me):
    #============================
        text = "test terminated for debugging purposes"
        if me.isAlreadyStopping() == False:
            me.setStoppingState(True, text)
            me.LOG(text)
            print text
            me.DRIVER.quit()
            sys.exit(0)

    #=======================================
    def getNextStepNameByStepName(me, sStepName):
    #=======================================
        me.LOG("try create next step name by current step name  '"+sStepName+"'")
        NO_NEXT_STEP_NAME = ""
        try:
            p = re.compile('(\w+)(\d+)')
            matchObj = p.match(sStepName)
            if matchObj:
                sStepNamePart = matchObj.group(1)
                sStepNbrPart = str(matchObj.group(2))
                nStepNbrPart = int(sStepNbrPart)
                me.LOG("step name parts are '"+sStepNamePart+"' and '"+sStepNbrPart+"'")
                try:
                    nStepNbr = int (nStepNbrPart)
                    nNextStepNbr = nStepNbr+1
                    sNextStepName = str(sStepNamePart)+str(nNextStepNbr)
                    me.LOG("next step will be '"+sNextStepName+"'")
                    return sNextStepName
                except:
                    me.LOG("step name '"+sStepName+"'does not contain integer end")
                    return NO_NEXT_STEP_NAME
            else:
                me.LOG("no string+integer -match in '"+sStepName+"'")
                return NO_NEXT_STEP_NAME
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype)+" "+str(value)
            me.LOG("regex match attempt:"+ errorText)
            return NO_NEXT_STEP_NAME


#===============================================================
    def tidyRawErrorText(me, sErrorText):
#===============================================================
        sErrorText.replace("Stacktrace","")
        sErrorText.replace("selenium","")
        sErrorText.replace("common","")
        sErrorText.replace("exceptions","")
        sErrorText.replace("Message","")
        sErrorText.replace("class","")
        sErrorText.replace("u\'","")
        sErrorText.replace("NoSuchElementException", "given web page element is not found")
        sErrorText.replace("ElementExceptionNotVisibleException", "given web page element is not visible")
        sErrorText.replace("Element is not currently visible and may not be interacted with", "")
        sErrorText.replace("IncompleteRead", "")
        sErrorText.replace("BadStatusLine", "Bad Status Line")
        sErrorText.replace("TimeoutException", "Selenium Timeout")
        return (sErrorText)
