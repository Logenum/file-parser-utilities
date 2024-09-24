#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  
#use UTILS;
use Data::Dumper

my $OtlFileTopLinePattern ="\s*=\s+V.*Outline.*";
my $sTopicNameCapturePattern = "^H=\"(\S+.*)\"";  # no indent at name start
my $sTopicAttrCapturePattern = "^H=\"\s+(.*)\""; # indent (= tab or several spaces) at name start
my $FALSE=0;
my $TRUE=1;
my @asTopSection=();

my $sInFile   			= shift @ARGV;  
my $sOutFile   			= shift @ARGV;
my $OrderingType	  	= shift @ARGV;

#=comment
#TODO: 
open (LOG_FILE, ">TRACE.LOG");

open (INPUT_FILE, "<$sInFile") || print LOG_FILE "Cannot open input file '$sInFile'\n";
my $eState = "st_FindNextTopicName";
my @asFileLines = <INPUT_FILE>; 
my $nLineNbr=0;
my$sFirstLine = shift @asFileLines; # note: removes first line

if ($sFirstLine !~ /$OtlFileTopLinePattern/) {  # note: negation compare
	print LOG_FILE "first line is '$sFirstLine', so '$sInFile' is NOT an outline file";  
	close LOG_FILE;
	close INPUT_FILE;
	exit; # note: terminates script
}
foreach my $sLine (@asFileLines) {
	if ($eState eq "st_FindNextTopicName") {
		if ($sLine =~ /$sTopicNameCapturePattern/) {
			$sTopicName = $1;
			$eState = "st_FindNextAttr";
		}
	} elsif ($eState eq "st_FindNextAttr") {
		$eState = "st_FindNextAttr";
	
	}
}

close INPUT_FILE;

my $nLineNbr = -1;
my $nInsertionPos=0;
my $nFocusLinePos=-1;
my $nLastNonEmptyLinePos = 0;
my $FIRST_ADDIBLE_LINE_POS = 2;

print LOG_FILE "state set to ".$sState."\n";
foreach my $sLine (@asFileLines) {
	$nFocusLinePos++;
	if ($sLine =~ /\S+/) {
		$nLastNonEmptyLinePos = $nFocusLinePos;
	}
	if ($sState eq "FindGivenHeading") {
		if ($sLine =~ /$sGivenTopicNameLine/) {
		    $nInsertionPos = $nFocusLinePos + 1;
			push(@asAddBlock, "\n");
		    push(@asAddBlock,$sAddText);
			push(@asAddBlock, "\n");
			print LOG_FILE "adds text to topic stop\n";
			$sState = "AddingDone";
		}
	} 
}

# statuses when file ended
if ($sState eq "FindGivenHeading") {   # given heading did not exist
	$nInsertionPos = $FIRST_ADDIBLE_LINE_POS; 
	push(@asAddBlock, $sGivenTopicNameLine);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	#push(@asAddBlock, "\n");
	#push(@asAddBlock, "\n");
}
splice @asFileLines, $nInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sOutFile") || print LOG_FILE "Cannot open output file '$sOutFile'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

close LOG_FILE;
close OUTPUT_FILE;

