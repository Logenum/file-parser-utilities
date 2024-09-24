  
import javax.swing.*;
// http://www.java2s.com/Tutorial/Java/0240__Swing/
import org.freeplane.core.util.LogUtils
import groovy.swing.SwingBuilder
//Swingbuilder slideshare    http://www.slideshare.net/aalmiray/codemash/38-For_More_Information_ulliG_r
import java.awt.BorderLayout as BL
import groovy.beans.Bindable
import static javax.swing.JFrame.EXIT_ON_CLOSE 
import java.awt.*
import java.awt.Font
import javax.swing.WindowConstants as WC
import javax.swing.BorderFactory as BF
import javax.swing.BoxLayout as BXL
import java.awt.Dimension

//import Groovy.Utils2.*

//evaluate(new File("E:/KIT/Groovy/Utils2.groovy"))  // causes observable slower execution !!!
// http://www.oracle.com/technetwork/systems/ts-5098-1-159011.pdf
//import groovy.model.MvcDemo

// JDialogWithJScrollPane()
// Simple1()
// More1()
// FieldsByTable1()
// Checkboxes()
//PanelsAndBoxes1()

//PileOfFieldsAndButtons()
//SwingDemo.run()

//FrameWithTextEditAreaAndSelectionList()
// GivenFunctionGraphPlotter()
//EditableFormWithComboBoxesAndButtons()
//Ut2 = new Utils2()
// HelloWorld()
//EditableFormWithCheckBoxesAndButtons() 
//SetNodeAttributeTags()
//rename_finally()
// FieldsAndButtonsAsPile()
// SelectStringFromList()
// AskFileNameBodyAndExtension()
//textUtils.setClipboardContentsToHtml("xxxxx") // a textUtils -method, what does this do ????
//textUtils.getText('xxx')

//JustOpenWebPage()
ScrollPaneAndTextFieldAsPileAndButtons()

//================================================
def JustOpenWebPage() {
//================================================
	// TODO: create selection list which displays program names "JIRA", "TestRail", ... etc. and launches corresponding URL:s
	
	String.metaClass.browse = { ->      // !: from WWW
		java.awt.Desktop.desktop.browse(new URI(delegate))
	}
	"http://www.iltalehti.fi".browse()  // WORKS OK !!!
}

//================================================
def FrameWithTextEditAreaAndSelectionList() {
//================================================
// TODO: as simple as possible

	oSwing = new SwingBuilder();
	oGui = oSwing.frame(title:'Test 2', size:[400,200]) {
		panel(layout:new FlowLayout()) {
			scrollPane(constraints:BL.CENTER){   // !: brings text-editable pane at top
				textArea = oSwing.textArea() 
			} 
/* 			panel(layout:new FlowLayout()) {
				comboBox(items:["Red", "Green", "Blue", "Orange"],
						 selectedIndex:2);
			} */
		}
	}
	oGui.show();
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//------------------------------------
def submitFileNameParts(xName, xExt) {  // !: 'textField' id:s are some kind of structs, NOT just text contents 
//------------------------------------
	sName 	= xName.text 
	sExt 	= xExt.text
	LogUtils.info ("file name/extension = '$sName'/'$sExt'")
}
//================================================
def AskFileNameBodyAndExtension() {
//================================================
	def nUI_TO_RIGHT = 50
	def nUI_TO_DOWN = 800
	oSwing = new SwingBuilder()
	
	
	oDialog = oSwing.dialog(title: 'Create External File',location:[nUI_TO_RIGHT, nUI_TO_DOWN])   // !: 'Dialog' can be located by coordinates
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
				button(action: action(name: 'OK', mnemonic: 'O', closure: { submitFileNameParts(xPlainFileName, xFileExtension); dispose()})) // call to text handler
				button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
			}
		} //...vbox...
	}
	oDialog.getContentPane().add(panel)
	oDialog.pack()
	oDialog.show()
}


//==============================================================================================


