package MM; #  package name (here acronym of "Main Module") gives class methods to use non-methods (see eg. StateUtils.pm and TraceUtils.pm) 
BEGIN {push @INC,"C:/the/MILL/YARD/APPS/PERL/UTILS"} # to get access to modules in "MILL"

# this "main" program is here below a "LOT", utility modules are (and will stay) below "MILL" 

use TraceUtils;
use MiscUtils;
use BufferUtils;
use GraphvizUtils;

# started 151223
# This script reads imaginary log file. 
# Every log file line contains tag or keyword which gives specific role for that line
# result is a dot syntax file 
#  - contains graph of hard-coded mutual relationships of role lines 

$READ_ONLY = 0;
my $sTaggedLinesInFileName;
my $sCaptureConfigJsonFileName;
my $sDotGraphOutFileName;
my @asCfgDataAsJson;
my $rasCfgDataAsJson;
my $sCommLine;
my $rasDotLines;
my $rasValidatedDotLines;
my $bStatus;

my $num_args = $#ARGV + 1;

my $sThisScript = __FILE__;
if ($num_args < 1) {
    print ("\nUsage: perl $sThisScript <tags capture config file>\n");
    exit;
} else {
	$sCaptureConfigJsonFileName = $ARGV[0];
}
TRACE_INIT("TRACE.CFG", __FILE__);
TRACE("kukkuu");
#=comment
my $oOrigin  = new BufferUtils("operation log lines",$READ_ONLY);  
my $oInCfg = new BufferUtils("log lines role capture configuration lines",$READ_ONLY);
my $oResult = new BufferUtils("result dot graph");


$oInCfg->fillFromFile($sCaptureConfigJsonFileName);
$rasCfgDataAsJson = $oInCfg->getAllLines();  # todo add reading of origin and result file names

TRACE_BAG($rasCfgDataAsJson, "configuration data as JSON");
#=comment

my $oDotProc = new GraphvizUtils("tagged lines to dot graph lines");
$oDotProc->convJsonToCaptureCfg($rasCfgDataAsJson);

($sOriginFileName, $sResultFileName) = $oDotProc->getInOutFileNamesByCfgData();
$oOrigin->fillFromFile($sOriginFileName); 

$oResult->insertLineToStart("digraph justtest {");
$oResult->addLineToEnd("// Date and Time: ".getDateTime());
$oResult->addLineToEnd("node [style=filled, fillcolor=yellow]");  # default parameters for ALL nodes in graph
# "...filled...fillcolor..." produces colored nodes with black frames
$oDotProc->addActivityNode("startup");  # first node needs to be created explicitly

while(1) {
	$sLine = $oOrigin ->getNextLine();
	if ($sLine eq "EOF") {
		TRACE("node role log file line='EOF', so terminate script");
		last;
	}

	($bStatus, $rasDotLines) = $oDotProc->tryBuildDotLinesByCaptures($sLine);
	if ($bStatus == 1) {
		$rasValidatedDotLines = removePossibleEscapesEtc($rasDotLines); # in MiscUtils.pm
		$oResult->addLinesToEnd($rasValidatedDotLines);
	}
}
$oResult->addLineToEnd("}");
$oResult->contentsTraceBag("to see what buffer actually contains");
$oResult->writeUniquesToFile($sResultFileName);

=cut

1;


