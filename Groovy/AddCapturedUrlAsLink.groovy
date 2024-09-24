
import javax.swing.*;
import org.freeplane.core.ui.components.UITools;
import groovy.time.*
import java.util.Timer;
import org.freeplane.core.util.HtmlUtils;
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
import groovy.swing.SwingBuilder
//===================================================================
// PURPOSE: pastes hyperlink to to focus note cursor position
//  - clipboard contents is assumed to be an URL
//  - prompts a query for hyperlink label
//===================================================================	
// note: no need to call Python script etc.

sMARK = "CursorPos"
sFILE_PATH_PREFIX = "file://"
cCRLF = System.getProperty("line.separator")
sHYPERLINK_HEADER = "<a href="
sHYPERLINK_FOOTER = "</a>"
sEMPTY_HTML_LINE ="<p>"+cCRLF+"</p>"+cCRLF  // seems to produce double lines !?
//-----------------------------
	
JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
// - note pane is saved here before query prompt catches the focus
Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
sFullAddr = clipboard.getContents(null).getTransferData(DataFlavor.stringFlavor)

sHyperlinkLabel = ui.showInputDialog(node.delegate, "Give label for URL '$sFullAddr'","")
//  TODO: add check: if sFulleAddr is a file name, add file path prefix"

sHtmlText = sHYPERLINK_HEADER+"\""+sFullAddr+"\">"+sHyperlinkLabel+sHYPERLINK_FOOTER

//============================================================================================
// !: very fast and compact sequence to insert HTML block into node note cursor position
//--------------------------------------------------------------------------------------------
oFocusEditorPane.getDocument().insertString(oFocusEditorPane.getCaretPosition(),sMARK, null)
oFocusEditorPane.text = oFocusEditorPane.text.replaceAll(sMARK, sHtmlText)