// @CacheScriptContent(true)
// @ExecutionModes({ON_SINGLE_NODE})
// note: all 'import' statements removed here to fix 'unicode' error caused by unconnected internet
//*************************************************************************************
//	LEGEND: outputs svn log of file name at clipboard
//-------------------------------------------------------------------------------------
//import javax.swing.*
//import org.freeplane.core.ui.components.UITools
import org.freeplane.core.util.LogUtils
import javax.swing.JEditorPane
import java.awt.KeyboardFocusManager 	
//*************************************************************************************
sFocusScriptPath = new File(getClass().protectionDomain.codeSource.location.path).parent
sTHESE_DRIVE_LETTER = sFocusScriptPath.take(1)  // !: groovy way to get drive letter
sPYTHON_EXE_PATH = sTHESE_DRIVE_LETTER+":/HUT/Portable_Python_3.2.0.1/App/"
sPYTHON_SCRIPTS_PATH = sTHESE_DRIVE_LETTER+":/KIT/Python/APPS/"
sDATA_EXCHANGE_FILES_PATH =  sTHESE_DRIVE_LETTER+":/KIT/TRAY/"

sNoteContentsFileFullName =  sDATA_EXCHANGE_FILES_PATH+"NoteContentsAsHtml.txt"
JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
sMapFullName = node.map.file // !: gives focus map full name
LogUtils.info("========== BEGIN InterpretNoteDownToCursorLine.groovy ================================")
LogUtils.info("THIS map file full name = '"+sMapFullName+"'")

sFocusScriptPath = new File(getClass().protectionDomain.codeSource.location.path).parent  // !: gives focus file path

// !: using own library by "evaluate(....)", consumes several seconds, so avoid using such !!!
//=====================================================================================
sMARK = "CursorPos"

//==================================================================================
// !: fast sequence (no library by 'execute', no clipboard , no savings, no loopings etc.)
//----------------------------------------------------------------------------------
sUnmarkedNoteTextAsHtml  = oFocusEditorPane.text // saving the unmarked HTML text
oFocusEditorPane.getDocument().insertString(oFocusEditorPane.getCaretPosition(),sMARK, null)  // marking the HTML text
sMarkedNoteTextAsHtml = oFocusEditorPane.text   // capturing the marked HTML text for further usage
oFocusEditorPane.text = sUnmarkedNoteTextAsHtml  // restoring the unmarked HTML text
//----------------------------------------------------------------------------------

//sPythonExe = sPYTHON_EXE_PATH+"python"
sEMPTY = ""
sPythonExe = "python"  // works OK, when uses C: -drive installed Python
// TODO: add check, if C: -installed python is not found, then uses python at USB


sPythonScript = "InterpretHtmlDownToMarkedLine.py"
sPythonScriptFullName = sPYTHON_SCRIPTS_PATH+sPythonScript  //  !: path contains spaces, so surrounding '"' -chars are needed !!!

LogUtils.info ("===== COMMAND = "+sPythonExe)
LogUtils.info ("===== SCRIPT NAME = "+sPythonScriptFullName)
LogUtils.info ("===== DRIVE LETTER = "+sTHESE_DRIVE_LETTER)
LogUtils.info ("===== MARK = "+sMARK)
LogUtils.info ("===== MAP NAME = "+sMapFullName)
LogUtils.info ("===== NOTE FILE = "+sNoteContentsFileFullName)   // TODO: add output to file because some cut-offs when delivered as call parameter


new File(sNoteContentsFileFullName).delete() 
oNoteContentsFile = new File(sNoteContentsFileFullName)
oNoteContentsFile << sMarkedNoteTextAsHtml

//oNoteContentsFile.close()

asCommand = "$sPythonExe $sPythonScriptFullName $sTHESE_DRIVE_LETTER $sMARK $sMapFullName $sNoteContentsFileFullName"
LogUtils.info(asCommand)
def proc = asCommand.execute()

proc.waitFor()
LogUtils.info("This is output: " + proc?.in?.text)
LogUtils.info("This is output: " + proc?.err?.text)  // !: returns possible python error message. Seems very useful

LogUtils.info("========== END InterpretNoteDownToCursorLine.groovy ================================")
//proc.waitFor()  



