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
my $sGivenTopicName = shift @ARGV;
my $sAddText 		= shift @ARGV;
my $sTodayDate 		= shift @ARGV;
open (LOG_FILE, ">TRACE.LOG");

print LOG_FILE "in/out = $sInFile/$sOutFile\n";
#  "aaaa bbbb 111" 	# topic name
my $sTopicNameLinePattern = "H=\".*\"";
my $NAME_PATTERN = "\".*\"";


my $sJournalSectionTodayBlockHeadingLine="[=============== $sTodayDate ============================]";

my $JOURNAL_AREA_TAIL_LINE = "[===========================================================]";

my $sDAILY_BLOCK_HEADING_CATCH_regex = "\[===.*\s+(\d+-\d+-\d+)\s+==.*";

#TRACE_INIT("TRACE.LOG",__FILE__);
#my $sTopicNameLine = quotemeta $sTopicNameLinePattern;
my $sGivenTopicNameLine = $sTopicNameLinePattern;
$sGivenTopicNameLine =~ s/$NAME_PATTERN/\"$sGivenTopicName\"/;

my $nOverWriteLen = 0;  # nothing is overwritten, just transferred forwards
my @asAddBlock=();
open (INPUT_FILE, "<$sInFile") || print LOG_FILE "Cannot open input file '$sInFile'\n";
my @asFileLines = <INPUT_FILE>; 
close INPUT_FILE;
my $sState = "FindGivenTopicHeading";
my $nLineNbr = -1;
my $nInsertionPos=0;
my $nFocusLinePos=-1;
my $nLastNonEmptyLinePos = 0;
my $sSomeDate;

print LOG_FILE "state set to ".$sState."\n";
foreach my $sLine (@asFileLines) {
	$nFocusLinePos++;
	if ($sLine =~ /\S+/) {
		$nLastNonEmptyLinePos = $nFocusLinePos;
	}
	if ($sState eq "FindGivenTopicHeading") {
		if ($sLine =~ /$sGivenTopicNameLine/) {
			$sState = "FindTodaySectionHeading";
			print LOG_FILE "state set to ".$sState."\n";
		}
	} elsif ($sState eq "FindTodayBlockHeading") {
		if (($sSomeDate) = ($sLine =~ /$sDAILY_BLOCK_HEADING_CATCH_regex/)) {
			if ($sSomeDate eq $sTodayDate) {
				push(@asAddBlock,$sAddText);
				push(@asAddBlock, "\n");
				$nInsertionPos = $nFocusLinePos;  # just 
				$sState = "AddingDone";
			}
			print LOG_FILE "state set to ".$sState."\n";
		} elsif ($sLine =~ /$sTopicNameLinePattern/) {
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
	$nInsertionPos = 2; # just after top line and empty line
	push(@asAddBlock, $sGivenTopicNameLine);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
	push(@asAddBlock, $sJournalSectionTodayBlockHeadingLine."\n");
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
open (OUTPUT_FILE, ">$sOutFile") || print LOG_FILE "Cannot open output file '$sOutFile'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

#TRACE_END();
close LOG_FILE;
close OUTPUT_FILE;

