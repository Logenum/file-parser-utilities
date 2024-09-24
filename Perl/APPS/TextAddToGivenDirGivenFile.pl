#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  

use Data::Dumper

my $FALSE=0;
my $TRUE=1;
my $sOutDir   	= shift @ARGV;  
my $sOutFile   	= shift @ARGV;
my $sComment  	= shift @ARGV;
my $sAddText 	= shift @ARGV;





my $sGivenTopicNameLine = $sTopicNameLinePattern;
$sGivenTopicNameLine =~ s/$NAME_PATTERN/\"$sGivenTopicName\"/;

my $nOverWriteLen = 0;  # nothing is overwritten, just transferred forwards
my @asAddBlock=();
open (INPUT_FILE, "<$sInFile") || print "Cannot open input file '$sInFile'\n";
my @asFileLines = <INPUT_FILE>; 
close INPUT_FILE;
my $sState = "FindGivenHeading";
my $nLineNbr = -1;
my $nInsertionPos=0;
my $nFocusLinePos=-1;
my $nLastNonEmptyLinePos = 0;
foreach my $sLine (@asFileLines) {
	$nFocusLinePos++;
	if ($sLine =~ /\S+/) {
		$nLastNonEmptyLinePos = $nFocusLinePos;
	}
	if ($sState eq "FindGivenHeading") {
		if ($sLine =~ /$sGivenTopicNameLine/) {
			$sState = "FindNextHeading";
		}
	} elsif ($sState eq "FindNextHeading") {
		if ($sLine =~ /$sTopicNameLinePattern/) {
			push(@asAddBlock,$sAddText);
			push(@asAddBlock, "\n");
			$nInsertionPos = $nFocusLinePos - 1;
			$sState = "AddingDone";
		} 
	} else {}
}

# statuses when file ended
if ($sState eq "FindGivenHeading") {   # given heading did not exist
	$nInsertionPos = 2; # just after top line and empty line
	push(@asAddBlock, $sGivenTopicNameLine);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
} elsif ($sState eq "FindNextHeading") { # given heading was last heading
	$nInsertionPos = $nLastNonEmptyLinePos+1;
	#push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	push(@asAddBlock, "\n");
} else {}

splice @asFileLines, $nInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sOutFile") || print "Cannot open output file '$sOutFile'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

#TRACE_END();
close OUTPUT_FILE;

