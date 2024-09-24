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
import org.freeplane.core.util.LogUtils

//===================================================================
// PURPOSE: adds scrollable text area to focus note cursor pos
//	-	can be used to add long text blocks in a compact way
//===================================================================	

// works OK via function key 160529

cCRLF = System.getProperty("line.separator")  		// assures correct CR/LF usage

sEMPTY_HTML_LINE ="<p>"+cCRLF+"</p>"+cCRLF
sTEXT_AREA_HTML_BLOCK = sEMPTY_HTML_LINE+"<textarea cols=\"100\" rows=\"5\">"+cCRLF+"</textarea>"+sEMPTY_HTML_LINE
sHtmlText = sTEXT_AREA_HTML_BLOCK

sSPECIAL_FONT_PREFIX = "<font size=\"1\" color=\"#33cc00\">.file</font>"
sFONT_POSTFIX = "</font>"
sTEXT_AREA_HTML_BLOCK = sSPECIAL_FONT_PREFIX + sMinitagText + sFONT_POSTFIX
sHtmlText = sTEXT_AREA_HTML_BLOCK

JEditorPane notePane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner



Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
clipboard.setContents(new StringSelection("TagForHtmlInsert"), null)
notePane.paste()  // inserts tag from clipboard
node.map.save(true)  // note: saves the focus map




def sUpdatedNoteTextWithHtmlTags=""
def sCurrentNoteTextWithHtmlTags		= node.getNoteText()

if (sCurrentNoteTextWithHtmlTags != null)  {
	List asLinesWithHtmlTags = sCurrentNoteTextWithHtmlTags.tokenize(cCRLF)  	// every line to an array item
	def nLineNbr=0
	asLinesWithHtmlTags.each() { 	// Iterates list OK
		def sLineWithHtmlTags = it
		if (sLineWithHtmlTags ==~ /.*TagForHtmlInsert.*/) {
			sLineWithHtmlTags = sLineWithHtmlTags.replace("TagForHtmlInsert", sHtmlText)
		} //...each()...
		sUpdatedNoteTextWithHtmlTags = sUpdatedNoteTextWithHtmlTags + sLineWithHtmlTags + cCRLF
	}
	node.setNoteText(sUpdatedNoteTextWithHtmlTags)
}

// https://docs.oracle.com/javase/7/docs/api/javax/swing/JEditorPane.html
// https://docs.oracle.com/javase/7/docs/api/javax/swing/text/JTextComponent.html#paste%28%29