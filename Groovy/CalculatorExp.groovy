import groovy.swing.SwingBuilder
import java.awt.GridLayout
import java.awt.BorderLayout
import javax.swing.JOptionPane
 
def GUI = new CalcGUI()
 
 
public class CalcGUI    {
    def swing = new SwingBuilder()
 
    def operatorCheck = ""
    def temp1 = ""
    def type1 =    { swing.updateValue.text = swing.updateValue.text + '1' }
    def type2 =    { swing.updateValue.text = swing.updateValue.text + '2' }
    def type3 =    { swing.updateValue.text = swing.updateValue.text + '3' }
    def type4 =    { swing.updateValue.text = swing.updateValue.text + '4' }
    def type5 =    { swing.updateValue.text = swing.updateValue.text + '5' }
    def type6 =    { swing.updateValue.text = swing.updateValue.text + '6' }
    def type7 =    { swing.updateValue.text = swing.updateValue.text + '7' }
    def type8 =    { swing.updateValue.text = swing.updateValue.text + '8' }
    def type9 =    { swing.updateValue.text = swing.updateValue.text + '9' }
    def type0 =    { swing.updateValue.text = swing.updateValue.text + '0' }
    def typeClr =    { swing.updateValue.text = '' }
    def optPlus =    { temp1 = swing.updateValue.text;operatorCheck = '+'; typeClr();}
    def optSub =     {temp1 = swing.updateValue.text;operatorCheck = '-'; typeClr();}
    def optMul =    {temp1 = swing.updateValue.text;operatorCheck = '*'; typeClr();}
    def optDiv =    {temp1 = swing.updateValue.text;operatorCheck = '/'; typeClr();}
    def calculate = {
        def temp2 = swing.updateValue.text;
        temp1 = temp1.toInteger()
        temp2 = temp2.toInteger()
        if(operatorCheck == "")    { JOptionPane.showMessageDialog(null, 'Operator Error!')}
        if(operatorCheck == '+')    { swing.updateValue.text = temp1 + temp2;operatorCheck=""}
        if(operatorCheck == '-')    { swing.updateValue.text = temp1 - temp2;operatorCheck=""}
        if(operatorCheck == '*')    { swing.updateValue.text = temp1 * temp2;operatorCheck=""}
        if(operatorCheck == '/')    { swing.updateValue.text = temp1 / temp2;operatorCheck=""}
        temp2 = ""
    }
      
    def frameButtons =    {
         
         swing.panel(layout :new BorderLayout(), constraints : BorderLayout.NORTH)    {
         textField(id : 'updateValue', columns : 20)
         } 
         swing.panel(layout :new GridLayout(4, 4, 1, 1), constraints : BorderLayout.CENTER)  {
            button(text : '1', actionPerformed : type1)
            button(text : '2', actionPerformed : type2)
            button(text : '3', actionPerformed : type3)
            button(text : '+', actionPerformed : optPlus) 
            button(text : '4', actionPerformed : type4)
            button(text : '5', actionPerformed : type5)      
            button(text : '6', actionPerformed : type6)
            button(text : '-', actionPerformed : optSub) 
            button(text : '7', actionPerformed : type7) 
            button(text : '8', actionPerformed : type8) 
            button(text : '9', actionPerformed : type9) 
            button(text : '*', actionPerformed : optMul) 
            button(text : 'Clr', actionPerformed : typeClr)
            button(text : '0', actionPerformed : type0) 
            button(text : '=', actionPerformed : calculate) 
            button(text : '/', actionPerformed : optDiv) 
          
        }
    }
     
    def frameMenu =    {
            swing.menuBar() {
            menu(text: "File", mnemonic: 'F') {
                menuItem(text: "Exit", mnemonic: 'X', actionPerformed: {System.exit(0)})
            }
 
        }
    }
 
    // creating frame and dialog of remaining objects
    def frame = swing.frame(title: 'Caculator 1.0', size: [300, 400], show: true, locationRelativeTo: null) {
        frameMenu()    
        frameButtons()
    }
}