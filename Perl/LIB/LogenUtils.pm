
#!/usr/bin/perl
package LogenUtils;   # same package name must be in application script

use vars qw($VERSION @ISA @EXPORT $PERL_SINGLE_QUOTE);
use strict;  # -obs: requires ALL variables defined before usage
use Cwd qw(abs_path);

#=comment
use Exporter;
use Data::Dumper;

@ISA = qw(Exporter);
# $A $B $C $D $E $F $G $H $I

# TODO: a perl script, which parses, subs, '$g_'-prefixed and $\w -symbols and builds the "@EXPORT" block (191212)
@EXPORT = qw($A $B $C $D $E $F $G $H $I $gPOS
			$g_sOTL_FILE_FIRST_LINE_MATCH_rgx
			$g_sOTL_TOPIC_NAME_CATCH_rgx
			$g_sDOT_GRAPH_HEADER_tpl
			$g_sDOT_NODE_PLOT_tpl
			$g_sDOT_NODE_ATTR_tpl
			$g_sDOT_EDGE_PLOT_tpl
			$g_sDOT_EDGE_ATTR_tpl
			$g_sOTL_TOPIC_LINK_CATCH_rgx
			$g_sDOT_GRAPH_FOOTER_tpl
			getDateTimeAsNtbFormat
			TRACE
			GRACE
			traceOtlHeading
			fileErrors
			openReadFile
			shedReadFile
			openWriteFile
			openAppendFile
			writeToFile
			fillWriteFile
			cramWriteFile
			INITLOGEN
			extractArguments
			QUITLOGEN
			sym
			str
			lbl
			asc
			trimThrough
			slashBw
			dutyH
			useH
			putH
			getH
			incH
			cloneH
			CATCH
			CATCHFIRST
			processTitleCaseTagsTemplate
			setState
			isState
			isStateNot
			setEvent
			produceEvent
			consumeIfEvent
			wasEvent
			wasEventNot
			setFlag
			resetFlag
			isFlag
			isFlagNot
			commentIfInvalidGraphvizLine
			KUKKUU
			);
#=cut

# IDEA: THIS "<BAG>" library module contains ALL utility functions for ANY file converter
# - earlier multiple-file, class-based solution was practically too complex for basically very short applications
# - these features can be manually copied to any language within couple days (Python, QT, C#, C-embedded, ...)
# - each application contains single file script, which calls THESE non-classy functions 
# - an application script contains hard-coded extraction regexes, extraction logic and hard-coded report templates
# -	if some generic feature emerges in application, it will be added in THIS library file 



# created 191112 
# -	first usage: utilities for "configured-by-Perl" (=hard coded), classless, single-function, Graphviz/PlantUML converter scripts
# TBD: collect and create more and more functions here
# -idea: trace file syntax is Notetab OTL file syntax
# global copies of local match variables

# "m_" prefixed are module variables (= NOT visible to application script)
# "g_" prefixed are global variables (= visible to application script)

####################################################################
#=============== MISC REGION =======================================
####################################################################
my $g_sKUKKUU = "KUKKUU";

my $Zero=0;
my $One=1;

my %m_hDefaultHash = ();
our $g_sFILE_NAME_BODY_CATCH_rgx = "^.*?(\\w+)\\.\\w+.*\$"; # -obs: "?" means non-greedy match

#####################################################################
#=============== DATE AND TIME REGION ===============================
#####################################################################

my $g_sScriptStartDateTime;

#=================================================================
sub getDateTimeAsNtbFormat   {
#=================================================================
	my @RawDateTime = localtime(time);	# note: these are built-in functions

	my $yy = $RawDateTime[5] - 100;  		# year since 1900
	if ($yy <= 9) {$yy = "0"."$yy";}

	my $mm = $RawDateTime[4] + $One;			# January is ZERO
	if ($mm <= 9) {$mm = "0"."$mm";}

	my $dd = $RawDateTime[3];
	if ($dd <= 9) {$dd = "0"."$dd";}

	my $hh = $RawDateTime[2];
	if ($hh <= 9) {$hh = "0"."$hh";}

	my $nn = $RawDateTime[1];
	if ($nn <= 9) {$nn = "0"."$nn";}

	my $ss = $RawDateTime[0];
	if ($ss <= 9) {$ss = "0"."$ss";}

	my $DateTime = "($yy$mm$dd-$hh$nn$ss)";
	return $DateTime;
}

