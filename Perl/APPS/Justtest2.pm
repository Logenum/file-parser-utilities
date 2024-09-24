
package StateVault;
use v5.20;
#===============================================================================
sub new { my $class = shift;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();  # note: these state methods are in different package than TRACE methods
	my $sState = shift;
	my $sContext = shift;
	
	my $self = {
		stState => $sState, 	# initial state
		stPrevState => $sState, # initial state
		context => $sContext, 	# that thing whose states are changed
		
	};
	bless $self, $class;
	PERL_SCRIPTS::TRACE("'$sContext': '$sState' by 'initialization'");
	PERL_SCRIPTS::TRACE_RET();
	return $self;
}

# TODO: make generic state saving object (with TRACES) which can be instantiated to all flag-alike purposes 

#===============================================================================
sub setState { my ($self, $sNewState, $sEvent) = @_;   # generic function for changing processing state
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	$self->{stPrevState} = $self->{stState};
	$self->{stState} = $sNewState;
	my $sContext = $self->{context};
	PERL_SCRIPTS::TRACE("'$sContext': '$sNewState' by '$sEvent'");
	PERL_SCRIPTS::TRACE_RET();	
}
#===============================================================================
sub getState { my ($self) = @_;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $sState = $self->{stState};
	my $sContext = $self->{context};
	PERL_SCRIPTS::TRACE("'$sContext': '$sState'");
	PERL_SCRIPTS::TRACE_RET();
	return $sState;
}
#===============================================================================
sub isState { my ($self, $sIsState) = @_; 
#===============================================================================
	#PERL_SCRIPTS::TRACE_SUB();
	my $bStatus;
	my $sState = $self->{stState};
	my $sContext = $self->{context};	
	if ($sState eq $sIsState) {
	#	PERL_SCRIPTS::TRACE("'$sContext': is '$sState'");
		$bStatus = 1;
	}  else {
	#	PERL_SCRIPTS::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 0;
	}
	#PERL_SCRIPTS::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub isNotState { my ($self, $sIsNotState) = @_; 
#===============================================================================
	#PERL_SCRIPTS::TRACE_SUB();
	my $bStatus;
	my $sState = $self->{stState};
	my $sContext = $self->{context};	
	if ($sState ne $sIsNotState) {
		# PERL_SCRIPTS::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 1;
	}  else {
		#PERL_SCRIPTS::TRACE("'$sContext': is '$sState'");
		$bStatus = 0;
	}
	#PERL_SCRIPTS::TRACE_RET();
	return $bStatus;
}	

#===============================================================================
sub isPrevState { my ($self, $sIsState) = @_; 
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $bStatus;
	my $sPrevState = $self->{stPrevState};
	my $sContext = $self->{context};	
	if ($sPrevState eq $sIsState) {
		PERL_SCRIPTS::TRACE("'$sContext': is '$sPrevState'");
		$bStatus = 1;
	}  else {
		PERL_SCRIPTS::TRACE("'$sContext': is NOT '$sPrevState'");
		$bStatus = 0;
	}
	PERL_SCRIPTS::TRACE_RET();
	return $bStatus;
}
# END OF CLASS

#-----------------------------------------------------------------------------------------
package ConvData;
use Data::Dumper;
#===============================================================================
sub new { my $class = shift;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();  # note: these state methods are in different package than TRACE methods
	my $raoh_ConvData 	= shift;
	my $sContext 		= shift;
	my $self = {
		AllConvBlocks => $raoh_ConvData,
		RestartPos => 0, # typically first capture block within focus topic
		CurrentPos => -1,  # after first 'getNextBlock' -call points to block 0
		context => $sContext, 	
	};
	bless $self, $class;
	PERL_SCRIPTS::TRACE("'$sContext': 'initialization'");
	PERL_SCRIPTS::TRACE("all conv blocks: ".Dumper($raoh_ConvData));
	PERL_SCRIPTS::TRACE_RET();
	return $self;
}

#===============================================================================
sub goToFirstBlock { my ($self) = @_;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	$self->{CurrentPos} = -1;
	PERL_SCRIPTS::TRACE_RET();
	return;
}
#===============================================================================
sub getNextBlock { my ($self) = @_;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();

	my @aoh_allConv = $self->{AllConvBlocks};
	my $raoh_allConv = \@aoh_allConv;
	my $nCurrentPos = $self->{CurrentPos};
	my $nNextPos = $nCurrentPos + 1;
	
	my $rh_SingleConvBlock = $raoh_allConv->[0]->[$nNextPos];
	PERL_SCRIPTS::TRACE("conv block from pos '$nNextPos': ".Dumper($rh_SingleConvBlock));
	#PERL_SCRIPTS::TRACE("single conv block at pos '$pos': ".Dumper($raoh_allConv->[0]->[$pos]));
	$self->{CurrentPos} = $nNextPos;
	PERL_SCRIPTS::TRACE_RET();
	return $rh_SingleConvBlock;
}

#===============================================================================
sub goToRestartBlock { my ($self) = @_;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $nPos = $self->{RestartPos} - 1;
	$self->{CurrentPos} = $nPos;
	PERL_SCRIPTS::TRACE("pos=$nPos");
	PERL_SCRIPTS::TRACE_RET();
	return;
}

#===============================================================================
sub markAsRestartBlock { my ($self) = @_;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $nPos = $self->{CurrentPos};
	$self->{RestartPos} = $nPos;
	PERL_SCRIPTS::TRACE("pos=$nPos");
	PERL_SCRIPTS::TRACE_RET();
	return;
}

#/////////////////////////////////////////////////////////////////////////
package SupplyFile;
use Data::Dumper;

#===============================================================================
sub new { my $class = shift;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();  # note: these state methods are in different package than TRACE methods
	my $sFileName 	= shift;
	my $sPath 		= shift;
	my $sContext 	= shift;
	my $fhTmp;
	my $sFullFileName;
	my $result;
	# class for creating "input-file" -objects
	
	PERL_SCRIPTS::TRACE("path/file/context = '$sPath'/'$sFileName'/'$sContext'");
	$sFullFileName = PERL_SCRIPTS::assureFullFileName($sFileName, $sPath);
	my $self = {
		FileName => $sFullFileName,
		fhSupply => $fhTmp,
		context => $sContext,
		asFileContents => [],  # anonymous array
		pos => 1,		
	};
	$result = open($fhTmp, "<", $sFullFileName);
	if ($result) {
		PERL_SCRIPTS::TRACE("'file '$sFullFileName' open SUCCEEDED");
		PERL_SCRIPTS::TRACE("read all file array");
		@{$self->{asFileContents}} = <$fhTmp>;
		push(@{$self->{asFileContents}}, "EOF");
		PERL_SCRIPTS::TRACE("close file");
		close $fhTmp;
	} else {
		PERL_SCRIPTS::TRACE("file '$sFullFileName' open FAILED");
	}	
	bless $self, $class;	
	PERL_SCRIPTS::TRACE_RET();
	return $self;
}

#===============================================================================
sub getNextLine { my ($self) = @_; 
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();

	PERL_SCRIPTS::TRACE_RET();
}

#===============================================================================
sub close { my ($self) = @_; 
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $sFile = $self->{FileName};
	my $handle = $self->{fhReport};
	PERL_SCRIPTS::TRACE("close '$sFile'/'$handle'");
	close $handle;
	if ( -e $sFile) {
	} else {
		PERL_SCRIPTS::TRACE("file '$sFile'/'$handle' does NOT exist !!!");
	}
	PERL_SCRIPTS::TRACE_RET();
}


#/////////////////////////////////////////////////////////////////////////
package ReportFile;
use Data::Dumper;


#===============================================================================
sub new { my $class = shift;
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();  # note: these state methods are in different package than TRACE methods
	my $sFileName 	= shift;
	my $sPath 		= shift;
	my $sContext 	= shift;
	my $fhTmp;
	my $sFullFileName;
	my $result;
	
	PERL_SCRIPTS::TRACE("path/file/context = '$sPath'/'$sFileName'/'$sContext'");
	$sFullFileName = PERL_SCRIPTS::assureFullFileName($sFileName, $sPath);
	
	#open(OUT_FILE, ">", $sFileName) or die "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
	$result = open($fhTmp, ">", $sFileName);
#=comment
	#$result = open($fhTmp, ">", $sFileName);
	#$result = open($fh_InternalGraphFile, ">", $sFileName);
	PERL_SCRIPTS::TRACE("Report file '$sFullFileName' open result = '$result'");
=comment
	if ($result) {
		PERL_SCRIPTS::TRACE("Report file '$sFullFileName' open SUCCEEDED");
	} else {
		PERL_SCRIPTS::TRACE("Report file '$sFullFileName' open FAILED");
	}	
=cut
	#print OUT_FILE "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n";
	#close OUT_FILE;
	
	my $self = {
		FileName => $sFullFileName,
		fhReport => $fhTmp,
		context => $sContext, 	
	};
	bless $self, $class;	
	PERL_SCRIPTS::TRACE_RET();
	return $self;
}

