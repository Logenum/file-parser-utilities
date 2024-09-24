#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  
#use UTILS;
use Data::Dumper

my $FALSE=0;
my $TRUE=1;

my $sInFile   	= shift @ARGV;  
my $sOutFile   	= shift @ARGV;
#my $sTopicNameLinePattern  = shift @ARGV;
my $sGivenTopicName  	= shift @ARGV;
my $sTimedDelim 	= shift @ARGV;
my $sAddText 		= shift @ARGV;

my $sTraceLogFullName 	= shift @ARGV;

my $sNEWLINE_TAG="_NL_"; # replacement was made by caller (Notetab Clip)
# originally possible multi-line text was made single-lined to pass it through dos batch

open (LOG_FILE, ">$sTraceLogFullName");

$sAddText =~s/$sNEWLINE_TAG/\n/g;
# - from single-line back to original (possibly multi-lined)

print LOG_FILE "in/out = $sInFile/$sOutFile\n";
#  "aaaa bbbb 111" 	# topic name
my $sTopicNameLinePattern = "H=\".*\"";
my $NAME_PATTERN = "\".*\"";

$sAddText = $sTimedDelim."\n".$sAddText;
#TRACE_INIT("TRACE.LOG",__FILE__);
#my $sTopicNameLine = quotemeta $sTopicNameLinePattern;
my $sGivenTopicNameLine = $sTopicNameLinePattern;
$sGivenTopicNameLine =~ s/$NAME_PATTERN/\"$sGivenTopicName\"/;

my $nOverWriteLen = 0;  # nothing is overwritten, just transferred forwards
my @asAddBlock=();
open (INPUT_FILE, "<$sInFile") || print LOG_FILE "Cannot open input file '$sInFile'\n";
my @asFileLines = <INPUT_FILE>; 
close INPUT_FILE;
my $sState = "FindGivenHeading";
my $nLineNbr = -1;
my $nInsertionPos=0;
my $nFocusLinePos=-1;
my $nLastNonEmptyLinePos = 0;
my $bSomeTopicFound = 0; # initial quess

print LOG_FILE "state set to ".$sState."\n";
foreach my $sLine (@asFileLines) {
	$nFocusLinePos++;
	if ($sLine =~ /\S+/) {
		$nLastNonEmptyLinePos = $nFocusLinePos;
	}
	if ($sState eq "FindGivenHeading") {
		if ($sLine =~ /$sGivenTopicNameLine/) {
			$bSomeTopicFound = 1;
			$sState = "FindNextHeading";
			print LOG_FILE "state set to ".$sState."\n";
		}
	} elsif ($sState eq "FindNextHeading") {
		if ($sLine =~ /$sTopicNameLinePattern/) {
			$bSomeTopicFound = 1;
			push(@asAddBlock,$sAddText);
			push(@asAddBlock, "\n");
			$nInsertionPos = $nFocusLinePos - 1;
			$sState = "AddingDone";
			print LOG_FILE "state set to ".$sState."\n";
		} 
	} else {}
}

# statuses when file ended
if ($sState eq "FindGivenHeading") {   # given heading did not exist
	print LOG_FILE "given heading not found, so it is created now\n";
	if ($bSomeTopicFound == 0){
		push(@asAddBlock, "\n");
		push(@asAddBlock, "\n");
		$nInsertionPos = 2; # just after top line and empty line
	}
	#
	push(@asAddBlock, $sGivenTopicNameLine);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
} elsif ($sState eq "FindNextHeading") { # given heading was last heading
	print LOG_FILE "next heading not found, so text is added to file end\n";
	$nInsertionPos = $nLastNonEmptyLinePos+1;
	#push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	push(@asAddBlock, "\n");
} else {}

splice @asFileLines, $nInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sOutFile") || print LOG_FILE "Cannot open output file '$sOutFile'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

#TRACE_END();
close LOG_FILE;
close OUTPUT_FILE;

