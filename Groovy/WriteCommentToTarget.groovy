// @CacheScriptContent(true)
// @ExecutionModes({ON_SINGLE_NODE})
// https://docs.oracle.com/javase/tutorial/uiswing/examples/layout/index.html#FlowLayoutDemo
//*************************************************************************************
//-------------------------------------------------------------------------------------
import org.freeplane.core.ui.components.UITools;
import java.awt.datatransfer.*
import groovy.json.JsonSlurper
import groovy.swing.SwingBuilder
import java.awt.FlowLayout as FL
import javax.swing.JOptionPane
import javax.swing.JEditorPane 	
import org.freeplane.core.resources.ResourceController
import org.freeplane.core.util.LogUtils;
import org.freeplane.features.mode.Controller
import org.freeplane.features.mode.mindmapmode.MModeController
import org.freeplane.features.url.mindmapmode.MFileManager
import org.freeplane.plugin.script.proxy.Proxy
import java.awt.*
import java.awt.BorderLayout
import java.awt.AWTPermission
import java.text.DateFormat
import java.text.SimpleDateFormat

// purpose: opens "editor dialog" by Freeplane function key and saves given text to target(s)
// http://alvinalexander.com/java/jwarehouse/groovy/src/examples/groovy/swing/SwingDemo.groovy.shtml
// https://docs.oracle.com/javase/tutorial/uiswing/components/textarea.html
// http://stackoverflow.com/questions/19196454/how-to-fit-textarea-width-to-parent-in-groovy



oDatePattern 	= new java.text.SimpleDateFormat("yyyy-MM-dd")  	// !: creates date-time pattern
oDatePatternTiny 	= new java.text.SimpleDateFormat("yyMMdd")
oTimePatternTiny 	= new java.text.SimpleDateFormat("kkmmss")

// sDateForTopicHeading = oDatePattern.format(new Date())

sLINE_JOINER = "__NL__"  // for building single line to be delivered as parameter
sOTL_TOPIC_JOURNAL_SECTION_UPDATE_IND = "OTL_FOCUS_TOPIC_JOURNAL_SECTION_UPDATE_REQ" // this string must be identical to that checked in Clip "OnClipboardChange"

// sOtlTopicHeadingName = sDateForTopicHeading


def sTimestamp

sFocusScriptPath = new File(getClass().protectionDomain.codeSource.location.path).parent
sTHESE_DRIVE_LETTER = sFocusScriptPath.take(1)  // !: groovy way to get drive letter
sTHESE_DRIVE_PYTHON_PATH = sTHESE_DRIVE_LETTER+":/SET/WinPython-32bit-3.4.4.2/python-3.4.4/"
// - for such cases where Python is NOT installed on PC (C-drive)
sMapPathName = ""
sMapFullName = node.map.file // !: gives focus map full name
// ... getting path name of focus map ...
// NOTE: OTL file updating fails, if focus map is some sketch which is not yet saved to <LOT>
//	-	such map does not have a name to be used as "baseline"
oRegex = (sMapFullName=~ /(.*\\).*/);  // path name capturing
if (oRegex.matches()) {
	sMapPathName = oRegex[0][1]  // = [<first match>][<second group within match>] (first group contains whole line)
}



sPythonInstallationCheckCmd = "python --version"  // !: displays, if Python is installed (in C) (otherwise will use Python on USB)

def proc = sPythonInstallationCheckCmd.execute()
sResp = proc.text
LogUtils.info ("response to 'python --version' -command "+sResp)
if (sResp =~ "Python\\s+\\d.*\\d.*") { // tries to match eg. "Python 3.5.1"
	sPYTHON_EXE_PATH = ""   // uses 
	LogUtils.info ("'"+sResp+"' found installed, so '"+sTHESE_DRIVE_PYTHON_PATH+"' -version is NOT used")
} else {
	sPYTHON_EXE_PATH = sTHESE_DRIVE_PYTHON_PATH 	
	LogUtils.info ("Python seems NOT installed, so "+sTHESE_DRIVE_PYTHON_PATH+" -version is used" )
}
sPythonExeCmd = sPYTHON_EXE_PATH+"python"

