package StoreUtils;
use Data::Dumper;
use v5.20;
# copied here 151022
my $sOBJECT_TITLE = "OBJECT";
# -	store and retrieval of strings and objects
# - handling and checks whether strings are JSON structures
# - objects of this class can be inserted recursively to other objects of this class

# TODO: search perl script, which converts "flat" text to JSON hierarchy (151111)
#  - similar to this Javascript example: https://www.npmjs.com/package/string-to-json  
#  http://www.sitepoint.com/community/t/perl-sort-array-of-arrays/5885/2 

#===============================================================================
sub new { my $class = shift;
#===============================================================================
  
	my $sContext = shift;
	my $self = {
		context => $sContext, 		# the role or purpose of THIS object
		bTemplateFilledOk => 0,
		hSingleItemStore => {},  		# !!: single hash
		haListItemStore => {},			# !!: hash of arrays: no specific notation at definition !!!
		haListItemBackupStore => {}	# contains all values which are pushed to 'haListSingleItemStore' but nothing is popped away
		# Item stores can contain strings, JSON strings, numbers, objects (=also other instances of THIS class) or structs
		#TODO: add hash of Lists
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

#===============================================================================
sub set	{ my ($self, $sKey, $xAnything) = @_;  
#===============================================================================
	# for storing data for retrieving by 'get' or by 'fill template' 
	# stored values can be also JSON strings
	MM::TRACE_SUB($self->{context});
	my $sOptionalComment 	="";
	my $rhSingleItemStore 		= \%{$self->{hSingleItemStore}};

	if (MM::isValidJson($xAnything)) {
		$sOptionalComment = "(syntax is JSON)";
	}
	MM::TRACE_BAG(Dumper($xAnything));
	my $xOldAnything = $rhSingleItemStore->{$sKey};
	if ($xOldAnything eq "") {
		MM::TRACE("set key {$sKey} item '$xOldAnything' $sOptionalComment");
	} else {
		MM::TRACE("changed key {$sKey} item '$xOldAnything' to value '$xAnything' $sOptionalComment");
	}
	$$rhSingleItemStore{$sKey} = $xAnything;
	MM::TRACE_RET();
}
#===============================================================================
sub get { my ($self, $sKey) = @_;
#===============================================================================
	# for retrieving data stored by 'put()'
	# if value is valid JSON string, a reference to corresponding Perl structure is returned as another parameter
	MM::TRACE_SUB($self->{context});
	my $sOptionalComment ="";
	my $xAnything;
	my $sAnythingAsStr;
	my $rxPossibleStruct= 0;  #  TODO: add usage 151113
	my $rhSingleItemStore 	= \%{$self->{hSingleItemStore}};
	$xAnything 			= $rhSingleItemStore->{$sKey};  	# accessing a hash when has reference is available
	my ($sAnythingAsStr, $sDataType) 		= MM::getDataByType($xAnything);
	#MM::TRACE_BAG($sValAsStr);
	if ($xAnything eq "") {
		$xAnything="EMPTY";
		MM::TRACE("key {'$sKey'} contains no value");
	} else {
		MM::TRACE("key {'$sKey'} gave value '$xAnything' (data type ='$sDataType')");
	}
	MM::TRACE_RET();
	return ($xAnything);
}
#===============================================================================
sub push { my ($self, $sKey, $xAnything) = @_;  
#===============================================================================
	# for adding item 'labeled' by given key
	# stored item can be also JSON strings
	
	my $sOptionalComment ="";
	MM::TRACE_SUB($self->{context});
	my $rhaListItemStore 		= \%{$self->{haListItemStore}};   # !!: hash of arrays
	my $rhaListItemBackupStore 	= \%{$self->{haListItemBackupStore}};   # !!: hash of arrays

	if (MM::isValidJson($xAnything)) {
		$sOptionalComment = "(syntax is JSON)";
	}

	MM::TRACE("key {'$sKey'[]} val '$xAnything' $sOptionalComment");
	push @{$$rhaListItemStore{$sKey}}, $xAnything;     		#!!: adding value to array by hash key
	push @{$$rhaListItemBackupStore{$sKey}}, $xAnything;     	# adding value to non-poppable array for possible 'rewind' usage later
	#my $sForTrace = MM::getDataByType($rhaListItemStore);
	MM::TRACE_BAG(Dumper($rhaListItemStore));
	# http://stack$overflow.com/questions/3779213/how-do-i-push-a-value-onto-a-perl-hash-of-arrays
	# http://archive.oreilly.com/pub/a/perl/excerpts/9780596000271/data-structures.html
	MM::TRACE_RET();
}

#===============================================================================
sub fill { my ($self, $sKey, $raxAnything) = @_;  
#===============================================================================
	# for storing multiple items at once by given key

	MM::TRACE_SUB($self->{context});
	my $xAnything;
	my @axAnything = @$raxAnything;
	foreach $xAnything (@axAnything) {
		$self->push($sKey, $xAnything);
	}
	MM::TRACE_RET();
}
#===============================================================================
sub pop { my ($self, $sKey) = @_;  # name capitalized to avoid collision with standard function
#===============================================================================
	# for retrieving item from array 'labeled' by given key
	# if value is valid JSON string, a reference to corresponding Perl structure is returned as another parameter 
	MM::TRACE_SUB($self->{context});
	my $xAnything;
	my $sAnythingAsStr;
	my $rxPossibleStruct 	= 0;  # initial quess: value is not a JSON string
	my $sOptionalComment 	= "";
	my $rhaListItemStore 	= \%{$self->{haListItemStore}};   #!!: hash of arrays

	my $xAnything = pop @{$$rhaListItemStore{$sKey}};    #!!: retrieving value from array by hash key
	my ($sAnythingAsStr, $sDataType) 		= MM::getDataByType($xAnything);
	if (MM::isValidJson($xAnything)) {
		$sOptionalComment = "(syntax is JSON)";
		$xAnything = MM::fromJson($xAnything);
	}
	if ($xAnything ne "") {
		MM::TRACE("key {'$sKey'[]}  val '$xAnything'");		
	} else {
		MM::TRACE("key {'$sKey'[]} is now EMPTY");
	}
	MM::TRACE_RET();
	return ($xAnything);
}

#===============================================================================
sub pick { my ($self, $sKey, $nPosNbr) = @_;  
#===============================================================================
# similar to pop, but position number is explicitly given
	MM::TRACE_SUB($self->{context});
	my $xAnything;
	my $sAnythingAsStr;
	my $rxPossibleStruct 	= 0;  # initial quess: value is not a JSON string
	my $sOptionalComment 	= "";
	my $rhaListItemStore 	= \%{$self->{haListItemStore}};   #!!: hash of arrays

	my $xAnything = $$rhaListItemStore{$sKey}[$nPosNbr];    #!!: retrieving value from array by hash key
	my ($sAnythingAsStr, $sDataType) 		= MM::getDataByType($xAnything);
	if (MM::isValidJson($xAnything)) {
		$sOptionalComment = "(syntax is JSON)";
		$rxPossibleStruct = MM::fromJson($xAnything);
	}
	if ($xAnything ne "") {
		MM::TRACE("key {'$sKey'[$nPosNbr]}  val '$xAnything'");		
	} else {
		MM::TRACE("key {'$sKey'[]} is now EMPTY");
	}
	MM::TRACE_RET();
	MM::TRACE_RET();
	return ($xAnything);
}

#===============================================================================
sub drain { my ($self, $sKey) = @_;  
#===============================================================================
	# # for retrieving all items at once from array 'labeled' by given key
	
	# MM::TRACE_SUB($self->{context});
	# my $xAnything;
	# my @axAnything = @$raxAnything;
	# $xAnything = pop @{$$rhaListItemStore{$sKey}}; 
	
	# foreach $xAnything (@axAnything) {
		# $xAnything = $self->pop($sKey);
	# }
	# MM::TRACE_RET();
	# return ($xAnything);
}
#===============================================================================
sub sortLex { my ($self, $sKey, $nSortOrder) = @_;  
#===============================================================================
	# sort single array within a hash of Arrays 
	# - in lexical order (not in numerical order)
	# http://perlmaven.com/sorting-arrays-in-perl
	# http://perldoc.perl.org/functions/sort.html
	MM::TRACE_SUB($self->{context});
	my @asSorted;
	my $rhaListItemStore 	= \%{$self->{haListItemStore}};   #!!: hash of arrays
	
	if (defined $nSortOrder) {
		@asSorted = sort {$b cmp $a} @{$$rhaListItemStore{$sKey}};  # !!: perl: lexical sort in descending order
	} else {
		@asSorted = sort {$a cmp $b} @{$$rhaListItemStore{$sKey}};  # !!: perl: lexical sort in ascending order
		# = default, if 'sort order' -parameter is not given at all
	} 
	@{$$rhaListItemStore{$sKey}} = @asSorted;
	
	MM::TRACE_RET();
}
#===============================================================================
sub sortLexAll { my ($self, $nPos, $nSortOrder) = @_;  
#===============================================================================
	# sort all items in hash of arrays   TODO: 151115
	#  
	# - in lexical order (not in numerical order)
	# http://stackoverflow.com/questions/8531849/perl-sort-hash-of-arrays
	#	-	sorts also keys !!?  (see example)
	my $rhaListItemStore 		= \%{$self->{haListItemStore}};   # !!: hash of arrays
	MM::TRACE_SUB($self->{context});
	
	for my $key ( sort { $$rhaListItemStore{$a}[$nPos] <=> $$rhaListItemStore{$b}[$nPos] } keys %$rhaListItemStore ) {
		print "$key => '", join(", ", @{$$rhaListItemStore{$key}}), "'\n";
	}

	MM::TRACE_RET();
}


#===============================================================================
sub getSingleItemAccess { my ($self) = @_;  
#===============================================================================
	# for retrieving value from array 'labeled' by given key
	#MM::TRACE_SUB();
	my $rhSingleItemStore 		= \%{$self->{hSingleItemStore}};
	my $sContext 		= $self->{context};
	#MM::TRACE("$sOBJECT_TITLE: '$sContext'");
	
	#MM::TRACE_RET();
	return $rhSingleItemStore;
}
#===============================================================================
sub getListItemAccess { my ($self) = @_;  
#===============================================================================
	# for retrieving value from array 'labeled' by given key
	#MM::TRACE_SUB();
	my $rhaListItemStore 	= \%{$self->{haListItemStore}};   #!!: hash of arrays
	my $sContext 		= $self->{context};	
	#MM::TRACE_RET();
	return $rhaListItemStore;
}
#===============================================================================
sub  getListSize{ my ($self, $sKey) = @_;  
#===============================================================================
	# for retrieving value from array 'labeled' by given key
	
	MM::TRACE_SUB($self->{context});
	my $rhaListItemStore 	= \%{$self->{haListItemStore}};   #!!: hash of arrays
	MM::TRACE("key='$sKey'");
	my $nSize = @{$$rhaListItemStore{$sKey}};    #!!: array size by hash key
	MM::TRACE_RET();
	return $nSize;
}
#===============================================================================
sub clearAll{ my ($self) = @_;
#===============================================================================
	# for stored data by 'put()'
	MM::TRACE_SUB($self->{context});
	%{$self->{hSingleItemStore}} 		=();   
	%{$self->{haListItemStore}}		=();
	%{$self->{haListItemBackupStore}}	=();
	MM::TRACE_RET();	
}

#===============================================================================
sub rewind{ my ($self, $sKey) = @_;
#===============================================================================
	# each 'popVal()' call removes value from list store
	# this method sets list store such a state, that it contains all values which has been pushed into it
	# http://stackoverflow.com/questions/11017523/copying-values-from-one-hash-to-another-in-perl
	MM::TRACE_SUB($self->{context});
	my $rhaListItemStore 			= \%{$self->{haListItemStore}};   		#!!: hash of arrays
	my $rhaListItemBackupStore 	= \%{$self->{haListItemBackupStore}};		#!!: hash of arrays

	$$rhaListItemStore{$_} = $$rhaListItemBackupStore{$_} for keys %$rhaListItemStore;  #!!: copies a hash to another
	# http://stackoverflow.com/questions/11017523/copying-values-from-one-hash-to-another-in-perl  #!!: copying a hash to another (example,guide,web)
	MM::TRACE_RET();	
}
#===============================================================================
sub dubTemplate { my ($self, $sTaggedTemplate) = @_;  
#===============================================================================
# TODO: change this function to StoreUtils
	# builds an array combination of strings, where each tag is replaced by value
	# example: 
	#	my $sTemplateWithTags = "^.*([% ARRAY_KEY_1 %]) + ([% ARRAY_KEY_2 %]).*";
	#	result dubbed
	#	"^.*(val_11) + (val_21).*"
	#	"^.*(val_12) + (val_21).*"
	#	"^.*(val_11) + (val_22).*"
	#	"^.*(val_12) + (val_22).*"
	#
	#---------------------------------------------------------------------------
	my @saDubbedTemplates;
	my $sPreEditTemplate;
	my $sPostEditTemplate;
	my @asEditedTemplates;
	my $sHashKeyInTag;
	my $rasTagFrames;
	my $rasTagCores;
	my $nTagPos;
	my $nTagCnt;
	my $nTemplatePos;
	my $nTemplateCnt;
	my $nListItemPos;
	my $nListItemCnt;
	my $sHashKey;
	my $sListItem;
	my $rxPossibleStruct;
	my $nPopCnt;
	my $sDump;
	my $sTagFrame;
	my $sEscapedTagFrame;
	my $sTagCore;
	my $sTAG_FRAME_CAPTURE_regex =  "(\\[\\%\\s*\\w+\\s*\\%\\])";   #  tag frames
	my $sTAG_CORE_CAPTURE_regex =  "\\[\\%\\s*(\\w+)\\s*\\%\\]";   # hash keys within tag frame
	
	MM::TRACE_SUB($self->{context});
	
	($nTagCnt, $rasTagFrames, $rasTagCores) = MM::captureTags($sTaggedTemplate, $sTAG_FRAME_CAPTURE_regex, $sTAG_CORE_CAPTURE_regex); # all framed tags within given template
	if ($nTagCnt > 0) { # tag frames did exist, and each tag frame did contain one tag core
		@asEditedTemplates = ($sTaggedTemplate); # initialization
		$nTemplateCnt = @asEditedTemplates; # initialization
		for ($nTagPos=0; $nTagPos < $nTagCnt; $nTagPos++) {   # for each tag found in unedited template
			$sTagFrame 	= $$rasTagFrames[$nTagPos]; 
			$sTagCore 	= $$rasTagCores[$nTagPos];
			MM::TRACE("start process tag '$sTagCore'");
			#MM::TRACE("tags/frame/core = '$nTagCnt'/'$sTagFrame'/'$sTagCore'");
			$sHashKey 	= $sTagCore;
			$nListItemCnt = $self->getListSize($sHashKey);
			for ($nListItemPos=0; $nListItemPos < $nListItemCnt; $nListItemPos++) {
				($sListItem)  = $self->pop($sHashKey);
				if (MM::isValidJson($sListItem)) {  # data value is JSON string
					MM::TRACE("value is a JSON string: not suitable for template value insertion");
					last;
				}
				if ($sListItem ne "") { # tag core string is a hash key to array of values
					MM::TRACE_IND("start process list val '$sListItem' at [$nListItemPos]");
					for ($nTemplatePos=0; $nTemplatePos < $nTemplateCnt; $nTemplatePos++) {  # process all unedited, edited or completed templates
						$sPreEditTemplate = $asEditedTemplates[$nTemplatePos];
						MM::TRACE_IND("start process template '$sPreEditTemplate' at [$nTemplatePos]");	
						$sEscapedTagFrame = MM::escapeTagFrame($sTagFrame);
						#MM::TRACE("template '$sEditedTemplate' before trying to replace '$sEscapedTagFrame' with '$sListItem'");
						$sPostEditTemplate = $sPreEditTemplate;
						$sPostEditTemplate =~ s/$sEscapedTagFrame/$sListItem/g;
						MM::TRACE("template '$sPostEditTemplate' after replacement");
						if ($sPostEditTemplate ne $sPreEditTemplate) {
							push(@asEditedTemplates, $sPostEditTemplate); 
							$nTemplateCnt = @asEditedTemplates; # reallocation
						}
					}
				} else {  # last array value passed
					MM::TRACE_IND("storage now empty, '$nPopCnt' items popped, jump out of while loop");
					$nPopCnt = 0;
					last;
				}
			}
		}
		@saDubbedTemplates = @asEditedTemplates;  # all templates are now actually fully filled
	} else {
		MM::TRACE("regex template '$sTaggedTemplate' did not contain any tags");
		push(@saDubbedTemplates, $sTaggedTemplate); # just single string because no tags were replaced 
	}
	@saDubbedTemplates = grep(!/$sTAG_FRAME_CAPTURE_regex/, @saDubbedTemplates);  # !!: removal of array items containing certain string
	$sDump = Dumper(@saDubbedTemplates);
	MM::TRACE_BAG($sDump, $self->{context});
	MM::TRACE_RET();
	return \@saDubbedTemplates;
}
#================================================================
sub fillTemplates{ my ($self, $ra_Templates) = @_;
#================================================================
# TODO: change this function to StoreUtils
	# TODO: try to make just ONE template filler/dubber function 151113
	# for retrieving data stored by 'put()'
	# loops through an array of 1...N tagged templates and tries to replace tags with values
	# if '.lbl' or '.sym' extensions found, corresponding strings are processed accordingly
	# if replacement is not found for some tag, filled-ok bit is set to 0 
	my $sRawTemplate;
	my $sFilledTemplate;
	my @asFilledTemplates;
	my $sSym;
	my $sVal;
	my $sFormatSymCandidate;
	my $sFormatLblCandidate;
	my $sValSymbolified;
	my $sValLabelified;
	
	my $rhSingleItemStore 		= \%{$self->{hSingleItemStore}};

	MM::TRACE_SUB($self->{context});

	if ($$ra_Templates[0] ne "NONE") {
		foreach $sRawTemplate (@$ra_Templates) {
			MM::TRACE("raw template: '$sRawTemplate'");
			$sFilledTemplate = $sRawTemplate;
			foreach $sSym (keys %$rhSingleItemStore) {
				$sVal= $$rhSingleItemStore{$sSym};
				$sFormatSymCandidate = $sSym.".sym";
				if ($sFilledTemplate =~ /^.*$sFormatSymCandidate/ig) {   # case insensitive
					$sValSymbolified = MM::sym($sVal);
					# TODO: maybe '$' would be better tag than '%'
					$sFilledTemplate =~ s/\$$sFormatSymCandidate/$sValSymbolified/g;
				}
				$sFormatLblCandidate = $sSym.".lbl";
				if ($sFilledTemplate =~ /^.*$sFormatLblCandidate/ig) {   # case insensitive
					 $sValLabelified = MM::lbl($sVal);
					$sFilledTemplate =~ s/\$$sFormatLblCandidate/$sValLabelified/g;
				}	
				$sFilledTemplate =~ s/\$$sSym/$sVal/g;
			}
			if ($sFilledTemplate =~ /^.*\$\w+.*/) {  # all fields are not filled
				MM::TRACE("template '$sFilledTemplate' all fields are not filled !!!");
				$self->{bTemplateFilledOK} = 0;
			} else {
				MM::TRACE("completely filled template: '$sFilledTemplate'");
				$self->{bTemplateFilledOK} = 1;
			}
			push(@asFilledTemplates, $sFilledTemplate);
		}
	} else {
		MM::TRACE("error: templates missing");
	}
	MM::TRACE_RET();
	return \@asFilledTemplates;
}
#===============================================================================
sub isTemplateFilled { my ($self) = @_; 
#===============================================================================
	return $self->{bTemplateFilledOK};
}
1;
