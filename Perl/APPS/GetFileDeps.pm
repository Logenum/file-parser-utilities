package MM; #  package name (here acronym of "Main Module") gives class methods to use non-methods (see eg. StateUtils.pm and TraceUtils.pm) 
BEGIN {push @INC,"../PerlUtils"} # to get access to parallel directory modules use TraceUtils;
use EventUtils; 
use StateUtils; 
use MiscUtils;
use StoreUtils;
use ReportUtils;
use BufferUtils;

my $num_args = $#ARGV + 1;
my $sTraceCfgFileName;  # configuration file, which contains multiple regexes to select trace output
my $sCfgFilesNameFile;
my $sVal;
my @asSomeArray;
my $sIgnore;

#my $sSomeRegexStrWithTags = "^.*\\w+[% key_1 %]->foo->[% key_2 %].*(\\d+).*";

my $sSomeRegexStrWithTags = '^.*\\w+([% function %])->foo->([% struct %]).*(\\d+).*';

if ($num_args < 1) {
    print "\nUsage: <this file> <configuration file names file name> <trace configuration file name> \n";
    exit;
}  elsif ($num_args < 2) {
	$sTraceCfgFileName = "NONE"
} else {
	$sTraceCfgFileName = $ARGV[1];
}

$sCfgFilesNameFile = $ARGV[0];  # configuration file, which contains names of files

TRACE_INIT($sTraceCfgFileName, __FILE__);

isValidJson("some non-JSON string");

my @asTextBlock1 = "kukkuu";
my @asTextBlock2 = "hahhaa";

my $oRepA = new ReportUtils("Report A");
my $oStoA = new StoreUtils("Store A");
my $oStoA1 = new StoreUtils("Store A1");
my $oStoA11 = new StoreUtils("Store A11");
my $oStoTmp;


TRACE_END("the end");