#####################################################################
#=============== TRACE LOG REGION ===================================
#####################################################################
# -legend: trace log has notetab outline file syntax: it is simple and has few nice features (topics, hyperlinks, www-links and red/blue colorization)
# -legend: trace log file is created automatically and named peerly to name of the application script
my $g_sTRACE_OTL_FILE_FIRST_TOPIC_NAME =  "h=\"CONTENTS\"";
my $g_sTRACE_OTL_FILE_LAST_TOPIC_NAME =  "h=\"INFO\"";
my $g_pTRACE;
my $g_pGRACE; 	# graphviz trace file for application script internal usage

my $sLatestCallerSubroutine = "";
my $sEmptyReplacementOfSubroutine;

#=================================================================
sub TRACE {  my ($xTraceData, $sHeadingOpt)=@_;
#=================================================================
	my $sTraceLine;
	my $sTraceData;
	my $sArrayItem;
	my $sLinePrefix;

	my ($package0, $sRelFilename0, $line0, $sModuleAndSubroutine0) = caller(0);  # note: getting caller info
	my ($package1, $sRelFilename1, $line1, $sCallerModuleAndSubroutine) = caller($One);  # note: getting caller info
	
	if (defined $sHeadingOpt) {
		traceOtlHeading($sHeadingOpt);
	}
	# TBD: remove module name from subroutine name (because all are in trickbox.pm)
	$sRelFilename0 = slashBw($sRelFilename0);
	
	# my ($sSubroutine0)	=	($sModuleAndSubroutine0 =~ m/^.*\:\:(.*)/g); 
	my ($sCallerSubroutine)	=	($sCallerModuleAndSubroutine =~ m/^.*\:\:(.*)/g); 
	#print "caller subroutine: $sCallerSubroutine\n";
	
	if ($sCallerSubroutine eq $sLatestCallerSubroutine) { 
		$sLinePrefix = $sEmptyReplacementOfSubroutine;	  # repeated subroutine names are replaced by just indention
	} else {
		$sLinePrefix 		= $sCallerSubroutine."()";
		($sEmptyReplacementOfSubroutine = $sLinePrefix) =~ s/./ /g;  # saved for possible repeated subroutine name
	}
	#print "line prefix: $sLinePrefix\n";
	$sLatestCallerSubroutine = $sCallerSubroutine;
	
	my $sDataType = ref($xTraceData);
	
	if ($sDataType eq "HASH") {
		my $sKey;
		my $sVal;
		
		my $sDuty = $xTraceData->{"DUTY"};
		$sTraceData = "DUTY: '$sDuty' ";
		while ( ($sKey, $sVal) = each %$xTraceData) {
			if ($sKey ne "DUTY") {
				$sTraceData = $sTraceData."; $sKey:$sVal";
			}
		}
	} elsif ($sDataType eq "ARRAY") {
		foreach (@$xTraceData) {
			$sTraceData = $sTraceData." ----- $_";
		}
	} else {
		$sTraceData = $xTraceData;
		$sTraceData =~ s/\n//g;	# removes possible internal line feeds
	}
	
	my $sTraceLine =  "$sLinePrefix $sTraceData\t\t\t\t\t\t[$sRelFilename1::$line1^L] [$sRelFilename0::$line0^L]";
	
	print ($sTraceLine."\n");	 
	print $g_pTRACE $sTraceLine."\n";
}

#=================================================================
sub traceOtlHeading {  my ($sHeading)=@_;  # for "Trickbox" internal usage
#=================================================================
		my $sTraceLine = "\nH=\"$sHeading\"\n";
		print $g_pTRACE $sTraceLine."\n";
}



#####################################################################
#=============== FILE HANDLING REGION ===============================
#####################################################################
my $m_nFileErrors = $Zero;

my %m_hAllFiles;

