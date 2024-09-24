#=====================================================================================================================================================
package PERL_SCRIPTS;


#BEGIN {push @INC, $0 =~ /^(.*)\/.*/;}

use SRC::UTILS  	    # perl: seems necessary, because caller dos batch is in parent directory !!!!

$FALSE 					= 0;
$TRUE 					= 1;
$SYMBOLIFY				= "convert to valid symbol name";
$TEXTIFY				= "remove periods etc characters";
$STRINGIFY				= "no changes to string";

my $sWellMode = "";


#--- read CALL parameters 
my $sCallerPath = shift @ARGV;  # from '%CD%' environment variable
my $sConfigFile = shift @ARGV;
my $sTraceFile 	= shift @ARGV;

TRACE_INIT($sTraceFile, __FILE__);



setAppPath($sCallerPath);

my $hndWellFile;
my $rasFilledTemplateLines;
my @aa_CollAllPhraseMappings=();
	
my ($resultFileExtension, $bTerminate, @afhROLE_FILES) = openAllRoleFilesByCfgFile($sConfigFile);

if ($bTerminate == 1) {
	TRACE("terminate script due to configuration file parsing failure");
	closeAllRoleFiles(@afhROLE_FILES);
	TRACE_END("the end");
	die;
}

my ($fhMOOR_FILE,  # file containing 1...N file names with paths
	$fhCONV_CFG_OTL_FILE, 
	$fhPHRASE_CFG_OTL_FILE,
	$fhHEADER_FILE, 
	$fhINCLUDE_FILE, 
	$fhRESULT_FILE, 
	$fhFOOTER_FILE) = @afhROLE_FILES; 	# return order must match the order in LOCUTILS.PM
	
my $SrcLineNbr = 0;
my $rhCaptures;
my $rasFilledTemplateLines;
my $fhWellFile;
my $bEndStatus;
my $asConfItem;
my $sWellLine;
my $sScriptLine;
my $sFileName;
my $sWellFileFullName;
my $sFileNameCand;
my $sStatus;
my @asCaptureSymbols; 	# all captures by single regex match
my $rasCaptureSymbols;
my $rasReportTemplates;
my $sTemplate;
my $sCapturedVal;	# single capture within all captures
my %hValBySym;	# the hash. where captured values are stored, keys are configured symbol names


my $fd = fileno $fhCONV_CFG_OTL_FILE;
my $xxxx = readlink("/proc/$$/fd/$fd");
TRACE("file name from file handle: '$xxx'");


OUT_SET($fhRESULT_FILE);
buildConvConfData($fhCONV_CFG_OTL_FILE, $resultFileExtension);  # data is stored in "UTILS" -library side
my $raoh_ConversionActionBlocks = buildAllConversionActionBlocks();

my $oConvData =  new ConvData($raoh_ConversionActionBlocks, "Conversion Configuration");

my $rh_ConvBlock; 
#PERL_SCRIPTS::TRACE("BlockType = ".$rh_ConvBlock->{BlockType});
#TRACE("conversion configuration, first block ".Dumper($oConvData->getNextBlock()));
#TRACE("conversion configuration: \\\$raoh_ConversionActionBlocks ".Dumper($raoh_ConversionActionBlocks));
extractMoorFileContents($fhMOOR_FILE); # data is stored in "UTILS" -library side
tryInsertFile($fhHEADER_FILE, $fhRESULT_FILE,"Header");
tryInsertFile($fhINCLUDE_FILE, $fhRESULT_FILE,"Include");

my $tmp;
my $bJusttest;
my $bProcMoorFile=1;
my $bProcWellFile=1;
my $bFindingAnchor=1;
my $bFindingCapture=1;
my $bActGetNextWellLine=0;
my $bActGoToFirstWellLine=0;
my $bActGetNextConvBlock=0;
my $bActGoFirstConvBlock=0;
my $sType;
my $sNextType;
my $bStatus;

my $oStWell = new StateVault("ST_GOTO_FIRST_WELL_LINE", "Well File Navigation");
my $oStConv = new StateVault("ST_GOTO_START", "Conversion Blocks Navigation");
my $oStProc = new StateVault("ST_IDLE", "Conversion Process");
#===========================

