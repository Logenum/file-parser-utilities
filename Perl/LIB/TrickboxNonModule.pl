
#!/usr/bin/perl
package Trickbox;   # same package name must be in application script


use strict;  # -obs: requires ALL variables defined before usage


#=comment



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
#my ($A, $B, $C, $D, $E, $F, $G, $H, $I) = "";

#####################################################################
#=============== GLOBAL VARIABLES REGION ============================
#####################################################################

# contains module variables which would otherwise cause error by being used before definition

my $m_sKUKKUU = "KUKKUU";
my $m_sScriptStartDateTime;
my $m_sFILE_NAME_BODY_CATCH_rgx = "^.*?(\\w+)\\.\\w+.*\$"; # -obs: "?" means non-greedy match

# sub openWriteFile
# sub openAppendFile
# sub openReadFile
# sub ventReadFile
#
my $m_nFileErrors = 0;
my $m_sDOT_GRAPH_HEADER_tpl = "digraph Cname{\n\n";
my $m_sDOT_GRAPH_FOOTER_tpl = "\n\n}\n\n";
my $m_sDOT_GRAPH_HEADER_MATCH_rgx = "^\\s*digraph\\s+\\S+\\s+{.*\$";

our $m_sOTL_FILE_FIRST_LINE_tpl 		= "= V4 Outline MultiLine NoSorting TabWidth=30";
our $m_sTopicName 					= "";
our $m_sTOPIC_NAME_tpl 				= "\nH=\"%HeadingName%\"\n\n";
our $m_sOTL_TOPIC_NAME_CATCH_rgx 		= "^H=\"(.*)\"\$";
our $m_sOTL_TOPIC_LINK_CATCH_rgx			= "^(.*)[(.*)](.*)\$"; 	
our $m_sOTL_FILE_TOPIC_LINK_CATCH_rgx	= "^(.*)[(.*)::(.*)](.*)\$";
our $m_sOTL_FILE_FIRST_LINE_MATCH_rgx = "^=\s+V4\s+Outline\s+MultiLine.*";

my @asCLangReservedWords=
	("auto","break","case","char","continue","default","do","double","else","extern","float","for",
	 "goto","if","int","long","register","return","short","sizeof","static","struct","switch","typedef",
	 "union","unsigned","while");

my $sTITLE_CASE_TAG_CATCH_rgx = "([A-Z]{1}[a-z]+).*\$";

my $m_sTRACE_OTL_FILE_FIRST_TOPIC_NAME =  "h=\"CONTENTS\"";
my $m_sTRACE_OTL_FILE_LAST_TOPIC_NAME =  "h=\"INFO\"";
my $m_pTRACE;

# global copies of local match variables
our ($A, $B, $C, $D, $E, $F, $G, $H, $I) = "";


my %m_hoaAllStateMachines 	=();  # each named state machine val is a history array of event/state -pair arrays
my %m_hDefaultHash = ();

my $m_rhFocusHash;
my $m_sFocusHashDuty;

#####################################################################
#=============== DATE AND TIME REGION ===============================
#####################################################################



