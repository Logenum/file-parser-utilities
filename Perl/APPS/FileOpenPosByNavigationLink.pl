
my $FALSE=0;
my $TRUE=1;
my $THIS_FILE_NAME = $0;

my $nLinePos = 0;

my $MAP_SEPARATOR_TAG = "===>";
my $MAP_CAPTURE_REGEX = "(\\w+)\\s*$MAP_SEPARATOR_TAG\\s*(.*)"; 

# link example: [PROJECT_PATH|DoThings.pl|mainfunc|index|a=5]

my $LINK_PATH_AND_FILE_REGEX = ".*\\[(\\w+)\\|([\\w\\.]*)\\|(.*)\\]";   # note: use DOUBLE backslashes in STRING regex!!! 

my $bLinkChainEndMatchOK = $FALSE;
my %hKeyValPair = {};

my $nLinkChainLastPartPos = 0;
my $nLinkChainFocusPartPos = 0;

my @aCommandLineParams=[];

my @saMapFileLines=[];
my $ConfFile = shift @ARGV;  

#########  CONF FILE STRUCTURE: ############################################
#line 0: <navigation link syntax chain string>
#line 1: <whole link tag mapping configuration file name>
#line 2: <whole file open editor startup line> 
############################################################################

die "Failed to open trace log file '" unless open(TRACE_LOG,">TRACE.LOG");
print TRACE_LOG "------------ start this file updating ----------------\n";
close TRACE_LOG;

die "Failed to open file '$ConfFile'" unless open(CONF_FILE,"<$ConfFile"); 
die "Failed to read file '$ConfFile'" unless $sNavigationLink=<CONF_FILE>;
chop $sNavigationLink;
die "Failed to read file '$ConfFile'" unless $sWholeLinkTagMapConfFileName=<CONF_FILE>;
chop $sWholeLinkTagMapConfFileName;
die "Failed to read file '$ConfFile'" unless $sEditorStartupLineTemplate=<CONF_FILE>;
chop $sEditorStartupLineTemplate;
close CONF_FILE;

#----------------------------------------------------------------------------------------------------------
die "Failed to open file '" unless open(MAP_FILE,"<$sWholeLinkTagMapConfFileName");
die "Failed to read file '$sWholeLinkTagMapConfFileName'" unless @saMapFileLines=<MAP_FILE>;
TRACE("lines '@saMapFileLines' (from file $sWholeLinkTagMapConfFileName)");
close MAP_FILE;
#-----------------------------------------------------------------------------------------------------------
if (($PathMap, $FileName, $sRawLinkChain) = ($sNavigationLink =~ m/$LINK_PATH_AND_FILE_REGEX/g))
{
	TRACE("$sNavigationLink <>--- 1: $PathMap 2: $FileName 3: $sRawLinkChain  by $LINK_PATH_AND_FILE_REGEX");

	@aLinkChain	= split (/\|/, $sRawLinkChain);
	$nLinkChainLastPartPos = $#aLinkChain;
	TRACE("Link chain:  @aLinkChain, item count: $nLinkChainLastPartPos+1");
}
else
{
	TRACE("'$LINK_PATH_AND_FILE_REGEX' did NOT match to '$sNavigationLink'");
}
#-----------------------------------------------------------------------------------------------------------
foreach $Line (@saMapFileLines)
{
	TRACE("MAP $Line (from $sWholeLinkTagMapConfFileName)");
	if (($Key,$Val) = ($Line =~ m/$MAP_CAPTURE_REGEX/g))
	{
		TRACE("Key: '$Key' / Value: '$Val'");
		$hKeyValPair{$Key} = $Val;
	}
	else
	{
		TRACE("Regex '$MAP_CAPTURE_REGEX' did NOT match to $_");
	}
}

$sPathName = $hKeyValPair{$PathMap};
$sWholeTargetFileName = "$sPathName$FileName";
$aCommandLineFields[0] = $sWholeTargetFileName;

#----------------------------------------------------------------------------------------------------------

die "Failed to open file '$sWholeTargetFileName'" unless open(TARGET_FILE, "<$sWholeTargetFileName");
TRACE("Opened file '$sWholeTargetFileName'");

die "Failed to read file '$sWholeTargetFileName'" unless @saTargetFileLines=<TARGET_FILE>;
close TARGET_FILE;
#----------------------------------------------------------------------------------------------------------
foreach $Line (@saTargetFileLines)
{
	#TRACE("check line  '$Line'[$nLinePos]");
	if ($nLinkChainFocusPartPos <= $nLinkChainLastPartPos)
	{
		$sChainFocusPart = $aLinkChain[$nLinkChainFocusPartPos];
		if ($Line =~ m/.*$sChainFocusPart.*/g )
		{
			$nLinkChainFocusPartPos++;
		TRACE("string '$sChainFocusPart' found at line '$Line' ($nLinePos)");
		}
		else
		{
			#TRACE("string '$sChainFocusPart' not found at line '$Line'");
		}
		$nLinePos++;
	}
	else
	{
		TRACE("string all chain '$sRawLinkChainParts' parts found ");
		$bLinkChainEndMatchOK = $TRUE;
		$aCommandLineFields[1] = $nLinePos;
		last;
	}
}
#------------------------------------------------------------------------------------------------------------------------
if ($bLinkChainEndMatchOK == $TRUE)
{
	if ($sEditorStartupLineTemplate)  # not empty
	{
		$i=1;
		$j=0;
		foreach (@aCommandLineFields)
		{
			$sEditorStartupLineTemplate  =~ s/%$i%/$aCommandLineFields[$j]/g;
			$i++; $j++;
		}
	
		TRACE("Execute system command: '$sEditorStartupLineTemplate'");
	
		system($sEditorStartupLineTemplate);
	}
	else
	{	
		TRACE("ERROR: editor line is empty");
	}
}
#------------------------------------------------------------------------------------------------------------------------

sub TRACE
{
	my ($Comment) = @_;
	open(TRACE_LOG,">>TRACE.LOG");
	my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info
	print TRACE_LOG "$Comment  ($line)\n";
	close TRACE_LOG;
}

