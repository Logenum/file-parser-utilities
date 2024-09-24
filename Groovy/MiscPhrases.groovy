


// !: Maybe this kind of file would better be a Notetab outline file ??!
//============================================================================================
/* // !: very fast and compact sequence to insert HTML block into node note cursor position
//--------------------------------------------------------------------------------------------
JEditorPane oFocusEditorPane = KeyboardFocusManager.currentKeyboardFocusManager.focusOwner
oFocusEditorPane.getDocument().insertString(oFocusEditorPane.getCaretPosition(),sMARK, null)
oFocusEditorPane.text = oFocusEditorPane.text.replaceAll(sMARK,sHtmlText)




class Filename {
  private String fullPath;
  private char pathSeparator, extensionSeparator;

  public Filename(String str, char sep, char ext) {
    fullPath = str;
    pathSeparator = sep;
    extensionSeparator = ext;
  }

  public String extension() {
    int dot = fullPath.lastIndexOf(extensionSeparator);
    return fullPath.substring(dot + 1);
  }

  public String filename() { // gets filename without extension
    int dot = fullPath.lastIndexOf(extensionSeparator);
    int sep = fullPath.lastIndexOf(pathSeparator);
    return fullPath.substring(sep + 1, dot);
  }

  public String path() {
    int sep = fullPath.lastIndexOf(pathSeparator);
    return fullPath.substring(0, sep);
  } 
} */