#=================================================================
sub fileErrors {
#=================================================================
	return $m_nFileErrors;
}
#=================================================================
sub openReadFile { my($Name) = @_;
#=================================================================
	my $SOME_FILE; # note: variable capsulated in a function
	$Name=~s/\\/\//g;
	chomp $Name;

	if (open($SOME_FILE, "<$Name")) {
	
		TRACE("success to open read file: '$Name'");
	} else {
		TRACE("failed to open read file: '$Name'");
		$m_nFileErrors++;
	}
	$m_hAllFiles{$SOME_FILE} = $Name;
	return $SOME_FILE; # note: return capsulated value
}
#=================================================================
sub shedReadFile { my($Name) = @_;
#=================================================================
	my $SOME_FILE; # note: variable capsulated in a function
	$Name=~s/\\/\//g;
	chomp $Name;
	my @asFileContents;

	if (open($SOME_FILE, "<$Name")) {
		TRACE("success to open read file: '$Name'");
	} else {
		TRACE("failed to open read file: '$Name'");
		$m_nFileErrors++;
	}
	
	@asFileContents = <$SOME_FILE>; # returns array of file contents
	close $SOME_FILE;
	
	return @asFileContents;
}


#=================================================================
sub openWriteFile { my($Name) = @_;
#=================================================================
	my $SOME_FILE; # note: variable capsulated in a function
	$Name=~s/\\/\//g;
	chomp $Name;

	if (open($SOME_FILE, ">$Name")) {
		TRACE("success to open write file: '$Name'");
	} else {
		TRACE("failed to open write file: '$Name'");
		$m_nFileErrors++;
	}
	$m_hAllFiles{$SOME_FILE} = $Name;
	return $SOME_FILE; # note: return capsulated value
}
#=================================================================
sub openAppendFile { my($Name) = @_;
#=================================================================
	my $SOME_FILE; # note: variable capsulated in a function
	$Name=~s/\\/\//g;
	chomp $Name;

	if (open($SOME_FILE, ">>$Name")) {
		TRACE("success to open append file: '$Name'");
	} else {
		TRACE("failed to open append file: '$Name'");
		$m_nFileErrors++;
	}
	$m_hAllFiles{$SOME_FILE} = $Name;
	return $SOME_FILE; # note: return capsulated value
}

#=================================================================
sub writeToFile { my($sText, $fhFile) = @_;
#=================================================================
	my $sFileName = $m_hAllFiles{$fhFile};
	TRACE("($sFileName) $sText");
	print $fhFile $sText;
}
#=================================================================
sub fillWriteFile { my($Name, $raLines) = @_;
#=================================================================

}

#=================================================================
sub cramWriteFile { my($Name, $raLines) = @_;
#=================================================================

}

#####################################################################
#=============== DATA EXTRACTION REGION =============================
#####################################################################


#####################################################################
#=============== GRAPHVIZ REGION ====================================
#####################################################################

our $g_sDOT_GRAPH_HEADER_tpl = "digraph Cname{\n\n";
our $g_sDOT_GRAPH_FOOTER_tpl = "\n\n}\n\n";
our $g_sDOT_GRAPH_HEADER_MATCH_rgx = "^\\s*digraph\\s+\\S+\\s+{.*\$";

our $g_sDOT_NODE_PLOT_tpl 	= "Name [Label Anyattr Shape Height Width Color Style Fontsize Fontcolor Linewidth Fontname ". # -obs: string split to multiple lines
								"Fontsize Fillcolor]";
								# "Anyattr" tag can be used to give any combination multiple attributes at once
								
								
our $g_sDOT_EDGE_PLOT_tpl	= "Sname -> Tname [Label Anyattr Fontsize Dir Linetype Linewidth Headtype Tailtype Taillabel ". # -obs: string split to multiple lines
								"Headlabel]";
								# "Anyattr" tag can be used to give any combination multiple attributes at once


our $g_sDOT_NODE_ATTR_tpl 	= "node [Anyattr Shape Color]";	 # for setting default attributes for all nodes							
our $g_sDOT_EDGE_ATTR_tpl 	= "edge [Anyattr Fontsize Dir Linetype Linewidth]";  # for setting default attributes for all nodes	

my @asVALID_GRAPHVIZ_LINE_CHECK_rgx = 
			("^\\s*\\w+\\s*->\\s*\\w+\\s*\\[\\.*label\\.*\\]\\.*\$",   	# A -> B [label="foo"]
			"^\\s*(\\w+).*\\[\\.*label\\.*\\.*]\\s*\$");   				# A [label="foo"]
			
