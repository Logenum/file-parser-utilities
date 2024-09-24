use v5.20;
package BufferUtils;
use Data::Dumper;
use Data::Dumper;
use JSON;
use TraceUtils;
use EventUtils;

# replaced "inFileUtils" and "outfileutils" with this generic "buffer utils" (#)
#  buffer contents is read from a file or written to a file
#  data is extracted, reduced, trimmed and strucured     
# http://www.tek-tips.com/viewthread.cfm?qid=1352043
# TODO: make ALL kinds of buffer extraction into a three -level hierarchy
# 	-	concepts: 'region', 'section' and 'group'
# 		-	if not found, default strings are used as headings 
#-----------------------------------------------------------------------------
my $sNOTETAB_OTL_FILE_TOP_LINE_MATCH_regex = ".*Outline.*MultiLine.*TabWidth.*";
#my $sNOTETAB_ACTIVE_OTL_TOPIC_HEADING_CAPTURE_regex = "^H\=\"(?!#.*)\"";  # for NOT having '#' prefix in name
#my $sNOTETAB_ACTIVE_OTL_TOPIC_HEADING_CAPTURE_regex = "^H\=\\\"(.*)\\\""; 
my $sNOTETAB_ACTIVE_OTL_TOPIC_HEADING_CAPTURE_regex = qw /^H\=\"(.*)\"/;  # note: 'qw' usage reduces quoting backslashes remarkably
my $sNOTETAB_COMMENTED_OTL_TOPIC_HEADING_MATCH_regex = qw /^H\=\"#.*\"/;
#----------------------------------------------------------------------------
my $sPERL_EXTENSIONLESS_FILE_DETECT_LINE_MATCH_regex = qw /^\s*#!.*perl.*/;
my $sPERL_SUBROUTINE_HEADING_CAPTURE_regex = qw /^\s*sub\s*(\w+).*/;
#----------------------------------------------------------------------------
my $sMATCH_ANYTHING_CAPTURE_regex = qw /(^.*$)/;
my $sMATCH_ANYTHING_regex = qw /^.*$/;

# for parsed data:
my $sSECTION_HEADING_KEYWORD = "heading";
my $sSECTION_CONTENTS_KEYWORD = "contents";

my $nVERY_SMALL_SIZE=3;  # for detecting possibly invalid contents etc.
my $m_sSECTIONS_PRE_LINE_IND = qw/_SECTIONS_PRE_/; # to put something to section heading positions

my $m_sTRIPOD_REGION_DUMMY_HEADING_NAME 	= "_REGION_";  
my $m_sTRIPOD_SECTION_DUMMY_HEADING_NAME 	= "_SECTION_";
my $m_sTRIPOD_GROUP_DUMMY_HEADING_NAME 		= "_GROUP_";

