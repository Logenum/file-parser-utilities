#package TraceUtils;   # no module name used ---> these functions can be called from application level without "<MODULE>::" prefix
use v5.20;

# TODO: add usage of TRACE.CFG file
my $sTRACE_LOG_FILE_DEFAULT_BODY = "TRACE";
my $sTRACE_LOG_FILE_EXT = "LOG";


my $nTraceIndentPos;
my $sTraceIndentBar="";
my $nTraceLocalIndentPos;
my $sTraceLocalIndentBar="";  # for creating indent hierarchy within a function
my $fhTRACE_LOG;  # file handle
my $fhTRACE_CFG;  # file handle
my $cSPACE_CHAR = " ";
my $sPlainSubrPrev = "";
my @aCommentTexts;
my $sNOTETAB_OUTLINE_FILE_TOP_LINE = "= V5 Outline MultiLine NoSorting TabWidth=30";
my $sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING_CORE = "Trace File Contents";
my $sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING_FRAME = "H=\"".$sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING_CORE."\"";
my $m_sAppPath;
my $m_nSubtraceLogFileOrderNbr=1;
my $m_nTraceBagLogFileTopicOrderNbr=1;
my $m_sTraceLogFileName;
my $m_sTraceLogFileNameBody;

my $m_sTraceBagLogFileName; # for collecting complex outputs in single file
my $m_sTraceCfgFileNameBody;
my $m_sTraceCfgFileNameExt;
my @m_asTraceOutputFilterRegexes;
my $sDEFAULT_TRACE_OUTPUT_FILTER_REGEX = "^.*";  # should match to all strings
my $m_bTraceLogOutputActive;
my $m_sPossibleFocusObjectTitle;  # TODO: add usage

#===============================================================================
sub TRACE_INIT { my ($sTraceCfgFileName, $sComment) = @_;
#===============================================================================
	$m_bTraceLogOutputActive = 1; # initial quess
	$m_sPossibleFocusObjectTitle = "";
	
	if ($sTraceCfgFileName ne "NONE") {
		open($fhTRACE_CFG,"<$sTraceCfgFileName");
		if ($fhTRACE_CFG) {  # existing trace configuration file name parameter given
			($m_sTraceCfgFileNameBody, $m_sTraceCfgFileNameExt) = ( $sTraceCfgFileName =~ /^(\w+)\.(\w+)/g);
			$m_sTraceLogFileNameBody = $m_sTraceCfgFileNameBody;
			$m_sTraceLogFileName = $m_sTraceLogFileNameBody.".".$sTRACE_LOG_FILE_EXT;
			@m_asTraceOutputFilterRegexes = <$fhTRACE_CFG>;
			
		} else {  # non-existing trace configuration file name parameter given
			@m_asTraceOutputFilterRegexes = ($sDEFAULT_TRACE_OUTPUT_FILTER_REGEX);
			$m_sTraceLogFileNameBody = $sTRACE_LOG_FILE_DEFAULT_BODY;
			$m_sTraceLogFileName = $sTRACE_LOG_FILE_DEFAULT_BODY.".".$sTRACE_LOG_FILE_EXT;	
		}
		
		$m_sTraceBagLogFileName = $m_sTraceLogFileNameBody."_BAG.".$sTRACE_LOG_FILE_EXT;
		open($fhTRACE_LOG,">$m_sTraceLogFileName") || print "Cannot open trace file '$m_sTraceLogFileName' for '$sComment'\n";
		TRACE($sNOTETAB_OUTLINE_FILE_TOP_LINE."\n\n".$sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING_FRAME."\n\n");
		TRACE(getDateTime()."   ".$sComment);
		TRACE("Trace output configuration, see [".$sTraceCfgFileName."]");
		my $sSubtraceLogFileNamesRegex = $m_sTraceLogFileNameBody."_*.".$sTRACE_LOG_FILE_EXT;
		TRACE("deletes subtrace files by pattern '$sSubtraceLogFileNamesRegex'");
		unlink glob $sSubtraceLogFileNamesRegex; # note: for deletion of files by wildcards
		TRACE("creates trace bag log file '$m_sTraceBagLogFileName'");
		# creates "parallel" trace file for collecting long outputs to notetab OTL topic sections
		open(TRACEBAG_LOG_FILE,">$m_sTraceBagLogFileName") || print "Cannot open tracebag file '$m_sTraceBagLogFileName'\n";
		print TRACEBAG_LOG_FILE "$sNOTETAB_OUTLINE_FILE_TOP_LINE\n\n";
		close TRACEBAG_LOG_FILE;
	}  else {   # no trace configuration file name parameter given at all
		$m_sTraceLogFileName = $sTRACE_LOG_FILE_DEFAULT_BODY.".".$sTRACE_LOG_FILE_EXT;	
		#print "Trace log file: '$m_sTraceLogFileName'";
		@m_asTraceOutputFilterRegexes = ($sDEFAULT_TRACE_OUTPUT_FILTER_REGEX);
		open($fhTRACE_LOG,">$m_sTraceLogFileName") || print "Cannot open trace file '$m_sTraceLogFileName' for '$sComment'\n";
		TRACE(getDateTime()."   ".$sComment);
		TRACE_END("given trace configuration file is not valid, so this trace log file is not updated after this comment");
		$m_bTraceLogOutputActive = 0;  # disables following trace operations
	}

}
#===============================================================================
sub TRACE { my ($Comment,$rOption1) = @_;
#=============================================================================== 
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	$nTraceLocalIndentPos = 0;
	$sTraceLocalIndentBar = ""; # initialization
	foreach my $sRegex (@m_asTraceOutputFilterRegexes) {
		if ($Comment =~ /$sRegex/g) {
			print $fhTRACE_LOG $sTraceIndentBar.$Comment."\n";
			last;
		}
	}
	if (defined($rOption1)) {
		TRACE_BAG($rOption1);
	}
}

