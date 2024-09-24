// @CacheScriptContent(true)
// @ExecutionModes({ON_SINGLE_NODE})
//*************************************************************************************
import javax.swing.*
import org.freeplane.core.ui.components.UITools
import groovy.time.*
import java.util.Timer
import org.freeplane.core.util.HtmlUtils
import java.util.regex.Matcher
import java.util.regex.Pattern
import java.awt.KeyboardFocusManager 	// to access and manipulate the text of a node
import java.awt.datatransfer.*
import java.awt.Toolkit
import javax.swing.JEditorPane 			// to access and manipulate the text of a node
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import java.util.TimeZone
import java.lang.*
import groovy.swing.SwingBuilder
import org.freeplane.core.util.LogUtils
//===================================================================
// PURPOSE: creates external file by Clipboard contents and inserts hyperlink to to focus note cursor position
//  - prompts a query for hyperlink label and file name extension
//===================================================================

sFocusScriptPath = new File(getClass().protectionDomain.codeSource.location.path).parent
sTHESE_DRIVE_LETTER = sFocusScriptPath.take(1)  // !: groovy way to get drive letter

// sTHESE_DRIVE_PYTHON_PATH = sTHESE_DRIVE_LETTER+":/HUT/Portable_Python_3.2.0.1/App/"
sTHESE_DRIVE_PYTHON_PATH = sTHESE_DRIVE_LETTER+":/HUT/WinPython-32bit-3.4.4.2/python-3.4.4/"
// - for such cases where Python is NOT installed on PC (C-drive)

//===== defining which python to use ==============================================
// commented, because failed when using in Job ultrabook (Groovy error from 'python' command)
sPythonInstallationCheckCmd = "python --version"  // !: displays, if Python is installed (in C) (otherwise will use Python on USB)

def proc = sPythonInstallationCheckCmd.execute()
sResp = proc.text
LogUtils.info ("response to 'python --version' -command "+sResp)
if (sResp =~ "Python\\s+\\d.*\\d.*") { // tries to match eg. "Python 3.5.1"
	sPYTHON_EXE_PATH = ""   // uses 
	LogUtils.info ("'"+sResp+"' found installed, so '"+sTHESE_DRIVE_PYTHON_PATH+"' -version is NOT used")
} else {
	sPYTHON_EXE_PATH = sTHESE_DRIVE_LETTER+sTHESE_DRIVE_PYTHON_PATH 	
	LogUtils.info ("Python seems NOT installed, so "+sTHESE_DRIVE_PYTHON_PATH+" -version is used" )
}
// sPYTHON_EXE_PATH = sTHESE_DRIVE_PYTHON_PATH
sPythonExeCmd = sPYTHON_EXE_PATH+"python"

  // for installed Pythons: included in "path" environment variable
sPYTHON_SCRIPTS_PATH = sTHESE_DRIVE_LETTER+":/KIT/Python/APPS/"
sDATA_EXCHANGE_FILES_PATH =  sTHESE_DRIVE_LETTER+":/KIT/TRAY/"

sClipboardFileFullName =  sDATA_EXCHANGE_FILES_PATH+"ClipboardContentsByGroovy.txt"
sResponseFromCalledFileFullName =  sDATA_EXCHANGE_FILES_PATH+"ExternalFileNameByPython.txt"
cCRLF = System.getProperty("line.separator")  		// assures correct CR/LF usage
sEMPTY_HTML_LINE ="<p>"+cCRLF+"</p>"+cCRLF
// <a href="http://freeplane.sourceforge.net/doc/FP_Key_Mappings_Quick_Guide.pdf">This is link</a>
sHYPERLINK_HEADER = "<a href="
sHYPERLINK_FOOTER = "</a>"
sMARK = "CursorPos"
def JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
// -	note pane caught here, because input dialog will change the focus to 'button'!

sMapPathName = ""
sMapFullName = node.map.file // !: gives focus map full name
// ... getting path name of focus map ...
oRegex = (sMapFullName=~ /(.*\\).*/);  // path name capturing
if (oRegex.matches()) {
	sMapPathName = oRegex[0][1]  // = [<first match>][<second group within match>] (first group contains whole line)
}

LogUtils.info ("focus map path = '$sMapPathName'")

// LogUtils.info("Installed Python status: " + proc?.err?.text)

sPythonScript = "CreateUniqueNameTextFile.py"
sPythonScriptFullName = sPYTHON_SCRIPTS_PATH+sPythonScript

Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
def sCapturedText = clipboard.getContents(null).getTransferData(DataFlavor.stringFlavor) // !: gives clipboard contents