#===============================================================================
sub write { my ($self, $sLine) = @_; 
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $sFile = $self->{FileName};
	my $handle = $self->{fhReport};
	PERL_SCRIPTS::TRACE("write '$sLine' to '$sFile'/'$handle'");
	print $handle "$sLine\n";
	if ( -e -f -w $sFile) {
	} else {
		PERL_SCRIPTS::TRACE("writable file '$sFile'/'$handle' does NOT exist !!!");
	}
	PERL_SCRIPTS::TRACE_RET();
}

#===============================================================================
sub close { my ($self) = @_; 
#===============================================================================
	PERL_SCRIPTS::TRACE_SUB();
	my $sFile = $self->{FileName};
	my $handle = $self->{fhReport};
	PERL_SCRIPTS::TRACE("close '$sFile'/'$handle'");
	close $handle;
	if ( -e $sFile) {
	} else {
		PERL_SCRIPTS::TRACE("file '$sFile'/'$handle' does NOT exist !!!");
	}
	PERL_SCRIPTS::TRACE_RET();
}

#------------------------------------------------------------------------------------------
package PERL_SCRIPTS;
use v5.20;
### the name of this file means that it contains local utilities
#	= functions used by scripts of THIS directory
my $var;
use Data::Dumper;
{
  local $Data::Dumper::Terse = 1;
  local $Data::Dumper::Indent = 1;
  local $Data::Dumper::Useqq = 1;
  local $Data::Dumper::Deparse = 1;
  local $Data::Dumper::Quotekeys = 0;
  local $Data::Dumper::Sortkeys = 1;
  warn Dumper($var);
}

#use Switch;
use feature "switch";
use FileHandle;

# note: caller files shall contain lines: "package PERL_SCRIPTS;" and "use LOCUTILS;"
 
################################################################################
my $fhTRACE_LOG;  # file handle
my $fhOUT_FILE; # file handle
my $g_sAppPath;

my @asAllOutLines=(); 		# for chechking, if something has already been written out
my $sTRACE_FILE_NAME;
my $nTraceIndentPos;
my $sTraceIndentBar="";
my @aCommentTexts;
my @afhFILE_HANDLES=();

#===== for conversion configuration file =========
my @aasConfItems=();
my @asConvConfLines;
my $nConfLinePos=0;  # for initial file-read processing phase
my $nConfItemPos=0; 
my $nFocusTopicConfItemPos=0;
#----- for result file additional info purposes ----
my $sFocusConvTopicName= "UNKNOWN";
my $sPrevConvTopicName= "UNKNOWN";
#---------------------------------------------------
my $nFocusTopicFirstCaptureConfItemPos=0;
my $nLastConfItemPos=0;
#-------------------------------------------------
#=====  for moor file =======================
my @asMoorFileActiveLines;
my $nMoorFileActiveLinePos;
my $nMoorFileActiveLinesLastPos;
#--------------------------------------------------

#=====  for each well line =======================
# maybe it would be better to store only active lines of well file ???
my $sCurrentWellFileFullName;
my @asWellFileLines;
my $sPrevWellFileFullName;  
my $nWellLinesLastPos;
my $nWellFileLinePos;
#--------------------------------------------------
my $sResultFileName;  # saved for TRACE purposes
my @asFileAllLinesTmp;  # raw input before filtering commented etc. stuff out

#my $FILE_HANDLE;
my $DELIM_STR = '%';
my $sNOTETAB_OUTLINE_FILE_TOP_LINE = "= V5 Outline MultiLine NoSorting TabWidth=30";
my $sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING = "H=\"Trace File Contents\"";

my $NOT_IN_USE = 0;

my $cSPACE_CHAR = " ";

my $sPlainSubrPrev = "";  # for TRACE usage
#===== for main state machine ====================
my $ST_SOME_PROCESSING_STATE = "ST_UNKNOWN";
my $ST_SOME_PREV_PROCESSING_STATE = "ST_UNKNOWN";
#-------------------------------------------------




my @aFixedFileRoleTags =  (	"< MOOR_FILE",   					# if missing, then fails
							"< CONV_CFG_OTL_FILE", 				# if missing, then fails  
								# -	capture and report defs in same file
							"< PHRASE_CFG_OTL_FILE", 			# if missing, then skipped  
								# - for possible conversion of captured strings to final visible output strings
							"< HEADER_FILE", 					# if missing, then skipped
							"< INCLUDE_FILE",					# if missing, then skipped
							"> RESULT_FILE", 					# if missing, then fails
							# TODO: add Graphviz/Plantuml usage selection by the EXTENSION of result file name 
							"< FOOTER_FILE");					# if missing, then skipped
							
							
my %hFilesByRole=();   # for saving file names for report and trace usages
							
#================================================================
sub setAppPath { my ($sAppPath) = @_;
#================================================================
	TRACE_SUB();
	$g_sAppPath = $sAppPath."\\";
	TRACE("path='$g_sAppPath'");
	TRACE_RET();
}	
#================================================================
sub getAppPath { 
#================================================================
	TRACE_SUB();
	TRACE("path='$g_sAppPath'");
	TRACE_RET();
	return $g_sAppPath;
}	

