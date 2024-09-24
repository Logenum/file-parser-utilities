// TBD: writes link label "[<map file name body>::<node name>]" to note cursor pos
//  -   before this script map file name, node name and node URI are saved by another script (TBD...)
// -	<map file name body> is taken from saved map file name (environment variable ?)
// -	<node name> is taken from saved node name (environment variable ?)
// -	link contents is taken from saved URI (environment variable ?)


def env = System.getenv()
// http://www.mytechtoday.com/2009/01/read-environment-variables-with-groovy.html

String sLinkNodeLabel = env['FREEPLANE_NODE_LABEL']
String sLinkNodeUri = env['FREEPLANE_NODE_URI']
// sLinkFileNameBody= <parse from sLinkNodeUri>

//.... TBD

// link syntax example: <a href="INDEX.mm#ID_277046421">[INDEX::Simulator]</a><font color="#009933">