new File(sClipboardFileFullName).delete() 
oTmpFile = new File(sClipboardFileFullName)  // temporary file, which will finally be copied to a uniquely name external file
oTmpFile << sCapturedText
LogUtils.info ("temporary file name = '$sClipboardFileFullName'")

sFullURL = "NOT_INITIALIZED"   // !: shall be received from Python script
sHyperlinkLabel = "NOT_INITIALIZED" // !: TODO set equal to file name part

sHYPERLINK_BLOCK = sEMPTY_HTML_LINE+sHYPERLINK_HEADER+"_FULL_URL_TAG_"+">"+"_LABEL_TAG_"+sHYPERLINK_FOOTER+sEMPTY_HTML_LINE

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AskFileNameBodyAndExtension(oFocusEditorPane,sMapPathName)  // !: editor pane delivered down updater method
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//////////////////////////////// QUERY PROMPT //////////////////////////////////////////////////////////////////////////////
//------------------------------------
def submitFileNameParts(oSavedPane, xName, xExt, sTargetPath) {  // !: 'textField' id:s are some kind of structs, NOT just text contents 
//------------------------------------
	sEditedNamePart = xName.text 
	sEditedExt 		= xExt.text
	sSubdirName = sEditedExt  // external file subdir name is set same as the file extension (=just a simple way for classification)
	LogUtils.info ("temporary file name = '$sClipboardFileFullName'")
	LogUtils.info ("final file name/extension = '$sEditedNamePart'/'$sEditedExt'")
	LogUtils.info ("python exe full name = '$sPythonExeCmd'")
	
	
	asCommand = "$sPythonExeCmd $sPythonScriptFullName $sTHESE_DRIVE_LETTER $sClipboardFileFullName $sResponseFromCalledFileFullName $sMapFullName $sEditedNamePart $sEditedExt"
	LogUtils.info(asCommand)
	// !: SEE: http://www.joergm.com/2010/09/executing-shell-commands-in-groovy/
	def proc = asCommand.execute()

	proc.waitFor()
	
	LogUtils.info("Possible error: " + proc?.err?.text)  // !: returns possible python error message.
	sNewExternalFilePlainName = new File(sResponseFromCalledFileFullName).text  // reads response from file filled by called script
	
	sNewExternalFileRelName = sSubdirName+"/"+sNewExternalFilePlainName
	
	sHYPERLINK_BLOCK = sHYPERLINK_BLOCK.replaceAll("_FULL_URL_TAG_", sNewExternalFileRelName)
	sHYPERLINK_BLOCK = sHYPERLINK_BLOCK.replaceAll("_LABEL_TAG_", sNewExternalFilePlainName)  // TODO: replace with simpler label
	// TODO: add faint-fonted date/time stamp
	
	oSavedPane.getDocument().insertString(oSavedPane.getCaretPosition(),sMARK, null)
	oSavedPane.text = oSavedPane.text.replaceAll(sMARK,sHYPERLINK_BLOCK)
}
//================================================
def AskFileNameBodyAndExtension(oSavedPane, sMapPath) {
//================================================
	def nUI_POS_X = 50
	def nUI_POS_Y = 600
	// TODO: add width and height
	oSwing = new SwingBuilder()
	
	sExtFilePath = sMapPath+"\\EXT\\"   // location for ALL type external files: sub directory of focus map 
	
	
	oDialog = oSwing.dialog(title: "Create External File to '$sExtFilePath'",location:[nUI_POS_X, nUI_POS_Y])   // !: 'Dialog' can be located by coordinates
	def panel = oSwing.panel{
		vbox { // !: 'vbox': all following 'hboxes' are piled
			vbox {  // !: vbox: rows piled
			   label(text: 'file name body    ')
			   textField(columns: 20, id: 'xPlainFileName')
			}
			vbox { // !: vbox: rows piled
			   label(text: 'file name extension ')
			   textField(columns: 20, id: 'xFileExtension')
			}
			hbox { // !: 'hbox': first at left, second at right
				button(action: action(name: 'OK', mnemonic: 'O', closure: { submitFileNameParts(oSavedPane, xPlainFileName, xFileExtension, sExtFilePath); dispose()})) // call to text handler and prompt closing
														// !: editor pane delivered down updater method
				button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
			}
		} //...vbox...
	}
	oDialog.getContentPane().add(panel)
	oDialog.pack()
	oDialog.show()
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


//====================================================================================================




// https://docs.oracle.com/javase/7/docs/api/javax/swing/JEditorPane.html
// https://docs.oracle.com/javase/7/docs/api/javax/swing/text/JTextComponent.html#paste%28%29