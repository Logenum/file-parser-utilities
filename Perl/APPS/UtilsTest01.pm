package MM; #  package name (here acronym of "Main Module") gives class methods to use non-methods (see eg. StateUtils.pm and TraceUtils.pm) 
BEGIN {push @INC,"../PerlUtils"} # to get access to parallel directory modules use TraceUtils;
use EventUtils;  # added 151119
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

$oStoA->set("scalar hash key", "scalar hash val"); 
$sVal = $oStoA->get("scalar hash key"); 

$oStoA->push("function", "initialize");
$oStoA->push("function", "reset");
$oStoA->push("function", "process");

$oStoA->push("struct", "database");
$oStoA->push("struct", "configuration");
$oStoA->push("struct", "message");

$oStoA1->push("struct", "database");
$oStoA1->push("struct", "configuration");
$oStoA1->push("struct", "message");

$oStoA->set("object A1", $oStoA1);

($oStoTmp) = $oStoA->get("object A1");  # !!: perl: returning object reference requires parentheses (otherwise considered a SCALAR value)

$oStoTmp->pop("struct");
$oStoTmp->pop("struct");
$oStoTmp->pop("struct");
$oStoA->rewind("key_1");

(@asSomeArray) = $oStoA->dubTemplate($sSomeRegexStrWithTags);

$oStoA->clearAll();

=Commented
my $oStJustTest = new StateUtils("ST_JUST_TEST", "just test"); 

my $READ_ONLY = 0;
my $oOutOtl = new BufferUtils("for testing OTL file output");
my $oInCfg = new BufferUtils("for testing file roles file parsing",$READ_ONLY);

$oInCfg->fillFromFile("LvalRvalTest1.txt"); 

# note: "qq" minimizes amount of quotes and backslashes
# each "key" means the "role" of corresponding regex (shall be inserted to result data)
my $sSectionParseRegexArrayAsJson = qq({"comparison":"\W*if(\W*.*)",
										"assignment":"(.*)=(.*)"});
# TODO: get familiar with complicate regexes to capture anything (#)
#   - how to escape parentheses eg.						
my $sConvConfRegex = qq({"capture":"^(.*(.*)\?)\s*(%.*?)", "output":"^\s*(%.*)\$"}); 
my $sOtlTopicHeadingRegexAsJson = qq([H=\"(.*)\""]); 
$sOtlTopicHeadingRegexAsJson = qq(["H=\\"(.*)\\""]);
my $sObsoleteSectionHeadingInd ="N/A";

#my $sectionHeadingParseRegexAsJson = qw/["heading":/;

$oOutOtl->writeToFile("justtest.txt");
$oOutOtl->appendFile(\@asTextBlock2);
$oInCfg->pickAct();
$oInCfg->trimAct();
$oInCfg->getTree($sObsoleteSectionHeadingInd, $sConvConfRegex);


#$SomeIn->getTree($sConvConfRegex); 
#$SomeIn->getTree($sSectionParseRegexArrayAsJson); 
=cut
TRACE_END("the end");
