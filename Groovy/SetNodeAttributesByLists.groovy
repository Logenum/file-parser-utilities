
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
//============================================================================

// http://freeplane.sourceforge.net/doc/api/org/freeplane/plugin/script/proxy/Proxy.NodeRO.html
//http://freeplane.sourceforge.net/doc/api/org/freeplane/plugin/script/proxy/Proxy.Node.html
// http://groovy.jmiguel.eu/groovy.codehaus.org/SwingBuilder.comboBox.html
// http://freeplane.sourceforge.net/doc/api/org/freeplane/plugin/script/proxy/Proxy.Attributes.html
// http://groovy.jmiguel.eu/groovy.codehaus.org/Alphabetical+Widgets+List.html


//-----------------------------------------------
def loadRoleTagsList() { 
//-----------------------------------------------
    return (",file,directory,idea,issue,aggregate,parent").split(",")  // first array item is set "empty"
}
//-----------------------------------------------
def loadStatusTagsList() { 
//-----------------------------------------------
    return (",TODO,initial,ask,pending,done,obsolete").split(",")  // first array item is set "empty"
}


def s = new SwingBuilder() 
def vars = s.variables

def dialog = s.dialog(title:'Set Node Attributes', modal:true, locationRelativeTo:ui.frame, owner:ui.frame, pack:true) {
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
		button(action: action(name: 'OK', mnemonic: 'O', closure: {vars.ok = true; dispose()}))
		button(action: action(name: 'Cancel', mnemonic: 'C', closure: {dispose()}))
		
	}
}
ui.addEscapeActionToDialog(dialog)
dialog.visible = true

// attributes updating with validity checks
if (vars.ok) {	
	sRoleTag = vars.roleTag.selectedItem
	sStatusTag = vars.statusTag.selectedItem
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