//------------------------------------
def FieldsAndButtonsAsPile() {
//------------------------------------
	oSwing = new SwingBuilder()
	oDialog = oSwing.dialog(title: 'Entry')
	def panel = oSwing.panel{
		vbox { // !: 'vbox': all following 'hboxes' are piled
			hbox {  // !: 'hbox': first at left, second at right
			   label(text: 'Name    ')
			   textField(columns: 20, id: 'name')
			}
			hbox { // !: 'hbox': first at left, second at right
			   label(text: 'Password ')
			   passwordField(columns: 20, id: 'password')
			}
			hbox { // !: 'hbox': first at left, second at right
				button('OK') // add actionPerformed:
				button('Cancel')
			}
		} //...vbox...
	}
	oDialog.getContentPane().add(panel)
	oDialog.pack()
	oDialog.show()
}





//=======================================================================================================================
//------------------------------------
def handleEditedText (oTextArea) {   // called, if function name is given at button definition context
//------------------------------------
	sComment = oTextArea.getText()
	// TODO: add text handling here
	oTextArea.setText("")	// clears the text
}
//------------------------------------
def getComboBoxItemsList () {   // called, if function name is given at 'comboBox' definition context
//------------------------------------
	asRetVal = ["one", "two", "three", "four"]
	return asRetVal
}
//------------------------------------
def getCheckBoxItemsList () {    // called, if function name is given at 'checkBox' definition context
//------------------------------------
	asRetVal = ["one", "two", "three", "four","five"]
	return asRetVal
}
//=============================================
def EditableFormWithComboBoxesAndButtons() {
//=============================================
	def nFRAME_TO_RIGHT = 50
	def nFRAME_TO_DOWN = 600
	def nFRAME_WIDTH = 300
	def nFRAME_HEIGHT = 200
	def oTA
	def BL = new BorderLayout()
	def oSwing = new SwingBuilder()
	def oSwingVars = oSwing.variables
	
	oFrame = oSwing.frame(title:'Comment', location:[nFRAME_TO_RIGHT, nFRAME_TO_DOWN], size:[nFRAME_WIDTH, nFRAME_HEIGHT]) {
		scrollPane(constraints:BL.CENTER) {
			oTA = textArea() 
		}  
		panel(constraints:BL.SOUTH){ // puts following items to frame bottom
			gridLayout() // puts following items evenly on a single row
			comboBox(id:"sCbSelItem",items:getComboBoxItemsList(), selectedIndex:0)  // TODO: replace with call to list builder
			// -   when clicked, displays all items as a pile
			button(action: action(name: 'OK', mnemonic: 'O', closure: {handleEditedText(oTA)})) // call to text handler
			button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
		} //... panel... 
	}
	oFrame.show()
	
	sComboBoxSelectedItem = oSwingVars.sCbSelItem
	// frame.setAlwaysOnTop(true)
}
//------------------------------------
def handleCheckBoxEvent (sLabel) {   // called, if function name is given at button definition context
//------------------------------------
	println "Hello world '$sLabel'"
}

//=============================================
def EditableFormWithCheckBoxesAndButtons () {
//=============================================
	def nFRAME_TO_RIGHT = 50
	def nFRAME_TO_DOWN = 600
	def nFRAME_WIDTH = 300
	def nFRAME_HEIGHT = 300
	def oTA
	def BL = new BorderLayout()
	def oSwing = new SwingBuilder()
	def oSwingVars = oSwing.variables
	
	oFrame = oSwing.frame(title:'EditableFormWithCheckBoxesAndButtons', location:[nFRAME_TO_RIGHT, nFRAME_TO_DOWN], size:[nFRAME_WIDTH, nFRAME_HEIGHT]) {
		vbox {   // !: 'wbox' and 'hbox' are a tabular-alike way for UI layout
			hbox {
				scrollPane() {
					oTA = textArea() 
				}  
			}
			hbox {
				for (name in getCheckBoxItemsList()) {
					checkBox(text:name, actionPerformed:{handleCheckBoxEvent(name)}) // TODO: find a way to handle and store each checbox on/off -state
				}
			}
			hbox {
				button(action: action(name: 'OK', mnemonic: 'O', closure: {handleEditedText(oTA)})) // call to text handler
				button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
			}
		} //... panel... 
	}
	oFrame.show()
	// frame.setAlwaysOnTop(true)
}

