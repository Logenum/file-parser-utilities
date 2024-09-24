#!/usr/bin/perl
use strict;
use warnings;
package PERL_SCRIPTS;

BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  
#use UTILS;
use Data::Dumper

# started 140822
# DONE 140823
my $FALSE=0;
my $TRUE=1;
my $sInFile   			= shift @ARGV;  
my $sOutFile   			= shift @ARGV;
#my $sTopicNameLinePattern  = shift @ARGV;
my $sGivenTopicName  	= shift @ARGV;
my $sAddText 			= shift @ARGV;
#=comment
#TODO: 
open (LOG_FILE, ">TRACE.LOG");
my @asAddText = split('\n',$sAddText);  # note: splitting reguired the splitter char
$sAddText="";
foreach (@asAddText) { # removes possibly empty lines
	next if /^\s*$/;  # note: way to check if line is empty
	$sAddText=$sAddText.$_."\n";
} 

if ($sAddText =~ /^\s*$/) {
	
}
#=cut

print LOG_FILE "in/out = $sInFile/$sOutFile\n";
#  "aaaa bbbb 111" 	# topic name
my $sTopicNameLinePattern = "H=\".*\"";
my $NAME_PATTERN = "\".*\"";

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
			#push(@asAddBlock, "\n");
			print LOG_FILE "adds text to topic top\n";
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
	push(@asAddBlock, "\n");
	push(@asAddBlock, "\n");
}
splice @asFileLines, $nInsertionPos, $nOverWriteLen, @asAddBlock;
open (OUTPUT_FILE, ">$sOutFile") || print LOG_FILE "Cannot open output file '$sOutFile'\n";
foreach (@asFileLines) {
    print OUTPUT_FILE $_;
}

close LOG_FILE;
close OUTPUT_FILE;

