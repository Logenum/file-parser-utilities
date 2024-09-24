package PERL_SCRIPTS;

use Data::Dumper;
use JSON;

use FileHandle;


# this file is copied from backups because contains functions "collect.*Contents()"  (150204)
# note: caller files shall contain lines: "package PERL_SCRIPTS;" and "use LOCUTILS;"
 
################################################################################
my $TRACE_LOG;  # file handle
my $sTRACE_FILE_NAME;
my @aCommentTexts;
my @aFILE_HANDLES=();
#my $FILE_HANDLE;
my $DELIM_STR = '%';

my $DUMMY_VAL = 0;

my $sDEFAULT_RESULT_FILE_NAME = "RESULT\\RESULT.txt";

my $sREGEX_CFG_EXTRACT_FILE_NAME = "RESULT\\RegexCfgExtractResults.aut";   # see: "aut" means "automatically created"
my $sTEMPLATE_CFG_EXTRACT_FILE_NAME = "RESULT\\TemplateCfgExtractResults.aut";
###my $sJSON_FILE_NAME = "RESULT\\TemplateCfgExtractResults.aut";


@aHardFileRoleTags =  (	"< WELL_FILES_FILE",   				# if missing, then 'WELL_FILE' must exist
						"< WELL_FILE",		   				# if missing, then 'WELL_FILES_FILE' must exist
						"< CAPTURE_BY_REGEX_CFG_FILE", 		# if missing, then fails.   
						"< REPORT_BY_CAPTURE_CFG_FILE", 	# if missing, then skipped.  (for possible conversion of captured strings to final visible output strings) 
						"< HEADER_FILE", 					# if missing, then skipped
						"< INCLUDE_FILE",					# if missing, then skipped
						"> RESULT_FILE", 					# if missing, then default file is used
						"< FOOTER_FILE");					# if missing, then skipped

