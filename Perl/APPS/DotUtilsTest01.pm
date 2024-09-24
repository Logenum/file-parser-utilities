package MM; #  package name (here acronym of "Main Module") gives class methods to use non-methods (see eg. StateUtils.pm and TraceUtils.pm) 
BEGIN {push @INC,"../PerlUtils"} # to get access to parallel directory modules use TraceUtils;

use TraceUtils;
use MiscUtils;
use BufferUtils;
use DotUtils;

# started 151223
# This script reads imaginary log file. 
# Every log file line contains tag or keyword which gives specific role for that line
# result is a dot syntax file 
#  - contains graph of hard-coded mutual relationships of role lines 

$READ_ONLY = 0;
my $sTaggedLinesInFileName;
my $sTagsCaptureConfigFileName;
my $sDotGraphOutFileName;
my @asCfgDataAsJson;
my $rasCfgDataAsJson;
my $sCommLine;
my $rasDotLines;

my $num_args = $#ARGV + 1;

my $sThisScript = __FILE__;
if ($num_args < 3) {
    print ("\nUsage: perl $sThisScript <tagged lines log file name> <tags capture config file> <dot graph file name>\n");
    exit;
} else {
	$sTaggedLinesInFileName = $ARGV[0];
	$sTagsCaptureConfigFileName = $ARGV[1];
	$sDotGraphOutFileName = $ARGV[2];
}
TRACE_INIT("TRACEXP.CFG", __FILE__);
TRACE("kukkuu");
#=comment
my $oInComm = new BufferUtils("operation log lines",$READ_ONLY);
my $oInCfg = new BufferUtils("log lines role capture configuration lines",$READ_ONLY);
my $oOutDotGraph = new BufferUtils("result dot graph");

$oInComm->fillFromFile($sTaggedLinesInFileName);
$oInCfg->fillFromFile($sTagsCaptureConfigFileName);
$rasCfgDataAsJson = $oInCfg->getAllLines();
TRACE_BAG($rasCfgDataAsJson, "configuration data as JSON");
#=comment

my $oDotProc = new DotUtils("tagged lines to dot graph lines");

$oDotProc->cfgBySimpleCaptureJson($rasCfgDataAsJson);

$oOutDotGraph->insertLineToStart("digraph justtest {");
$oOutDotGraph->addLineToEnd("node [style=filled, fillcolor=yellow]");  # default parameters for ALL nodes in graph
# "...filled...fillcolor..." produces colored nodes with black frames
$oDotProc->addActionNode("startup");  # first node needs to be created explicitly

while(1) {
	$sLine = $oInComm->getNextLine();
	if ($sLine eq "EOF") {
		TRACE("node role log file line='EOF', so terminate script");
		last;
	}
	$rasDotLines = $oDotProc->buildDotLinesBySimpleCaptureConfig($sLine);
	if (@$rasDotLines) {
		$oOutDotGraph->addLinesToEnd($rasDotLines);
	}
}
$oOutDotGraph->addLineToEnd("}");
$oOutDotGraph->contentsTraceBag("to see what buffer actually contains");
$oOutDotGraph->writeToFile($sDotGraphOutFileName);

#=cut

1;