TRACE("goes through all well files");
while ($bProcMoorFile) {
	$sFileNameCand = getMoorNext();
	if ($sFileNameCand eq "EOF") {
		TRACE("no more well files, so do end actions");	
		last;
	} 
	#%hValBySym=(); # initializes symbol/value hash
	$sWellFileFullName = openWellFileReadAllLines($sFileNameCand);  # data is stored in "UTILS" -library side
	if ($sWellFileFullName eq "NONE") {
		TRACE("no more well files, so do end actions");
		last;
	}  

	$hValBySym{WellFileName} = $sWellFileFullName;
	$oConvData->goToFirstBlock(); 
	$oStWell->setState("ST_GOTO_FIRST_WELL_LINE","...");
	$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","...");
	while ($bProcWellFile) {
		if ($oStWell->isState("ST_GOTO_FIRST_WELL_LINE")) {
			goToFirstWellLine();
			$oStWell->setState("ST_IDLE", "...");
		}
		if ($oStConv->isState("ST_GET_NEXT_CONV_BLOCK")) {
			if (($sNextType eq "TOPIC") or ($sType eq "EOF")) {  # previous conversion action returned next topic or file end, so stay within current conversion topic
				#goToTopicFirstCaptureConfItem();
			}
			$rh_ConvBlock 			= $oConvData->getNextBlock(); #########################################################
			$sType 					= $rh_ConvBlock->{BlockType};
			$sNextType				= $rh_ConvBlock->{NextBlockType};
			$sRegex 				= $rh_ConvBlock->{CaptureRegex};
			$rasCaptureSymbols 		= $rh_ConvBlock->{CaptureSymbols};
			$rasReportTemplates 	= $rh_ConvBlock->{ReportTemplates};
			$sTopic 				= $rh_ConvBlock->{TopicName};
			setFocusConvTopicName($sTopic);
			$oStConv->setState("ST_IDLE","...");
		}
		if ($sType eq "EOF") {
			TRACE("conversion config file ended, so go to read next well file");
			last;
		}
		if ($sType eq "PERL") {  # special topic in conversion configuration file
			evaluatePerlScript($rasCaptureSymbols);
			$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","perl script evaluated");
		} elsif ($sType eq "ANCHOR") {   # a string to be found, nothing to capture
			while ($bFindingAnchor) {
				$sWellLine = getNextWellLine();
				if ($sWellLine eq "EOF") { 
					$oStWell->setState("ST_GOTO_FIRST_WELL_LINE","anchor '$sType' not found");
					$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","well file ended");
					last;  # exits this INNER while loop
				}
				if ($sWellLine =~ /$sRegex/) {
					$oStConv->setState("ST_GET_NEXT_CONV_BLOCK"," anchor found by '$sRegex' at line '$sWellLine'");
					$oStProc->setState("ST_GET_FIRST_CAPTURE_AFTER_ANCHOR", "anchor found");
					last;  # exits this INNER while loop
				}
			}
		} elsif	($sType eq "CAPTURE"){   # a string to be found, something to capture
			if ($oStProc->isState("ST_GET_FIRST_CAPTURE_AFTER_ANCHOR")) {
				$oStProc->setState("ST_GO_ON", "first capture after ANCHOR");
				$oConvData->markAsRestartBlock();
			}	
			while ($bFindingCapture) {
				$sWellLine = getNextWellLine();
				if ($sWellLine eq "EOF") { 
					$oStConv->setState("ST_GET_NEXT_CONV_BLOCK"," well file ended");
					$oStWell->setState("ST_GOTO_FIRST_WELL_LINE"," well file ended");
					last;   # exits this INNER while loop
				}
				#if (@asCaptures = ($sWellLine =~ /$sRegex/)) {
				($bStatus, $rasCaptures) = tryRegexCaptureMatch($sWellLine,$sRegex);
				if ($bStatus == 1) { 
					saveCaptures($rasCaptures, $rasCaptureSymbols, \%hValBySym);
					if ($$rasReportTemplates[0] ne "NONE") {
						fillAndOutputTemplates(\%hValBySym, $rasReportTemplates); 
						if ("EOF" eq peekNextWellLine() ) {
							$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","EOF met");
							$oStWell->setState("ST_GOTO_FIRST_WELL_LINE", "EOF met");
						} else {
							$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","output done");
							#$oConvData->goToRestartBlock();
						}
					}	else {  # just capture and store for later use
						$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","capture regex without following report templates in same topic");
					}
					$oStConv->setState("ST_GET_NEXT_CONV_BLOCK"," report output done");
					last;
				} 
			}
		} elsif ($sType eq "REPORT"){  # nothing to find or capture, just output previous captures
			if ($$rasReportTemplates[0] ne "NONE") {
				fillAndOutputTemplates(\%hValBySym, $rasReportTemplates); 
			} else {
				TRACE("error with '$sType' but no report templates");
			}
		} elsif ($sType eq "TOPIC"){
			TRACE("config action block type is '$sType' so just continue");
			$oStConv->setState("ST_GET_NEXT_CONV_BLOCK","???");
		} else {
			TRACE("invalid config action block type: '$sType'");
			last;
		}
	} #...while well file
	TRACE("well file [$sWellFileFullName] processing ended");
}	
TRACE("moor file processing ended");

tryInsertFile($fhFOOTER_FILE, $fhRESULT_FILE, "Footer");
closeAllRoleFiles(@afhROLE_FILES);  #
print "see configuration file '".assureFullFileName($sConfigFile, getAppPath())."'\n";

TRACE_END("the end");