# http://www.devshed.com/c/a/perl/file-tests-in-perl/
#===============================================================================
sub new { my ($class, $sContext, $sFileWriteEnabled) = @_;
#===============================================================================
	# note: these state methods are in different package than TRACE methods

	my $self = {
		filler_file_full_name 	=> "UNKNOWN",
		write_file_full_name 	=> "UNKNOWN",
		path_name 				=> "UNKNOWN",
		file_write_allowed 		=> $sFileWriteEnabled,
		file_name 				=> "UNKNOWN",
		context 				=> $sContext,
		file_ext 				=> "UNKNOWN",		
		sBufferContentsType 	=> "UNKNOWN",   # equal to file type
		buffer_state  			=> "ST_EMPTY",
		asRawLines 				=> [],   #  also 'sortLines()' updates this
		asActLines 				=> [],
		asTrimLines 			=> [],
		aasEnlistedLists 		=> [],   		# e.g. each section in separate array (for two-level files)
		aaasTripodLists				=> [],		# for "forced" extraction of ANY file into a three-level hierarchy
		rasLinesArrayByLatestState 	=> [], 		# points to asRaw_lines, asAct_lines or asTrim_lines
		nLinePos 					=> -1,
        nCharPosAtLine 				=> 0,
		bHasBeenEnlisted 			=> 0,  		# flag to indicate whether buffer contents has succesfully been extracted to array of arrays
		# bArrayHasBeenSorted
		nLineLastCharPos 			=> 0,
		bHasBeenFilled 				=> 0,
		bHasBeenWritten 			=> 0,
		nBookmarkLinePos 			=> 0,
		bBufferEnded				=> 0 # flag to indicate "EOF" string finding 	
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
sub assignFile { my ($self, $sFileFullName) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	$self->{full_file_name} = $sFileFullName;
	MM::TRACE("file '$sFileFullName'");
	MM::TRACE_RET();	
}
#===============================================================================
sub fillFromFile { my ($self, $sFileFullName) = @_;
#===============================================================================
	# file name can be given as a parameter or it can be given by "assignFile()" method
	
	my $bStatus 		= 0; # initial quess
	my $rasTmp; 
	my $sBufferState 	= $self->{buffer_state};
	MM::TRACE_SUB($self->{context});
	$self->{nLinePos} 	= -1;
	$self->{nLineCharPos} = 0;
	
	if (defined $sFileFullName) {
		$self->{full_file_name} = $sFileFullName;
	} else {
		$sFileFullName = $self->{full_file_name};
	}
	
	if ( -e $sFileFullName) {
		if ( -s $sFileFullName) {
		} else {
			MM::TRACE("NOT filled from empty file '$sFileFullName'");
			MM::TRACE_RET();
			return $bStatus;
		}
		if (open (fhFILE, "<$sFileFullName")) {  
			MM::TRACE("file '$sFileFullName' open succeeded");
			#@m_asRawLines = <$fhFILE>;
			if ($sBufferState eq "ST_EMPTY") {
				$rasTmp = \@{$self->{asRawLines}};
				@$rasTmp = <fhFILE>;
				close fhFILE;
				$self->{bHasBeenFilled} = 1;
				MM::TRACE("is filled from file '$sFileFullName'");
				$bStatus = 1;
			} else {
				MM::TRACE("state is '$sBufferState' so it is NOT filled from file '$sFileFullName'");
			}
		} else {
			MM::TRACE("FAILED to open file '$sFileFullName'");
		}
	} else {
		MM::TRACE("file '$sFileFullName' does NOT exist");
	}
	
	$self->{rasLinesArrayByLatestState} = \@{$self->{asRawLines}};
	MM::TRACE_BAG(\@{$self->{asRawLines}});
	MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub fillFrom{ my ($self, $rasLines) = @_;
#===============================================================================
	# fills buffer from given array reference
	my $bStatus 		= 0; # initial quess
	MM::TRACE_SUB($self->{context});
	$self->resetPos();
	@{$self->{asRawLines}} = @$rasLines;
	$self->{bHasBeenFilled} = 1;
	$self->{rasLinesArrayByLatestState} = \@{$self->{asRawLines}};
	MM::TRACE_BAG(\@{$self->{asRawLines}});
	MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub writeToFile { my ($self, $sFileFullName) = @_;
#===============================================================================
# file name can be given as a parameter or it can be given by "assignFile()" method
	if (defined $sFileFullName) {
		$self->{full_file_name} = $sFileFullName;
	} else {
		$sFileFullName = $self->{full_file_name};
	}
	MM::TRACE_SUB($self->{context});
	return ($self->bufferToFile($sFileFullName,"WRITE"));
	MM::TRACE_RET();	
}
#===============================================================================
sub writeUniquesToFile { my ($self, $sFileFullName) = @_;
#===============================================================================
	# identical buffer lines are written only once (eg. reduces cluttering in Graphviz diagrams)
	if (defined $sFileFullName) {
		$self->{full_file_name} = $sFileFullName;
	} else {
		$sFileFullName = $self->{full_file_name};
	}
	MM::TRACE_SUB($self->{context});
	return ($self->bufferToFile($sFileFullName,"WRITE_LINES_ONCE"));
	MM::TRACE_RET();	
}
#===============================================================================
sub appendToFile { my ($self, $sFileFullName) = @_;
#===============================================================================
# file name can be given as a parameter or it can be given by "assignFile()" method
	if (defined $sFileFullName) {
		$self->{full_file_name} = $sFileFullName;
	} else {
		$sFileFullName = $self->{full_file_name};
	}
	MM::TRACE_SUB($self->{context});
	return (bufferToFile($sFileFullName,"APPEND"));
	MM::TRACE_RET();	
}
#===============================================================================
sub appendUniquesToFile { my ($self, $sFileFullName) = @_;
#===============================================================================
	# identical buffer lines are appended only once (eg. reduces cluttering in Graphviz diagrams)
	if (defined $sFileFullName) {
		$self->{full_file_name} = $sFileFullName;
	} else {
		$sFileFullName = $self->{full_file_name};
	}
	MM::TRACE_SUB($self->{context});
	return (bufferToFile($sFileFullName,"APPEND_LINES_ONCE"));
	MM::TRACE_RET();	
}
#===============================================================================
sub bufferToFile { my ($self, $sFileFullName, $sUpdateType) = @_;
#===============================================================================
	my $bStatus = 0;
	my $sUpdateSwitches;
	my $bAllowed = $self->{file_write_allowed};
	my $rasLines = $self->{rasLinesArrayByLatestState}; 
	my $sBufferState = $self->{buffer_state};
	MM::TRACE_SUB($self->{context});
	my $nBufferSize = @$rasLines;
	my @asAlreadyWrittenLines;
	my $bEachLineOnlyOnce = 0;  # initial quess
	if ($bAllowed == 0) {
		if ($sUpdateType eq "WRITE") {
			$sUpdateSwitches = ">";
		} elsif ($sUpdateType eq "APPEND"){
			$sUpdateSwitches = ">>";
		} elsif ($sUpdateType eq "WRITE_LINES_ONCE"){
			$sUpdateSwitches = ">";
			$bEachLineOnlyOnce = 1;
		} elsif ($sUpdateType eq "APPEND_LINES_ONCE"){
			$sUpdateSwitches = ">>";
			$bEachLineOnlyOnce = 1;
		} else {
			MM::TRACE("'$sFileFullName' unknown update type '$sUpdateType'");
			MM::TRACE_RET();
			return $bStatus;
		}
		if ($nBufferSize < $nVERY_SMALL_SIZE) {
			MM::TRACE("size is only '$nBufferSize' so it is NOT written to file '$sFileFullName'");
			MM::TRACE_RET();
			return $bStatus;
		}
		if (open (fhFILE, "$sUpdateSwitches$sFileFullName")) {  
			MM::TRACE("state '$sBufferState': '$sUpdateType' to file '$sFileFullName'");
			$self->{write_file_full_name} = $sFileFullName;
			$self->{bHasBeenWritten} = 1; 
			foreach my $sLine (@$rasLines) {
				# http://stackoverflow.com/questions/7898499/grep-to-find-item-in-perl-array
				if ($bEachLineOnlyOnce == 1) {
					my $sModLine = $sLine;
					$sModLine =~ s/\\\///g;  # TODO: solve this problem 160106
					print fhFILE "$sLine\n";
					# if (grep(/$sModLine/, @asAlreadyWrittenLines)) {
						# MM::TRACE("line '$sLine' is not written to file 'sFileFullName' because it is already done");
					# } else {
						# print fhFILE "$sLine\n";
						# push(@asAlreadyWrittenLines, $sLine);
					# }
				} else {
					print fhFILE "$sLine\n";
				}
				
			}
			close fhFILE;
		} else {
			MM::TRACE("FAILED to open file '$sFileFullName'");
		}
	}  else {
		MM::TRACE("'$sUpdateType' to file '$sFileFullName' is NOT allowed");
	}
	MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub hasBeenFilled { my ($self) = @_;   # for queries
#===============================================================================
	return $self->{bHasBeenFilled};
}
#===============================================================================
sub hasBeenWritten { my ($self) = @_; # for queries
#===============================================================================
	return $self->{bHasBeenWritten};
}
#===============================================================================
sub hasBeenEnlisted { my ($self) = @_; # for queries
#===============================================================================
	# checks if buffer contents has been succesfully extracted into an array of arrays (for two-level files)
	return $self->{bHasBeenEnlisted};
}
#==================================================================================
sub setType { my ($self, $sType) = @_;   # sets file type (by extension or by some text tag)
#==================================================================================
	MM::TRACE_SUB($self->{context});
	MM::TRACE("$sType");
	$self->{sBufferContentsType} = $sType;
	MM::TRACE_RET();
}
#==================================================================================
sub getType { my ($self) = @_;   # gives file type (by extension or by some text tag)
#==================================================================================
	return ($self->{sBufferContentsType});
}
#==================================================================================
sub bufferEnded { my ($self) = @_;
#==================================================================================
	return ($self->{bBufferEnded});
}
#==================================================================================
sub removeLinesBy{ my ($self, $sIgnoreRegex) = @_;
#==================================================================================
# Simpler version of 'pickAct()' -function
#	-	can be used e.g. to remove 'french lines' comments from JSON files
	my $rasTmp1 = \@{$self->{asRawLines}};
	my $rasTmp2 = \@{$self->{asActLines}};
	MM::TRACE_SUB($self->{context});
	foreach(@$rasTmp1) {
		my $sLine = $_;
		#MM::TRACE("line is '$sLine'");
		if ($sLine !~  /$sIgnoreRegex/g) {
			push (@$rasTmp2, $sLine);
			
		} else {
			MM::TRACE("line '$sLine' removed by match to regex '$sIgnoreRegex'");
		}
	}
	$self->{buffer_state} = "ST_ACT";
	$self->{rasLinesArrayByLatestState} = \@$rasTmp2;
	MM::TRACE_RET();
}

#==================================================================================
sub pickAct { my ($self) = @_;
#==================================================================================
	# TODO: add JSON string call parameter for an array of comments starts
	# removes commented contents
	my $rasTmp1 = \@{$self->{asRawLines}};
	my $rasTmp2 = \@{$self->{asActLines}};
	MM::TRACE_SUB($self->{context});
	my $sBufferType = $self->{sBufferContentsType};
	my $sFileName = $self->{filler_file_full_name};
	MM::TRACE("$sFileName");
	my $bSkipCommentedTopicLines = 0;

	foreach(@$rasTmp1) {
		my $sLine = $_;
		if ($sBufferType eq "OTL") {  # Notetab otl -specific filtering
			if ($sLine	=~ /$sNOTETAB_OTL_FILE_TOP_LINE_MATCH_regex/g) {next;}	# conversion configuration (otl) file badge
			if ($sLine =~ /$sNOTETAB_COMMENTED_OTL_TOPIC_HEADING_MATCH_regex/) {  # if topic heading is "commented", then whole topic contents is ignored
				MM::TRACE("start ignore section lines because section heading is '$sLine'");
				$bSkipCommentedTopicLines=1;
			} elsif ($sLine =~ /$sNOTETAB_ACTIVE_OTL_TOPIC_HEADING_CAPTURE_regex/) {
				$bSkipCommentedTopicLines=0;			
			}
			if ($bSkipCommentedTopicLines==1) {next;}
		}
		$sLine = MM::removePossibleComments($sLine); # passing reference to array
		push (@$rasTmp2, $sLine);
	}
	$self->{buffer_state} = "ST_ACT";
	$self->{rasLinesArrayByLatestState} = \@$rasTmp2;
	MM::TRACE_RET();
}
#==================================================================================
sub trimAct { my ($self) = @_;
#==================================================================================
	#PURPOSE: removes empty lines and multiple spaces
	my $rasTmp1 = \@{$self->{asActLines}};
	my $rasTmp2 = \@{$self->{asTrimLines}};
	MM::TRACE_SUB($self->{context});
	my $sBufferType = $self->{sBufferContentsType};
	my $sFileName = $self->{filler_file_full_name};
	MM::TRACE("$sFileName");
	foreach(@$rasTmp1) {
		my $sLine = $_;
		#print "$sLine\n";
		if (MM::checkIfIgnoreLine($sLine)) {next;}
		$sLine = MM::trimThrough($sLine);
		push (@$rasTmp2, $sLine)
	}
	#MM::TRACE("\@m_asTrimLines: ".Dumper(@m_asTrimLines));
	$self->{buffer_state} = "ST_TRIM";
	$self->{rasLinesArrayByLatestState} = \@$rasTmp2;
	MM::TRACE_RET();
}
#==================================================================================
sub buildTripod { my ($self,$sREGION_HEADING_CAPTURE_REGEXES_AS_json,       # eg. namespace names
							$sSECTION_HEADING_CAPTURE_REGEXES_AS_json,		# eg. class names
							$sGROUP_HEADING_CAPTURE_REGEXES_AS_json) = @_;	# eg. method names
#==================================================================================
	# for creating array of arrays of arrays of arrays from ANY kind of buffer (=file) contents
	#  -   _IDEA_: three levels could be a "standard"
	#		-	enough for most source code files parsing
	#		-	multiple levels are hard to remember in manually editable "outliners" (see Freeplane)
	#
	# _RESULT_: 
	#	first item of each array contains keyword, which describes the role of that array
	#	-	regions level:
	#		-	array, which contains arrays:
	#			-	_REGION_HEADING_:  
	#			-	_REGION_TEXT_: possible plain text lines  
	#			-	_SECTION_: 
	#	-	sections level:
	#		-	array which contains arrays:
	#			-	_SECTION_HEADING_:
	#			-	_SECTION_TEXT_: possible plain text lines
	#			-	_GROUP_:
	#	-	groups level:
	#		-	array which contains arrays:
	#			-	_GROUP_HEADING_:
	#			-	_GROUP_TEXT_: plain text lines 
	#
	#
	#----------------------------------------------------------------------------------------------

	my $bStatus = 0;
	my $sLine;
	my $sState;
	my $sMatchEvent;
	MM::TRACE_SUB($self->{context});
	my $rasInputLines = $self->{rasLinesArrayByLatestState};
	my $oStProc = new StateUtils("ST_INIT", "tripod building");
	my $oEvMatch = new EventUtils("EV_NONE", "tripod building");
	my $rhRegionHeadingCatchers 	= MM::fromJson($sREGION_HEADING_CAPTURE_REGEXES_AS_json, "region heading catchers");
	my $rhSectionHeadingCatchers 	= MM::fromJson($sSECTION_HEADING_CAPTURE_REGEXES_AS_json, "section heading catchers");
	my $rhGroupHeadingCatchers 		= MM::fromJson($sGROUP_HEADING_CAPTURE_REGEXES_AS_json, "group heading catchers");
	foreach $sLine (@$rasInputLines) {
		$oEvMatch->flushEvent();  # clears latest event
		if (! MM::matchFirstOf($sLine, $rhRegionHeadingCatchers)) {
			if (! MM::matchFirstOf($sLine, $rhSectionHeadingCatchers)) {
				if (! MM::matchFirstOf($sLine, $rhGroupHeadingCatchers)) {
				}  else {$oEvMatch->doEvent("EV_GROUP_HEADING_FOUND");}
			} else {$oEvMatch->doEvent("EV_SECTION_HEADING_FOUND");}
		} else {$oEvMatch->doEvent("EV_REGION_HEADING_FOUND");}

		$sMatchEvent = $oEvMatch->askEvent();
		my $sState = $oStProc->getState();
		
		if ($sState eq "ST_INIT") {
		} elsif ($sState) {
		
		} else {
			MM::TRACE("Error: invalid state '$sState'");
			last;
		}
	}
	MM::TRACE_RET();
	return $bStatus;
}
#==================================================================================
sub getTree { my ($self, $sSECTION_HEADING_CAPTURE_REGEXES_AS_json, 
				          $sSECTION_CONTENTS_CAPTURE_REGEXES_AS_json) = @_;
#==================================================================================
	# assumed file structure:
	# - text sections with headings at start of section
	# 	-	every heading consists of single line
	#		-	heading data is captured by a regex which is specific for each file type
	#	-	text section contents is captured by 1..N one line regexes  
	#		
	# eg. otl topic contents without topic heading
	# eg. perl subroutine contents without 'sub' heading line
	# ----------------------------------------------------------------------------
	# example: $sSectionParseRegexArrayAsJson = qq({"comparison":"\W*if(\W*.*)",
	#									"assignment":"(.*)=(.*)"});
	#-----------------------------------------------------------------------------
	
	MM::TRACE_SUB($self->{context});
	my $sBufferType = $self->{sBufferContentsType};
	my $sFileName = $self->{filler_file_full_name};
	my $rasLines = $self->{rasLinesArrayByLatestState};
	MM::TRACE("input file '$sFileName' type is '$sBufferType'");	
	my $sLine;
	my @aBufferContents;
	my @aSectionItems;						# single instance for each section
	my %hSectionContents;					# single instance for each section
	my %hHeadingKeywordValPair;				# single instance for each section
	my %hSectionContentsKeywordArrayPair;  	# single instance for each section
	my %hLineDataKeywordArrayPair;			# multiple instances for each section
	my @asLineFieldsArray;					# 0...N items
	my $sSectionHeadingRegex;
	my $bStatus; 
	my $rasLineCaptures;
	my $sHeadingName;
	my $bStatus;
	my $rasCaptures;
	my $raSectionHeadingCatchers;
	my $bSearchHeadings=0;
	
	my $oStStruct = new StateUtils("ST_INIT", "struct parsing from trimmed file");
	
	if ($sSECTION_HEADING_CAPTURE_REGEXES_AS_json eq "N/A") {
		MM::TRACE("heading regex is '$sSECTION_HEADING_CAPTURE_REGEXES_AS_json' so everything belongs to single, default section");
		MM::setToHash(\%hSectionContents, $sSECTION_HEADING_KEYWORD,  $sBufferType, "section heading to section contents hash");
		$oStStruct->setState("ST_COLLECTING_CONTENTS");
	} else {
		$raSectionHeadingCatchers = MM::fromJson($sSECTION_HEADING_CAPTURE_REGEXES_AS_json, "Section heading captures regex");  # reference to array
		$oStStruct->setState("ST_FIND_FIRST_HEADING");
		$bSearchHeadings = 1;
	}
	
	if (defined $sSECTION_CONTENTS_CAPTURE_REGEXES_AS_json) {
		#MM::TRACE("data item capture regex json is given as call parameter");
	} else {
		$sSECTION_CONTENTS_CAPTURE_REGEXES_AS_json = qw/[.*]/;
		MM::TRACE("data item capture regex json is NOT given as call parameter, so default is used");
	}
	
	MM::TRACE("section headings item capture regexes json = '$sSECTION_HEADING_CAPTURE_REGEXES_AS_json'");
	MM::TRACE("section contents line capture regexes json = '$sSECTION_CONTENTS_CAPTURE_REGEXES_AS_json'");
	
	my $rhSectionContentsCatchers = MM::fromJson($sSECTION_CONTENTS_CAPTURE_REGEXES_AS_json, "section contents catchers");   # reference to hash
	my %hSectionContentsCatchers = %$rhSectionContentsCatchers;
	

	foreach(@$rasLines) {
		$sLine = $_;
		
		#MM::TRACE("line='$sLine'");
		$bStatus=0; # initial quess
		if ($bSearchHeadings == 1) {
			($bStatus, $rasCaptures) = MM::getByFirstOfRegexes($sLine, $raSectionHeadingCatchers, "get heading");
		}
		if ($oStStruct->isState("ST_FIND_FIRST_HEADING")) {
			if ($bStatus==1) {
				$sHeadingName = $rasCaptures->[0];
				MM::TRACE("First section heading '$1' found, so start section contents collection");
				MM::setToHash(\%hSectionContents, $sSECTION_HEADING_KEYWORD,  $sHeadingName, "section");
				$oStStruct->setState("ST_COLLECTING_CONTENTS");
			}
		}	elsif ($oStStruct->isState("ST_COLLECTING_CONTENTS")) {
			if ($bStatus==1) {
				$sHeadingName = $rasCaptures->[0];
				MM::TRACE("next section heading '$1' found, so save section contents collection");
				MM::pushToArray(\@aBufferContents, {%hSectionContents},"section contents hash to file contents array"); 
				MM::TRACE("start initializations before new section storages");
				MM::clearHash(\%hSectionContents,"section contents");
				MM::clearArray(\@aSectionItems,"section items");
				MM::clearArray(\@asLineFieldsArray,"line fields array");
				MM::clearHash(\%hLineDataKeywordArrayPair, "line data keyword array pair");
				MM::TRACE("starts new section storage");
				MM::setToHash(\%hSectionContents, $sSECTION_HEADING_KEYWORD,  $sHeadingName, "new section started");
			} else {
				# loops matching data item regex to focus line
				foreach my $sRole (keys %hSectionContentsCatchers) {
					my $sLineCaptureRegex = $hSectionContentsCatchers{$sRole};
					($bStatus, $rasLineCaptures) = MM::tryRegexCaptureMatch($sLine, $sLineCaptureRegex, $sRole);
					if ($bStatus == 1) {
						@asLineFieldsArray = @$rasLineCaptures;
						foreach my $sSingleCapture (@asLineFieldsArray) {
							MM::TRACE("single captured field '$sSingleCapture' at line '$sLine'");
							# TODO: add push to hash/array
						}
						#TODO: add key text insertion ahead of each item
						MM::setToHash(\%hLineDataKeywordArrayPair, $sRole ,  [@asLineFieldsArray], "line fields array to line data keyword array pair hash");
						MM::pushToArray(\@aSectionItems, {%hLineDataKeywordArrayPair},"line data keyword array pair hash to section array");	
						MM::clearHash(\%hLineDataKeywordArrayPair, "line data keyword array pair");
						MM::setToHash(\%hSectionContents, $sSECTION_CONTENTS_KEYWORD,  [@aSectionItems], "section items array to section contents hash");
						last;
					}
				} 	
			}	
		}  
	}
	if ($oStStruct->isState("ST_COLLECTING_CONTENTS")) {
		MM::TRACE("file ended, so save pending collections");
		MM::pushToArray(\@aBufferContents, {%hSectionContents},"section contents hash to file contents array"); 
		# where is pushToArray() ????????????? 151218
	}
	my $sBufferStructAsJson = MM::toJson(\@aBufferContents, "extracted from whole file");
	MM::fromJson($sBufferStructAsJson,"extracted from whole file");
	#MM::TRACE("\$sFileStructAsJson = $sFileStructAsJson");
	MM::TRACE_RET();
	# TODO: ad return value which indicates the "deepness" and "form" of the tree-alike structure
	return \@aBufferContents;
}
#===============================================================================
sub getNextChar{ my ($self) = @_; 
#===============================================================================
	my $char;
	my $nLinePos = $self->{nLinePos};
    my $nCharPosAtLine = $self->{nCharPosAtLine};
	my $ras = $self->{rasLinesArrayByLatestState};

    $nCharPosAtLine = $nCharPosAtLine + 1;
	if ($nCharPosAtLine > $self->{nLineLastCharPos}) {
		if ("EOF" ne getNextLine()) {
			
		} else {
			$nCharPosAtLine=0;
		}
	}
	$self->{nCharPosAtLine} = $nCharPosAtLine;
	$char = $$ras[$nLinePos][$nCharPosAtLine];
	return $char;
}
#===============================================================================
sub resetPos { my ($self) = @_; 
#===============================================================================
#  resets file position counters to wait for eg. 'get next' method calls
	MM::TRACE_SUB($self->{context});
	$self->{nLinePos} = -1;
	$self->{nCharPosAtLine} = -1;
	MM::TRACE_RET();
}
#===============================================================================
sub getAllLines { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	# TODO: 151223
	my $ras = $self->{rasLinesArrayByLatestState};
	MM::TRACE_RET();
	
	return $ras;

}
#===============================================================================
sub contentsTraceBag { my ($self, $sComment) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	
	my $ras = $self->{rasLinesArrayByLatestState};
	MM::TRACE_BAG($ras, $sComment);
	MM::TRACE_RET();
	
	return $ras;

}

#===============================================================================
sub getFirstLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	$self->{nLinePos} = 0;
	$self->{nCharPosAtLine} = -1;
	my $ras = $self->{rasLinesArrayByLatestState};
	my $sLine = $$ras[0];
	chomp ($sLine);
	$self->{nLineLastCharPos} = length $sLine - 1;
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub getNextLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $sLine;
	$self->{nCharPosAtLine} = -1;
	my $nLinePos = $self->{nLinePos};
	my $ras = $self->{rasLinesArrayByLatestState};
	#MM::TRACE_BAG($ras,"buffer contents");
	my $nBufferLastPos = @$ras - 1;
	#MM::TRACE("buffer last pos = '$nBufferLastPos'");
	$nLinePos = $nLinePos+1;
	if ($nLinePos > $nBufferLastPos) {
		
		$sLine = "EOF";   # "EOF" is an explicit indication, NOT a string in array end
		$self->{bBufferEnded} = 1;
	} else {
		
		$sLine = $$ras[$nLinePos];
		chomp ($sLine);
		MM::TRACE("line '$sLine' from pos [$nLinePos]");
		$self->{nLinePos} = $nLinePos;
		$self->{nLineLastCharPos} = length $sLine - 1;  # for char position within line
	}
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub peekNextLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $ras = $self->{rasLinesArrayByLatestState};
	my $nLinePos = $self->{nLinePos};
	my $nNextLinePos=$nLinePos+1;
	my $sLine = $$ras[$nNextLinePos];	
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub peekPrevLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $ras = $self->{rasLinesArrayByLatestState};
	my $nLinePos = $self->{nLinePos};
	my $nPrevLinePos=$nLinePos-1;
	my $sLine = $$ras[$nPrevLinePos];	
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub bookmarkFocusLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $ras = $self->{rasLinesArrayByLatestState};
	my $nLinePos = $self->{nLinePos};
	$self->{nBookmarkLinePos}=$nLinePos;
	my $sLine = $$ras[$nLinePos];
	MM::TRACE("line pos '$nLinePos'");
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub goToBookmarkLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $ras = $self->{rasLinesArrayByLatestState};
	$self->{nCharPosAtLine} = -1;
	my $nLinePos=$self->{nBookmarkLinePos};
	my $sLine = $$ras[$nLinePos];
	$self->{nLineLastCharPos} = length $sLine - 1;
	MM::TRACE("line pos '$nLinePos'");
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub goPrevLine { my ($self) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $ras = $self->{rasLinesArrayByLatestState};
	$self->{nCharPosAtLine} = -1;
	my $nLinePos = $self->{nLinePos};
	$nLinePos=$nLinePos-1;
	my $sLine = $$ras[$nLinePos];
	$self->{nLineLastCharPos} = length $sLine - 1;
	$self->{nLinePos} = $nLinePos;
	MM::TRACE("line pos '$nLinePos'");
	MM::TRACE_RET();
	return $sLine;
}
#===============================================================================
sub findAllOf { my ($self, $sRegexListAsJson) = @_; 
#===============================================================================
# searches multiple strings  
# can be used for a sophisticated way to define file type/subtype by file contents
# TODO: replace this method with incremental search
#-------------------------------------------------------------------------------
	MM::TRACE_SUB($self->{context});
	my $sFileName = $self->{filler_file_full_name};
	my $sLine;
	my $nLastPos;
	my $bStatus=0; # initial quess
	my $raMatchers = MM::fromJson($sRegexListAsJson);
	resetPos();
	while (1) {
		$sLine = getNextLine();
		$nLastPos = length @$raMatchers - 1;
		for (my $i=0; $i<=$nLastPos; $i++) {
			my $sMatcher = @$raMatchers[$i];
			if ($sLine =~ /$sMatcher/g) {
				splice @$raMatchers, $i, 1; #removes element from array
				# http://perlmaven.com/splice-to-slice-and-dice-arrays-in-perl
				$nLastPos = length @$raMatchers - 1;
			}
		}
		if ($nLastPos == -1) {
			$bStatus=1;
			
			last;
		}
	}
	if ($bStatus == 1) {
		MM::TRACE("all strings '$sRegexListAsJson' found in file '$sFileName'");
	} else {
	}
	resetPos();
	MM::TRACE_RET();
	return $bStatus;
}

#===============================================================================
sub findNextOf { my ($self, $sRegex) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my @asCaptures=();
	while (1) { 
		my $sLine = getNextLine();
		if ($sLine eq "EOF") {
			last;
		}
		if (@asCaptures = ($sLine =~ /$sRegex/)){
			last;
		}
	}
	MM::TRACE_RET();
	return \@asCaptures;
}
#===============================================================================
sub findNextBySeq { my ($self, $s) = @_;
#===============================================================================
	#  	searches (and possibly captures) using last regex of given JSON array of arrays
	#   each subarray:
	#   	pos 0 contains navigation keyword (relative to previous match)
	#		pos 1 contains numeric value for navigation amount (relative to previous match)
	#		pos 2 contains operator regex
	# 	TODO: accomplish this 151029
	MM::TRACE_SUB($self->{context});

	MM::TRACE_RET();

}
#===============================================================================
sub findNextAnyOf { my ($self, $sRegexHashAsJson) = @_;
#===============================================================================
#  finds next line which matches any of regexes in given hash
#  the "key" part of the hash is actually a document (=role) for corresponding "val" part
	MM::TRACE_SUB($self->{context});
	my $rhCatchers = MM::fromJson($sRegexHashAsJson);
	my %hCatchers = %$rhCatchers;
	my @PossibleCaptures=();
	my $sMatchRole="NONE";
	my $sMatchRegex;
	my $sMatchLine;
	while (1) { 
		my $sLine = getNextLine();
		if ($sLine eq "EOF") {
			last;
		}
		foreach my $sRole (keys  %hCatchers) {
			my $sRegex = $hCatchers{$sRole};
			if (@PossibleCaptures = ($sLine =~ /$sRegex/)) {   # match can occurr without any captures
				$sMatchRole	= $sRole;
				$sMatchRegex = $sRegex;
				$sMatchLine = $sLine;
				last;
			}
		}
	}
	if ($sMatchRole eq "NONE") {
		MM::TRACE("nothing found by '$sRegexHashAsJson'");
	} else {
		my $nLinePos = $self->{nLinePos};
		MM::TRACE("match by role '$sMatchRole' regex '$sMatchRegex' from line '$sMatchLine' at pos [$nLinePos]");
	}
	return ($sMatchRole, \@PossibleCaptures);
	MM::TRACE_RET();
}
#==================================================================================
sub collectUpToStr { my ($self, $str, $rasText) = shift;
#==================================================================================



}
#==================================================================================
sub collectUpToMatchingPair{ my ($self, $cLeft) = shift;
#==================================================================================
# eg. between '{...}'
	MM::TRACE_SUB($self->{context});
	my $char;
	my $nPairCnt=0;
	my $sCollection="";
	my $cRight="";
	my $bRightSearchActive=0;
	if ($cLeft eq '(') { 
		$cRight = ')';
	} elsif ($cLeft eq '{') {
		$cRight = '}';
	} elsif ($cLeft eq '[') {
		$cRight = ']';
	} elsif ($cLeft eq '<') {
		$cRight = '>';
	} else {
		MM::TRACE("there is no pair for char '$cLeft'");
		return "";
		MM::TRACE_RET();
	}
	while (1) {
		$char = getNextChar();
		if (fileEnded()) {
			$sCollection="";
			last;
		}
		if ($char eq $cRight) {
			$nPairCnt = $nPairCnt - 1;
		} elsif ($char eq $cLeft) {
			$bRightSearchActive = 1;   # first left must encountered first 
			$nPairCnt = $nPairCnt + 1;
		} else {
		}
		
		$sCollection = $sCollection.$char;    # !!: concatenation of single character to end of array
		
		if ($bRightSearchActive == 1) {
			if ($nPairCnt == 0) {
				last;
			}
		}
	}
	MM::TRACE_RET();
	return $sCollection;
}
#===============================================================================
sub insertLineToPos{ my ($self, $nPos, $sLine) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $nOVER_WRITE_LEN = 0;
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	
	splice @$rasTmp, $nPos, $nOVER_WRITE_LEN, $sLine;

	MM::TRACE_RET();
}
#===============================================================================
sub insertLinesToPos{ my ($self, $nPos, $rasLines) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my @asLines = @$rasLines;
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	my $nOVER_WRITE_LEN = 0;
	splice @$rasTmp, $nPos, $nOVER_WRITE_LEN, @asLines;
	MM::TRACE_RET();
}
#===============================================================================
sub addLinesToEnd{ my ($self, $rasAddText) = @_;
#===============================================================================
#  	adds given array to buffer end
	MM::TRACE_SUB($self->{context});
	my @asAddText = @$rasAddText;
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	MM::TRACE_BAG(\@asAddText, "lines created");
	push (@$rasTmp,@asAddText);
	MM::TRACE_RET();
}
#===============================================================================
sub addLineToEnd{ my ($self, $sLine) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	push (@$rasTmp, $sLine);
	MM::TRACE_RET();
}
#===============================================================================
sub addLineIfNotYet{ my ($self, $sLine) = @_;   # only once 
#===============================================================================
	# for avoiding eg. arrows jungle in Graphviz file
	MM::TRACE_SUB($self->{context});
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	my @matches = grep { /$sLine/ } @$rasTmp;
	if (@matches == 0) {
		push (@$rasTmp, $sLine);
	}
	MM::TRACE_RET();
}
#===============================================================================
sub insertLineToStart { my ($self, $sLine) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $nPos=0;
	insertLineToPos($self, $nPos, $sLine);
	MM::TRACE_RET();
}
#===============================================================================
sub insertLinesToStart { my ($self, $rasLines) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $nPos=0;
	insertLinesToPos($self, $nPos, $rasLines);
	MM::TRACE_RET();
}
#===============================================================================
sub insertLinesBeforeLine { my ($self, $sRegexHashAsJson, $rasAddText) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $nOffsetPos = 0;
	insertLinesRelativeToLineByRegex($sRegexHashAsJson, $rasAddText, $nOffsetPos);
	MM::TRACE_RET();
}
#===============================================================================
sub insertLinesAfterLine { my ($self, $sRegexHashAsJson, $rasAddText) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $nOffsetPos = 1;
	insertLinesRelativeToLineByRegex($sRegexHashAsJson, $rasAddText, $nOffsetPos);
	MM::TRACE_RET();
}
#===============================================================================
sub findNextAnyOf{ my ($self, $sRegexHashAsJson) = @_;
#===============================================================================
#  finds next line which matches any of regexes in given hash
#  the "key" part of the hash is actually a document (=role) for corresponding "val" part
#  TODO: add identical method also to In File -module 
	MM::TRACE_SUB($self->{context});
	my $rhCatchers = MM::fromJson($sRegexHashAsJson,"ADD COMMENT");
	my %hCatchers = %$rhCatchers;
	my @PossibleCaptures=();
	my $sMatchRole="NONE";
	my $sMatchRegex;
	my $sMatchLine;
	while (1) { 
		my $sLine = getNextLine();
		if ($sLine eq "EOF") {
			last;
		}
		foreach my $sRole (keys  %hCatchers) {
			my $sRegex = $hCatchers{$sRole};
			if (@PossibleCaptures = ($sLine =~ /$sRegex/)) {   # match can occurr without any captures
				$sMatchRole	= $sRole;
				$sMatchRegex = $sRegex;
				$sMatchLine = $sLine;
				last;
			}
		}
	}
	if ($sMatchRole eq "NONE") {
		MM::TRACE("nothing found by '$sRegexHashAsJson'");
	} else {
		my $nLinePos = $self->{asBufferLines};
		MM::TRACE("match by role '$sMatchRole' regex '$sMatchRegex' from line '$sMatchLine' at pos [$nLinePos]");
	}
	return ($sMatchRole, \@PossibleCaptures);
	MM::TRACE_RET();
}
#===============================================================================
sub insertLinesRelativeToLineByRegex { my ($self, $sRegexHashAsJson, $rasAddText, $nOffsetPos) = @_;
#===============================================================================
# inserts array of lines to given relative position to first line
# which matches any of the regexes of given hash
	MM::TRACE_SUB($self->{context});
	my $nOVER_WRITE_LEN = 0;
	my $rasTmp = \@{$self->{rasLinesArrayByLatestState}};
	my $nLinePos = $self->{nLinePos};
	my @asAddText = @$rasAddText;
	my ($sRole, $raPossibleCaptures) =	findNextAnyOf($sRegexHashAsJson);
	if ($sRole ne "NONE") {
		splice @$rasTmp, $nLinePos + $nOffsetPos, $nOVER_WRITE_LEN, @asAddText;
	}
	MM::TRACE_RET();
}
#===============================================================================
sub sortLexLines { my ($self,  $nSortOrder, $sSortSubstrCaptureRegex) = @_;
#===============================================================================
	# for single-level files
	my @asTagged;
	my @asSorted;
	my $sTagCore;
	my $sTagFrame;
	my $sTaggedLine;
	my $sEMPTY_STR="";
	MM::TRACE_SUB($self->{context});
	$self->resetPos();
	if (! defined $sSortSubstrCaptureRegex) {
		$sSortSubstrCaptureRegex = $sMATCH_ANYTHING_regex;
	}
	while (1) { 
		my $sLine = $self->getNextLine();
		if ($sLine eq "EOF") {
			last;
		}
		($sTagCore) = ( $sLine =~ /$sSortSubstrCaptureRegex/g);
		$sTagFrame = "STAG".$sTagCore."ETAG";  # note: IDEA: keywords for run-time tagging  
		$sTaggedLine = 	$sTagFrame.$sLine;	
		push(@asTagged, $sTaggedLine);
	}
	if (defined $nSortOrder) {
		@asSorted = sort {$b cmp $a} @asTagged;  # !!: perl: lexical sort in descending order
	} else {
		@asSorted = sort {$a cmp $b} @asTagged;  # !!: perl: lexical sort in ascending order
		# = default, if 'sort order' -parameter is not given at all
	} 
	s/^STAG.*ETAG/$sEMPTY_STR/ for @asSorted;    # !!: Perl one-liner for array-wide sunstitution
	$self->fillFrom(\@asSorted);  # replaces current 'asRaw_lines' with an array contents
	MM::TRACE_RET();
}
#===============================================================================
sub enlistSections { my ($self, $sSECTION_HEADING_CAPTURE_REGEXES_AS_json) = @_;  # !!: english: 'enlist' = "to make a list"
#===============================================================================
	# collects section lines to array of arrays.	
	# pos 0 contains section heading , pos 1...N contain section lines
	# for two-level hierarchy files, which contain single line headings
	# TODO: make function to handle multi-level hierarchies	(apply JSON)
	my @aasTopLines;   # possible lines above first section heading (not included in sorting)
	my @asSection;
	my @aasSections;   # !!: perl: multi-dimensional array is defined similarly as single-dimensional array !!!
	my $raasSections;
	my $rasLineCaptures;
	my $bHeadingMatch;
	my $sState;
	my $raasEnlistedLists = \@{$self->{aasEnlistedLists}};
	MM::TRACE_SUB($self->{context});
	
	my $raSectionHeadingCatchers = MM::fromJson($sSECTION_HEADING_CAPTURE_REGEXES_AS_json,"ADD COMMENT");
	my $oSt = new StateUtils("ST_FIND_FIRST_HEADING", "sections to lists");
	while (1) { 
		my $sLine = $self->getNextLine();
		$sState = $oSt->getState();
		if ($sLine eq "EOF") {
			last;
		}
		($bHeadingMatch, $rasLineCaptures) = MM::getByFirstOfRegexes($sLine, $raSectionHeadingCatchers, "get heading");
		if ($sState eq "ST_FIND_FIRST_HEADING") {
			if ($bHeadingMatch==1) {
				@asSection = ($sLine); # first elemen of new array
				$oSt->setState("ST_FIND_OTHER_HEADINGS");
			} else {
				MM::pushToArray(@aasTopLines, [$m_sSECTIONS_PRE_LINE_IND, $sLine]); 
			}
		} elsif ($sState eq "ST_FIND_OTHER_HEADINGS") {
			if ($bHeadingMatch==1) {
				push(@$raasEnlistedLists, \@asSection); # !!: perl: array to array requires _reference_ usage
				@asSection = ($sLine); # first element of new array
			} else {
				MM::pushToArray(@asSection, $sLine); 
			}
		} else {
			MM::TRACE("invalid state '$sState'");
			last;
		}
	}
	if ($sState eq "ST_FIND_OTHER_HEADINGS") {
		push(@$raasEnlistedLists, \@asSection); # !!: perl: pushing array to array requires _reference_ usage
		MM::TRACE("enlisting succeeded");
		$self->{bHasBeenEnlisted} = 1;
	} else {
		MM::TRACE("no sections found");
	}
	MM::TRACE_RET();
}
#===============================================================================
sub fillFromEnlisted { my ($self) = @_;         # _fillFrom..._  means, that buffer raw lines are written from somewhere 
#===============================================================================
	# "flattens" array of arrays to _this_ buffer raw lines array 
	my $bStatus = 0;
	my $raasEnlistedLists = \@{$self->{aasEnlistedLists}};
	my $rasRawLines = \@{$self->{asRawLines}};
	@$rasRawLines=();	# _perl_: drain
	MM::TRACE_SUB($self->{context});
	if ($self->hasBeenEnlisted()) {
		foreach my $rasList (@$raasEnlistedLists) {
			foreach my $sLine (@$rasList) {
				push (@$rasRawLines, $sLine);
			}
		}
		$self->{bHasBeenFilled} = 1;
		$self->resetPos();
	}  else {
		MM::TRACE("buffer was NOT enlisted, so no filling was done");
		$bStatus = 0;
	}
	MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub sortLexEnlisted { my ($self, $nSorterPos, $sSortOrder) = @_;
#===============================================================================
	# sorts sections according to lexical order of section heading contents
	# for two-level hierarchy files, which contain single line headings
	# TODO: change all hierarchy handlings from two to three levels (=enough for most programming language source files) _151118_
	# _IDEA_: comment keywords, date stamps, etc. are '_FRAMED_' by underscores
	# http://perlmaven.com/splice-to-slice-and-dice-arrays-in-perl  _perl_: ultimate array handling 
	my @aasPreSectionLinesList;
	my @aasSortedListedList;
	my $sLine;
	my $rasRemovedList;
	MM::TRACE_SUB($self->{context});
	# my $raasEnlistedLists = \@{$self->{aasEnlistedLists}};
	# $self->enlistSections($sSectionHeadingRegex);
	# foreach my $rasList (@$raasEnlistedLists) {
		# if ($$rasList[0] eq $m_sSECTIONS_PRE_LINE_IND) {
			# $rasRemovedList = splice (@$raasEnlistedLists,0,1);
			# push(@aasPreSectionLinesList, $rasRemovedList);
		# } else {
			# last;
		# }
	# }
	# if ($self->hasBeenEnlisted()) {
		# if (defined $nSortOrder) { # descent order
			# @sorted_by_last = sort { $b->[$nSorterPos] cmp $a->[$nSorterPos] } @$raasEnlistedLists;
		# } else {	# ascent order
			# @sorted_by_last = sort { $a->[$nSorterPos] cmp $b->[$nSorterPos] } @$raasEnlistedLists;
		# }
		
		# splice @$raasEnlistedLists, 0, 0, @$rasRemovedList;  # pre-sections list back into sorted list of lists start
		
	# }  else {
		# MM::TRACE("buffer has NOT been enlisted, so sorting is not done");
	# }
	MM::TRACE_RET();
}
1;