#=================================================================
sub openAllRoleFilesByCfgFile { my ($sCfgFileName) = @_;
#================================================================
	my $sLine;
	my %hConfFileItems;
	#my $sFileRoleTAG, 
	my $sConfFileName;
    my @aFILE_HANDLES;  # each item will have handle or zero

	my $bGoodbye = 0;
	my $bSucceeded=0;
	my $nHandlePos = 0;
	
	unless (open (CFG_FILE, "<$sCfgFileName") ) {
		 TRACE("input config file '$sCfgFileName' open FAILED"); 
	} else {
		TRACE("input config file '$sCfgFileName' open SUCCEEDED"); 
	}
	
	@asConfFileLines = <CFG_FILE>;
	foreach $sConfLine (@asConfFileLines) {
		# creates hash table
		my ($sFileRoleTAG, $sConfFileName) = ($sConfLine =~ /^\s*(\w+)\s*\=\s*(\S+)\s*/g);
		$hConfFileItems{$sFileRoleTAG} = $sConfFileName;
		#TRACE("$sFileRoleTAG => $sFileName");
	}
	
	#-----------------------------------------------------
	foreach my $sHardRawTag (@aHardFileRoleTags) {
		#TRACE("tag item: '$sHardRawTag'");
		my ($sHardOpenType, $sHardFileRole) = ($sHardRawTag =~ /\s*(\S*)\s*(\w+)/g);
		$bSucceeded=0;
		foreach my $sConfFileRole (keys %hConfFileItems) {
			if ($sHardFileRole eq $sConfFileRole) {
				$sConfFileName = $hConfFileItems{$sConfFileRole};
				if (open ($aFILE_HANDLES[$nHandlePos], $sHardOpenType.$sConfFileName) ) { # perl: file handles array for return
					TRACE("role '$sHardFileRole' file '$sConfFileName' open by '$sHardOpenType' SUCCEEDED");  
					$sConfFileName = "";
					$bSucceeded = 1;
				} 
			}
		}
		if ($bSucceeded == 0) {
			if ($sHardFileRole eq 'RESULT_FILE')  {  # missing in configuration file
				if (open ($aFILE_HANDLES[$nHandlePos], $sHardOpenType.$sDEFAULT_RESULT_FILE_NAME) ) { # 
					TRACE("role '$sHardFileRole' default file '$sDEFAULT_RESULT_FILE_NAME' open by '$sHardOpenType' SUCCEEDED");  
					$sConfFileName = "";
					$bSucceeded = 1;
				}  else {
					$aFILE_HANDLES[$nHandlePos] = $DUMMY_VAL;
					TRACE("role '$sHardFileRole' default file '$sDEFAULT_RESULT_FILE_NAME' open by '$sHardOpenType' FAILED"); 
				}
			}  else {
				$aFILE_HANDLES[$nHandlePos] = $DUMMY_VAL; 
				TRACE("role '$sHardFileRole' file '$sConfFileName' open by '$sHardOpenType' FAILED"); 
				$sConfFileName = "";
				$bGoodbye = 1;
			}
		}
		$nHandlePos++;
	}
	
	#if ($bGoodbye == 1) {
	#	TRACE_END("terminates due to missing files");
	#	die;
	#}
	return (@aFILE_HANDLES);	# caller must access these in same order as in roles array
}
#================================================================
sub closeAllRoleFiles { my @FILES = @_;
#================================================================
	foreach my $FILE (@FILES) {	
		if ($FILE) {
			TRACE("close file '$FILE'");
			close ($FILE);
		}
	}
}
#================================================================
sub getWellFileMode { my ($WELL_FILE, $WELL_FILES_FILE) = @_;
#================================================================
	my $sWellMode = ""; # initial quess: will fail
	if ($WELL_FILES_FILE != 0) {
		$sWellMode = "multifile";
	} else {
		if ($WELL_FILE != 0) {
			$sWellMode = "singlefile";
		}
	}
	TRACE("well mode is '$sWellMode' because WELL_FILE='$WELL_FILE' and  WELL_FILES_FILE='$WELL_FILES_FILE'");
	return $sWellMode;
}
#==================================================================================
sub checkIfLastWellFile{ my ($hndWellWilesFile) = shift;
#==================================================================================
	my $bIfIsLastWellFile = 0;   # initial quess
	my $sWellFileName=<$hndWellWilesFile>;
	if ($sWellFileName eq "") {
		TRACE("no more well files");
		$bIfIsLastWellFile = 1;
	}
	
	if (open ($sWellFileName, "<$sWellFileName")) {   # opens well file in well files file
		TRACE("well file '$sWellFileName' open FAILED");
		$bIfIsLastWellFile = 1;
	} else {
		TRACE("well file '$sWellFileName' open SUCCEEDED");
	}
	return ($bIfIsLastWellFile, $hndWellFile);
}
#================================================================
sub checkIfExit { my ($sCriterion, $nLineNbr) = @_;
#================================================================
if (($sCriterion eq "") or ($sCriterion eq '0') or ($sCriterion eq 'invalid')){
	TRACE_END("end due to criterion '$sCriterion'  (L:$nLineNbr)");
	die;
	}
}
#==========================================
sub tryInsertFile { my ($hndSource, $hndTarget, $sComment) = @_;
#------------------------------------------
	if ($hndSource) {   
		while (<$hndSource>) {
			print $hndTarget $_;
		}
		TRACE("$sComment file inserted");
	} else {
		TRACE("$sComment file not inserted");
	}
}		