#===============================================================================
sub TRACE_IND { my ($Comment,$rOption1) = @_;
#=============================================================================== 
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	
	$nTraceLocalIndentPos += 8;
	$sTraceLocalIndentBar =  $cSPACE_CHAR x $nTraceLocalIndentPos;
	foreach my $sRegex (@m_asTraceOutputFilterRegexes) {
		if ($Comment =~ /$sRegex/g) {
			print $fhTRACE_LOG $sTraceIndentBar.$sTraceLocalIndentBar.$Comment."\n";
			last;
		}
	}
	if (defined($rOption1)) {
		TRACE_BAG($rOption1);
	}
}
#===============================================================================
sub TRACE_WRITE { my ($sText) = @_;
#===============================================================================
	# each call creates individually named subtrace log file which is linked to trace log file
	# can be used to log long, complex text blocks such as perl dumper outputs and JSON structures. 
	# that keeps the main trace log file more compact
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	my $sSubtraceLogFileName = buildSubtraceLogFileName(caller(1));
	# subtrace log file name contains info of the creation code location

	open(SUBTRACE_LOG_FILE,">$sSubtraceLogFileName") || print "Cannot open subtrace file '$sSubtraceLogFileName'\n";
	print SUBTRACE_LOG_FILE $sText;
	close SUBTRACE_LOG_FILE;
	TRACE("created file [".$sSubtraceLogFileName."]");
	# - Notetab OTL file link syntax
}
#===============================================================================
sub TRACE_BAG { my ($sText, $sComment) = @_;
#======================================================$=========================
	# each call creates individually named topic into OTL syntax file
	# topic names are linked in trace log name
	# can be used to log long, complex text blocks such as perl dumper outputs and JSON structures. 
	# that keeps the main trace log file more compact
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	
	TRACE_SUB();
	my $sWholeText;
	my $sNewTopicHeading = buildTraceBagLogFileTopicHeading(caller(1));
	if (defined $sComment) {
		$sWholeText = "COMMENT: ".$sComment."\n\n".Dumper($sText);
		TRACE("'$sComment' [".$m_sTraceBagLogFileName."::".$sNewTopicHeading."]");
	} else {
		$sWholeText = Dumper($sText);
		TRACE("[".$m_sTraceBagLogFileName."::".$sNewTopicHeading."]");
	}
	TRACE_RET();
	open(TRACEBAG_FILE,">>$m_sTraceBagLogFileName") || print "Cannot open tracebag file '$m_sTraceBagLogFileName'\n";
	print TRACEBAG_FILE "\nH=\"$sNewTopicHeading\"\n\n";
	print TRACEBAG_FILE "[".$m_sTraceLogFileName."::".$sNOTETAB_OUTLINE_FILE_DEFAULT_TOPIC_HEADING_CORE."]\n\n";
	print TRACEBAG_FILE "$sWholeText\n";
	close TRACEBAG_FILE;	
}
#===============================================================================
sub TRACE_END { my ($sComment) = @_;
#===============================================================================
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	TRACE($sComment);
	###TRACE("TRACE ended");
	close $fhTRACE_LOG; 
	print "see trace file '".assureFullFileName($m_sTraceLogFileName, $m_sAppPath)."'";
}
#===============================================================================
sub TRACE_SUB { my ($sPossibleObjectTitle) = @_;
#===============================================================================
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	if (! defined($sPossibleObjectTitle)) {
		$m_sPossibleFocusObjectTitle ="";
	} else {
		$m_sPossibleFocusObjectTitle = "[$sPossibleObjectTitle].";
	}
	$nTraceLocalIndentPos = 0; # initialization
	$sTraceLocalIndentBar = ""; # initialization
	my ($package1, $sRelFilename1, $line1, $subroutine1) = caller(1);  # note: getting caller info
	my ($package0, $sRelFilename0, $line0, $subroutine0) = caller(0);  # note: getting caller info
	my ($sPlainSubr) = ($subroutine1 =~ /.*\:\:(.*)/g);
	my ($sFileName1) = ($sRelFilename1 =~ /.*\/(\w+\.\w+)/g);
	my ($sFileName0) = ($sRelFilename0 =~ /.*\/(\w+\.\w+)/g);
	if ($sPlainSubr !~ m/.*TRACE.*/g) {
		if (($subroutine1 eq "") or (!defined($subroutine1))) {
			$sPlainSubr = "MAIN";
		}
		my $sTmpStr = $sPlainSubr."()---------------------------------<>[".$sRelFilename0."::".$line0."^ L]  	<===      [".$sRelFilename1."::".$line1."^ L]\n";
		print $fhTRACE_LOG $sTraceIndentBar.$m_sPossibleFocusObjectTitle.$sTmpStr;
		$sPlainSubrPrev = $sPlainSubr;
	}
	# increases indent
	$nTraceIndentPos += 8;
	$sTraceIndentBar =  $cSPACE_CHAR x $nTraceIndentPos;
	$m_sPossibleFocusObjectTitle = "";
}
#===============================================================================
sub TRACE_RET {
#===============================================================================
	if ($m_bTraceLogOutputActive == 0) {
		return;
	}
	$nTraceLocalIndentPos = 0; # initialization
	$sTraceLocalIndentBar = ""; # initialization
# decreases indent
	if ($nTraceIndentPos >= 8) {
		$nTraceIndentPos -= 8;
		$sTraceIndentBar = $cSPACE_CHAR x $nTraceIndentPos;
	} else {
		TRACE("ERROR: trace indent is '$nTraceIndentPos', so outdent prevented");
	}
}
#===============================================================================
sub __ { 	my ($Comment) = @_;# element of active commenting
#===============================================================================
	if (!grep(/$Comment/, @aCommentTexts)) { # every active comment is written only once (to limit log output)
		push(@aCommentTexts, $Comment);
		TRACE($Comment);
	}
}
#===============================================================================
sub getDateTime {
#===============================================================================
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my $sRet = "TIME $hour:$min:$sec";	
	return $sRet;
}
#===============================================================================
sub getMinSecAsSym {
#===============================================================================
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my $sRet = $min."_".$sec;
	return $sRet;
}	
#===============================================================================
sub buildTraceBagLogFileTopicHeading { my ($package1, $filename1, $line1, $subroutine1) = @_;
#======================================================$=========================
	my $sHeading;
	my ($sFileName1) = ($filename1 =~ /.*\/(\w+\.\w+)/g);
	my $sNewTopicHeading = $m_nTraceBagLogFileTopicOrderNbr."_".$sFileName1."_".$line1."_".$subroutine1;
	$sNewTopicHeading =~ s/\:\://; # removes possible module name attached to subroutine name
	$sNewTopicHeading =~ s/MM//; 
	$m_nTraceBagLogFileTopicOrderNbr = $m_nTraceBagLogFileTopicOrderNbr + 1;
	return $sNewTopicHeading;
}
#===============================================================================
sub buildSubtraceLogFileName { my ($package1, $filename1, $line1, $subroutine1) = @_;
#======================================================$=========================
	my ($sFileName1) = ($filename1 =~ /.*\/(\w+\.\w+)/g);
	my $sSubtraceLogFileName = $m_sTraceLogFileNameBody."_".$m_nSubtraceLogFileOrderNbr."_".$sFileName1."_".$line1.".".$sTRACE_LOG_FILE_EXT;
	$m_nSubtraceLogFileOrderNbr = $m_nSubtraceLogFileOrderNbr + 1;
	return $sSubtraceLogFileName;
}
1;