#=================================================================
sub getDateTimeAsNtbFormat   {
#=================================================================
	my @RawDateTime = localtime(time);	# note: these are built-in functions

	my $yy = $RawDateTime[5] - 100;  		# year since 1900
	if ($yy <= 9) {$yy = "0"."$yy";}

	my $mm = $RawDateTime[4] + 1;			# January is ZERO
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
#=============== NOTETAB OTL FILE HANDLING REGION ===================
#####################################################################


#####################################################################
#=============== TRACE LOG REGION ===================================
#####################################################################
# -legend: trace log has notetab outline file syntax: it is simple and has few nice features (topics, hyperlinks, www-links and red/blue colorization)
# -legend: trace log file is created automatically and named peerly to name of the application script

#=================================================================
sub TRACE {  my ($sText, $sHeadingOpt)=@_;
#=================================================================
	my $sTraceLine;
	my ($package0, $sRelFilename0, $line0, $subroutine0) = caller(0);  # note: getting caller info
	my ($package1, $sRelFilename1, $line1, $subroutine1) = caller(1);  # note: getting caller info
	
	if (defined $sHeadingOpt) {
		traceOtlHeading($sHeadingOpt);
	}
	
	$sRelFilename0 = slashBw($sRelFilename0);
		
	my $sTraceLine =  "$sText [$sRelFilename0::$line0^L]     $subroutine1()";
	$sTraceLine =~ s/\n//g; 		# removes possible internal line feeds 
	
	print $m_pTRACE $sTraceLine."\n";
}


#=================================================================
sub traceOtlHeading {  my ($sHeading)=@_;  # for "Trickbox" internal usage
#=================================================================
		my $sTraceLine = "\nH=\"$sHeading\"\n";
		print $m_pTRACE $sTraceLine."\n";
}


#####################################################################
#=============== FILE HANDLING REGION ===============================
#####################################################################


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
	return $SOME_FILE; # note: return capsulated value
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



#####################################################################
#=============== PLANTUML REGION ===============================
#####################################################################

#####################################################################
#=============== NOTETAB REGION ===============================
#####################################################################

###########################################################################
#============== PROGRAM LANGUAGE SPECIFIC DEFINITIONS REGION =========
###########################################################################



#####################################################################
#=============== ENTRY REGION =======================================
#####################################################################
#=================================================================
sub INITRICKS {  my ($sScriptPlainName)=@_;
#=================================================================
	my $sScriptNameBody;
	($sScriptNameBody) = ($sScriptPlainName =~ m/$m_sFILE_NAME_BODY_CATCH_rgx/g);  # cuts possible extension
	my $sTraceFilePlainName = $sScriptNameBody.".log";
	#print $sScriptPlainName."\n";
	#print $sScriptNameBody."\n";
	#print $sTraceFilePlainName."\n";
	$m_sScriptStartDateTime = getDateTimeAsNtbFormat();
	open($m_pTRACE, ">$sTraceFilePlainName")	|| print "Cannot open TRACE file $sTraceFilePlainName";
	print $m_pTRACE $m_sOTL_FILE_FIRST_LINE_tpl."\n\n";
	print $m_pTRACE $m_sTRACE_OTL_FILE_FIRST_TOPIC_NAME."\n\n";
	print $m_pTRACE $m_sScriptStartDateTime;
	
	my $m_rhFocusHash = \%m_hDefaultHash;
#=begin OUT	

#=cut	
}

#=================================================================
sub extractArguments {  my ($raARGV)=@_;
#=================================================================
	my $nPos = 0;
	foreach (@$raARGV) {
		TRACE("ARGV[$nPos] = '$_'\n");
		$nPos++;
	}
	return @$raARGV;
}
#=================================================================
sub QUITRICKS {  my ($sComment)=@_;
#=================================================================
	getDateTimeAsNtbFormat();
	print $m_pTRACE "\n\n".$m_sTRACE_OTL_FILE_LAST_TOPIC_NAME."\n\n";
	if (! $sComment) {
		$sComment = "no known errors";
	}
	
	print $m_pTRACE "Script termination status: $sComment\n";
	close $m_pTRACE; 
	
	exit 1;
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
   	return "\"".$ResultStr."\"";
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




#=================================================================
sub useHash { my ($rhRequestHash, $sDutyOpt)=@_;
#=================================================================
	if (defined $sDutyOpt) {
		$m_sFocusHashDuty = " DUTY: $sDutyOpt ";
	} else {
		$m_sFocusHashDuty = "";
	}

	if ($m_rhFocusHash == $rhRequestHash) {
		#TRACE("already using requested Hash $rhRequestHash $m_sFocusHashDuty");
	} else {
		TRACE("changed from $m_rhFocusHash to $rhRequestHash $m_sFocusHashDuty");
		$m_rhFocusHash = $rhRequestHash;
	}
}

#=================================================================
sub putHash { my ($sKey, $sVal, $rhRequestHashOpt)=@_;
#=================================================================
	my $rhHash;
	my $sCommentOpt="";
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
		$sCommentOpt="bypass";
	} else {
		$rhHash = $m_rhFocusHash;
	}
	
	$rhHash->{$sKey} = $sVal;
	TRACE("key/val/Hash = $sKey/$sVal/$rhHash $sCommentOpt");
}

#=================================================================
sub getHash { my ($sKey, $rhRequestHashOpt)=@_;
#=================================================================
	my $rhHash;
	my $sRetVal;
	my $sCommentOpt="";
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
		$sCommentOpt="bypass";
	} else {
		$rhHash = $m_rhFocusHash;
	}
	$sRetVal = $rhHash->{$sKey};
	TRACE("key/val/Hash = $sKey/$sRetVal/$rhHash $sCommentOpt");
}

#=================================================================
sub incHash { my ($sKey, $rhRequestHashOpt)=@_;  
#=================================================================
	my $rhHash;
	my $nRetVal;
	my $nVal;
	my $sCommentOpt="";
	if (defined $rhRequestHashOpt) {  # for temporary bypassing of focus Hash
		$rhHash = $rhRequestHashOpt;
		$sCommentOpt="bypass";
	} else {
		$rhHash = $m_rhFocusHash;
	}
	$nVal = $rhHash->{$sKey};
	$nRetVal = $nVal + 1;  # assumes integer value
	$rhHash->{$sKey} = $nRetVal;
	return $nRetVal;
}
#####################################################################
#=============== REGEX REGION =======================================
#####################################################################



