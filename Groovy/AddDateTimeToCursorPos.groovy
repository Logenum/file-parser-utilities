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

LogUtils.info("======================================================================")
sMARK = "CursorPos"
cCRLF = System.getProperty("line.separator")
sFAINT_FONT_PREFIX = "<font size=\"1\" color=\"#33cc00\">"
sFONT_POSTFIX = "</font>  "
oDateTimePattern 	= new java.text.SimpleDateFormat("yyMMdd-kkmmss")  	// creates date-time pattern
sDateTime 			= oDateTimePattern.format(new Date())

sHtmlText = sFAINT_FONT_PREFIX + "("+sDateTime +")"+ sFONT_POSTFIX+"&#160;"

// !: fast and compact sequence to insert any HTML block into node note cursor position !!!
JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
oFocusEditorPane.getDocument().insertString(oFocusEditorPane.getCaretPosition(),sMARK, null)
oFocusEditorPane.text = oFocusEditorPane.text.replaceAll(sMARK,sHtmlText)

