
my $sInLine;
my $sOutLine;



my $sTopicHeading = "";
my $sTOPIC_NAME_TPL 				= "\nH=\"%Topicname%\"\n\n";
my $sNOTETAB_OTL_FILE_FIRST_LINE_tpl 	= "= V4 Outline MultiLine TabWidth=30\n\n"; # adds allways at least this
my $sNOTETAB_OTL_FILE_FIRST_LINE_MATCH_rgx 	= "^=\\s+V\\d\\s+Outline\\s+MultiLine\\s+TabWidth=.*";
my $sTOPIC_NAME_FIRST 				= "CONTENTS";
my $sTOPIC_NAME_LAST 				= "INFO";  # anything can be added and conctenated here (by BAT or CLIP)
my $sAckGrepResultLineCatchRgx		=  "^(\\S+):(\\d+):(.*)";


my $sCallingPathName = $ARGV[0]; 
open(IN_FILE, "$ARGV[1]") || print "Cannot open input file $ARGV[1]";
open(OUT_FILE, ">$ARGV[2]") || print "Cannot open output file $ARGV[2]";

($sTopicHeading = $sTOPIC_NAME_TPL) =~ s/%\w+%/$sTOPIC_NAME_FIRST/g; # -perl: keeps the template



int $bAlreadyOtlFile = 0;

$nLineNbr = 0;
while ($sInLine = <IN_FILE>) {

	if ($nLineNbr == 0) {
		if ($sInLine=~ m/$sNOTETAB_OTL_FILE_FIRST_LINE_MATCH_rgx/g) {
			$bAlreadyOtlFile = 1; 
			print("file ".$ARGV[1]." is already an OTL file !")
		} else {
			print OUT_FILE $sNOTETAB_OTL_FILE_FIRST_LINE_tpl;
			print OUT_FILE $sTopicHeading;
		}
		
	} 
	$nLineNbr++;
	
	if ($bAlreadyOtlFile == 0) {
		if (-d $sInLine) {
			$sOutLine = "[\"explorer.exe\" $sInLine]";  # directory found
		}
		elsif (-s $sInLine) {    			# line is whole existing non-zero size file name (eg. "DIR /b..." result) 
			$sOutLine = "[$sInLine]";
		} elsif (-z $sInLine) {    		# line is whole existing empty file name (eg. "DIR /b..." result) 
			$sOutLine = "[$sInLine]  -EmptyFile: <---";	
		} elsif (($sFileRelName, $sLineNbr, $sLineRest) = ($sInLine=~ m/$sAckGrepResultLineCatchRgx/g)){
			$sOutLine = "[$sCallingPathName\\$sFileRelName::$sLineNbr^L] $sLineRest"; 
		} else {
			$sOutLine = $sInLine;
		}
	} else {
		$sOutLine = $sInLine;
	}
	print OUT_FILE $sOutLine."\n";
	
}

if ($bAlreadyOtlFile == 0) {
	($sTopicName = $sTOPIC_NAME_TPL) =~ s/%\w+%/$sTOPIC_NAME_LAST/g; # -perl: keeps the template
	print OUT_FILE $sTopicHeading;
}

close IN_FILE;
close OUT_FILE;