#================================================================
sub getFileNameByRole { my ($sRole) = @_;
#================================================================
	TRACE_SUB();
	my $sFileFullName = $hFilesByRole{$sRole};
	TRACE("role '$sRole' file is '$sFileFullName'");
	TRACE_RET();
}					
#=================================================================
sub openAllRoleFilesByCfgFile { my ($sCfgFileName) = @_;
#================================================================
	my $sLine;
	my %hConfFileItems;
	my $sFileRoleTAG, 
	my $sRoleFileName;
	my $sRoleFileFullName;
    my @afhFILE_HANDLES;  # each item will have handle or zero
	my $bGoodbye 	= 0;
	my $bSucceeded	= 0;   # initial quess
	my $nHandlePos 	= 0;
	my $sResFileExt = "";
	my $arrowDir;
	my $sFileNameAsSym;
	my $sFileNameAsLbl;
	
	TRACE_SUB();
	
	my $oGraphvizDiagram = new ReportFile("C:/job/neteye/FileConverter.txt","","init");   # note: path name requires forwards slashes here !!!!??
	
	$oGraphvizDiagram->write("digraph FileConverter  {");
	$oGraphvizDiagram->write("rankdir=\"LR\"");
	my $sTheScript = "FileConverter";
	
	$oGraphvizDiagram->write("$sTheScript [label=\"$sTheScript\", shape=\"ellipse\", size=\"2\"]");
	
	unless (open (CFG_FILE, "<$sCfgFileName") ) {
		 TRACE("input config fh file '$sCfgFileName' open FAILED"); 
	} else {
		TRACE("input config file '$sCfgFileName' open SUCCEEDED"); 
	}
	
	my @asConfFileLines = <CFG_FILE>;
	TRACE("collects name and role of each file listed in configuration file");
	foreach my $sConfLine (@asConfFileLines) {
		if (checkIfIgnoreLine($sConfLine)) {next;}  # empty or fully commented lines etc.
	
		if ($sConfLine =~ /^\s*(\w+)\s*\=\s*(\S+)\s*/g) {
			my $sSuggestedFileRoleTAG = $1;
			TRACE("role file opening candidate found '$2'");
			$sRoleFileName = removePossibleFrameBrackets($2);
			$hConfFileItems{$sSuggestedFileRoleTAG} = $sRoleFileName;
			#TRACE("role file opening candidate found '$sRoleFileName'");
		} else {
			#TRACE("line '$sConfLine' is not a file open operation line"); 
		}
		#TRACE("$sFileRoleTAG => $sFileName");
	}
	#-----------------------------------------------------
	TRACE("tries to get file name for each fixed file role");
	foreach my $sFixedRawTag (@aFixedFileRoleTags) {
		#TRACE("tag item: '$sFixedRawTag'");
		my ($sFixedOpenType, $sFixedFileRole) = ($sFixedRawTag =~ /\s*(\S*)\s*(\w+)/g);
		$bSucceeded=0;
		TRACE("tries to get file name for file role '$sFixedFileRole' (open type = '$sFixedOpenType')");
		foreach my $sSuggestedFileRole (keys %hConfFileItems) {
			if ($sFixedFileRole eq $sSuggestedFileRole) {
				my $sRoleFileName = $hConfFileItems{$sSuggestedFileRole};			
				$sRoleFileFullName = assureFullFileName($sRoleFileName, $g_sAppPath);
				$hFilesByRole{$sFixedFileRole} = $sRoleFileFullName;
				if (open ($afhFILE_HANDLES[$nHandlePos], $sFixedOpenType.$sRoleFileFullName) ) { # perl: file handles array for return
					TRACE("role '$sFixedFileRole' file [$sRoleFileFullName] open by '$sFixedOpenType' SUCCEEDED");  
					if ($sFixedFileRole eq  'RESULT_FILE') {
						$sResultFileName = $sRoleFileFullName;
						($sResFileExt) = ($sRoleFileName=~ /.*\.(\w+).*/g);  # note
						TRACE("result file extension = '$sResFileExt'");
						# - can be used to select Graphviz or PlantUML output line structures
					}
					if ($sFixedOpenType eq '>') {
						$arrowDir="forward";
					}
					if ($sFixedOpenType eq '<') {
						$arrowDir="back";
					}				
					$sFileNameAsSym = sym($sRoleFileFullName);
					$sFileNameAsLbl = lbl($sRoleFileFullName);
					$oGraphvizDiagram->write("$sFileNameAsSym [label=\"$sFileNameAsLbl\", height=\"1\", shape=\"box\"]");
					
					$oGraphvizDiagram->write("$sTheScript -> $sFileNameAsSym [dir=\"$arrowDir\"]");
					$sRoleFileName = "";
					$bSucceeded=1;
					
					
				}  else {
					TRACE("role '$sFixedFileRole' file '$sRoleFileFullName' open by '$sFixedOpenType' FAILED"); 
				}
			}
		}
		if ($bSucceeded == 0) {
			TRACE("role '$sFixedFileRole' file missing in configuration file");
			if ($sFixedFileRole eq 'RESULT_FILE')  {  # missing in configuration file
					$bGoodbye = 1;
			} elsif ($sFixedFileRole eq 'MOOR_FILE') {
					$bGoodbye = 1;
			} elsif ($sFixedFileRole eq 'CONV_CFG_OTL_FILE') {
					$bGoodbye = 1;
			} else {
				$afhFILE_HANDLES[$nHandlePos] = $NOT_IN_USE; 
				TRACE("role file '$sFixedFileRole' does not exist. so it is just ignored"); 
				$sRoleFileName = "";
			}
		}
		$nHandlePos++;
	} # ...foreach fixed role tags
	if ($bGoodbye == 1) {
		TRACE("stops execution due to missing role file");
	}
	
	$oGraphvizDiagram->write("}");
	$oGraphvizDiagram->close();
	TRACE_RET();
	return ($sResFileExt, $bGoodbye, @afhFILE_HANDLES);	# caller must access these in same order as in roles array
}


#================================================================
sub closeAllRoleFiles { my @afhFILES = @_;
#================================================================
	TRACE_SUB();
	foreach my $fhFILE (@afhFILES) {	
		if ($fhFILE != 0) {
			TRACE("close file '$fhFILE'");
			close ($fhFILE);
		}  else {
			TRACE("no closing for unopened file '$fhFILE'");
		}
	}
	TRACE_RET();
}
#==================================================================================
sub extractConvConfFile { my ($fhFile) = @_;
#==================================================================================
	my $bSkipCommentedTopicLines = 0;
	foreach(<$fhFile>) {
		my $sInLine = $_;
		if ($sInLine	=~ /.*Outline.*MultiLine.*/g) {next;}	# conversion configuration (otl) file badge
		if ($sInLine =~ /^H\=\"#.*\"/) {
			$bSkipCommentedTopicLines=1;
		} elsif ($sInLine =~ /^H\=\"\s*(\S).*\"/) {
			if ($1 ne '#') {
				$bSkipCommentedTopicLines=0;			
			}
		}
		if ($bSkipCommentedTopicLines==1) {next;}
		if (checkIfIgnoreLine($sInLine)) {next;}
		$sInLine = removePossibleLineEndComments($sInLine);
		$sInLine = trimTrough($sInLine);
		TRACE("picked conversion configuration line '$sInLine'");
		push (@asConvConfLines, $sInLine);
	}
	push (@asConvConfLines, "EOF");
}
#==================================================================================
sub getNextConvConfLine {
#==================================================================================
	my $sLine = $asConvConfLines[$nConfLinePos];
	$nConfLinePos++;
	return $sLine;
}