LogUtils.info ("focus map path = '$sMapPathName'")
sTargetOtlFilesPath = sMapPathName+"../OTL"   // takes JOURNAL/INDEX file names relative to FOCUS
LogUtils.info ("sTargetOtlFilesPath = '$sTargetOtlFilesPath'")
sJOURNAL_FILE_PLAIN_NAME = "JOURNAL"
sINDEX_FILE_PLAIN_NAME = "INDEX"
sJOURNAL_FILE_FULL_NAME = sTargetOtlFilesPath+"/" + sJOURNAL_FILE_PLAIN_NAME    // !: Notetab Outline file (updated via Freeplane !!!)
sINDEX_FILE_FULL_NAME = sTargetOtlFilesPath+"/" + sINDEX_FILE_PLAIN_NAME     // !: Notetab Outline file (updated via Freeplane !!!)
// TBD: OTL file names to some configuration file (also for Notetab usage)



sPythonExeCmd = sPYTHON_EXE_PATH+"python"
sPYTHON_SCRIPTS_PATH = sTHESE_DRIVE_LETTER+":/KIT/Python/APPS/"
sDATA_EXCHANGE_FILES_PATH =  sTHESE_DRIVE_LETTER+":/KIT/TRAY/"
sLOG_FILES_PATH =  sTHESE_DRIVE_LETTER+":/KIT/LOG/"

sTraceFileFullName = sLOG_FILES_PATH+"PythonTrace.txt"
sAUTOGEN_BAT_FULL_NAME = sDATA_EXCHANGE_FILES_PATH+"Autogen.bat" // for troubleshooting purposes

sTRAY_FILE_FULL_NAME = sDATA_EXCHANGE_FILES_PATH+"ScriptDataExchange.txt" // for eg. Notetab Clip input

sHTML_LINE_START_tag 	= "<p>"
sHTML_LINE_END_tag 		= "</p>"
sHTML_BODY_START_tag 	= "<body>"
sHTML_BODY_END_tag 		= "</body>"

sHTML_LIST_ITEM_START_tag = "<li>"
sHTML_LIST_ITEM_END_tag = "</li>"

//sCAST_SECTION_START_MATCH_REGEX_str = /^.*(CAST).*$/   // just for testing
// sCAST_SECTION_START_MATCH_REGEX_str = "CAST:.*<ul>"  // tries to match to bulleted list start just before specific keyword
sBULLETED_LIST_START_CATCH_REGEX_str = /.*(<ul>).*/   // matches to first bulleted list within focus node note
sBULLETED_LIST_START_TAG_str = "<ul>" 
/*   example:  
	<p>
      <u>CAST:</u>  // "<u>" means "underlined"
    </p>
    <ul>  // @HTML: "<ul>" means "unordered list", produces bullets   
      <li>  // @HTML: "<li>" means "list item"  (bullets or sequence numbers are defined at parent level !)
        this is text, which
      </li>
      <li>
        and this
      </li>
    </ul> 
*/
 
