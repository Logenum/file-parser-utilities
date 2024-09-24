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
my $sGivenTopicName  	= shift @ARGV;  	# is without 'H="' -prefix 
my $sGivenSubtopicName  = shift @ARGV;  	# is a complete line
# for example: [=================== YYYY-MM-DD ============================
my $sScratchpadFile 		= shift @ARGV;
my $sWholeTraceLogFileName 		= shift @ARGV;

print "input file: '$sInFile'\n";
print "output file: '$sOutFile'\n";
print "topic name: '$sGivenTopicName'\n";
print "subtopic name: '$sGivenSubtopicName'\n";
print "insert file: '$sScratchpadFile'\n";
print "log file: '$sWholeTraceLogFileName'\n";
my $sErrorMes="";
my $sGivenSubtopicNameForComparison = $sGivenSubtopicName;
$sGivenSubtopicNameForComparison =~ s/\[/\\[/;

if (!open (LOG_FILE, ">$sWholeTraceLogFileName")) {print "Cannot open log file '$sWholeTraceLogFileName'\n"; exit;}  # note: file open check

print LOG_FILE "in/out = $sInFile/$sOutFile\n";
print LOG_FILE "Topic=$sGivenTopicName\n";
print LOG_FILE "Subtopic=$sGivenSubtopicName\n";
#  "aaaa bbbb 111" 	# topic name
my $sTopicNameLinePattern = "H=\".*\"";
my $NAME_PATTERN = "\".*\"";
print LOG_FILE "topic name line pattern = '$sTopicNameLinePattern'\n";
print LOG_FILE "topic name pattern = '$NAME_PATTERN'\n";

my $sGivenTopicNameLine = $sTopicNameLinePattern;
### $sGivenTopicNameLine =~ s/$NAME_PATTERN/\\"$sGivenTopicName\\"/; # complete line is formed
$sGivenTopicNameLine =~ s/$NAME_PATTERN/\"$sGivenTopicName\"/; # complete line is formed
my $sGivenTopicNameLineRegex = "H\=\"$sGivenTopicName\"";

my $nOverWriteLen = 0;  # nothing is overwritten, just transferred forwards
my @asAddBlock=();
if (!open (INPUT_FILE, "<$sInFile")) {$sErrorMes = "Cannot open input file '$sInFile'\n";}  # note: file open check
my @asFileLines = <INPUT_FILE>; 
close INPUT_FILE;
if (!open (INSERT_FILE, "<$sScratchpadFile")) {$sErrorMes= $sErrorMes."Cannot open insert file '$sScratchpadFile'\n";}  # note: file open check
my @asAddLines = <INSERT_FILE>; 
chomp @asAddLines;
close INSERT_FILE;
if ($sErrorMes ne "") {
	print LOG_FILE $sErrorMes;
	print LOG_FILE "terminates script\n";
	close LOG_FILE;
	exit;
}


print Dumper \@asAddLines;
my $sState = "st_FindGivenTopicHeading";
my $nLineNbr = -1;
my $nBlockInsertionPos=0;
my $nFocusLinePos=-1;
my $nLastNonEmptyLinePos = 0;
my $eEvent = "";
my $sTopicNameLine = "";
my $nGivenTopicLinePos=0;
my $nNextTopicLinePos=0;
my $nFocusTopicLinePos=0;
print LOG_FILE "Try find topic line '$sGivenTopicNameLine'\n";
print LOG_FILE "Try find subtopic line '$sGivenSubtopicName'\n";
print LOG_FILE "STATE: initialized to ".$sState."\n";
foreach my $sLine (@asFileLines) { 
	$nFocusLinePos++;
	chop $sLine;
	
	#$sLine =~ s/\"/\\"/g;
	
	if ($sLine =~ /\S+/) {
		$nLastNonEmptyLinePos = $nFocusLinePos;
	}
	 # IDEA: creates "events" here at loop start
	if ($sLine =~ /$sGivenTopicNameLineRegex/) {
		$eEvent = "ev_GivenTopicLineFound";
	} elsif ( $sLine =~ /$sGivenSubtopicNameForComparison/) {
		$eEvent = "ev_GivenSubtopicLineFound";
	} else {  
		$eEvent = "";
	}
	if ($eEvent ne "") {
		print LOG_FILE "EVENT: '$eEvent' by line '$sLine'[$nFocusLinePos]\n"; 
	} else {
		print LOG_FILE "NO event by line '$sLine'[$nFocusLinePos]\n";
		###print LOG_FILE "line '$sLine' did not match to '$sGivenTopicNameLine'\n"; 
	}
	
	# IDEA: updates "states" by checking "events" here at loop end
	if ($sState eq "st_BlockBuilt") {
		print LOG_FILE "end processing because state is '$sState'\n";
		last;  # !!! a way to exit loop
	} elsif ($sState eq "st_FindGivenTopicHeading") {
		if ($eEvent eq  "ev_GivenTopicLineFound") {
			$sState = "st_FindGivenSubtopicHeading";
			$eEvent = "";
			print LOG_FILE "STATE: set to ".$sState."\n";
			$nGivenTopicLinePos = $nFocusLinePos;
		}
	} elsif ($sState eq "st_FindGivenSubtopicHeading") {
		if ($eEvent eq "ev_GivenTopicLineFound") {
			print LOG_FILE "next topic '$sTopicNameLine' found before given subtopic '$sGivenSubtopicName', so creates subtopic and inserts text";
			push(@asAddBlock, $sGivenSubtopicName);
			push(@asAddBlock, "\n");
			push(@asAddBlock, @asAddLines);
			push(@asAddBlock, "\n");			
			$nBlockInsertionPos = $nFocusLinePos - 1;
			$sState = "st_BlockBuilt";
		}  elsif ($sLine =~ /$sGivenSubtopicNameForComparison/) {
			print LOG_FILE "given Subtopic '$sGivenSubtopicName' found, so inserts text just below it\n";
			push(@asAddBlock, @asAddLines);
			push(@asAddBlock, "\n");
			#$nBlockInsertionPos = $nFocusLinePos;
			$nBlockInsertionPos = $nFocusLinePos + 1;
			$sState = "st_BlockBuilt";
			print LOG_FILE "state set to ".$sState."\n";
		} else {}
	} else {print LOG_FILE "state is ".$sState."\n";}
}


print LOG_FILE "all $nFocusLinePos lines handled, state remained '$sState'\n";
# creates topic and/or subtopic if was not found in file
if ($sState eq "st_FindGivenHeading") {   # given heading did not exist
	$nBlockInsertionPos = 2; # just after otl file top line and empty line
	print LOG_FILE "creates topic '$sGivenTopicNameLine' starting at position $nBlockInsertionPos\n";
	push(@asAddBlock, $sGivenTopicNameLine);
	push(@asAddBlock, "\n");
	#push(@asAddBlock, "\n");
	print LOG_FILE "creates subtopic '$sGivenSubtopicName'\n";
	push(@asAddBlock,$sGivenSubtopicName);
	push(@asAddBlock, "\n");
	print LOG_FILE "adds text\n";
	push(@asAddBlock, @asAddLines);
	#push(@asAddBlock, "\n");
} elsif ($sState eq "st_FindGivenSubtopicHeading") { # given heading was last heading
	$nBlockInsertionPos = $nGivenTopicLinePos+1;
	#$nBlockInsertionPos = $nGivenTopicLinePos;
	push(@asAddBlock, "\n");
	print LOG_FILE "creates subtopic '$sGivenSubtopicName' starting at position $nBlockInsertionPos\n";
	push(@asAddBlock, $sGivenSubtopicName);
	push(@asAddBlock, @asAddLines); # TODO: see if this works OK
	#push(@asAddBlock, "\n");
} else {}
my $nBlockPos=0;
print LOG_FILE "Inserts block:\n";
foreach  (@asAddBlock) {
	print LOG_FILE "[$nBlockPos] $_\n";
	$nBlockPos++;
}
print LOG_FILE "To position '$nBlockInsertionPos', overwrites '$nOverWriteLen' lines\n";

splice @asFileLines, $nBlockInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sOutFile") || print LOG_FILE "Cannot open output file '$sOutFile'\n";
$nLineNbr=0;
my $sOutLine;
foreach (@asFileLines) {
	chomp;  # note: removes additional '\n' characters which did appear for some reason
	$sOutLine = $_."\n"; 
    #print OUTPUT_FILE "$_\n";
	print LOG_FILE "[$nLineNbr] $sOutLine";
	print OUTPUT_FILE $sOutLine;
	$nLineNbr++;
}

close LOG_FILE;
close OUTPUT_FILE;