my @asINVALID_GRAPHVIZ_LINE_CHECK_rgx =    # TBD: add usage
			("^\\s*->.*\$",   		# missung source node
			"^\\s*\\[.*\$",    		# missing node name or edge node-pair part
			"^.*->\\s*\\[\$");  	#  missing target node			


#=================================================================
sub commentIfInvalidGraphvizLine { my ($sLine)=@_; 
#=================================================================
# to avoid syntax errors when running "dot.exe"
# to detect missing node names etc.
	my $sValidLine = $Zero;
	my $nPos=$Zero;
	$nPos = CATCHFIRST($sLine, \@asVALID_GRAPHVIZ_LINE_CHECK_rgx);
	if ($nPos = 0) {
		$sValidLine = "// $sLine";  # invalid line is commented
		TRACE("Invalid graphviz line commented: '$sValidLine'\n");
	} else {
		$nPos = CATCHFIRST($sLine, \@asINVALID_GRAPHVIZ_LINE_CHECK_rgx);
		if ($nPos > 0) {
			$sValidLine = "// $sLine";  # invalid line is commented
			TRACE("Invalid graphviz line commented: '$sValidLine'\n");
		} else {
			$sValidLine = $sLine;
			TRACE("valid graphviz line: '$sValidLine'\n");
		}
	}
	
	return $sValidLine;
}

#=================================================================
sub GRACE {  my ($sLabelFrame, $sFileNameOpt, $nLineNbrOpt)=@_;
#=================================================================
# -TBD: continue 200121 ###
	# convCasecoeLineToGraphvizLines($sLabelFrame, $sFileNameOpt, $nLineNbrOpt); 
	# "CASECOE" = Context/Activity/State/Event/Comment/Output/External
	#  - eg. "// <any text>" means comment for previous node

}
#####################################################################
#=============== PLANTUML REGION ===============================
#####################################################################

#####################################################################
#=============== NOTETAB REGION ===============================
#####################################################################
our $g_sOTL_FILE_FIRST_LINE_tpl 		= "= V4 Outline MultiLine NoSorting TabWidth=30";
our $g_sTopicName 						= "";
our $g_sTOPIC_NAME_tpl 					= "\nH=\"%HeadingName%\"\n\n";
our $g_sOTL_TOPIC_NAME_CATCH_rgx 		= "^H=\"(.*)\"\$";
our $g_sOTL_TOPIC_LINK_CATCH_rgx		= "^(.*)\[(.*)\](.*)\$"; 	
our $g_sOTL_FILE_TOPIC_LINK_CATCH_rgx	= "^(.*)[(.*)::(.*)](.*)\$";
our $g_sOTL_FILE_FIRST_LINE_MATCH_rgx = "^=\\s+V4\\s+Outline\\s+MultiLine.*";


###########################################################################
#============== PROGRAM LANGUAGE SPECIFIC DEFINITIONS REGION =========
###########################################################################

my @asCLangReservedWords=
	("auto","break","case","char","continue","default","do","double","else","extern","float","for",
	 "goto","if","int","long","register","return","short","sizeof","static","struct","switch","typedef",
	 "union","unsigned","while");