//===================================
def rename_finally() {
//===================================

	// jsyntaxpane.DefaultSyntaxKit.initKit();
	def frame = new JFrame()
	frame.title = "Test"

	def panel = new JPanel()
	def editor = new JEditorPane()
	def scPane = new JScrollPane(editor)
	editor.setContentType("text/groovy")

	panel.add(scPane)
	frame.add(panel)

	scPane.setPreferredSize(new Dimension(1000,400))
	frame.pack()
	frame.show()

	def swing = new SwingBuilder()

	jsyntaxpane.DefaultSyntaxKit.initKit();

	swing.edt{
		frame( title:'Test', pack:true, show:true ){
			panel(){
				scrollPane( preferredSize:[1000, 400], maximumSize:[1000, 450] ){
					editorPane( id:'ePane', text:"println \"Hello\"")
					swing.ePane.setContentType('text/groovy')
				}
			}
		}
	}
}
//================================================
def JDialogWithJScrollPane () {
//================================================
	def dialog = new JDialog(ui.frame)
	// http://www.java2s.com/Tutorial/Java/0240__Swing/1220__JDialog.htm
    dialog.setSize(350, 450)
    dialog.setLocationRelativeTo(ui.frame)
    dialog.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
    dialog.add(new JScrollPane(new JTextArea(text)))
	// http://www.java2s.com/Tutorial/Java/0240__Swing/0800__JScrollPane.htm
			// http://www.java2s.com/Tutorial/Java/0240__Swing/0280__JTextArea.htm
    ui.addEscapeActionToDialog(dialog)
    dialog.visible = true
}
//================================================
def Simple1 () {
//================================================
	// http://groovy-lang.org/dsls.html#swingbuilder
	// ...Swing Builder is a groovy way for UI...
	// copied from www
	count = 0
	new SwingBuilder().edt {
		frame(title: 'Frame', size: [300, 300], show: true) {
			borderLayout()
			textlabel = label(text: 'Click the button!', constraints: BL.NORTH)
			button(text:'Click Me', actionPerformed: {count++; textlabel.text = "Clicked ${count} time(s)."; println "clicked"}, constraints:BL.SOUTH)
		}
	}
}
//================================================
def More1 () {
//================================================
	// TODO try add more "fields" within frame
	count = 0
	new SwingBuilder().edt {
		frame(title: 'Frame', size: [300, 300], show: true) { // a frame is an independent ui "card"
			borderLayout()
			textlabel = label(text: 'Click the button!', constraints: BL.NORTH)
			button(text:'Click Me',actionPerformed: {count++; textlabel.text = "Clicked ${count} time(s)."; println "clicked"}, constraints:BL.SOUTH)
		}
	}
}


// @Bindable
class Address {  
    String street, number, city
    String toString() { "address[street=$street,number=$number,city=$city]" }
}
  

