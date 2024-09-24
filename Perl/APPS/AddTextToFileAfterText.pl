
my $FALSE=0;
my $TRUE=1;

my $bMatchOK = $FALSE;
my $ConfFile = shift @ARGV;  
#########  CONF FILE STRUCTURE: #################
#line 0: <whole target file name>
#line 1:	<navigation target string>
#line 2 - line N: <text to be added>
#################################################

die "Failed to open trace log file '" unless open(TRACE_LOG,">$TRACE.LOG");

die "Failed to open file '$ConfFile'" unless open(CONF_FILE,"<$ConfFile");
die "Failed to read file '$ConfFile'" unless $sWholeTargetFileName=<CONF_FILE>; 
die "Failed to read file '$ConfFile'" unless $sNavigationTargetStr=<CONF_FILE>;
die "Failed to read file '$ConfFile'" unless @TextToBeAdded=<CONF_FILE>;
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

#===========================
sub addText
#===========================
{
	my (@saTargetFileLines) = @_;
	print TRACE_LOG "add new lines:\n";
	foreach $Line (@saTargetFileLines)
	{
		print TRACE_LOG $Line;
		print TARGET_FILE $Line; 
	}
}