#####################################################################
#=============== ENTRY REGION =======================================
#####################################################################
#=================================================================
sub INITLOGEN {  my ($sScriptPlainName)=@_;
#=================================================================

# TBD: add trace file path reading from environment variable
	my $sScriptNameBody;
	my $sTraceFilesPathName = $ENV{'LOGEN_WORK_FILES_PATH'}; 
    #my $sScriptPath = abs_path($0);
	($sScriptNameBody) = ($sScriptPlainName =~ m/$g_sFILE_NAME_BODY_CATCH_rgx/g);  # cuts possible extension
	my $sTraceFileWholeName = $sTraceFilesPathName.$sScriptNameBody.".log";
	my $sGraceFileWholeName = $sTraceFilesPathName.$sScriptNameBody.".gvz";   # graphviz trace file
	#print $sScriptPlainName."\n";
	#print $sScriptNameBody."\n";
	#print $sTraceFilePlainName."\n";
	print ("Trace file used: '$sTraceFileWholeName'\n\n");
	$g_sScriptStartDateTime = getDateTimeAsNtbFormat();
	open($g_pTRACE, ">$sTraceFileWholeName")	|| print "Cannot open TRACE file $sTraceFileWholeName\n";
	print $g_pTRACE $g_sOTL_FILE_FIRST_LINE_tpl."\n\n";
	print $g_pTRACE $g_sTRACE_OTL_FILE_FIRST_TOPIC_NAME."\n\n";
	print $g_pTRACE "script started at $g_sScriptStartDateTime\n";
	
	
	# "GRACE" file is for Graphviz Triad Diagram or PlantUML Sequence Diagram
	open($g_pGRACE, ">$sGraceFileWholeName")	|| print "Cannot open GRACE file $sGraceFileWholeName\n";
	print $g_pGRACE $g_sDOT_GRAPH_HEADER_tpl."\n\n";
	
	
	my $m_rhFocusHash = \%m_hDefaultHash;
#=begin OUT	

#=cut	
	return $sScriptNameBody;
}
#=================================================================
sub extractArguments {  my ($raARGV)=@_;
#=================================================================
	my $nPos = $Zero;
	foreach (@$raARGV) {
		TRACE("ARGV[$nPos] = '$_'\n");
		$nPos++;
	}
	return @$raARGV;
}
#=================================================================
sub QUITLOGEN {  my ($sComment)=@_;
#=================================================================
	getDateTimeAsNtbFormat();
	print $g_pTRACE "\n\n".$g_sTRACE_OTL_FILE_LAST_TOPIC_NAME."\n\n";
	if (! $sComment) {
		$sComment = "no known errors";
	}
	
	print $g_pTRACE "Script termination status: $sComment\n";
	close $g_pTRACE;
 
	print $g_pGRACE "Script termination status: $sComment\n";
	close $g_pGRACE; 
	
	exit $One;
}

#####################################################################
#=============== STRING HANDLING REGION =============================
#####################################################################

#=================================================================
sub sym {  my ($s)=@_;
#=================================================================	
	my $s= asc($s);
	$s =~ s/\W/_/g;
	$s =~ s/^\d/_/g;
	if ($s eq "") {
		$s="EMPTY";
		TRACE(" symbol name is $s");
	}
	return $s;
}
#=================================================================
sub str { 	my ($s)=@_;
#=================================================================
	my $s= asc($s);
	$s=~ s/\\/\\\\\\\\/;
	if ($s eq "") {
		$s="EMPTY";
		TRACE("label is $s");
		return $s;
	}
	return $s;
}
#=================================================================
sub lbl  { my($s) = @_;
#=================================================================
    $s= asc($s);
	$s =~ s/\\/\\ /g; # spaces added to make split candidate positions
	$s =~ s/\//\/ /g;
	$s =~ s/_/\_ /g;
	$s =~ s/\"/ /g;
	
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: label is $s");
		return $s;
	}
    my @Parts = split(/\s+/, $s);
	
	my $maxPartLen = 32;
    my $ResultStr = "";
    my $NextStepPos = $maxPartLen;
    
    foreach (@Parts) {
        $ResultStr = $ResultStr." ".$_;
        my $TotalLen = length($ResultStr);
        
        if ($TotalLen > $NextStepPos) {
            $ResultStr      = $ResultStr.'\\n';
            $TotalLen       = length($ResultStr);
            $NextStepPos    = $TotalLen + $maxPartLen;
        }
    }
    $ResultStr =~ s/\\ /\\/g;  # to return non-splitted positions to original
	$ResultStr =~ s/\/ /\//g;
	$ResultStr =~ s/_ /\_/g;
   	# return "\"".$ResultStr."\"";
	
	$ResultStr = trimThrough($ResultStr);
	return $ResultStr;
}

#=================================================================
sub asc { my ($s)=@_;
#=================================================================
	$s=~ s/ä/a/g;   #note: editor "Encode in ANSI" selected
	$s=~ s/Ä/A/g;   #   - to disable graphviz error condition 
	$s=~ s/ö/o/g;
	$s=~ s/Ö/O/g;
	$s=~ s/å/o/g;
	$s=~ s/Å/O/g;
	return $s;
}

#=================================================================
sub trimThrough { my ($s)=@_;
#=================================================================
	# - removes all leading and trailing spaces
	# - converts remaining multiple spaces to single spaces
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	$s =~ s/\s+/ /; 
	return $s;
}
#=================================================================
sub slashBw { my ($s)=@_;
#=================================================================
	$s =~ s/\//\\/g;
	return $s;
}

