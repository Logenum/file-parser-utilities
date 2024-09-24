
my $FALSE=0;
my $TRUE=1;

my $bMatchOK = $FALSE;
my $ConfFile = shift @ARGV;  
#########  CONF FILE STRUCTURE: #################
#	line 0: <line text>
#	line 1: <header part>
#	line 1: <footer part>
#################################################

die "Failed to open trace log file '" unless open(TRACE_LOG,">$TRACE.LOG");

die "Failed to open file '$ConfFile'" unless open(CONF_FILE,"<$ConfFile");
die "Failed to read file '$ConfFile'" unless $sRawLine=<CONF_FILE>; 
close CONF_FILE;
#---------------------------------------------------
die "Failed to open file '$sWholeTargetFileName'" unless open(TARGET_FILE, "<$sWholeTargetFileName");
die "Failed to read file '$sWholeTargetFileName'" unless @saTargetFileLines=<TARGET_FILE>;
close TARGET_FILE;
#---------------------------------------------------
die "Failed to open file '$sWholeTargetFileName'" unless open(TARGET_FILE, ">$sWholeTargetFileName");

foreach $Line (@saTargetFileLines)
{
	print TRACE_LOG "write '$Line' to $sWholeTargetFileName";
	print TARGET_FILE $Line; 
	if ($Line =~ /$sNavigationTargetStr/g)
	{
		$bMatchOK = $TRUE;	
		print TRACE_LOG "$sNavigationTargetStr was found\n";
		addText(@TextToBeAdded);
	}
}

if ($bMatchOK == $FALSE)
{
	print TRACE_LOG "$sNavigationTargetStr was NOT found\n";
	print TRACE_LOG "write 'sNavigationTargetStr\' to $sWholeTargetFileName";
	print TARGET_FILE "\n\n$sNavigationTargetStr\n\n";
	addText(@TextToBeAdded);
}

close TARGET_FILE;
close TRACE_LOG;

