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
// GOAL: displays a list of tool names (Jira,TestRail, ...) and opens corresponding URL

//===================================================================	
// TBD: displays all tools simultaneously. 'OK' and 'Cancel' -buttons removed
mToolsAccess = ['Jira':'http://dentuusvrdjira:8080', 'TestRail':'http://fihelas11/testrail/testrail/index.php'] // TBD: more key/value pairs
	// !: IDEA: prefix 'm' for 'map' in Groovy ('hash' or 'dictionary' in some other languages)
	// TBD: add tools where map values are names of executables, not just URL:s which launch browsers

LogUtils.info("======================================================================")


// - IDEA: reads map contents from configuration (JSON ?) file

//========================
def loadToolNames(mTools) { 
//========================
	// mToolsAccess = ['Jira':'http://dentuusvrdjira:8080', 'TestRail':'http://fihelas11/testrail/testrail/index.ph'] // TBD: more key/value pairs
	// !: IDEA: prefix 'm' for 'map' in Groovy ('hash' or 'dictionary' in some other languages)
	// TBD: add tools where map values are names of executables, not just URL:s which launch browsers

	// !: http://grails.asia/groovy-map-tutorial
	// TODO: extract tool names (=keys) from tool map
	asToolNames = []   // !: creating empty array
	// !: getting keys from map
	for (mPair in mTools) {  // !: creating list of map keys
		 asToolNames.push(mPair.key)
	}

	return asToolNames
}

//================================================
def openGivenWebPage(sAssumedUrl) {
//================================================
	String.metaClass.browse = { ->      // !: from WWW
		java.awt.Desktop.desktop.browse(new URI(delegate))
	}
	sAssumedUrl.browse()  // !: opens url in browser
}

//######################################################################################################

def oSwing = new SwingBuilder() 
def oSwingVars = oSwing.variables


def oDiag = oSwing.dialog(title:'select', modal:true, locationRelativeTo:ui.frame, owner:ui.frame, pack:true) {
	panel() {
		gridLayout(rows: 2, columns: 1, vgap: 10) // 
		panel() {
			label(text:'select to open') // 
			comboBox(id:"sMapKey", items:loadToolNames(mToolsAccess), selectedIndex:0)
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
	sToolName		=	oSwingVars.sMapKey.selectedItem
	LogUtils.info("selected tool name: '"+sToolName+"'")
	sAssumedUrl 	=	mToolsAccess.get(sToolName)  // !: getting value by key (note: a function !!!)
	LogUtils.info("try open web page '"+sAssumedUrl+"'")
	openGivenWebPage(sAssumedUrl)
} 




