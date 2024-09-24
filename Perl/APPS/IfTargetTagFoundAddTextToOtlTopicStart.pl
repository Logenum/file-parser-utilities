#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  
#use UTILS;
use Data::Dumper

my $sFileName;
my $sTopicName;
my $FALSE=0;
my $TRUE=1;
my $sAddTextFile				= shift @ARGV;  # shall contain possible navigation tags
my $sTargetFilePath				= shift @ARGV;  
my $sFILE_TOPIC_CAPTURE_regex 	= "^\s*#\s*(\w+)\s*,\s*(\w+)";

#=comment
#TODO: 
open (LOG_FILE, ">TRACE.LOG");
#  tries to find certain tagged line, which defines file/topic/(possible subtopic) names
open (ADD_FILE, "<$sAddTextFile") || print LOG_FILE "Cannot open add text file '$sAddTextFile'\n";
my @asAddFileLines = <ADD_FILE>; 
foreach my $sLine (@asAddFileLines) {
	if (($sTargetFileName,$sTargetTopicName) = ($sLine =~ /$sFILE_TOPIC_CAPTURE_regex/)) {
		print LOG_FILE "found tag for target file/topic = '$sFileName'/'$sTopicName'\n";
	}
}

my $sTopicNameLinePattern = "H=\".*\"";
my $NAME_PATTERN = "\".*\"";
$sTargetTopicNameFullLine =~ s/$NAME_PATTERN/\"$sTargetTopicName\"/;

my $nOverWriteLen = 0;  # nothing is overwritten, just transferred forwards
my @asAddBlock=();
my $sTargetFileFullName = $sTargetFilePath."\\".$sTargetFileName;
open (INPUT_FILE, "<$sTargetFileFullName") || print LOG_FILE "cannot read contents from target file '$sTargetFileFullName'\n";
my @asFileLines = <INPUT_FILE>; 
close INPUT_FILE;
my $sState = "FindGivenHeading";
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
		if ($sLine =~ /$sTargetTopicNameFullLine/) {
		    $nInsertionPos = $nFocusLinePos + 1;
			push(@asAddBlock, "\n");
		    push(@asAddBlock,$sAddText);
			#push(@asAddBlock, "\n");
			print LOG_FILE "adds text to topic top\n";
			$sState = "AddingDone";
		}
	} 
}

# statuses when file ended
if ($sState eq "FindGivenHeading") {   # given heading did not exist
	$nInsertionPos = $FIRST_ADDIBLE_LINE_POS; 
	push(@asAddBlock, $sTargetTopicNameFullLine);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
	push(@asAddBlock, $sAddText);
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
}
splice @asFileLines, $nInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sTargetFileFullName") || print LOG_FILE "Cannot open output file '$sTargetFileFullName'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

close LOG_FILE;
close OUTPUT_FILE;