//---------------------------------------------------------------------------------------------
def submitTextAndIndication(oComment) {
//---------------------------------------------------------------------------------------------
	Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
	sComment = oComment.getText()
	fhOut = new File(sTRAY_FILE_FULL_NAME)
	// Writing to the files with the write method:
	fhOut.write sComment+"\n"
	clipboard.setContents(new StringSelection(sOTL_TOPIC_JOURNAL_SECTION_UPDATE_IND), null)  
	// clipboard change -event launches Notetab Clip call to a python script
	oComment.setText("")  // clears the note widget

}
//------------------------------------
def addTextToJournalOtlFileTopic (sComment, sTodayTopicHeadingName, sTimeStamp) {
//------------------------------------
	sPYTHON_SCRIPT_PLAIN_NAME = "AddTextToFirstOtlTopicEnd.py"
	sCommentAsSingleLine = ""
	//sComment = oComment.getText()
	sCommentCleaned = sComment.replace("\"", "")
	sPythonScriptFullName = sPYTHON_SCRIPTS_PATH+"/"+sPYTHON_SCRIPT_PLAIN_NAME
	sInFile = sJOURNAL_FILE_FULL_NAME
	sOutFile = sJOURNAL_FILE_FULL_NAME
	LogUtils.info("get clipboard handle")
	Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
	//sClipboardSaved = clipboard.getContents(null).getTransferData(DataFlavor.stringFlavor)  // saved before it is replaced with control tag 
	LogUtils.info("clear clipboard")
	clipboard.setContents(new StringSelection(""), null)
	sTimedDelim = "--------------------------------------------- "+sTimeStamp
	
	sCommentAsSingleLine = sCommentCleaned.replace("\n", sLINE_JOINER)
	LogUtils.info("create autogen bat")
	fhAutogenBat = new File(sAUTOGEN_BAT_FULL_NAME) 
	
	String[] asLines = sComment.split("\n")
	LogUtils.info("------------------------------------------------------------------")
	for (String sLine : asLines) {
		// System.out.println(item)
		//LogUtils.info(sLine)
	}
	LogUtils.info("sPythonExeCmd: $sPythonExeCmd")
	LogUtils.info("sPythonScriptFullName: $sPythonScriptFullName")
	LogUtils.info("sInFile: $sInFile")
	LogUtils.info("sOutFile: $sOutFile")
	LogUtils.info("sTodayTopicHeadingName: $sTodayTopicHeadingName")
	LogUtils.info("sTimedDelim: $sTimedDelim")
	LogUtils.info("sComment: $sComment")
	LogUtils.info("sTraceFileFullName: $sTraceFileFullName")
	
	sCommand = "$sPythonExeCmd $sPythonScriptFullName $sInFile $sOutFile \"$sTodayTopicHeadingName\" \"$sTimedDelim\" \"$sCommentAsSingleLine\" $sPythonScriptFullName"
	LogUtils.info("Python command: "+sCommand)
	fhAutogenBat.write("")
	fhAutogenBat << sCommand
	fhAutogenBat << "\nPAUSE"
	
	// !: SEE: http://www.joergm.com/2010/09/executing-shell-commands-in-groovy/
	def proc = sCommand.execute()
	proc.waitFor()
	LogUtils.info("Possible error: " + proc?.err?.text)  // !: returns possible python error message.

	clipboard.setContents(new StringSelection("CORE_OTL_FILES_UPDATED"), null)   // to launch Notetab Clip "OnClipboardChange" for OTL files reloading
	//LogUtils.info("return original clipboard contents")
	//sleep(1000)
	//clipboard.setContents(new StringSelection(sClipboardSaved), null)  // saved (="real") contents is restored and can be used for possible pastings
}

//------------------------------------
def addTextToIndexOtlFileTopic (sComment, sOtlTopicHeadingName, sDateTimeStamp) {
//------------------------------------
	sPYTHON_SCRIPT_PLAIN_NAME = "AddTextToAlphabetOtlTopicEnd.py"
	sCommentAsSingleLine = ""
	//sComment = oComment.getText()
	sCommentCleaned = sComment.replace("\"", "")
	sPythonScriptFullName = sPYTHON_SCRIPTS_PATH+"/"+sPYTHON_SCRIPT_PLAIN_NAME
	sInFile = sINDEX_FILE_FULL_NAME
	sOutFile = sINDEX_FILE_FULL_NAME
	sCommentAsSingleLine = sCommentCleaned.replace("\n", sLINE_JOINER)
	fhAutogenBat = new File(sAUTOGEN_BAT_FULL_NAME) 
	
	LogUtils.info("sPythonExeCmd: $sPythonExeCmd")
	LogUtils.info("sPythonScriptFullName: $sPythonScriptFullName")
	LogUtils.info("sInFile: $sInFile")
	LogUtils.info("sOutFile: $sOutFile")
	LogUtils.info("sOtlTopicHeadingName: $sOtlTopicHeadingName")
	LogUtils.info("sDateTimeStamp: $sDateTimeStamp")
	LogUtils.info("sTraceFileFullName: $sTraceFileFullName")
	
	asCommand = "$sPythonExeCmd $sPythonScriptFullName $sInFile $sOutFile \"$sOtlTopicHeadingName\" \"$sDateTimeStamp\" \"$sCommentAsSingleLine\" $sPythonScriptFullName"
	LogUtils.info("Python command: "+asCommand)
	fhAutogenBat.write("")
	fhAutogenBat << asCommand
	fhAutogenBat << "\nPAUSE"
	def proc = asCommand.execute()
	proc.waitFor()
	LogUtils.info("Possible error: " + proc?.err?.text)  // !: returns possible python error message.
}