#=================================================================
sub slashFw { my ($s)=@_;
#=================================================================
	$s =~ s/\\/\//g;
	return $s;

}
#####################################################################
#=============== HASH AND ARRAY HANDLING REGION =====================
#####################################################################

my $m_rhFocusHash;


#=================================================================
sub dutyH { my ($rhHash, $sDuty)=@_;  
#=================================================================
	TRACE("sets duty '$sDuty to hash '$rhHash'");
	%$rhHash = ();	
	$rhHash->{'DUTY'} = $sDuty;
}

#=================================================================
sub clearH { my ($rhHash)=@_;  
#=================================================================
	my $sSavedHashDuty = $rhHash->{'DUTY'};
	TRACE("clears hash '$rhHash'");
	%$rhHash = ();	
	$rhHash->{'DUTY'} = $sSavedHashDuty;
}

#=================================================================
sub useH { my ($rhRequestHash)=@_;
#=================================================================
	my $sHashDuty = $rhRequestHash->{'DUTY'};
	if ($m_rhFocusHash == $rhRequestHash) {
		#TRACE("already using requested Hash $rhRequestHash");
	} else {
		TRACE("changed to hash '$sHashDuty'");
		$m_rhFocusHash = $rhRequestHash;
	}
}

#=================================================================
sub putH { my ($sKey, $sVal, $rhRequestHashOpt)=@_;
#=================================================================
	my $rhHash;
	my $sHashDuty;
	
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
	} else {
		$rhHash = $m_rhFocusHash;
	}
	$sHashDuty = $rhHash->{'DUTY'};

	$rhHash->{$sKey} = $sVal;
	TRACE("'$sKey':'$sVal'   ($sHashDuty)");
}

#=================================================================
sub getH { my ($sKey, $rhRequestHashOpt)=@_;
#=================================================================
	my $rhHash;
	my $sRetVal;
	my $sHashDuty;

	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
	} else {
		$rhHash = $m_rhFocusHash;
	}

	$sHashDuty = $rhHash->{'DUTY'};
	$sRetVal = $rhHash->{$sKey};
	TRACE("'$sKey':'$sRetVal'   ($sHashDuty)");
	return $sRetVal;
}






#=================================================================
sub incH { my ($sKey, $rhRequestHashOpt)=@_;  
#=================================================================
	my $rhHash;
	my $nRetVal;
	my $nVal;
	my $sHashDuty;
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
	} else {
		$rhHash = $m_rhFocusHash;
	}

	$sHashDuty = $rhHash->{'DUTY'};

	$nVal = $rhHash->{$sKey};
	$nRetVal = $nVal + $One;  # assumes integer value
	$rhHash->{$sKey} = $nRetVal;
	TRACE("'$sKey':'$nVal'->'$nRetVal'   ($sHashDuty)");
	return $nRetVal;
}

#=================================================================
sub cloneH { my ($rhSourceHash, $rhTargetHash)=@_;  
#=================================================================
	my $sSourceHashDuty;
	my $sTargetHashDuty;

	$sSourceHashDuty = $rhSourceHash->{'DUTY'};
	$sTargetHashDuty = $rhTargetHash->{'DUTY'};

	TRACE("clones hash '$sSourceHashDuty' to hash '$sTargetHashDuty'");
	%$rhTargetHash = %{$rhSourceHash}; 
	$rhTargetHash->{'DUTY'} = $sTargetHashDuty;
	
} 


#=================================================================
sub extH { my ($sKey, $sCatchRegex, $rhRequestHashOpt)=@_;  # extract selected part from value by regex
#=================================================================
	my $sTargetStr;
	my $bRetStatus;
	
=comment
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
	} else {
		$rhHash = $m_rhFocusHash;
	}
	
	#$sTargetStr = getH($sKey, $rhHash);
	# $bRetStatus = CATCH($sTargetStr, $sCatchRegex) = @_;
=cut	
	return $bRetStatus;
}
#####################################################################
#=============== REGEX REGION =======================================
#####################################################################

# global copies of local match variables
our ($A, $B, $C, $D, $E, $F, $G, $H, $I) = "";
our $gPOS=$Zero;