//================================================
def FieldsByTable1 () {
//================================================

	def address = new Address(street: 'Evergreen Terrace', number: '742', city: 'Springfield')
	def swingBuilder = new SwingBuilder()
	swingBuilder.edt {  // edt method makes sure UI is build on Event Dispatch Thread.
		lookAndFeel 'nimbus'  // Simple change in look and feel.
		frame(title: 'Address', size: [350, 230], 
				show: true, locationRelativeTo: null, 
				defaultCloseOperation: EXIT_ON_CLOSE) { 
			borderLayout(vgap: 5)
			
			panel(constraints: BorderLayout.CENTER, 
					border: compoundBorder([emptyBorder(10), titledBorder('Enter your address:')])) {
				tableLayout {
					tr {    // !: HTML-alike tag to indicate table row
						td {  // !: HTML-alike tag to indicate table column
							label 'Street:'  // text property is default, so it is implicit.
						}
						td {
							textField address.street, id: 'streetField', columns: 20
						}
					}
					tr {
						td {
							label 'Number:'
						}
						td {
							textField id: 'numberField', columns: 5, text: address.number
						}
					}
					tr {
						td {
							label 'City:'
						}
						td {
							textField id: 'cityField', columns: 20, address.city
						}
					}
				}
			}
			panel(constraints: BorderLayout.SOUTH) {
				button text: 'Save', actionPerformed: {
					println address
				}
			}
			
			// Binding of textfield's to address object. 
			bean address, 
				street: bind { streetField.text }, 
				number: bind { numberField.text }, 
				city: bind { cityField.text }
		}  
	}
}

//================================================
def WithCheckboxes() {
//================================================
	swing = new SwingBuilder();
	gui = swing.frame(title:'Test 2', size:[400,200]) {
		panel(layout:new FlowLayout()) {
			// http://groovy.jmiguel.eu/groovy.codehaus.org/SwingBuilder.flowLayout.html
			panel(layout:new FlowLayout()) {
				for (name in ["Tom", "Dick", "Harry", "Bill"]) {
					checkBox(text:name);
				}
			}
			panel(layout:new FlowLayout()) {
				comboBox(items:["Red", "Green", "Blue", "Orange"],
						 selectedIndex:2);
			}
		}
	}
	gui.show();
}

//================================================
def PanelsAndBoxes1() {
//================================================
// !: this is versatile example
 // TODO: use as "basic prompt" modification start
	def swing = new SwingBuilder() 

	Font font = new Font("Serif", Font.BOLD, 16) 
	 def frame = swing.frame(title:'Frame', size:[1200,300]) { 
		 borderLayout() 
		scrollPane(constraints:BL.CENTER){   // !: brings text-editable pane at top
			textArea = swing.textArea() 
		} 
		panel(constraints:BL.SOUTH){   // !: all items within this reside on frame margin
			borderLayout() 
				   panel(constraints: BL.WEST){ 	 // brings text-editable field low left
					 //GROUP ONE 
					  label("user "                     ).setFont(font) 
					  textField(columns:10      ) 
					  label("password "                 ).setFont(font) 
					  passwordField(columns:10  ) 
				  } 
				   panel(constraints: BL.CENTER){     // !: brings checkbox row to low center
					 // GROUP TWO 
					  undeploy_checkBox = checkBox() 
					  label("undeploy "                ) 
					  delete_checkBox = checkBox() 
					  label("delete "                  ) 
					  deploy_checkBox = checkBox() 
					  label("deploy "                  ) 
					}   
				panel(constraints: BL.EAST) {   // !: brings button to low right corner
					panel(){ 
					  exportButton  = button(text:"Align me to the right please", actionPerformed:{ 
						   Thread.start{ 
							   buttonAction() 
						   } 
					   }) 
					 } 
			  }     
		  } 
	} 
	frame.show() 
}
	
//========================================================================================

//================================================
def PileOfFieldsAndButtons() {
//================================================
	int numPanels = 20

	swing = new SwingBuilder()
	frame = swing.frame(title:'test', pack:true, visible:true, defaultCloseOperation:WC.HIDE_ON_CLOSE) {
	  panel(id:'mainPanel'){
		scrollPane( verticalScrollBarPolicy:JScrollPane.VERTICAL_SCROLLBAR_ALWAYS ) {
		  vbox {
			(1..numPanels).each { num ->
			  def panelID = "panel$num"
			  def pane = panel( alignmentX:0f, id:panelID, background:java.awt.Color.GREEN ) {
				label('description') 
				textField( id: "description$num", text:panelID, columns: 70 )
				button( id: "buttonpanel$num", text:panelID, actionPerformed:{
				  swing."$panelID".background = java.awt.Color.RED
				} )
			  }
			}
		  }
		}

		boxLayout(axis: BXL.Y_AXIS)
		panel(id:'secondPanel' , alignmentX: 0f){                       
		  button('Quit', actionPerformed:{
			frame.visible = false
		  })
		}
	  }       
	}
	frame.size = [ frame.width, 600 ]
}	
//#########################################################################################

