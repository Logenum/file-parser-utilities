#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;
my $sThisScriptPath="";
my $sThisScriptName="";
# TODO: modify this for Freeplane/Notetab compliant and not Linux-specific script (160320)



BEGIN { 
	#print @INC;
	my $sThisScriptFullName = $0;
	my $sCommandLine = join " ", $sThisScriptFullName, @ARGV;
	print "\ncommand line: $sCommandLine";
	($sThisScriptPath, $sThisScriptName) = ($sThisScriptFullName =~ /^(.*)\\(.*)/);
	print "\n$sThisScriptPath";
	print "\n$sThisScriptName";
	push @INC, $sThisScriptPath;
	# note: required to make focus path referable !!!!!!!!!! 
	#print @INC;
}  

use UTILS;

use Data::Dumper;
######################################################################################
# Interprets given text 130408
#
#  	Result actions:
#	-	opens given file in given text editor with cursor at navigated line
#	-	TODO: add more actions
#
######################################################################################



my $nFocusLineNbr;
my $sFocusLine;
my $sWholeText;
my $sCallPar_ActionType;

my $sTraceFileFullName="";

if ($ARGV[0] eq "-t") {
    $nFocusLineNbr       = 123;
    $sFocusLine          = "|aaa|bbb|";
    $sWholeText          = "jeeeeeeeeeeeee";
    $sCallPar_ActionType = "ACT_OPEN_TARGET_AT_NAVIG_LINE";
	$sTraceFileFullName	 = "C:\\ELU\\TMP\\TRACE.LOG";
} else {
    $nFocusLineNbr       = $ARGV[0]-1;
    $sFocusLine          = $ARGV[1];
    $sWholeText          = $ARGV[2];
	#$sWorkFile			 = $ARGV[3];
    $sCallPar_ActionType = $ARGV[3];
    $sTraceFileFullName  = $ARGV[4];
	# trace file name changed to call parameter for easier finding
}


TRACE_INIT($sTraceFileFullName,"start TRACE at interpret top to file '$sTraceFileFullName'");

TRACE("focus line number:   '$nFocusLineNbr'");
TRACE("focus line contents: '$sFocusLine'");
TRACE("focus text contents: '$sWholeText'");

my $sreFILE_DETAIL_NAVIG_DETECT = "\\W*\|.*\|\\W*";
my $sreFILE_DETAIL_NAVIG_CAPTURE = "(\\|.*\\|)"; 
my $FILE_DETAIL_NAVIG_SPLITTER = "\\|"; # note: string regex requires double backslash

my $nTextLineNbr      	= 0;
my $nTargetLineNbr	= 0;
my @aTextLines          = split ('\n',$sWholeText);

my $sFocusLineByNbr = $aTextLines[$nFocusLineNbr];
###TRACE("navig line by nbr: '$sNavigLineByNbr'");

my $sPossiblePathName = "";
my $sExistingPathName = "";

my $rasTRACE;
my $EXTERNAL_EDITOR_NAME = "kate";
my $LINE_NBR_SWITCH = "-l";
my $IMAGE_VIEWER_NAME = "eog";
my $sDOCUMENT_HANDLING_APPLICATION ="C:\\Program Files\\Microsoft Office 15\\root\\office15\\WINWORD.exe";
my $NE4_GNOME_SCRIPT_FULL_NAME = "/home/erkki/my/SCRIPTS.MM/GoToGivenNE4Dir.sh";
my $status;
my $sType = 'NONE';
my $sTargetType = 'NONE';
my $sTargetFullName="";
my $sExecutableFileFullName="";
my $sInputFileFullName="";
my $sOutputFileFullName="";

my $sTargetRole;
my $sTargetRace;
my $sStr;
my $sLine;
my $raohItemsInfo;
my @aohItemsInfo;

#######################"execute $EXTERNAL_EDITOR_NAME $sLatestFileFullName"#####################################
#  collects various stuff from focus note top down to given line
################################################################################################################

TRACE("script action type: '$sCallPar_ActionType'");

#($sTargetType, $sTargetFullName)= tryCaptureRecentExistingPathOrFileFullName(\@aTextLines, $sFocusLine, $nFocusLineNbr);

$raohItemsInfo = collectBuildCheckSpecificItems(\@aTextLines, $sFocusLine, $nFocusLineNbr);
#	-	full file name is collected from a text block 

my $sWholeCommand = "";  # initial quess

###TRACE(Dumper($raohItemsInfo));

#my @aohRevertedItemsInfo = reverse(@$raohItemsInfo);