#===============================================================================
sub collectRegexCaptureCfgFileContents { my ($hndRegexFile) = @_;
#===============================================================================
	#----------------------
	# file sample
	#----------------------
	# [\s(\w+)\W+(\d+).*.......]           // bracketed
	# $sfirstWord $nsecondNumber.......    // dollarized variable names
	#----------------------------------------------------------------
	TRACE ("-------------- start collect analysis regex config file data to structures --------------------");

	my $sFocusSectionName;
	my $sPossibleRegexBar;
	my @aSingleRegexKeys=();
	my $bSectionCollectionIsActive=0;
	my @aa_FocusSectionRegexBarsWithKeys =();
	my @aaa_AllSectionsRegexBarsWithKeys =();
	my @a_SingleRegexBarWithKeys=(); 
	
	my $ra_SingleRegexBarWithKeys = \@a_SingleRegexBarWithKeys;
	my $raa_FocusSectionRegexBarsWithKeys = \@aa_FocusSectionRegexBarsWithKeys;
	my $raaa_AllSectionsRegexBarsWithKeys = \@aaa_AllSectionsRegexBarsWithKeys;
	
	my $nLineNbr=0;
	my $nArrayIndex;
	my $sWorkLogText = "";
	
	while (<$hndRegexFile>) {
		chomp $_;
		my $sLine = $_;
		if ($sLine  =~ /^\s*#.*/) {  # skips commented lines
			next;
		}
		$nLineNbr++;
		if ($sLine =~ /\S+/) {
			TRACE ("line[$nLineNbr] = '$sLine'");
		}
		#===================================================================
		if  ($sLine  =~ /.*Outline.*MultiLine.*/g) {
		#-------------------------------------------------------------------
			TRACE ("Outline file indication: '$sLine' ");
		#===================================================================
		} elsif ( $sLine =~ /$H\=\"(.*)\"/) {  # Notetab topic heading start
		#-------------------------------------------------------------------
			my $sPrevSectionName = $sFocusSectionName;
			$sFocusSectionName = $1;
			if ($bSectionCollectionIsActive==1) { # previous section regexes collected, so add collection to file-wide save
				push(@aaa_AllSectionsRegexBarsWithKeys, [@aa_FocusSectionRegexBarsWithKeys]);
			#	TRACE_DUMP("section name changed to '$sFocusSectionName'", __LINE__,$raa_FocusSectionRegexBarsWithKeys);
				# - copies pending topic-wide array to file-wide array
				@aa_FocusSectionRegexBarsWithKeys=();
				# - resets topic-wide array
				# - initialize topic wide array with topic name
				$bSectionCollectionIsActive=0;
			}
			push(@aa_FocusSectionRegexBarsWithKeys, $sFocusSectionName);
		#=======================================================================
		} elsif (($sPossibleRegexBar) = ($sLine  =~ /.*\[(.*)$/g)) { # assumed regex line (starts with bracket for blue color in Notetab)
		#-----------------------------------------------------------------------
			$bSectionCollectionIsActive=1;
			push(@a_SingleRegexBarWithKeys, $sPossibleRegexBar);  # first item in array
		#========================================================================
		} elsif ((@aSingleRegexKeys) = ($sLine =~ /\W*(\w+)\W*/g)) {   # sequence of keys
		#------------------------------------------------------------------------
			foreach my $key (@aSingleRegexKeys) {
				push( @a_SingleRegexBarWithKeys , $key);					
			}
			push(@aa_FocusSectionRegexBarsWithKeys,  [@a_SingleRegexBarWithKeys]);	# see: brackets cause array copying (so the original array can be re-used)
			@a_SingleRegexBarWithKeys=();
				
		#========================================================================
		} else { 
		#------------------------------------------------------------------------
			# some ignored line 
		}
	} # ... for each regex key file line

	if ($bSectionCollectionIsActive==1) {   # last topic in Notetab file
		push(@aaa_AllSectionsRegexBarsWithKeys, [@aa_FocusSectionRegexBarsWithKeys]);
	#	TRACE_DUMP("no more section names'", __LINE__,$raa_FocusSectionRegexBarsWithKeys);
	} 
#	TRACE_DUMP("savings status of whole regex file", __LINE__, [@aaa_AllSectionsRegexBarsWithKeys]);  # requires bracket parentheses to output full stuff
	TRACE ("-------------- end collect analysis regex config file data to structures --------------------");
	
	createWriteExternalFile($sREGEX_CFG_EXTRACT_FILE_NAME, to_json($raaa_AllSectionsRegexBarsWithKeys),"Perl sstructure to file as JSON ");
	

	##TRACE_DUMP("PERL as JSON: ", __LINE__, $retJson);	
	
	return ($sREGEX_CFG_EXTRACT_FILE_NAME);
}

#===============================================================================
sub collectReportTemplateCgfFileContents { my ($hndTemplateFile) = @_;
#===============================================================================
	# reads through given file and saves data
	#--------------------------------------
	# file sample:
	#-------------------------
	# h="diibadaaba 1"
	# [ heading $nSecondNumber 
	# [ $sFirstWord -> $nSecondNumber  // This is just a comment
	#
	# h="diibadaaba 2"
	#
	TRACE ("-------------- start collect report template config file data to structures --------------------"); 

	my $sFocusSectionName;
	my $sPossibleTemplateBar;
	my $bSectionCollectionIsActive=0;
	 
	
	my @a_SingleTemplateBar;
	my $ra_SingleTemplateBar = \@a_SingleTemplateBar;
	my @a_FocusSectionTemplateBars =();
	my @aa_AllSectionsTemplateBars =();
	my $ra_FocusSectionTemplateBars = \@a_FocusSectionTemplateBars;
	my $raa_AllSectionsTemplateBars = \@aa_AllSectionsTemplateBars;
	my $nLineNbr=0;
	
	my $nArrayIndex;
	my $sWorkLogText = "";
	
	while (<$hndTemplateFile>) {
		chomp $_;
		my $sLine = $_;
		if ($sLine  =~ /^\s*#.*/) {  # skips commented lines
			next;
		}
		$nLineNbr++;
		if ($sLine =~ /\S+/) {
			TRACE ("line[$nLineNbr] = '$sLine'");
		}
		#====================================================================
		if ($sLine  =~ /.*Outline.*MultiLine.*/g) {
		#-------------------------------------------------------------------
			TRACE ("Outline file indication: '$sLine' ");
		#====================================================================	
		} elsif ( $sLine =~ /$H\=\"(.*)\"/) {  # Notetab topic heading start
		#-------------------------------------------------------------------
			my $sPrevSectionName = $sFocusSectionName;
			$sFocusSectionName = $1;

				if ($bSectionCollectionIsActive==1) { 
					push(@aa_AllSectionsTemplateBars, [@a_FocusSectionTemplateBars]); # see: brackets cause array copying (so the original array can be re-used)
					#TRACE_DUMP($sWorkLogText, __LINE__,$ra_FocusSectionTemplateBars);
					@a_FocusSectionTemplateBars=();
					$bSectionCollectionIsActive=0;
				}
			### push__(\@a_SingleTemplateBar, [$sFocusSectionName],__LINE__,"");
			push(@a_FocusSectionTemplateBars, $sFocusSectionName);
		#====================================================================
		} elsif (($sPossibleTemplateBar) = ($sLine  =~ /.*\[(.*)$/g)) { # assumed template line (starts with bracket for blue color in Notetab)
		#-------------------------------------------------------------------
			###push__(\@a_SingleTemplateBar, $sPossibleTemplateBar,__LINE__,""); 
		#	TRACE_DUMP($sWorkLogText, __LINE__,$ra_FocusSectionTemplateBars);
			push(@a_FocusSectionTemplateBars, [$sPossibleTemplateBar]); 
			$bSectionCollectionIsActive = 1;
		#====================================================================
		} else { 
		#-------------------------------------------------------------------
			# some ignored line 
		}
	} # ... for each template
	
	if ($bSectionCollectionIsActive == 1) {   # last topic in Notetab file
		push(@aa_AllSectionsTemplateBars, [@a_FocusSectionTemplateBars]);
		#TRACE_DUMP("section name '$sNewSectionName'", __LINE__,$ra_FocusSectionTemplateBars);
	} 
#	TRACE_DUMP("savings status of whole template file", __LINE__, @aa_AllSectionsTemplateBars);


	createWriteExternalFile($sTEMPLATE_CFG_EXTRACT_FILE_NAME, to_json($raa_AllSectionsTemplateBars),"Perl sstructure to file as JSON ");
	
	TRACE ("-------------- end collect analysis template config file data to structures --------------------");
	return ($sTEMPLATE_CFG_EXTRACT_FILE_NAME);
}

#===============================================================================
sub tryGetFirstRegexBarMatchForSingleWellLine { my ($sWellLine, @aoaAllRegexBarsWithTargetTags) = @_;
#===============================================================================
    # tries to match regex to well line and assign group item values to a 
	#----------------------------------------------------------------
	# example: [\s(\w+)\W+(\d+).*]
	#            $sfirstWord $nSecondNumber
	#----------------------------------------------------------------
	my $bStatus 				= 0;  # initial quess: will fail
	my %hRegexGroupVal;
	my $sRegexPattern;
	my $nAssumedCapturesCount;
	my $aSingleRegexBarWithTargetsTags=();
	
	my %hValByKey=();
	foreach $aSingleRegexBarWithTargetsTags (@aoaAllRegexBarsWithTargetTags) {
		$sRegexPattern 			= $aSingleRegexBarWithTargetsTags[0];
		$nAssumedCapturesCount	= @$aSingleRegexBarWithTargetsTags-1;
		TRACE ("try match regex '$sRegexPattern' to well line '$sWellLine' ");
		my (@aRegexCapturedGroups) = ($sWellLine =~ /$sRegexPattern/);
		my $nTrueGroupsCount = @aRegexCapturedGroups;
		if ($nTrueCapturesCount == $nAssumedCapturesCount) {  
			for (my $i=0; $1 < $nAssumedCapturesCount; $i++) {
				my $sHashKey =  @aoaAllRegexBarsWithTargetTags[$i-1];
				hashSet__ (\%hRegexGroupVal, $sHashKey, $aRegexCapturedGroups[$i], "regex match");
			}
			$bStatus=1;
		}
	}
	# returns hash where there is key-value -pairs
	return ($bStatus, \%hRegexGroupVal);
}
#===============================================================================
sub  createWriteExternalFile{ my ($sFileName, $rAnyStruct, $sComment) = @_;
#===============================================================================
	if (! open (WRITE_FILE, ">$sFileName")) {  
		TRACE("create write file '$sFileName' open FAILED");
	} else {
		TRACE("$sComment: create write file: '$sFileName'");
		print WRITE_FILE "$rAnyStruct\n";
		close WRITE_FILE;
	}
	return $sFileName;
}
#===============================================================================
sub  readAllExternalFile{ my ($sFileName) = @_;
#===============================================================================
	my @asFileContents;
	if (! open (READ_FILE, "<$sFileName")) {  
		TRACE("read all file '$sFileName' open FAILED");
	} else {
		TRACE("read all file: '$sFileName'");
		@asFileContents = <READ_FILE>;
		close READ_FILE;
	}
	return @asFileContents;
}
#===============================================================================
sub  fillFirstOkTemplateSet{ my (@aoa_AllTopicReportTemplateSets, @asTargetKeys) = @_;
#===============================================================================h
	my $bStatus = 1;   # initial quess: all reports will be filled
	my $sFilledTemplate;
	foreach my $aFocusTemplateSet (@aoa_AllTopicReportTemplateSets) {
		foreach my $sRawTemplate (\@aFocusTemplateSet) {
			foreach my $sCatchKey (@asTargetKeys) {
				my $sCatchVal = $hsTargetKeys[$sCatchKey];
				$sFilledTemplate =~ s/\$DELIM_STR.$sCatchKey.\$DELIM_STR/$sCatchVal/g;
			}
			if ($sFilledTemplate =~ m/^.*\$DELIM_STR\w+\$DELIM_STR.*$/g) {  # some key not changed to value
				$bStatus = 0;
				return ($bStatus, 0);
			} else {
				push(@aFilledTemplates, $sFilledTemplate);
			}
		}
	}
	return ($bStatus, @aFilledTemplates);
}
#======================================================	
sub extractMapLine{ my ($sLine, $MAP_SEPARATOR_TAG, $sCodeCommentStr) = @_;
#======================================================		
	my $sreMapLeftSide;
	my @aTagsRightSide; 
	my $bStatus;
	my $sRawRightSide;
	my $sPlainRightSide;
	
	###my $sAction = "ACT_SAVE_CONVERSION";   # initial quess: save gregex matches, but don't cause any output to result file 
	my $sAction = "ACT_WRITE_CONVERSION";   # initial quess: save gregex matches and write conversionresult file 
	# initial quess: will pass
	($bStatus, $sLine) = assureUsableLine($sRawLine, $sCodeCommentStr);
	my $sreLeftSide;
	my $stgRightSide;
	
	if ($sStatus) {
		($sRawLeftSide, $sRawRightSide) 	= split($sLine, $MAP_SEPARATOR_TAG);
		$sreMapLeftSide 	= trimRims($sRawLeftSide);
		$sPlainRighSide 	= trimRims($sRawRightSide);
		@aTagsRightSide 	= ($sPlainRighSide =~ m/[\%\$\&]([a-zA-Z1-9\=_]+)[\%\$\&]/g);
	}
	return ($bStatus, $sAction, $sreMapLeftSide, $sPlainRighSide, \@aTagsRightSide);
	# PLAN:
	# array_a = item_count + {item_a}
	# item_a = status +  action + left_Side + right_side + array_b
	# array_b = {right_side_tag} + tag_count
	}		
#======================================================	
sub getIfActiveLine{ my ($sRawLine, $sCommentTag) = @_;
#======================================================	
		my $bStatus = 1; # initial quess: will pass
		chomp $sRawLine;
		
		$bStatus = 1; # initial quess non-commented text will be found
		
		#$MapLineNbr++;
		if ($sRawLine =~ (m/^\s*\n/)) { 						# empty line
			$bStatus = 0;	
		} elsif ($sLine =~ (m/^\s*$sCommentTag.*/)) {			# full comment line
			$bStatus =0;
		} elsif ($sRawLine =~ (m/^(.*)\$sCommentTag.*/)) {  	# comment at line end
			$sRetLine = $_;
		}  else {												# no comments at line
			$sRetLine = $sRawLine;
		}
	return ($bStatus, $sRetLine);
}	


#======================================================	
sub getModifierType { my $sTagWithType = shift;
#======================================================	
	if ($sTagWithType =~ m/\%\S+\%/) { # use saved value as a substitute
		$sModifType=$STRINGIFY;
	} elsif ($sTagWithType =~ m/\$\S+\$/) {
		$sModifType=$SYMBOLIFY;
	} elsif ($sTagWithType =~ m/\&\S+\&/) {  # symbolify saved value before using it as a substitute
		$sModifType=$TEXTIFY;	
	} else {  # error condition
		TRACE ("ERROR: no type by '$sRightSideTagWithType'");
	}
	return $sModifyType; 
}
#=======================================================================================================
sub modifyByType {
	my $sData = shift;
	my $nTag = shift;
	my $sType = shift;
	if ($sType  =~ m/$SYMBOLIFY/) {
		$sSubstitution =~ s/\W+/_/g;
		TRACE ("make SYMBOLIFICATION");
		$sSubstituted =~ s/\$$nTag\$/$sSubstitution/g;
	} elsif ($sType  =~ m/$TEXTIFY/) {
		$sSubstitution =~ s/\W+/ /g;
		TRACE ("make TEXTIFICATION");
		$sSubstituted =~ s/\&$nTag\&/$sSubstitution/g;
	} elsif ($sType  =~ m/$STRINGIFY/) {
		$sSubstitution =~ s/\"/ /g;
		$sSubstitution =~ s/\'/ /g;
		TRACE("make STRINGIFICATION");
		$sSubstituted =~ s/\&$nTag\&/$sSubstitution/g;
	} else {
		#print TRACE "NO MODIFICATIONS\n";
	}

	return $substituted; 
}
# wrappers with trace logging
#-----------------------------------------------------------------------
sub push__ {
	my ($raItems, $newItem, $nLineNbr, $sComment)=@_;  # array reference as parameter
	push(@{$raItems}, $newItem);
	TRACE("$sComment: push new item '$newItem' to array (caller line:$nLineNbr) ");
	
	#TRACE("push__ DUMP: ".Dumper($raItems));
	#TRACE(Dumper(@{$raItems}));
}	
#-----------------------------------------------------------------------
sub pop__{
	my ($raItems,$sComment)=@_;
	$retItem = pop(@{$raItems});
	TRACE ("pop '$retItem' from array of: ");
	foreach $item (@{$raItems}) {
		TRACE("'$item', ");
	}

	return $retItem;
}
#-----------------------------------------------------------------------
sub peek__ {
	my ($raItems)=@_; # array reference as input parameter
	if (@{$raItems} > 0) {
		$retItem = @{$raItems}[-1]; # dereferencing and indexing array reference
	} else {
		$retItem = "EMPTY";
	}
	TRACE("peek '$retItem'");
	return $retItem;
}
#-----------------------------------------------------------------------
sub hashSet__ {
	my ($rHash, $key, $val, $sNameComment)=@_;  	# hash reference as parameter
	$rHash->{$key} = $val;  			# updating a hash when has reference is available
	TRACE("<$sNameComment>{$key} = $val");
}
#-----------------------------------------------------------------------
sub hashGet__ {
	my ($rHash, $key, $sNameComment)=@_;	# hash reference as parameter
	$val = $rHash->{$key};  	# accessing a hash when has reference is available
	if ($val eq "") {
		$val="EMPTY";
	}
	TRACE("$val = <$sNameComment>{$key}");
	return $val;
}
# -------------------------------------------------------------------------------
sub OUT_PRE { 
	my (@argv)=@_;
	$OutFile 			= shift @argv;
	$OutFile			=~s/\\/\//g;

	open(OUT_FILE, ">$OutFile") || print "Cannot open output file '$OutFile'\n";
	return (OUT_FILE);
}
#--------------------------------------------------------------------------------
sub OUT_POST { 
	my ($OUT)=@_;
	close $OUT;
}
#--------------------------------------------------------------------------------
sub OUT_INI{ 
	my ($OutFile)=@_;
	$OutFile	=~s/\\/\//g;
	open(OUT_FILE, ">$OutFile") || print "Cannot open output file '$OutFile'\n";
}
#--------------------------------------------------------------------------------
sub OUT_END {  # 
	my ($OUT)=@_;
	close $OUT;
}
#---------------------------------------------------------------------------------
sub OUT { 
	my ($str)=@_; # required parentheses !!!
    print OUT_FILE "$str \n";
}
##################################################################################
sub sym { 
	my ($s)=@_;

	$s= asc($s);
	$s =~ s/\W/_/g;
	$s =~ s/^\d/_/g;
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: symbol name is $s");
	}
	return $s;
}
#-----------------------------------------------------------------------
sub str {
	my ($s)=@_;
	$s= asc($s);
	$s=~ s/\\/\\\\\\\\/;
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: label is $s");
		return $s;
	}
	return $s;
}
#-----------------------------------------------------------------------
sub lbl  {
    my($s) = @_;
    $s= asc($s);
	$s =~ s/\\/\\ /g; # spaces added to make split candidate positions
	$s =~ s/\//\/ /g;
	$s =~ s/_/\_ /g;
	$s =~ s/\"/ /g;
	
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: label is $s");
		return $s;
	}
    @Parts = split(/\s+/, $s);
	
	$maxPartLen = 32;
    $ResultStr = "";
    $NextStepPos = $maxPartLen;
    
    foreach (@Parts) {
        $ResultStr = $ResultStr." ".$_;
        $TotalLen = length($ResultStr);
        
        if ($TotalLen > $NextStepPos) {
            $ResultStr      = $ResultStr.'\\n';
            $TotalLen       = length($ResultStr);
            $NextStepPos    = $TotalLen + $maxPartLen;
        }
    }
   
    $ResultStr =~ s/\\ /\\/g;  # to return non-splitted positions to original

	$ResultStr =~ s/\/ /\//g;
	$ResultStr =~ s/_ /\_/g;
   
   	return "\"".$ResultStr."\"";
}
#---------------------------------------------------------------------------------------
sub asc {
	my ($s)=@_;
	$s=~ s/\E4/a/g;   #note: editor "Encode in ANSI" selected
	$s=~ s/\C4/A/g;   #   - to disable graphviz error condition 
	$s=~ s/\F6/o/g;
	$s=~ s/\D6/O/g;
	$s=~ s/\E5/o/g;
	$s=~ s/\C5/O/g;
	return $s;
}
#----------------------------------------------------------------------------------------
sub trimTrough {
	# - removes all leading and trailing spaces
	# - converts remaining multiple spaces to single spaces
	my ($s)=@_;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	$s =~ s/\s+/ /; 
	return $s;
}
#----------------------------------------------------------------------------------------
sub trimRims {
	# - removes all leading and trailing spaces
	my ($s)=@_;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	return $s;
}
#---------------------------------------------------------------------------------------
sub TRACE_INIT
{
	my ($sName, $sComment) = @_;
	$sTRACE_FILE_NAME = $sName;
	open($TRACE_LOG,">$sTRACE_FILE_NAME") || print "Cannot open trace file '$sTRACE_FILE_NAME' for '$sComment'\n";
	TRACE($sComment);
}
#-----------------------------------------------------------------------
sub TRACE
{
	my ($Comment) = @_;
	###my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info
	print $TRACE_LOG "$Comment\n";
}
#-----------------------------------------------------------------------
sub TRACE_ARRAY{
	my ($Comment,@array) = @_;
	my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info
	#print TRACE("$Comment array:".\@array."\n");
	for $item (@array) {
		print $TRACE_LOG "    $item\n";
	}				 
}
#-----------------------------------------------------------------------
sub TRACE_DUMP{ my ( $sComment, $nLineNbr, $anyref) = @_;
	TRACE("TRACE DUMP (comment/line = '$sComment'/'$nLineNbr') ". Dumper($anyref));
}
#-----------------------------------------------------------------------
sub TRACE_END {
	my ($sComment) = @_;
	TRACE($sComment);
	TRACE("TRACE ended");
	close $TRACE_LOG; 
	print "see file $sTRACE_FILE_NAME";
}
#-----------------------------------------------------------------------
sub __ { # element of active commenting
	my ($Comment) = @_;
	if (!grep(/$Comment/, @aCommentTexts)) { # every active comment is written only once (to limit log output)
		push(@aCommentTexts, $Comment);
		TRACE($Comment);
	}
}
#===============================================================================
sub getDateTime__ {
	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	$sRet = "TIME $hour:$min:$sec";
	TRACE($sRet);
	
	return $sRet;
}
1;
# examples: dot -Tpng -o temp.png temp.dot
