package ReportUtils;
use Data::Dumper;
use v5.20;
# copied here 151022
my $sOBJECT_TITLE = "OBJECT";

# -	report template filling by stored values
# - regex string set generating by stored list values
# 	TODO: is this module needed at all ???

# TODO: search perl script, which converts "flat" text to JSON hierarchy (151111)
#  - similar to this Javascript example: https://www.npmjs.com/package/string-to-json   
#------------------------------------------------------------------------------------------------------------------
my $sARRAY_KEY_IND_TAG_regex = "\[\%\s*\W+\s*\%\]"; #
# example: my $sSampleRegex = "^(\w+)\-\>[% TARGET %].*"; # [%...%] syntax is adopted from Catalyst Template Toolkit
#  - string "TARGET" is a hash key. the hash value is an array which contains multiple values
#  - the "$sSampleRegex" string is duplicated and each value in array is used to replace '[% TARGET %]' in regex string
#  - the set of duplicated regex strings are then used one after another when trying to match given target string

#===============================================================================
sub new { my $class = shift;
#===============================================================================
	my $sContext = shift;
	my $self = {
		context => $sContext		# the role or purpose of THIS object
	};
	bless $self, $class;
	MM::TRACE_SUB($sContext); 
	MM::TRACE_RET();
	return $self;
}
#===============================================================================
sub getContext { my ($self) = @_;
#===============================================================================
	return $self->{context};
}




# END OF CLASS
1;
# [% TARGET.sym %] ---->