//------------------------------------
def addTextToFocusNodeNote (oComment) {
//------------------------------------
	sMapFullName = node.map.file // !: gives focus map full name
	sNodeLabel = node.getText()
	sNodeID = node.getId()
	
	sFAINT_FONT_PREFIX = "<font size=\"1\" color=\"#33cc00\">"
	sFONT_POSTFIX = "</font>  "
	oDateTimePattern 	= new java.text.SimpleDateFormat("yyMMdd-kkmmss")  	// creates date-time pattern
	sDateTime 			= oDateTimePattern.format(new Date())

	sDateTimeAsFaintHtml = sFAINT_FONT_PREFIX + "("+sDateTime +")"+ sFONT_POSTFIX+"&#160;"
	
	sDateForTopicHeading = oDatePattern.format(new Date())
	sTimeStampTiny = oTimePatternTiny.format(new Date())
	sDateStampTiny = oDatePatternTiny.format(new Date())
	// TBD: add code
	sMARK = "CursorPos"
	sCommentAsHtmlLine = ""
	sComment = oComment.getText()
	String[] asLines = sComment.split("\n")
	LogUtils.info("comment lines as ASCII:")
	sCommentAsHtmlListItem = sHTML_LIST_ITEM_START_tag + sComment + "       " + sDateTimeAsFaintHtml + sHTML_LIST_ITEM_END_tag
	LogUtils.info("sCommentAsHtmlListItem: '"+sCommentAsHtmlListItem+"'")
	for (String sLine : asLines) {
		// System.out.println(item)
		// TBD: each comment line conversion to html <p>...</p> -line
		LogUtils.info("comment line: '"+sLine+"'")
		sCommentAsHtmlLine = sCommentAsHtmlLine + sHTML_LINE_START_tag + sLine + sHTML_LINE_END_tag
	}

	// http://freeplane.sourceforge.net/doc/api/org/freeplane/plugin/script/proxy/Proxy.NodeRO.html#getNoteText--
	sNoteTextAsHtml = node.getNoteText() // !: gives existing HTML contents (as a single line !!!)
	sNoteTextAsAscii = node.note.plain  // returns single line
	LogUtils.info("sNoteTextAsHtml:"+sNoteTextAsHtml)
	//LogUtils.info("try catch by '"+sCAST_SECTION_START_CATCH_REGEX_str+"' from focus note text")
	// http://stackoverflow.com/questions/764387/groovy-syntax-for-regular-expression-matching
	
	sNoteTextAsHtml = sNoteTextAsHtml.replaceFirst(sBULLETED_LIST_START_TAG_str, sBULLETED_LIST_START_TAG_str+sCommentAsHtmlListItem)
	
	// if ((oMatcher = sNoteTextAsHtml =~  sCAST_SECTION_START_CATCH_REGEX_str)) {  // !: reguires DOUBLE parentheses !!! (WHY)
		// def sBulletedListStartAsHtml = oMatcher.group(1)          // works OK 
		// LogUtils.info("caught start pattern = $sBulletedListStartAsHtml")
		// sNoteTextAsHtml = sNoteTextAsHtml.replaceFirst(sBulletedListStartAsHtml, sBulletedListStartAsHtml+sCommentAsHtmlListItem)
	// } else {
		 // LogUtils.info("caught NOTHING")
	// }

	LogUtils.info("updated note text as HTML:'"+sNoteTextAsHtml+"'")

	LogUtils.info("sMapFullName: "+sMapFullName)
	LogUtils.info("sNodeID: "+sNodeID)
	LogUtils.info("sNodeLabel: "+sNodeLabel)
	//sMapFullName1 = sMapFullName
	sMapFullName1 = sMapFullName.getPath() //+sMapF ullName.getName()
	sMapFullName2 = sMapFullName1.replaceAll("\\\\","/")
	//sFramedComment = sMapFullName + " " + sNodeLabel + " @note updated: " + sComment
	sFramedComment = "[ freeplane:/%20/"+sMapFullName2 + "#" + sNodeID + "  (" + sNodeLabel+ ")\n" + sComment
	LogUtils.info("sFramedComment: "+sFramedComment)
	node.setNoteText(sNoteTextAsHtml) 
	addTextToJournalOtlFileTopic(sFramedComment, sDateForTopicHeading, sTimeStampTiny)
	oComment.setText("")
}
//------------------------------------
def clearComment (oComment, oTextField) {
//------------------------------------
	oComment.setText("")
	oTextField.setText("")
}
//-------------------------------------------------------------
def addTextToExternalFile(oComment, xKeywords, sTargetDir) {
//-------------------------------------------------------------
	// TBD: target "LOT" vs. "PIT" selection usage
	sDateForTopicHeading = oDatePattern.format(new Date())
	sTimeStampTiny = oTimePatternTiny.format(new Date())
	sDateStampTiny = oDatePatternTiny.format(new Date())
	
	sTargetTopic = xKeywords.text
	sAddText = oComment.getText()
	
	LogUtils.info("sTargetTopic = $sTargetTopic")
	LogUtils.info("sAddText = $sAddText")

	if (sTargetTopic == "") {
		addTextToJournalOtlFileTopic(sAddText, sDateForTopicHeading, sTimeStampTiny)
	} else {  // something shall always be written to JOURNAL file
		sLinkText = "["+sINDEX_FILE_PLAIN_NAME+"::"+sTargetTopic + "] @added"
		addTextToJournalOtlFileTopic(sLinkText, sDateForTopicHeading, sTimeStampTiny)
		addTextToIndexOtlFileTopic(sAddText, sTargetTopic, sDateStampTiny)
	}
	oComment.setText("")  // clears the note widget
}
// ==============================================================================================
def nFRAME_TO_RIGHT = 1000
def nFRAME_TO_DOWN = 500
def nFRAME_WIDTH = 300
def nFRAME_HEIGHT = 200
def nTEXT_FIELD_COLUMNS = 25