def GivenFunctionGraphPlotter() {
		// from Groovy book PDF
	swing = new SwingBuilder()
	paint = swing.action(
	name: 'Paint',
	closure: this.&paintGraph,
	mnemonic: 'P',
	accelerator: 'ctrl P'
	)
	about = swing.action(
	name: 'About',
	closure: this.&showAbout,
	mnemonic: 'A',
	accelerator: 'F1'
	)
	frame = swing.frame(title:'Plotter',
	location:[100,100], size:[300,300],
	defaultCloseOperation:WC.EXIT_ON_CLOSE) {
	menuBar (){
	menu(mnemonic:'A','Action'){
	menuItem(action:paint)
	}
	glue()
	menu(mnemonic:'H','Help'){
	menuItem(action:about)
	}
	}
	panel (border:BF.createEmptyBorder(6,6,6,6)) {
	borderLayout()
	vbox (constraints: BL.NORTH){
		
	hbox {
	hstrut(width:10)
	label 'f(x) = '
	textField(id:'function',action:paint,'Math.sin(x)')
	button(action:paint)
	}
	}
	vbox (constraints: BL.WEST){
	labeledSpinner('max',1d)
	20.times { swing.vglue()} // todo: check 'swing'
	labeledSpinner('min',-1d)
	}
	vbox(constraints: BL.CENTER,
	border:BF.createTitledBorder('Function Plot')) {
	panel(id:'canvas')
	}
	hbox (constraints: BL.SOUTH){
	hstrut(width:10)
	labeledSpinner('from',0d)
	10.times { swing.hglue()}
	// todo: check 'swing'
	labeledSpinner('to',6.3d)
	}
	}
	}
	frame.show()
}
	// implementation methods
	def labeledSpinner(label, value){
	swing.label(label)
	swing.hstrut()
	swing.spinner(id:label, stateChanged:this.&paintGraph,
	model:swing.spinnerNumberModel(value:value)
	)
	}
	def paintGraph(event) {
	calc = new Dynamo(swing.function.text)
	gfx = swing.canvas.graphics
	int width = swing.canvas.size.width
	int height = swing.canvas.size.height
	gfx.color = new Color(255, 255, 150)
	gfx.fillRect(0, 0, width, height)
	gfx.color = Color.blue
	xFactor = (swing.to.value - swing.from.value) / width
	yFactor = height / (swing.max.value - swing.min.value)
	int ceiling = height + swing.min.value * yFactor
	int lastY = calc.f(swing.from.value) * yFactor
	for (x in (1..width)) {
	int y = calc.f(swing.from.value + x * xFactor) * yFactor
	gfx.drawLine(x-1, ceiling-lastY, x, ceiling-y)	
	lastY = y
	}
	}
	void showAbout(event) {
	JOptionPane.showMessageDialog(frame,
	'''A Function Plotter
	that serves as a SwingBuilder example for
	Groovy in Action''')
	}
	// Keep all dynamic invocation handling in one place.
	class Dynamo {
	static final GroovyShell SHELL = new GroovyShell()
	Script functionScript
	Dynamo(String function){
	functionScript = SHELL.parse(function)
	}
	Object f(x) {
	functionScript.x = x
	return functionScript.run()
	}
	}
//}


//####################################################################################################
def loadRoleTagsList() {  // ELu
    return (",file,directory,idea,issue,aggregate,parent").split(",")
}

def loadStatusTagsList() {  // ELu
    return (",TODO,initial,ask,pending,done,obsolete").split(",")
}