#TRACE(Dumper(@aohRevertedItemsInfo));

my $rhItem;
foreach $rhItem (@$raohItemsInfo) {

    $sTargetType 		= $rhItem->{TYPE};
    $sTargetRole 		= $rhItem->{ROLE};
    $sTargetRace 		= $rhItem->{RACE};
    $sTargetFullName 		= $rhItem->{NAME};

    TRACE("target type = $sTargetType");
    TRACE("target role = $sTargetRole");
    TRACE("target race = $sTargetRace");
    
    if ($sCallPar_ActionType eq 'ACT_COLLECT_IN_OUT_CMD') {  # parameter from caller script
		if ($sTargetType eq 'FILE') {
			if ($sTargetRole eq 'PERL') {
				$sExecutableFileFullName = $sTargetFullName;
				last;  # 
			} elsif ($sTargetRole eq 'INPUT') { 
				$sInputFileFullName = $sTargetFullName;
			} elsif ($sTargetRole eq 'OUTPUT') {
				$sOutputFileFullName = $sTargetFullName;
			} else {

			}
		}
    } else {
		last;
    }
}




##############################################################################################################
#  try various matches to given single line
##############################################################################################################
if ($sCallPar_ActionType eq "ACT_OPEN_TARGET_AT_NAVIG_LINE") { 
    TRACE("line target type: '$sTargetType'");
    if ($sTargetType eq "FILE") {
		TRACE("line target race: '$sTargetRace'");
		if ($sTargetRace eq 'TEXT') {
			if ($sFocusLine =~ m/$sreFILE_DETAIL_NAVIG_DETECT/g) { 
				TRACE("line '$sFocusLine' does match to '$sreFILE_DETAIL_NAVIG_DETECT'");
				($nTargetLineNbr, $rasTRACE) = getLineNbrByIncSearch ($sTargetFullName,
										$sFocusLine,
										$sreFILE_DETAIL_NAVIG_CAPTURE,
										$FILE_DETAIL_NAVIG_SPLITTER);	
				TRACE(Dumper($rasTRACE));
				$sWholeCommand = "$EXTERNAL_EDITOR_NAME $LINE_NBR_SWITCH $nTargetLineNbr $sTargetFullName";
			} else {
				$sWholeCommand = "$EXTERNAL_EDITOR_NAME $sTargetFullName";
			}
		} elsif ($sTargetRace eq 'IMAGE') {
			$sWholeCommand = "$IMAGE_VIEWER_NAME $sTargetFullName";
		} else { # TODO: add more cases
		}
    }  elsif ($sTargetType eq "PATH") {
		$sWholeCommand = "$NE4_GNOME_SCRIPT_FULL_NAME $sTargetFullName";
    }  elsif ($sTargetType eq "TRAC_TICKET") {
		$sWholeCommand = "google-chrome http://trac.noval.fi:8000/neteye/ticket/".$sTargetFullName;
    } else {
		TRACE("no matches to line '$sFocusLine'");
    }
} elsif ($sCallPar_ActionType eq "ACT_SHOW_TARGET_SVN") {
	if (($sTargetType eq "FILE") || ($sTargetType eq "PATH")) {
	    $sWholeCommand = "/home/erkki/my/SCRIPTS.MM/SvnLog.sh $sTargetFullName";
	}
} elsif ($sCallPar_ActionType eq "ACT_COLLECT_IN_OUT_CMD") {
	 if ($sTargetRole eq 'PERL') {
	    $sWholeCommand = "perl $sExecutableFileFullName $sInputFileFullName $sOutputFileFullName";
	 }
} elsif ($sCallPar_ActionType eq "ACT_RUN_FOCUS_LINE") {
	 $sFocusLine =~ s/<.+?>//g;
	 $sFocusLine =~ s/__/ /g;
	 $sWholeCommand = $sFocusLine;
} elsif ($sCallPar_ActionType eq "ACT_OPEN_TARGET") {
	 if ($sTargetRace eq "DOCUMENT") {
		$sWholeCommand = "$sDOCUMENT_HANDLING_APPLICATION $sFocusLine";
	} else {
		TRACE("target race is '$sTargetRace' so do DO NOTHING !!!");
	}
} 

else {
	TRACE("DO NOTHING !!!");
}

if ($sWholeCommand ne "") {
    TRACE("execute '$sWholeCommand'");
    $status = system($sWholeCommand);
    #exec($sWholeCommand);
}

###TRACE(Dumper($rasTRACE));
###TRACE("trace ended");
#================================================================

1;