def BL = new BorderLayout()
def oTextArea  // 
def oScrollPane
def oBottomPanel
def oLotExternalFileButton
def oPitExternalFileButton
def oFocusNodeButton
def oOtlFocusTopicJournalSectionButton
def oClearCommentButton
def oCloseButton

// TODO: add prevention of creating new comment query if already exists (uses some lock file etc.)

def oSwing = new SwingBuilder()
//	-	http://code.wikia.com/wiki/Groovy.swing.SwingBuilder

oFrame = oSwing.frame(location:[nFRAME_TO_RIGHT, nFRAME_TO_DOWN], size:[nFRAME_WIDTH, nFRAME_HEIGHT]) {
	oScrollPane = scrollPane(constraints:BL.CENTER) {
		oTextArea = textArea()  // note: if this is missing, editing area stays GREY
			// http://stackoverflow.com/questions/28483107/groovy-swingbuilder-how-can-i-add-a-scrollpanel-to-my-frame
	}  
// TBD: add single-line editable pane below main pane: empty contents select "JOURNAL" file, any contents selects some "INDEX" file
//  ---> the only buttons shall be 'OK', 'Clear' and 'Close'
	oBottomPanel=panel(constraints:BL.SOUTH){
		vbox { // --> both following items are piled
			panel {
				oTextField = textField(columns: nTEXT_FIELD_COLUMNS, id: 'xTargetNavigationKeywords')	// TBF: how to set field height to a single line ?????
				// TBD: read topic names from INDEX file and suggest, when keying in letters
			} //... panel
			hbox {  // --> all following items are parallel
				oLotExternalFileButton	= button(action: action(name: 'LOT', mnemonic: 'O', closure: { addTextToExternalFile(oTextArea, xTargetNavigationKeywords,"LOT")})) // call to text handler
				oOtlFocusTopicJournalSectionButton		= button(action: action(name: 'SEC', mnemonic: 'O', closure: { submitTextAndIndication(oTextArea)}))
				oPitExternalFileButton	= button(action: action(name: 'PIT', mnemonic: 'O', closure: { addTextToExternalFile(oTextArea, xTargetNavigationKeywords,"LOT")})) // call to text handler
				//oFocusNodeButton		= button(action: action(name: 'Node', mnemonic: 'O', closure: { addTextToFocusNodeNote(oTextArea)}))
				oClearCommentButton 	= button(action: action(name: 'Clear', mnemonic: 'O', closure: {clearComment(oTextArea, oTextField)}))
				// oCloseButton 		= button(action: action(name: 'Close', mnemonic: 'C', closure: {dispose()}))
			} //... hbox
		}	//... vbox
	} //... panel...
}

// http://stackoverflow.com/questions/19225146/how-to-set-java-awt-awtpermission-in-policy-file
// https://www.cs.helsinki.fi/group/boi2016/doc/java/api/java/awt/AWTPermission.html
//AWTPermission("setWindowAlwaysOnTop")

oFrame.show()
oFrame.setAlwaysOnTop(true)  // !: ALL windows applications stay behind of this form