#=================================================================
sub CATCH { my ($sTargetStr, $sREGEX) = @_;   
#================================================================
	my $bRetStatus = $Zero;
	if ($sTargetStr =~ m/$sREGEX/g){
		$bRetStatus = $One;
		TRACE("regex '$sREGEX' OK match to '$sTargetStr'");
		
	} else {
		if ($sTargetStr =~ m/\w+/){  # only non-empty lines (reduces TRACE waste)
			#TRACE("regex '$sREGEX' FAIL match to '$sTargetStr'");
		}
	}
	
	($A, $B, $C, $D, $E, $F, $G, $H, $I) = ($1, $2, $3, $4, $5, $6, $7, $8, $9); # copies match variables to global variables
	
	return $bRetStatus;
}


#=================================================================
sub CATCHFIRST { my ($sTargetStr, $rasREGEX) = @_;   
#================================================================
	my $nRgxPos = $Zero;
	my $sRegex = "";
	$gPOS=$Zero;
	TRACE($rasREGEX);
	foreach $sRegex (@$rasREGEX) {
		$nRgxPos++;
		if (CATCH($sTargetStr, $sRegex)) {
			$gPOS = $nRgxPos;
			TRACE("pos: '$gPOS'");
			last; # -obs: skips the loop
		}
	}
	return $gPOS;
}
#####################################################################
#=============== REPORT GENERATION REGION ===========================
#####################################################################

my $sTITLE_CASE_TAG_CATCH_rgx = "[A-Z]{1}[a-z]+";

#=================================================================
sub processTitleCaseTagsTemplate { my ($sTpl, $rhValues) = @_;   
#================================================================
	my $sFilledTemplate = $sTpl;
	
	TRACE("template: '$sTpl', tag catcher regex: '$sTITLE_CASE_TAG_CATCH_rgx'");
	TRACE($rhValues);
	
	my @asOriginalTags = ($sTpl =~ /$sTITLE_CASE_TAG_CATCH_rgx/g); # Collects all tags	
	foreach (@asOriginalTags) {
		my $sVal			= $rhValues->{$_};
		if  (defined $sVal) { 
			$sFilledTemplate	=~ s/$_/$sVal/g
		}
	}

	
	my @asRemainingTags = ($sFilledTemplate =~ /$sTITLE_CASE_TAG_CATCH_rgx/g); # Title
	
	foreach (@asRemainingTags) {  # removes possible non-substituted tags 
		$sFilledTemplate 	=~ s/$_//g;
	}
	
	my $sTags = join(",", @asRemainingTags);
	TRACE("removed superfluous tags: '$sTags'");

	$sFilledTemplate 	=~ s/\s+/ /g;  # shrinks sequential spaces
	TRACE("filled template: '$sFilledTemplate'");
	return $sFilledTemplate."\n";
}

#=================================================================
sub processGroupOfTitleCaseTagsTemplates { my ($rArsTemplates, $rArhValues) = @_;   
#================================================================
	my @asFilledTemplates;
	
	# loop
	# processTitleCaseTagsTemplate()


	return \@asFilledTemplates;

}
#####################################################################
#=============== DIRECTORY TREE HANDLING REGION =====================
#####################################################################




#####################################################################
#=============== DATABASE INTERFACE REGION ==========================
#####################################################################

#####################################################################
#=============== INI FILE HANDLING REGION ===========================
#####################################################################

#####################################################################
#=============== JSON HANDLING REGION ===============================
#####################################################################

#####################################################################
#=============== XML HANDLING REGION ================================
#####################################################################


#####################################################################
#=============== STATE MACHINES REGION ==============================
#####################################################################

my %m_hoaAllStateMachines 	=();  # each named state machine val is a history array of event/state -pair arrays
my @m_asDefaultStateMachine = ();


#====================================================================
sub setState { my ($sNewState, $sMachine) = @_;   
#====================================================================
	my $sCurrentState;
	if (defined $sMachine) {
		my @asStateMachine = $m_hoaAllStateMachines{$sMachine};
		$sCurrentState =  $asStateMachine[0];
		TRACE("machine '$sMachine' state '$sCurrentState' changed to '$sNewState'");
		push(@asStateMachine, $sNewState);
		$m_hoaAllStateMachines{$sMachine} = [@asStateMachine];
	} else {
		$sCurrentState= %m_asDefaultStateMachine[0];
		push(@m_asDefaultStateMachine, $sNewState);
		TRACE("state '$sCurrentState' changed to '$sNewState'  (default state machine)");
	}
}

