#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

use Data::Dumper;

my $sThisFileWholeName = $0;

my ($sThisPathName) = ($sThisFileWholeName =~ /^(.*\/).*/ig);  # !: captures also terminating "/"

my $nFocusLineNbr;
my $sFocusLine;
my $sWholeText;

$sDEFAULT_HANDLER = "notepro.exe";

%hHandlerCmdByExt = 	(  # TODO: add handler paths
						"pl|pm|py|cpp" => "Notepad++.exe [-n%argument%|%%] %file%", # file extension as PART of key
						"html" => "Explorer.exe %file%",
						"mm" => "Freeplane",
						"rtf" => "Wordpad.exe",
						"LEO" => "Leo"
					); # TODO: add more items 

if ($ARGV[0] eq "-t") {
    $nFocusLineNbr       = 1;
    $sWholeText          = "jeeeeeeeeeeeee";
} else {
    $nFocusLineNbr       = $ARGV[0]-1;
    $sWholeText          = $ARGV[1];
}

my $sreFILE_DETAIL_NAVIG_DETECT = "\\W*\|.*\|\\W*";
my $sreFILE_DETAIL_NAVIG_CAPTURE = "(\\|.*\\|)"; 
my $FILE_DETAIL_NAVIG_SPLITTER = "\\|"; # note: string regex requires double backslash
my $rePATH_FILE_CAPTURE =  "^\\W*([a-zA-Z]\:\\.*)\\s*"; # e.g. "E:\toolbox\apps"
my $rePLAIN_FILE_CAPTURE = "^\\s*\\[\\s*(\\S+)\\s*$";  # e.g. "[ Utils.pm"

my $nLineNbr      	= -1;
my $nTargetLineNbr	= 0;
my @aTextLines      = split ('\n',$sWholeText);

my $sFocusLine = $aTextLines[$nFocusLineNbr];

my $sLatestExistingPathName = "";
my $sLatestExistingWholeFileName = "";
my $sNameCandidate;
my $nFileLineNbr=-1;
my $bThisIsCursorLine = 0;

my $nNavigationReadyLineNbr = 0;

foreach $sLine (@aTextLines) {
	$nLineNbr++;
	if ($nLineNbr == $nFocusLineNbr) {
		$bThisIsCursorLine = 1;
	}
	if ($sLine =~ m/$rePATH_FILE_CAPTURE/) {
		if (-f $1) {
			$sLatestExistingWholeFileName = $1;
		} elsif (-d $1) {
			$sLatestExistingPathName = $1;
		}
	} elsif ($sLine =~ m/$rePLAIN_FILE_CAPTURE/) {
		$sNameCandidate = $sLatestExistingPathName."\\".$1;
		if (-f $sNameCandidate) {
			$sLatestExistingWholeFileName = $sNameCandidate;
		}
	} elsif (($sLine =~ m/$sreFILE_DETAIL_NAVIG_CAPTURE/) and 
	($bThisIsCursorLine == 1) and 
	($sLatestExistingWholeFileName ne "")) {
		my @asNavStr = split("|",$1);
		open (INPUT_FILE, "<$sLatestExistingWholeFileName") || print "Cannot open input file '$sLatestExistingWholeFileName'\n";
		my @asFileLines = <INPUT_FILE>;
		close INPUT_FILE;
		my $reSearchStr = shift(@asNavStr); # first item
		foreach (@asFileLines) {
			$nFileLineNbr++;
			if (/$reSearchStr/) {
				$reSearchStr = shift(@asNavStr);
				if ($reSearchStr == "") {  # previous search string was the last one
					$nNavigationReadyLineNbr = $nFileLineNbr;
					exit;
				}
			}
		}
	}
}

#===== BUILDING COMMAND LINE ===== 
my $sCommandLine;
my $sHandlerName = "";
if ($sLatestExistingWholeFileName ne "")  {
	# get file extension
	my $ext = ($sLatestExistingWholeFileName =~ /^.*\.(\w+)$/);
	if ($ext ne "") {
		lc $ext;  # string to lower case
		foreach $key (keys %hHandlerCmdByExt) {
			if ($key =~ /^.*\b\$ext\b.*$/) {
				$sHandlerName = $hHandlerCmdByExt{$key};
				exit;
			}
		}
	} else {  #  file has no extension
		$sHandlerName = $sDEFAULT_HANDLER;
	}
	$sCommandLine = 
}
	
	

