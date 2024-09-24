import javax.swing.*
import org.freeplane.core.ui.components.UITools
import groovy.time.*
import java.util.Timer
import org.freeplane.core.util.HtmlUtils
import java.util.regex.Matcher
import java.util.regex.Pattern
import java.awt.KeyboardFocusManager 	
import java.awt.datatransfer.*
import java.awt.Toolkit
import javax.swing.JEditorPane 			
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import java.util.TimeZone
import org.freeplane.core.util.LogUtils
import groovy.swing.SwingBuilder

//===================================================================
// PURPOSE: inserts selected word to cursor position
// -	can be used to add attribute-alike information into text 
// -	small, fainted font assures better readability of the "actual" text
//===================================================================	

LogUtils.info("======================================================================")
sMARK = "CursorPos"
cCRLF = System.getProperty("line.separator")
sPOWER_FONT_PREFIX = "<font size=\"1\" color=\"#ff0000\">"
sFONT_POSTFIX = "</font>  "

sPOSTFIX_TEMPLATE = sPOWER_FONT_PREFIX + "_HTML_TEXT_TEMPLATE_" + sFONT_POSTFIX

JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
//========================
def loadStringsList() { 
//========================
    return (",(WHAT),(HOW),(WHERE),(WHY),(PASSED),(OK),(FAIL),(NOT)").split(",")
}

def oSwing = new SwingBuilder() 
def oSwingVars = oSwing.variables
def sItem

def oDiag = oSwing.dialog(title:'select', modal:true, locationRelativeTo:ui.frame, owner:ui.frame, pack:true) {
	panel() {
		gridLayout(rows: 2, columns: 1, vgap: 10) // 
		panel() {
			label(text:'remark') // !: text label at left from selection field
			comboBox(id:"sTag", editable: true, items:loadStringsList(), selectedIndex:0)
		}
		hbox {
			button(action: action(name: 'OK', mnemonic: 'O', closure: {oSwingVars.ok = true; dispose()}))
			button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
		}
	}
}

ui.addEscapeActionToDialog(oDiag)
oDiag.visible = true

if (oSwingVars.ok) {	
	sItem=oSwingVars.sTag.selectedItem
	sPostfixAsHtml = sPOSTFIX_TEMPLATE.replaceAll("_HTML_TEXT_TEMPLATE_", sItem)
	//============================================================================================
	// !: very fast and compact sequence to insert HTML block into node note cursor position
	//--------------------------------------------------------------------------------------------

	oFocusEditorPane.getDocument().insertString(oFocusEditorPane.getCaretPosition(),sMARK, null)
	oFocusEditorPane.text = oFocusEditorPane.text.replaceAll(sMARK, sPostfixAsHtml)
} 