#====================================================================
sub isState{ my ($sAskState, $sMachine) = @_;   
#====================================================================
	my $bRetStatus = $Zero;	
	my $sCurrentState;
	
	if (defined $sMachine) {
		if (defined $m_hoaAllStateMachines{$sMachine}) {
			my @asStateMachine = $m_hoaAllStateMachines{$sMachine};
			$sCurrentState = $asStateMachine[0];
		} else {
			TRACE("ERROR: unknown state machine '$sMachine'");
			return $bRetStatus;
		}
	} else {
		$sCurrentState = $m_asDefaultStateMachine[0];
	}
	#--------------------------------------------------------
	if ($sAskState == $sCurrentState) {
		TRACE("ask state '$sAskState' is not current state '$sCurrentState'");
	} else {
		TRACE("ask state is current state '$sCurrentState'");
		$bRetStatus = $One;
	}
	
	return $bRetStatus;
}

#====================================================================
sub isStateNot { my ($sAskState, $sMachine) = @_;   
#====================================================================
	return($One-isState($sAskState, $sMachine));  # -obs: 0 to 1 and 1 to 0
}


#####################################################################
#=============== EVENTS RISE REGION =================================
#####################################################################
my @m_asAllEvents 		= ();  # array, not a hash.
my $m_bEventProduced 	= $Zero; # to control p
#====================================================================
sub produceEvent { my ($sEvent) = @_;   
#====================================================================
	TRACE("produce event '$sEvent'");
	push(@m_asAllEvents, $sEvent);
	$m_bEventProduced=$One;
}

#====================================================================
sub latestEvent {   # no consuming
#====================================================================

	my $sLatestEvent = $m_asAllEvents[0];
	TRACE("latest event was '$sLatestEvent'");
	return $sLatestEvent;
}

#====================================================================
sub consumeIfEvent { my ($sAskEvent) = @_;   
#====================================================================
	my $sLatestEvent="";

	if ($m_bEventProduced > $Zero) {
		$sLatestEvent = pop(@m_asAllEvents);
		TRACE("consume event '$sLatestEvent'");
		$m_bEventProduced=$Zero;
	} 
	return $sLatestEvent;
}

#====================================================================
sub wasEvent { my ($sAskEvent) = @_;   # no consuming
#====================================================================
	my $bRetStatus=$Zero;
	if ($sAskEvent eq $m_asAllEvents[0]) {
		TRACE("latest event was '$sAskEvent'");
		$bRetStatus = $One;
	} else {
		TRACE("latest event was NOT '$sAskEvent'");
	}
	return $bRetStatus;
}

#====================================================================
sub wasEventNot { my ($sAskEvent) = @_;   # no consuming
#====================================================================
	return ($One-wasEvent($sAskEvent));
}

#####################################################################
#=============== CONTROL FLAGS REGION ===============================
#####################################################################

my %m_hAllFlags 	=();
#====================================================================
sub setFlag { my ($sFlagName) = @_;   
#====================================================================
	$m_hAllFlags{$sFlagName} = $One;
	TRACE("'$sFlagName'=$One");
}
#====================================================================
sub resetFlag { my ($sFlagName) = @_;   
#====================================================================
	$m_hAllFlags{$sFlagName} = $Zero;
	TRACE("'$sFlagName'=$Zero");
}
#====================================================================
sub isFlag { my ($sFlagName) = @_;   
#====================================================================	
	if (exists($m_hAllFlags{$sFlagName})) {
		my $nFlagVal = $m_hAllFlags{$sFlagName};
		TRACE("'$sFlagName'=$nFlagVal");
		return $nFlagVal;
	}  else {
		TRACE("ERROR: unknown flag '$sFlagName'");
		return $Zero;
	}	
}
#====================================================================
sub isFlagNot { my ($sFlagName) = @_;   
#====================================================================
	return ($One-isFlag($sFlagName));
}




#####################################################################
#=============== TEST STUFF REGION ==================================
#####################################################################


#=================================================================
sub KUKKUU {
#=================================================================

	print "xxx".$g_sKUKKUU."\n";

}




1;

























1;