//================================================
def SetNodeAttributeTags() {
//================================================
    def oSwing = new SwingBuilder() 
	def oSwingVars = oSwing.variables

    def oDiag = oSwing.dialog(title:'Set Node Attributes', modal:true, locationRelativeTo:ui.frame, owner:ui.frame, pack:true) {
        panel() {
            gridLayout(rows: 4, columns: 1, vgap: 10) // !: result: a pile of fields and buttons
			panel() {
				label(text:'Role:') // !: text label at left from selection field
				comboBox(id:"roleTag", editable: true, items:loadRoleTagsList(), selectedIndex:0)
			}
			panel() {
				label(text:'Status:')
				comboBox(id:"statusTag", editable: true, items:loadStatusTagsList(), selectedIndex:0)
			}
            button(action: action(name: 'OK', mnemonic: 'O', closure: {oSwingVars.ok = true; dispose()}))
            button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
            
        }
    }
    ui.addEscapeActionToDialog(oDiag)
    oDiag.visible = true
	if (oSwingVars.ok) {	
		sRoleTag = oSwingVars.roleTag.selectedItem
		sStatusTag = oSwingVars.statusTag.selectedItem
		if (sRoleTag == "") {
			// node["role"] = null
		} else {
			node["role"] = sRoleTag
		}
		if (sStatusTag == "") {
			//node["status"] = null
		} else {
			node["status"] = sStatusTag
		}
    } 
}


def loadStringsList() { 
    return (",file,directory,idea,issue,aggregate,parent").split(",")
}
//================================================
def SelectStringFromList() {
//================================================
    def oSwing = new SwingBuilder() 
	def oSwingVars = oSwing.variables
	def sItem

    def oDiag = oSwing.dialog(title:'select', modal:true, locationRelativeTo:ui.frame, owner:ui.frame, pack:true) {
        panel() {
            gridLayout(rows: 2, columns: 1, vgap: 10) // 
			panel() {
				label(text:'word:') // !: text label at left from selection field
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
    } 
}

//------------------------------------
def ScrollPaneAndTextFieldAsPileAndButtons() {
//------------------------------------
// TBD: scroll pane on top, editable field below it and buttons on down line

	def nFRAME_TO_RIGHT = 1000
	def nFRAME_TO_DOWN = 500

	def nFRAME_WIDTH = 300
	def nFRAME_HEIGHT = 200
	def nTEXT_FIELD_COLUMNS = 33

	def BL = new BorderLayout()
	def oTextArea  // 
	def oTextArea2 
	def oScrollPane
	def oScrollPane2
	def oBottomPanel
	def oOkButton
	def oClearCommentButton
	def oCloseButton
	// https://docs.oracle.com/javase/7/docs/api/java/awt/BorderLayout.html
	def oSwing = new SwingBuilder()
	//	-	http://code.wikia.com/wiki/Groovy.swing.SwingBuilder

	oFrame = oSwing.frame(title:'Comment', location:[nFRAME_TO_RIGHT, nFRAME_TO_DOWN], size:[nFRAME_WIDTH, nFRAME_HEIGHT]) {
		vbox {
			oScrollPane = scrollPane(constraints:BL.CENTER) {
				oTextArea = textArea()		
			}  // ... oScrollPane
		}
		oBottomPanel=panel(constraints:BL.SOUTH){
			vbox {  // produces single-line text field and a row of buttons below it
				panel {
					textField(columns: nTEXT_FIELD_COLUMNS, id: 'xIndexMapNodeLabel')	// TBF: how to set field height to a single line ?????
				} //... panel
			
				hbox {
					oOkButton 	= button(action: action(name: 'Commit', mnemonic: 'O', closure: {dispose()}))
					oClearCommentButton 	= button(action: action(name: 'Clear', mnemonic: 'O', closure: {dispose()}))
					oCloseButton 			= button(action: action(name: 'Close', mnemonic: 'C', closure: {dispose()}))
				}
			}
		} //... oBottomPanel...
	} // ...oFrame

	oFrame.show()
	oFrame.setAlwaysOnTop(true) 
}