#==================================================================================
sub setFocusConvTopicName { my ($sTopicName) = @_;
#==================================================================================
	TRACE_SUB();
	TRACE("set to '$sTopicName'");
	$sFocusConvTopicName = $sTopicName;
	TRACE_RET();
}
#==================================================================================
sub getFocusConvTopicName {
#==================================================================================
	return $sFocusConvTopicName;
}
#==================================================================================
sub buildConvConfData { my ($fhFile, $sReportType) = @_;
#==================================================================================
	# TODO: output will be an array of arrays

	TRACE_SUB();	
	my $sOutLine;
	my $sInLine;
	my $sItemType = "";
	my @asConfItem=();
	my $bArrayReady;
	my @asCaptureSymbols;
	my $sFocusTopicName;
	
	my $oStConvPre = new StateVault("ST_GOTO_START", "Conversion File Data Preprocessing");
	
	extractConvConfFile($fhFile);
	
	while (1) {
		$sInLine = getNextConvConfLine();
		if ($sInLine eq "EOF") { goto END_ACTIONS;}
		if ($oStConvPre->isState("ST_CATCH_REPORT")) {
			if ($sInLine !~ /^(.*\$.*)/)  {  
				TRACE("save report collection");
				$oStConvPre->setState("ST_IDLE","...");
				push (@aasConfItems, [@asConfItem]);
				@asConfItem =();
			}
		}
		if ($oStConvPre->isState("ST_COLLECT_UP_TO_NEXT_TOPIC")) {
			while (1) {
				$sInLine = getNextConvConfLine();
				if ($sInLine eq "EOF") { goto END_ACTIONS;}
				if ($sInLine =~ /^H\=\"\s*(\S).*\"/) {
					TRACE("next topic found at line '$sInLine' when collecting topic lines");			
					push (@aasConfItems, [@asConfItem]);
					@asConfItem =();
					last; # exits this while loop
				} else {
					push(@asConfItem, $sInLine);
				}
			}
		}
		

		if ($sInLine =~ /^H\=\"(.*perl.*)\"/i) {  # eg. H="this is script (perl)"
			# collects lines up to next topic or file end
			$sItemType = "PERL";
			$sFocusTopicName = $1;
			
			@asConfItem = ($sItemType, $sFocusTopicName); 
			$oStConvPre->setState("ST_COLLECT_UP_TO_NEXT_TOPIC",$sInLine);
		} elsif ($sInLine =~ /^H\=\"(.*)\"/) {
			$oStConvPre->setState("ST_CATCH_TOPIC",$sInLine);
			$sItemType = "TOPIC";
			$sFocusTopicName = $1;
			
			@asConfItem = ($sItemType, $sFocusTopicName);
		} elsif ($sInLine eq $sReportType) {			# graphviz or PlantUML
			$oStConvPre->setState("ST_CATCH_REPORT",$sInLine);
			$sItemType = "REPORT";
			@asConfItem = ($sItemType);  				# sets subarray heading
		} elsif ($sInLine =~ /^\[\s*(.*\(.*\).*)/) {	# regex starts with '[' for blue color and contains at least one capture ( by '('...')')
			$oStConvPre->setState("ST_CATCH_MATCH",$sInLine);
			$sItemType = "CAPTURE";
			@asConfItem = ($sItemType, $1);
		} elsif ($sInLine =~ /^\[\s*(.*)/) {    		# regex starts with '[' for blue color and doesn't contain captures
			$oStConvPre->setState("ST_CATCH_ANCHOR",$sInLine);
			$sItemType = "ANCHOR";		
			@asConfItem = ($sItemType, $1);
			
		} elsif ($sInLine =~ /^(.*\$.*)/)  { 				# contains $-headed variables
			if ($oStConvPre->isState("ST_CATCH_REPORT")) {
				push(@asConfItem, $1);
			} else {
				$oStConvPre->setState("ST_CATCH_GROUP",$sInLine);
				$sItemType = "GROUP";
				$sInLine  	=~ s/\s//g;    # removes spaces
				@asCaptureSymbols = split('\$', $sInLine);
				shift @asCaptureSymbols; # for removing empty item caused by split
				@asConfItem = ($sItemType, @asCaptureSymbols);
			}
		} else { 
			#setState("ST_IDLE",$sInLine);
		}
		if ($oStConvPre->isNotState("ST_IDLE") and 
			$oStConvPre->isNotState("ST_CATCH_REPORT") and
			$oStConvPre->isNotState("ST_COLLECT_UP_TO_NEXT_TOPIC")) {
				push (@aasConfItems, [@asConfItem]);
				@asConfItem=();
		}
	}  # ... while
	END_ACTIONS: # perl label
	if ($oStConvPre->isState("ST_CATCH_REPORT")) {
		TRACE("file ended while collecting report lines");
		push (@aasConfItems, [@asConfItem]);
		@asConfItem =();
	}
	
	if ($oStConvPre->isState("ST_COLLECT_UP_TO_NEXT_TOPIC")) {
		TRACE("file ended while collecting lines");
		push (@aasConfItems, [@asConfItem]);
		@asConfItem =();
	}
	
	push (@aasConfItems, ["EOF"]); # for easier indication of file data end
	#TRACE("conversion configuration: \\\@aasConfItems ".Dumper(\@aasConfItems));
	TRACE_RET();
	# $nLastConfItemPos = $aasConfItems;
}

#================================================================
sub extractMoorFileContents{  my ($fhMoorFile) = @_;
#================================================================
	# filters out commented lines etc.
	my $sLine;
	
	@asFileAllLinesTmp = <$fhMoorFile>;
	foreach $sLine (@asFileAllLinesTmp) {
	   if (checkIfIgnoreLine($sLine)) {
			next;
	   } else {
			$sLine = removePossibleLineEndComments($sLine);
			push(@asMoorFileActiveLines, $sLine);
	   }
	}
	push(@asMoorFileActiveLines, "EOF");  # for easier indication of line data end
	#$nMoorFileActiveLineLastPos = @asMoorFileActiveLines - 1;   # last pos = length - 1
	$nMoorFileActiveLinePos = 0;
}

#================================================================
sub getMoorNext{  my ($fhMoorFile) = @_;
#================================================================	
	my $sLine;

	$sLine = $asMoorFileActiveLines[$nMoorFileActiveLinePos];
	$nMoorFileActiveLinePos = $nMoorFileActiveLinePos + 1;
	chomp $sLine;
	if ($sLine eq "EOF") {
		TRACE_SUB();
		TRACE("moor file line '$sLine' at pos '$nMoorFileActiveLinePos'");
		TRACE_RET();
	}
	return ($sLine);

}

#================================================================
sub openWellFileReadAllLines {  my ($sFileNameCand) = @_;
#================================================================
# maybe it would be better to store only active lines of well file ???
	my $fhWellFile;
	$sCurrentWellFileFullName = "NONE"; # initial quess: open will fail
	TRACE_SUB();
	if ( -e $sFileNameCand) {
		if (open ($fhWellFile, "<$sFileNameCand")) {  
			TRACE("file [$sFileNameCand] open succeeded");
				$sCurrentWellFileFullName = $sFileNameCand;
				
				@asWellFileLines = <$fhWellFile>;
				push (@asWellFileLines,"EOF");  # indicates file end
				#$nLastWellLinePos = @asWellFileLines - 1;  # max position = length - 1
		} else {
			TRACE("file '$sFileNameCand' open FAILED");
		}
	}  else {
		TRACE("'$sFileNameCand' is not an existing file name, so no open trial");
	}	
	TRACE_RET();
	return $sCurrentWellFileFullName;
}

#================================================================
sub goToFirstWellLine {
#================================================================
	TRACE_SUB();
	TRACE("file '$sCurrentWellFileFullName' ");
	TRACE_RET();
	$nWellFileLinePos=0;
}

#================================================================
sub getNextWellLine {
#================================================================
	my $sWellLine;
	TRACE_SUB();
	$sWellLine = $asWellFileLines[$nWellFileLinePos];
	chomp $sWellLine;
	TRACE("line '$sWellLine' at pos [$nWellFileLinePos] in file '$sCurrentWellFileFullName'");
	$nWellFileLinePos = $nWellFileLinePos + 1;
	if ($sWellLine eq "EOF") {
		#TRACE_SUB();
		#TRACE("line '$sWellLine' at pos [$nWellFileLinePos] in file '$sCurrentWellFileFullName'");
		#TRACE_RET();
	}
	TRACE_RET();
	return ($sWellLine);
}

#================================================================
sub stepBackWellLine {
#================================================================
$nWellFileLinePos = $nWellFileLinePos - 1;
}
#================================================================
sub searchNext { my ($sGoalRegex) = @_;
#================================================================
	TRACE_SUB();
	my $sWellLine="";
	my $sLinePos;
	my $sStatus="NOT_FOUND";
	my @asPossibleCaptures =();
	TRACE("goal regex: '$sGoalRegex'");
	while (1) {
		$sWellLine = getNextWellLine();
		if ($sWellLine eq "EOF") {
			$sStatus = "EOF";
			TRACE("well line: '$sWellLine'");
			last;			
		} else {
			if (@asPossibleCaptures = ($sWellLine =~ /$sGoalRegex/g)) {
				$sStatus = "MATCH";
				TRACE("$sStatus '$sGoalRegex' regex to '$sWellLine'");
				last;
			} else {
				TRACE("'$sGoalRegex' regex does NOT match to '$sWellLine'");
			}
		}
	}
	TRACE_RET();
	return ($sStatus, @asPossibleCaptures);  # returns EOF or matching line
}
#================================================================
sub searchNextUntil { my ($sGoalRegex, $sOverflowRegex) = @_;
#================================================================
	TRACE_SUB();
	my $sWellLine;
	my $sLinePos;
	my $sStatus="NOT_FOUND";
	my @asPossibleCaptures =();
	TRACE("goal regex: '$sGoalRegex' until '$sOverflowRegex'");
	while (1) {
		$sWellLine = getNextWellLine();
		if ($sWellLine eq "EOF") {
			$sStatus = "EOF";
			TRACE("well line: '$sWellLine', so stop searching");
			last;
		} else {
			if ($sOverflowRegex ne "N/A") {
				if ($sWellLine =~ /$sOverflowRegex/g) {
					stepBackWellLine();
					$sStatus = "UNTIL_REACHED";
					TRACE("$sStatus '$sOverflowRegex' regex to '$sWellLine'");
					last;
				}
			} 
			if (@asPossibleCaptures = ($sWellLine =~ /$sGoalRegex/g)) {
				$sStatus = "MATCH";
				TRACE("$sStatus '$sGoalRegex' regex to '$sWellLine'");
				foreach my $sCapture (@asPossibleCaptures) {
					TRACE("capture: '$sCapture'");
				}
				
				last;
			} else {
				#TRACE("'$sGoalRegex' regex does NOT match to '$sWellLine'");
			}

		}
	}
	TRACE_RET();
	return ($sStatus, @asPossibleCaptures);  # returns EOF or matching line with regex match group
}
#================================================================
sub peekNextWellLine {
#================================================================
	my $sWellLine;
	$sWellLine = $asWellFileLines[$nWellFileLinePos+1];
	if ($sWellLine eq "EOF") {
		TRACE_SUB();
		TRACE("well file '$sCurrentWellFileFullName' line '$sWellLine' at pos '$nWellFileLinePos'");
		TRACE_RET();	
	}
	return ($sWellLine);
}

#================================================================
sub getNextConfItem {
#================================================================
	my @asConfItem=();
	my $rasConfItem;
	my $sItemType;
	my @asItem=0;
	TRACE_SUB();
	$rasConfItem = $aasConfItems[$nConfItemPos]; # pushed arrays in arrays are REFERENCES
	#TRACE("conversion configuration: \@asConfItem  ".Dumper(@asConfItem));
	@asItem = @{$rasConfItem};	# getting array by dereferencing array reference
	$sItemType = shift(@asItem);  # reads and removes first item
	#TRACE("item type '$sItemType' at pos '$nConfItemPos'");
	if ($sItemType eq "EOF") {
		TRACE("item type '$sItemType' at pos '$nConfItemPos'");
	} else {
		TRACE("item type '$sItemType' at pos '$nConfItemPos'");
		$nConfItemPos = $nConfItemPos + 1;
		if ($sItemType eq "TOPIC") {
			$nFocusTopicConfItemPos = $nConfItemPos;
		}
	}
	#TRACE("conversion configuration: type/array  = '$sItemType'/".Dumper(@asItem));
	TRACE_RET();
	return ($sItemType, \@asItem)
}
#================================================================
sub peekNextConfItemType {
#================================================================
	TRACE_SUB();
	my $rasConfItem;
	my @asItem;
	my $sItemType;
	if (defined ($aasConfItems[$nConfItemPos+1])) {
		$rasConfItem = $aasConfItems[$nConfItemPos+1];
		@asItem = @{$rasConfItem};
		$sItemType = shift(@asItem);
	} else {
		$sItemType="OVERFLOW";
	}
	TRACE("'$sItemType' at pos '$nConfItemPos+1'");
	
	TRACE_RET();
	return $sItemType;
}
#================================================================
sub stepBackConfItem {
#================================================================
#  used if previous 'get next' is actually a 'peek' -alike 
	$nConfItemPos = $nConfItemPos - 1;
	TRACE_SUB();
	TRACE_RET();
}
# TODO: various high-level functions to navigate within conversion configuration items

#================================================================
sub buildAllConversionActionBlocks {
#================================================================
	my %h_ConvActBlock;
	my @aoh_AllConvActBlocks=();
	TRACE_SUB();
	while(1) {
		my ($sType, $sNextType, $sRegex, $rasCaptureSymbols, $rasReportTemplates, $sTopic) = getNextConversionActionBlock();
		$h_ConvActBlock{TopicName} 			= $sTopic;
		$h_ConvActBlock{BlockType} 			= $sType;
		$h_ConvActBlock{NextBlockType} 		= $sNextType;
		$h_ConvActBlock{CaptureRegex} 		= $sRegex;
		$h_ConvActBlock{CaptureSymbols} 	= $rasCaptureSymbols;
		$h_ConvActBlock{ReportTemplates} 	= $rasReportTemplates;
		#TRACE("conversion configuration: \\\$h_ConvActBlock ".Dumper(%h_ConvActBlock));
		push (@aoh_AllConvActBlocks, {%h_ConvActBlock});  # note: requites '{...}' to put hash into array
		%h_ConvActBlock=();
		if ($sType eq "EOF") {
			last;
		}
	}
	TRACE_RET();
	#TRACE("conversion configuration: \\\$raoh_ConversionActionBlocks ".Dumper(@aoh_AllConvActBlocks));
	return \@aoh_AllConvActBlocks;
}
#================================================================
sub getNextConversionActionBlock {
#================================================================
# return alternatives
# ANCHOR: match string. no groups or reports
# CAPTURE: match string, groups, report
# CAPTURE: match string, groups, no report
# REPORT: report, no match string, no groups
# PERL: script for 'eval' function
	TRACE_SUB();
	my $bCollectingBlock = 1;
	my $sType;
	my $sBlockType;
	my @asItem;
	my $rasItem;
	my $sFocusTopic = "";
	my $sRegex="NONE";   	# initial quess
	my @asCaptureSymbols=("NONE");  # initial quess
	my @asReportTemplates=("NONE");	# initial quess
	my $bFirstItemHandled = 0;
	
	while ($bCollectingBlock) {
		($sType, $rasItem) = getNextConfItem();
		if ($sType eq "EOF") { 
			if ($bFirstItemHandled == 0) {
				$sBlockType = $sType;
			} else {
				stepBackConfItem();
			}
			last;
		}   # note: 'last' causes loop termination, not 'exit' !!!!!!!
		if ($sType eq "TOPIC") {
			$nFocusTopicFirstCaptureConfItemPos = 0; # initialization at topic start
			$sBlockType = $sType;
			$sFocusTopic = shift @{$rasItem};
			setFocusConvTopicName($sFocusTopic);
			#$sFocusTopic = @{$rasItem}[0];
		} elsif ($sType eq "ANCHOR") {
			$sBlockType = $sType;
			$sRegex = @{$rasItem}[0];
			last;
		} elsif ($sType eq "PERL") {
			$sBlockType = $sType;
			$sFocusTopic = shift @{$rasItem};
			setFocusConvTopicName($sFocusTopic);
			@asCaptureSymbols = @{$rasItem};  # perl script as an array of lines
			last;
		} elsif ($sType eq "CAPTURE") {
			if ( $nFocusTopicFirstCaptureConfItemPos == 0) { # not yet set within focus topic
				$nFocusTopicFirstCaptureConfItemPos = $nConfItemPos;
			}
			$sBlockType = $sType;
			$sRegex = @{$rasItem}[0];
			($sType, $rasItem) = getNextConfItem();
			if ($sType eq "EOF") {
				stepBackConfItem();
				last;
			}
			if ($sType eq "GROUP") {
				 @asCaptureSymbols = @{$rasItem};
				 ($sType, $rasItem) = getNextConfItem();
				 if ($sType eq "EOF") {
					stepBackConfItem();				 
					last;
				 }
				 if ($sType eq "REPORT") {
					@asReportTemplates = @{$rasItem};
				 } else {  
					stepBackConfItem(); # 
				 }
				 last;
			} else {				
				TRACE("invalid type '$sType' after 'CAPTURE' from config pos [$nConfItemPos]");		
				last;
			}
		} elsif ($sType eq "GROUP") {			
				TRACE("invalid block start type '$sType' from config pos [$nConfItemPos]");
				last;
		} elsif ($sType eq "REPORT") {  # just "report"  (captures and groups are somewhere in earlier blocks)
			$sBlockType = $sType;
			@asReportTemplates = @asItem;
			last;
		} else {
			TRACE("invalid type '$sType' from config pos [$nConfItemPos]");
			last;
		}
		$bFirstItemHandled = 1;
	} # ...while
	
	my $sTopic = getFocusConvTopicName();
	my $nextBlockType = peekNextConfItemType();
	TRACE("return block type/next/regex/topic = '$sBlockType'/'$nextBlockType'/'$sRegex'/'$sTopic'");
	if ($asCaptureSymbols[0] ne "NONE") {
		TRACE("\@asCaptureSymbols: ".Dumper(@asCaptureSymbols));
	}
	if ($asReportTemplates[0] ne "NONE") {
		TRACE("\@asReportTemplates: ".Dumper(@asReportTemplates));
	}
	TRACE_RET();
	return ($sBlockType, $nextBlockType, $sRegex, \@asCaptureSymbols, \@asReportTemplates, $sTopic);
}



#================================================================
sub tryRegexCaptureMatch {  my ($sText, $sRegex, $sComment) = @_;
#================================================================
	my @asCaptures;
	my $bStatus = 1; # initial quess
	
	TRACE_SUB();
	if (@asCaptures = ($sText =~ /$sRegex/)) {
		TRACE("MATCH OK: '$sRegex' to '$sText'");
	} else {
		TRACE("match FAIL: '$sRegex' to '$sText'");
		$bStatus=0;
	}
	TRACE_RET();
	return $bStatus, \@asCaptures;
}

#================================================================
sub saveCaptures {  my ($ra_CapturedVals, $ra_CaptureSymbols, $rh_ValBySym) = @_;
#================================================================
	TRACE_SUB();
	my $i = 0;
	foreach my $sVal (@$ra_CapturedVals) {
		my $sKey = $$ra_CaptureSymbols[$i];
		$i++;
		TRACE("set '\$rh_ValBySym{$sKey} = $sVal'");
		$rh_ValBySym->{$sKey} = $sVal;
	}
	TRACE_RET();
}

#================================================================
sub fillAndOutputTemplates{  my ($rh_Values, $ra_Templates) = @_;
#================================================================
	my $sRawTemplate;
	my $sFilledTemplate;
	my $sSym;
	my $sVal;
	my $sFormatSymCandidate;
	my $sFormatLblCandidate;
	my $sValSymbolified;
	my $sValLabelified;
	
	TRACE_SUB();
	if ($$ra_Templates[0] ne "NONE") {
		foreach $sRawTemplate (@$ra_Templates) {
			TRACE("raw template: '$sRawTemplate'");
			$sFilledTemplate = $sRawTemplate;
			foreach $sSym (keys %$rh_Values) {
				$sVal= $rh_Values->{$sSym};
				$sFormatSymCandidate = $sSym.".sym";
				if ($sFilledTemplate =~ /^.*$sFormatSymCandidate/g) {
					$sValSymbolified = sym($sVal);
					$sFilledTemplate =~ s/\$$sFormatSymCandidate/ $sValSymbolified/g;
				}
				$sFormatLblCandidate = $sSym.".lbl";
				if ($sFilledTemplate =~ /^.*$sFormatLblCandidate/g) {
					 $sValLabelified = lbl($sVal);
					$sFilledTemplate =~ s/\$$sFormatLblCandidate/$sValLabelified/g;
				}	
				$sFilledTemplate =~ s/\$$sSym/$sVal/g;
			}
			
			if ($sFilledTemplate =~ /^.*\$.*/) {  # all fields are not filled
				TRACE("inadequately filled template '$sFilledTemplate' is NOT delivered");
			} else {
				TRACE("filled template: '$sFilledTemplate'");
				OUT($sFilledTemplate);  # graphviz, PlantUML or HTML
			}
		}
	} else {
		TRACE("error: templates missing");
	}
	TRACE_RET();
}

#================================================================
sub evaluatePerlScript { my ($ras_ScriptLines) = @_;
#================================================================
	TRACE_SUB();
	my $sWholeScript = join(' ', @$ras_ScriptLines);
	TRACE("try to evaluate perl script: ".$sWholeScript);
	eval $sWholeScript;
	if ($@) {
		TRACE ("error: eval script returned '$@'");
	} else {
		TRACE ("eval script succeeded");
	}
	TRACE_RET();
}
#================================================================
sub removePossibleFrameBrackets { my ($str) = @_;
#================================================================
	# for non-well files having possible notetab hyperlinks
	#TRACE_SUB();
	#TRACE("removes possible '[' and ']' from '$str'");
	$str =~ s/^\[//g;
	$str =~ s/\]$//g;
	#TRACE("result: '$str'");
	#TRACE_RET();
	return $str;
}
#================================================================
sub removePossibleLineEndComments { my ($sInStr) = @_;
#================================================================
	# for well and non-well files 
	my $sOutStr;

	if ($sInStr =~ /^(.*)#?.*/g) {   # line end '#' -comments
		$sOutStr = $1;
	}  elsif ($sInStr =~ /^(.*)\/\/?.*/g) {  # line end '//' -comments
		$sOutStr = $1;
	}  else {
		$sOutStr = $sInStr;
	}
	return $sOutStr
}

#==================================================================================
sub checkIfIgnoreLine { my ($sInLine) = shift;
#==================================================================================
	# for well and non-well files
		if ($sInLine 	=~ /^\s*$/) 					{return 1;}	# skips totally empty lines
		if ($sInLine 	=~ /^\s*\-.*/) 					{return 1;}	# skips 'french lines' starting lines
		if ($sInLine  	=~ /^\s*#.*/) 					{return 1;} 	# skips fully '#' -commented lines
		if ($sInLine	=~ /^\s*\/\/.*/) 				{return 1;} 	# skips fully '//' -commented lines
		return 0;
}
#==================================================================================
sub tryExtractFileName { my ($sLine) = shift;
#==================================================================================
	my $bFileExistency = 0; # initial quess
	my $sFileName ="";		# initial quess
	TRACE_SUB();
	if (checkIfIgnoreLine($sLine)) {
		TRACE("'$sLine' is NOT a file name");
	} else {
		$sLine = removePossibleLineEndComments($sLine);
		$sLine = removePossibleFrameBrackets($sLine);
		if ($sLine !~ /[^A-Za-z0-9\\\. _]/){
			TRACE("'$sLine' is NOT a file name");
		} else {
			$sFileName = $sLine;
			if ( -e $sLine) {
				TRACE("file '$sLine' exist");
				$bFileExistency = 1
			} else {
				TRACE("file '$sLine' does NOT exist");
			}
		}
	}
	TRACE_RET();
	return ($sFileName, $bFileExistency);
}

#==================================================================================
sub tryOpenFile{ my ($sLine) = shift;
#==================================================================================
	my $fhWellFile;
	TRACE_SUB();	
	my $sFileNameCand = removePossibleFrameBrackets($sLine);
	TRACE("possible file: '$sFileNameCand'");
	chomp $sFileNameCand;
	
	if ($sFileNameCand !~ /[^A-Za-z0-9\\\. _]/){
		TRACE("'$sFileNameCand' is not a valid file name");
		TRACE_RET();
		return 0;
	}

	if ( -e $sFileNameCand) {
		if (open ($fhWellFile, "<$sFileNameCand")) {  
			TRACE("file '$sFileNameCand' open succeeded");
		} else {
			TRACE("file '$sFileNameCand' open FAILED");
		}
	}  else {
		TRACE("'$sFileNameCand' is not an existing file name, so no open trial");
	}	
	TRACE_RET();
	return  ($fhWellFile);
}

#==================================================================================
sub openReadFile{ my ($sFileName) = @_;
#==================================================================================
	my $fhFile;
	TRACE_SUB();
	if (open ($fhFile, "<$sFileName")) {   # opens well file in well files file
		TRACE("file '$sFileName' open SUCCEEDED");
	} else {
		TRACE("file '$sFileName' open FAILED");
	}
	TRACE_RET();
	return ($fhFile);
}
#==================================================================================
sub openWriteFile{ my ($sFileName) = @_;
#==================================================================================
	my $fhFile;
	TRACE_SUB();
	if (open ($fhFile, ">$sFileName")) {   # opens moor file
		TRACE("file '$sFileName' open SUCCEEDED");
	} else {
		TRACE("file '$sFileName' open FAILED");
	}
	TRACE_RET();
	return ($fhFile);
}

#================================================================
sub checkIfExit { my ($sCriterion, $nLineNbr) = @_;
#================================================================
	
	if (($sCriterion eq "") or 
	($sCriterion eq '0') or 
	($sCriterion eq 'invalid')){
		TRACE_SUB();
		TRACE_END("end due to criterion '$sCriterion'  (L:$nLineNbr)");
		die;
	}
	
}
#==========================================
sub tryInsertFile { my ($fhSource, $fhTarget, $sComment) = @_;
#------------------------------------------
	TRACE_SUB();
	if ($fhSource) {   
		while (<$fhSource>) {
			print $fhTarget $_;
		}
		TRACE("$sComment file inserted");
	} else {
		TRACE("$sComment file not inserted");
	}
	TRACE_RET();
}		

#==========================================
sub WRITE_LINE { my ($fhTarget, $sLine) = @_;
#------------------------------------------
	if ($fhTarget) {   
		print $fhTarget $sLine."\n";
	} else {
		TRACE("$sLine not inserted");
	}
}		


#===============================================================================
sub  createWriteExternalFile{ my ($sFileName, $rAnyStruct, $sComment) = @_;
#===============================================================================
	TRACE_SUB();
	if (! open (WRITE_FILE, ">$sFileName")) {  
		TRACE("create write file '$sFileName' open FAILED");
	} else {
		#TRACE("$sComment: '$sFileName' ".$rAnyStruct);
		print WRITE_FILE "$rAnyStruct\n";
		close WRITE_FILE;
	}
	TRACE_RET();
}
#===============================================================================
sub  readAllExternalFile{ my ($sFileName) = @_;
#===============================================================================
	my @asFileContents;
	TRACE_SUB();
	if (! open (READ_FILE, "<$sFileName")) {  
		TRACE("read all file '$sFileName' open FAILED");
	} else {
		TRACE("read all file: '$sFileName'");
		@asFileContents = <READ_FILE>;
		close READ_FILE;
	}
	TRACE_RET();
	return @asFileContents;
}

#======================================================	
sub getIfActiveLine{ my ($sRawLine, $sCommentTag) = @_;
#======================================================	
		my $bStatus = 1; # initial quess: will pass
		my $sRetLine;
		chomp $sRawLine;
		
		$bStatus = 1; # initial quess non-commented text will be found
		
		#$MapLineNbr++;
		if ($sRawLine =~ (m/^\s*\n/)) { 						# empty line
			$bStatus = 0;	
		} elsif ($sRawLine =~ (m/^\s*$sCommentTag.*/)) {			# full comment line
			$bStatus =0;
		} elsif ($sRawLine =~ (m/^(.*)\$sCommentTag.*/)) {  	# comment at line end
			$sRetLine = $_;
		}  else {												# no comments at line
			$sRetLine = $sRawLine;
		}
	return ($bStatus, $sRetLine);
}	
#======================================================	
sub getModifierType { my $sTagWithType = shift;  # TODO: replace sceial char prefixes with ".str", ".sym" and ".txt" postfixes
#======================================================	
	my $sModifyType;
	if ($sTagWithType =~ m/\%\S+\%/) { # use saved value as a substitute
		$sModifyType="STRINGIFY";
	} elsif ($sTagWithType =~ m/\$\S+\$/) {
		$sModifyType="SYMBOLIFY";
	} elsif ($sTagWithType =~ m/\&\S+\&/) {  # symbolify saved value before using it as a substitute
		$sModifyType="TEXTIFY";	
	} else {  # error condition
		TRACE ("string '$sTagWithType' does not contain modifier tags" );
	}
	return $sModifyType; 
}

#=======================================================================================================
sub modifyByType { my ($sData, $nTag, $sType) = @_;
#=======================================================================================================
	my $sSubstitution;
	my $sSubstituted;
	if ($sType  =~ m/SYMBOLIFY/) {
		$sSubstitution =~ s/\W+/_/g;
		TRACE ("make SYMBOLIFICATION");
		$sSubstituted =~ s/\$$nTag\$/$sSubstitution/g;
	} elsif ($sType  =~ m/TEXTIFY/) {
		$sSubstitution =~ s/\W+/ /g;
		TRACE ("make TEXTIFICATION");
		$sSubstituted =~ s/\&$nTag\&/$sSubstitution/g;
	} elsif ($sType  =~ m/STRINGIFY/) {
		$sSubstitution =~ s/\"/ /g;
		$sSubstitution =~ s/\'/ /g;
		TRACE("make STRINGIFICATION");
		$sSubstituted =~ s/\&$nTag\&/$sSubstitution/g;
	} else {
		#print TRACE "NO MODIFICATIONS\n";
	}

	return $sSubstituted; 
}
# wrappers with trace logging
#-----------------------------------------------------------------------
sub push__ { my ($raItems, $newItem, $nLineNbr, $sComment)=@_;  # array reference as parameter
	my ($package1, $filename1, $line1, $subroutine1) = caller(1);  # note: getting caller info
	my ($package0, $filename0, $line0, $subroutine0) = caller(0);  # note: getting caller info
	
	##push($raItems, $newItem);
	
	TRACE("after ,$newItem' push: ".Dumper(@{$raItems})."  Line=$line1");
}	
#-----------------------------------------------------------------------
sub pop__{
	my ($raItems,$sComment)=@_;
	my $retItem = pop(@{$raItems});
	TRACE ("pop '$retItem' from array of: ");
	foreach my $item (@{$raItems}) {
		TRACE("'$item', ");
	}

	return $retItem;
}
#-----------------------------------------------------------------------
sub peek__ {
	my ($raItems)=@_; # array reference as input parameter
	my $retItem;
	if (@{$raItems} > 0) {
		$retItem = @{$raItems}[-1]; # dereferencing and indexing array reference
	} else {
		$retItem = "EMPTY";
	}
	TRACE("peek '$retItem'");
	return $retItem;
}
#-----------------------------------------------------------------------
sub hashSet__ {
	my ($rHash, $key, $val, $sNameComment)=@_;  	# hash reference as parameter
	$rHash->{$key} = $val;  			# updating a hash when has reference is available
	TRACE("set hash <$sNameComment> key/value  = '$key'/'$val'");
	###TRACE("<$sNameComment>{$key} = $val");
}
#-----------------------------------------------------------------------
sub hashGet__ {
	my ($rHash, $key, $sNameComment)=@_;	# hash reference as parameter
	my $val = $rHash->{$key};  	# accessing a hash when has reference is available
	if ($val eq "") {
		$val="EMPTY";
	}
	TRACE("$val = <$sNameComment>{$key}");
	return $val;
}
# -------------------------------------------------------------------------------
sub OUT_SET { 
	my ($fhOUT)=@_;
	# TODO: change comment line prefix to adapt according to Graphviz/PlantUML etc.
	$fhOUT_FILE = $fhOUT;
	print $fhOUT_FILE "//----------- ".getDateTime()."\n";
	
}
#--------------------------------------------------------------------------------
sub OUT_POST { 
	my ($fhOUT)=@_;
	close $fhOUT;
}
#--------------------------------------------------------------------------------
sub OUT_INI{ 
	my ($OutFileName)=@_;
	$OutFileName	=~s/\\/\//g;
	open($fhOUT_FILE, ">$OutFileName") || print "Cannot open output file '$OutFileName'\n";
}
#--------------------------------------------------------------------------------
sub OUT_END {  # 
	my ($fhOUT)=@_;
	close $fhOUT;
}
#---------------------------------------------------------------------------------
sub OUT { 
	my ($str)=@_; # required parentheses !!!
	push (@asAllOutLines, $str);
	TRACE_SUB();
	TRACE ("write '$str' to '$sResultFileName'");
	# TODO: comment start '//' is according to graphviz. change configurable also for PlantUML
	if ($sCurrentWellFileFullName ne $sPrevWellFileFullName) {
	    print $fhOUT_FILE "//---------- FILE [$sCurrentWellFileFullName]\n";
	}
	
	my $sConvConfFileFullName = $hFilesByRole{CONV_CFG_OTL_FILE};
	$sPrevWellFileFullName = $sCurrentWellFileFullName;
	#print $fhOUT_FILE "focus topic name: '$sFocusTopicName'\n";
	if ($sFocusConvTopicName ne $sPrevConvTopicName) {
	    print $fhOUT_FILE "//---------- CONV [$sConvConfFileFullName::$sFocusConvTopicName]\n";
	}
	$sPrevConvTopicName = $sFocusConvTopicName;
	TRACE_RET();
    print $fhOUT_FILE "$str \n";
}

#---------------------------------------------------------------------------------
sub OUT_ONCE { 
	my ($str)=@_; # 
	unless (grep $str, @asAllOutLines) {  # if already exists, then no output
		TRACE_SUB();
		push (@asAllOutLines, $str);
		TRACE ("write '$str' to '$sResultFileName'");
		print $fhOUT_FILE "$str \n";
		TRACE_RET();
	}
}
##################################################################################
#==============================================================
sub assureFullFileName { my ($sPossiblyPathlessFileName, $sPath) = @_;
#==============================================================
	my $sFullFileName;
	TRACE_SUB();
	my $sFileName = $sPossiblyPathlessFileName;
	if ($sFileName=~ /^s*\w\:/g) {
		$sFullFileName =  $sFileName;
		TRACE("file name '$sFileName' contains already full path");
	} else {
		#TRACE("file name is combination of '$g_sAppPath' and '$sFileName'");
		$sFullFileName =$sPath.$sFileName;
	}
	$sFullFileName =~ s/\\+/\//;  # possible backward slashes to forward slashes for more robust file openings
	if ( -e $sFullFileName) {
		
	} else {
		TRACE("file '$sFullFileName' does not exist");
	}
	TRACE_RET();
	return ($sFullFileName);
}

#==============================================================
sub assurePlainFileName { my ($sPossiblyPathedFileName) = @_;
#==============================================================
	TRACE_SUB();
	#my ($sPathlessFileName) = $sPossiblyPathedFileName =~ m/^.*([a-zA-Z0-9)$/
	#TODO: add code

	TRACE_RET();
}

#==============================================================
sub sym { 
#==============================================================
	my ($s)=@_;
	my $sSym;
	#TRACE_SUB();
	$sSym= asc($s);
	$sSym =~ s/\W/_/g;
	$sSym =~ s/^\d/_/g;
	if ($sSym eq "") {
		$sSym="EMPTY";
	#	TRACE("Error: symbol name is $sSym");
	}
	#TRACE("'$s' is converted to '$sSym'");
	#TRACE_RET();
	return $sSym;
}
#-----------------------------------------------------------------------
sub str {
	my ($s)=@_;
	$s= asc($s);
	$s=~ s/\\/\\\\\\\\/;
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: label is $s");
		return $s;
	}
	return $s;
}
#-----------------------------------------------------------------------
sub lbl  {
    my($s) = @_;
	my $sLbl;
	#TRACE_SUB();
    ###$sLbl= asc($s);
	$sLbl= $s;
	#TRACE("labellable string before modifications: '$sLbl'");
	$sLbl =~ s/\\/\\\\\\\\/g;
	#TRACE("labellable string after possible backslashes added printable: '$sLbl'");
	$sLbl =~ s/\\\\\\\\/\\\\\\\\ /g; # spaces added to make split candidate positions
	$sLbl =~ s/\//\/ /g;
	$sLbl =~ s/_/\_ /g;
	$sLbl =~ s/\"/ /g;
    #TRACE("labellable string after cutting spaces adding: '$sLbl'");

	if ($sLbl eq "") {
		$sLbl ="EMPTY";
		#TRACE("Error: label is $sLbl");
		return $sLbl;
	}
    my @Parts = split(/\s+/, $sLbl);
	
	my $maxPartLen = 32;
    my $ResultStr = "";
    my $NextStepPos = $maxPartLen;
    
    foreach (@Parts) {
        $ResultStr = $ResultStr." ".$_;
        my $TotalLen = length($ResultStr);
        
        if ($TotalLen > $NextStepPos) {
            $ResultStr      = $ResultStr.'\\\\n';
            $TotalLen       = length($ResultStr);
            $NextStepPos    = $TotalLen + $maxPartLen;
        }
    }
    #TRACE("labelled string before removing cutting spaces '$ResultStr'");
    $ResultStr =~ s/\\\\ /\\\\/g;  # to return non-splitted positions to original
	$ResultStr =~ s/\\n /\\n/g;  # to return non-splitted positions to original
	$ResultStr =~ s/\/ /\//g;
	$ResultStr =~ s/_ /\_/g;
	
	#TRACE("string '$s' labelled to '$ResultStr'");
	#TRACE_RET();
   	return $ResultStr;
}

#---------------------------------------------------------------------------------------
sub asc {
	my ($s)=@_;
	$s=~ s/\E4/a/g;   #note: editor "Encode in ANSI" selected
	$s=~ s/\C4/A/g;   #   - to disable graphviz error condition 
	$s=~ s/\F6/o/g;
	$s=~ s/\D6/O/g;
	$s=~ s/\E5/o/g;
	$s=~ s/\C5/O/g;
	return $s;
}
#----------------------------------------------------------------------------------------
sub trimTrough {
	# - removes all leading and trailing spaces
	# - converts remaining multiple spaces to single spaces
	my ($s)=@_;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	$s =~ s/\s+/ /; 
	return $s;
}
#----------------------------------------------------------------------------------------
sub trimRims {
	# - removes all leading and trailing spaces
	my ($s)=@_;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	return $s;
}
#---------------------------------------------------------------------------------------
sub TRACE_INIT
{
	my ($sName, $sComment) = @_;
	$sTRACE_FILE_NAME = $sName;
	open($fhTRACE_LOG,">$sTRACE_FILE_NAME") || print "Cannot open trace file '$sTRACE_FILE_NAME' for '$sComment'\n";
	
	TRACE($sNOTETAB_OUTLINE_FILE_TOP_LINE."\n\n".$sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING."\n\n");
	TRACE(getDateTime()."   ".$sComment);

}
#-----------------------------------------------------------------------
sub TRACE { my ($Comment,$rOption1) = @_; 
	
	my ($package1, $filename1, $line1, $subroutine1) = caller(1);  # note: getting caller info
	my ($package0, $filename0, $line0, $subroutine0) = caller(0);  # note: getting caller info
	my ($sPlainFile0) = ($filename0 =~ /.*\W+(\w+\.\w+)/g);
	my ($sPlainFile1) = ($filename1 =~ /.*\W+(\w+\.\w+)/g);
	if (!defined($rOption1)) {
		print $fhTRACE_LOG $sTraceIndentBar."$Comment              		$sPlainFile1:$line1\n";	
		
	} else {
		print $fhTRACE_LOG $sTraceIndentBar."--------------------------------------------------------------------\n";
		print $fhTRACE_LOG $sTraceIndentBar."TRACE DUMP:  "."$sPlainFile0:$line0/$Comment:".  Dumper($rOption1);
		print $fhTRACE_LOG $sTraceIndentBar."....................................................................\n";
	}
}
#-----------------------------------------------------------------------
sub TRACE_ARRAY{
	my ($Comment,@array) = @_;
	my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info

	#print TRACE("$Comment array:".\@array."\n");
	for my $item (@array) {
		print $fhTRACE_LOG "    $item\n";
	}				 
}

#-----------------------------------------------------------------------
sub TRACE_END {
	my ($sComment) = @_;
	TRACE($sComment);
	###TRACE("TRACE ended");
	close $fhTRACE_LOG; 
	print "see trace file '".assureFullFileName($sTRACE_FILE_NAME, $g_sAppPath)."'";
}
#-----------------------------------------------------------------------
sub TRACE_SUB {
	my ($package1, $filename1, $line1, $subroutine1) = caller(1);  # note: getting caller info
	my ($package0, $filename0, $line0, $subroutine0) = caller(0);  # note: getting caller info
	my ($sPlainSubr) = ($subroutine1 =~ /.*\:\:(.*)/g);
	
	if ($sPlainSubr !~ m/.*TRACE.*/g) {
		if (($subroutine1 eq "") or (!defined($subroutine1))) {
			$sPlainSubr = "MAIN";
		}
		print $fhTRACE_LOG $sTraceIndentBar.$sPlainSubr."()  -----------------------------------            $filename1:$line1 -> $filename0:$line0\n";
		$sPlainSubrPrev = $sPlainSubr;

	}
	# increases indent
	$nTraceIndentPos += 8;
	$sTraceIndentBar =  $cSPACE_CHAR x $nTraceIndentPos;
}
#-----------------------------------------------------------------------
sub TRACE_RET {
# decreases indent
	if ($nTraceIndentPos >= 8) {
		$nTraceIndentPos -= 8;
		$sTraceIndentBar = $cSPACE_CHAR x $nTraceIndentPos;
	} else {
		TRACE("ERROR: trace indent is '$nTraceIndentPos', so outdent prevented");
	}
}
#-----------------------------------------------------------------------
sub __ { # element of active commenting
	my ($Comment) = @_;
	if (!grep(/$Comment/, @aCommentTexts)) { # every active comment is written only once (to limit log output)
		push(@aCommentTexts, $Comment);
		TRACE($Comment);
	}
}
#===============================================================================
sub getDateTime__ {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my$sRet = "TIME $hour:$min:$sec";
	TRACE($sRet);
	
	return $sRet;
}

#===============================================================================
sub getDateTime {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my $sRet = "TIME $hour:$min:$sec";
	
	return $sRet;
}
1;
=deactivated stuff
# examples: dot -Tpng -o temp.png temp.dot
# http://www.thegeekstuff.com/2010/06/perl-array-reference-examples/
#======================================================	
sub extractMapLine{ my ($sLine, $MAP_SEPARATOR_TAG, $sCodeCommentStr) = @_;
#======================================================		
	my $sreMapLeftSide;
	my @aTagsRightSide; 
	my $bStatus;
	my $sRawRightSide;
	my $sPlainRightSide;
	
	###my $sAction = "ACT_SAVE_CONVERSION";   # initial quess: save gregex matches, but don't cause any output to result file 
	my $sAction = "ACT_WRITE_CONVERSION";   # initial quess: save gregex matches and write conversionresult file 
	# initial quess: will pass
	($bStatus, $sLine) = assureUsableLine($sRawLine, $sCodeCommentStr);
	my $sreLeftSide;
	my $stgRightSide;
	
	if ($sStatus) {
		($sRawLeftSide, $sRawRightSide) 	= split($sLine, $MAP_SEPARATOR_TAG);
		$sreMapLeftSide 	= trimRims($sRawLeftSide);
		$sPlainRighSide 	= trimRims($sRawRightSide);
		@aTagsRightSide 	= ($sPlainRighSide =~ m/[\%\$\&]([a-zA-Z1-9\=_]+)[\%\$\&]/g);
	}
	return ($bStatus, $sAction, $sreMapLeftSide, $sPlainRighSide, \@aTagsRightSide);
	# PLAN:
	# array_a = item_count + {item_a}
	# item_a = status +  action + left_Side + right_side + array_b
	# array_b = {right_side_tag} + tag_count
	}	
	   TRACE ("DUMP stuff", @stuff);
	
	# while($sTopicName ne "") {
		#$sTopicName  = @{$rAllCaptureItems[$nTopLevel][$nTopicLevel]{TopicName}};
		# my (@stuff)  = $rAllCaptureItems->[0];
		# TRACE( "dumper ",\@stuff);
		#TRACE("topic name = '$sTopicName'");
		# $nTopicLevel++;
	# }
	#my $sBar  = $raaaAllCaptureItems->[0][0][1]{Bar};
	#TRACE(" bar = '$sBar'");
	
	#my $nLineNbrCnt = @$rasWellFileLines;


	# for ($nlineNbr=0; $nLineNbr < $nLineNbrCnt; $nLineNbr++) {
		# $line = $rasWellFileLines->[$nLineNbr];
		
		##TRACE("line $line:$nLineNumber");
	
		
	# }