#=================================================================
sub CATCH { my ($sTargetStr, $sREGEX) = @_;   
#================================================================
	my $bRetStatus = 0;
	if ($sTargetStr =~ m/$sREGEX/g){
		$bRetStatus = 1;
		TRACE("regex '$sREGEX' OK match to '$sTargetStr'");
		
	} else {
		#TRACE("regex '$sREGEX' FAIL match to '$sTargetStr'");
	}

	($A, $B, $C, $D, $E, $F, $G, $H, $I) = ($1, $2, $3, $4, $5, $6, $7, $8, $9); # copies match variables to global variables


	return $bRetStatus;
}


#####################################################################
#=============== REPORT GENERATION REGION ===========================
#####################################################################



#=================================================================
sub processTitleCaseTagsTemplate { my ($sTpl, $rhValues) = @_;   
#================================================================
	my $sFilledTemplate = $sTpl;
	
	TRACE("native template: '$sTpl'");
	my @asTags = ($sTpl =~ /$sTITLE_CASE_TAG_CATCH_rgx/g); # Title

	for my $sKey (keys %$rhValues) {	# subsititutes tags with values
		my $sVal 				= $rhValues->{$sKey};
		$sFilledTemplate	=~ s/$sKey/$sVal/g;
	}
	foreach (@asTags) {  # removes possible non-substituted tags 
		$sFilledTemplate 	=~ s/$_//g;
	}

	$sFilledTemplate 	=~ s/\s+/ /g;  # shrinks sequential spaces
	TRACE("filled template: '$sFilledTemplate'");
	return $sFilledTemplate;
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

#====================================================================
sub setState { my ($sNewState, $sMachine, $sNewEvent) = @_;   
#====================================================================

	my @aoaStateMachine = $m_hoaAllStateMachines{$sMachine};
	my $sCurrentState =  $aoaStateMachine[0][1];
	
	if (defined $sNewEvent) {
		TRACE("machine '$sMachine' state '$sCurrentState' changed to '$sNewState' by event '$sNewEvent'");
	} else {
		$sNewEvent = "DEFAULT";
		TRACE("'$sCurrentState' changed to '$sNewState'");
	}
	
	my @asStateAndEvent 			=[$sNewEvent, $sNewState];
	

	push(@aoaStateMachine, \@asStateAndEvent);
	$m_hoaAllStateMachines{$sMachine} = [@aoaStateMachine];
}

#====================================================================
sub isState { my ($sAskState, $sMachine) = @_;   
#====================================================================
	my $bRetStatus = 0;	
	my @aoaStateMachine = $m_hoaAllStateMachines{$sMachine};
	my @asStateAndEvent = $aoaStateMachine[0];
	my $sCurrentState =  $asStateAndEvent[1];
	if ($sAskState == $sCurrentState) {
		TRACE("ask state '$sAskState' is not current state '$sCurrentState'");
	} else {
		TRACE("ask state is current state '$sCurrentState'");
		$bRetStatus = 1;
	}
	return $bRetStatus;
}


#====================================================================
sub wasEvent { my ($sEventRgx, $sMachine) = @_;   
#====================================================================


}
#####################################################################
#=============== CONTROL FLAGS REGION ===============================
#####################################################################

my %m_hAllFlags 	=();
#====================================================================
sub setFlag { my ($sFlagName) = @_;   
#====================================================================
	$m_hAllFlags{$sFlagName} = 1;
	TRACE("set flag '$sFlagName'");
}

#====================================================================
sub resetFlag { my ($sFlagName) = @_;   
#====================================================================
	$m_hAllFlags{$sFlagName} = 0;
	TRACE("reset flag '$sFlagName'");
}

#====================================================================
sub isFlag { my ($sFlagName) = @_;   
#====================================================================
	return $m_hAllFlags{$sFlagName};
}

#====================================================================
sub isFlagNot { my ($sFlagName) = @_;   
#====================================================================
	my $nFlagVal = $m_hAllFlags{$sFlagName};
	if ($nFlagVal > 0) {
		return 0;
	} else {
		return 1;
	}
}




#####################################################################
#=============== TEST STUFF REGION ==================================
#####################################################################


#=================================================================
sub KUKKUU {
#=================================================================

	print "xxx".$m_sKUKKUU."\n";

}





























1;