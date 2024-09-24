// @CacheScriptContent(true)
// @ExecutionModes({ON_SINGLE_NODE})
// https://docs.oracle.com/javase/tutorial/uiswing/examples/layout/index.html#FlowLayoutDemo
//*************************************************************************************
//-------------------------------------------------------------------------------------

import groovy.json.JsonSlurper
import groovy.swing.SwingBuilder
import java.awt.FlowLayout as FL
import javax.swing.JOptionPane
import org.freeplane.core.resources.ResourceController
import org.freeplane.core.util.LogUtils;
import org.freeplane.features.mode.Controller
import org.freeplane.features.mode.mindmapmode.MModeController
import org.freeplane.features.url.mindmapmode.MFileManager
import org.freeplane.plugin.script.proxy.Proxy
import java.awt.*
import java.awt.BorderLayout
import java.awt.AWTPermission

// purpose: opens "editor dialog" by Freeplane function key and saves given text to target(s)
// http://alvinalexander.com/java/jwarehouse/groovy/src/examples/groovy/swing/SwingDemo.groovy.shtml
// https://docs.oracle.com/javase/tutorial/uiswing/components/textarea.html
// http://stackoverflow.com/questions/19196454/how-to-fit-textarea-width-to-parent-in-groovy

// SHALL DO:
// 1. captures [<FileName>::<TopicName>] on cursor line (pathname refers implicitly to peer OTL directory)
// 2. creates Autogen.clb file to BOX directory
//	-	contains clip "GoToFileTopic", which contains commands to open <FileName> and then go to topic  <TopicName>
// 3. launches 	Notetab at command line with "Autogen.clb" and "GoToFileTopic" 

// sJOURNAL_FILE_FULL_NAME = 


//------------------------------------
def addTextToJournalOtlFile (oComment) {
//------------------------------------	
	sComment = oComment.getText()
	String[] asLines = sComment.split("\n")
	for (String sLine : asLines) {
		// System.out.println(item)
		LogUtils.info(sLine)
	}
	oComment.setText("")
	// TODO: add call to Python script
	
}

//------------------------------------
def addTextToNodeNote (oComment) {
//------------------------------------
	
	sComment = oComment.getText()
	String[] asLines = sComment.split("\n")
	for (String sLine : asLines) {
		// System.out.println(item)
		LogUtils.info(sLine)
	}
	// TODO: add text to node note
	// def sSFramedComment = sMapName + sNodeName + sComment
	// addTextToJournalOtlFile(sSFramedComment)
	oComment.setText("")
	
}
//------------------------------------
def clearComment (oComment) {
//------------------------------------
	oComment.setText("")
}

// ==============================================================================================
def nFRAME_TO_RIGHT = 50
def nFRAME_TO_DOWN = 600

def nFRAME_WIDTH = 500
def nFRAME_HEIGHT = 200

def BL = new BorderLayout()
def oTextArea  // 
def oScrollPane
def oBottomPanel
def oJournalNodeButton
def oFocusNodeButton
def oClearCommentButton
def oCloseButton

// TODO: add prevention of creating new comment query if already exists (uses some lock file etc.)

def swing = new SwingBuilder()
//	-	http://code.wikia.com/wiki/Groovy.swing.SwingBuilder

frame = swing.frame(title:'Comment', location:[nFRAME_TO_RIGHT, nFRAME_TO_DOWN], size:[nFRAME_WIDTH, nFRAME_HEIGHT]) {
	oScrollPane = scrollPane(constraints:BL.CENTER) {
		oTextArea = textArea()  // note: if this is missing, editing area stays GREY
			// http://stackoverflow.com/questions/28483107/groovy-swingbuilder-how-can-i-add-a-scrollpanel-to-my-frame
	}  
	oBottomPanel=panel(constraints:BL.SOUTH){
		oJournalNodeButton 		= button(action: action(name: 'to JOURNAL', mnemonic: 'O', closure: {addTextToJournalOtlFile(oTextArea)}))
		oFocusNodeButton 		= button(action: action(name: 'to FOCUS', mnemonic: 'O', closure: {addTextToNodeNote(oTextArea)}))
		oClearCommentButton 	= button(action: action(name: 'Clear', mnemonic: 'O', closure: {clearComment(oTextArea)}))
		oCloseButton 			= button(action: action(name: 'Close', mnemonic: 'C', closure: {dispose()}))
	} //... panel...
}

// http://stackoverflow.com/questions/19225146/how-to-set-java-awt-awtpermission-in-policy-file
// https://www.cs.helsinki.fi/group/boi2016/doc/java/api/java/awt/AWTPermission.html
//AWTPermission("setWindowAlwaysOnTop")

frame.show()
frame.setAlwaysOnTop(true)

