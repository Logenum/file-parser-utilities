package PERL_SCRIPTS;

# TODO: remove application -specific methods
# copied here 150921

# note: caller files shall contain lines: "package PERL_SCRIPTS;" and "use UTILS;"
 
################################################################################

my $srePATH_NAME_CAPTURE = "(\/.*\/\\S+)"; 
my $sreHTML_HYPERLINK_CAPTURE = "\<.*href\s*\=\s*\"(.*)?\"\>";
my $sreFILE_NAME_CAPTURE = "\<u\>(.*)\<\/u\>";     # Underlining assumed
my $sreINPUT_DATA_FILE_NAME_CAPTURE = "INPUT\:\s+(\/.*\/\\S+)"; 
my $sreOUTPUT_WORK_FILE_NAME_CAPTURE = "OUTPUT\:\s+(\/.*\/\\S+)"; 
my $sreTRAC_TICKET_CAPTURE = "TRAC.*\\#(\\d+).*"; 

my $status;
my $sPath;
my $sCaptured;
my $sType;
my $sLatestType = 'NONE';
my $sFinalType = 'NONE';
my $sLatestPath;
my $sTargetFullName;
my $sStr;
my $sLine;
my @aCommentTexts;
my $sInputDataFileFullName ="";
my $sOutputWorkFileFullName ="";



#=================================================================================================
sub collectBuildCheckSpecificItems { 
    my ($raLines, $sFocusLine, $nFocusLineNbr) = @_;
    my $bFinish = 0;
    my $sLine;
    my $sType;
    my $hrSingleItemInfo;
    my @asAllItemsInfo;

    my @asAllItemsReversedInfo;
    my $sPossibleLatestPath="NONE";

    TRACE("calling collectBuildCheckSpecificItems()");
    foreach $sLine (@{$raLines}) {
	TRACE("line '$sLine'");
	$nTextLineNbr++;
	if  ($bFinish == 1) {
	    last;
	}

	if ($sFocusLine eq $sLine) {
	    TRACE("focus line '$sFocusLine' matches line '$sLine'[text line number: $nTextLineNbr]");
	    TRACE("------------------ this line is cursor line, so it is the last line to be processed-------------");
	    $bFinish=1;
	}

	($sType, $hrSingleItemInfo) = tryCaptureVerifyPathOrFileName($sLine, $nTextLineNbr, $sreHTML_HYPERLINK_CAPTURE, "N/A", __LINE__);
	if ($sType eq 'PATH') {
	    $sPossibleLatestPath =  $hrSingleItemInfo->{"NAME"};
	    push__(\@asAllItemsInfo, $hrSingleItemInfo);
	    next;
	} 

	($sType, $hrSingleItemInfo) = tryCaptureVerifyPathOrFileName($sLine, $nTextLineNbr, $srePATH_NAME_CAPTURE,  "N/A", __LINE__);
	if ($sType eq 'PATH') {
	    $sPossibleLatestPath =  $hrSingleItemInfo->{"NAME"};
	    push__(\@asAllItemsInfo, $hrSingleItemInfo);
	    next;
	} 

	($sType, $hrSingleItemInfo) = tryCaptureVerifyPathOrFileName($sLine, $nTextLineNbr, $sreFILE_NAME_CAPTURE, $sPossibleLatestPath, __LINE__);
	if ($sType eq 'FILE') {
	    push__(\@asAllItemsInfo, $hrSingleItemInfo);
	    next;
	} 

	
    }  # ...foreach
    @asAllItemsReversedInfo = reverse(@asAllItemsInfo);
    TRACE("DUMP:------------------------------------------------------");
    TRACE(Dumper(\@asAllItemsReversedInfo));
    return (\@asAllItemsReversedInfo);
}


#===================================================================
sub detectFileRole{
    my ($sLine) = @_;
    my $sCapt="";($sNameCandidate) = ($sLine =~ m/$sCAPTURE_REGEX/g);
    my $sRole = "UNKNOWN";
    my $srePattern;
    #-----------------------------------------------------------------------------------
    my @asRoleDetectionRegex = (".*(INPUT)\:.*", 
				".*(OUTPUT)\:.*", 
				".*\\w+\\.(pl),*",
				".*\\w+\\.(pm).*");  # note: requires double backslashes
    #-----------------------------------------------------------------------------------
    foreach (@asRoleDetectionRegex) {
	$srePattern =$_;
	($sCapt) = ($sLine =~ m/$srePattern/g );
	if ($sCapt ne "") {
	    if ($sCapt eq "INPUT") {
		  $sRole = 'INPUT';
	    } elsif ($sCapt eq "OUTPUT") {
		  $sRole = 'OUTPUT';
	    } elsif ($sCapt eq "pl") {
		  $sRole = 'PERL';
	    } elsif ($sCapt eq "pm") {
		  $sRole = 'PERL';
	    } else {
		$sRole = 'COMMAND';
	    }focus line 
	    last;
	}
    }

    if ($sRole ne "UNKNOWN")  {
	TRACE("captured role '$sRole' due to '$sCapt' (by '$srePattern' from line '$sLine')");
    } else {
	TRACE("no role captured from '$sLine'");
    }
    return $sRole;
}

#================================================================
sub detectFileRace {
    my ($sFileName, $nLineNbr) = @_;
    my $sFileRace = "TEXT"; 	# initial quess
    my $sNameExt =  ""; 	

    if ($sFileName =~ /.*\.(\w+)\s*$/) {
	$sNameExt = uc $1; # assures single (upper) case
	if ($sNameExt eq 'PNG') {
	    $sFileRace = 'IMAGE';
	} elsif ($sNameExt eq 'DOCX') {
	    $sFileRace = 'DOCUMENT';
	} elsif ($sNameExt eq 'RTF') {
	    $sFileRace = 'DOCUMENT';
	} else {}
    } else {
	 # TODO: add more cases
    }
    TRACE("file '$sFileName' race is '$sFileRace' by '$sNameExt' [$nLineNbr]");
    return ($sFileRace);
}
#================================================================
sub tryCaptureVerifyPathOrFileName{ my ($sLine, $nLineNbr, $sCAPTURE_REGEX, $sLatestPath, $nCallerLineNbr) = @_;

    my %hSingleItemInfo	= ();
    my $sCandidate 	= "";
    my $sRace 		= "";
    my $sType;
    my $name;

    $sLine = assureSomeHtmlStuffRemoval($sLine);

    ($sNameCandidate) = ($sLine =~ m/$sCAPTURE_REGEX/g);

    my $sFullFileNameCandidate = $sLatestPath.$sNameCandidate;  # will be uses if captured text is not a path name

    if (-d $sNameCandidate) {
		$sType = 'PATH';
		$name = $sNameCandidate;
		$hSingleItemInfo{ROLE} = "N/A";
		$hSingleItemInfo{RACE} = "N/A";
    } elsif (-f $sFullFileNameCandidate) {
		$sType = 'FILE';
		$name = $sFullFileNameCandidate;
		$hSingleItemInfo{ROLE} = detectFileRole($sLine);
		$hSingleItemInfo{RACE} = detectFileRace($sCandidate, __LINE__);
    } else {
		$sType = 'NONE';
		TRACE("string '$sNameCandidate' is not a path"); 
		TRACE("string '$sFullFileNameCandidate' is not a file"); 
    }

    if ($sType ne 'NONE') {
		$sStatus = "TRUE";
		$hSingleItemInfo{TYPE} = $sType;
		$hSingleItemInfo{NAME} = $name;
		TRACE("captured '$sType' at line '$sLine' by '$sCAPTURE_REGEX' ,latest path='$sLatestPath' (called at '$nCallerLineNbr')");
    } else {
	 # if ($sLatestPath ne "N/A") { # for debugging purposes
	#	TRACE("failed to capture path or file at line '$sLine' by '$sCAPTURE_REGEX' ,latest path='$sLatestPath' (called at '$nCallerLineNbr')");
	 # }
    }
   
    return ($sType,\%hSingleItemInfo);
}


#================================================================
sub tryCaptureOtherTypeItem {
    my ($sLine, $nLineNbr, $sCAPTURE_REGEX) = @_;

    my $sItemVal ="";

    $sLine = assureSomeHtmlStuffRemoval($sLine);
    ($sItemVal) = ($sLine =~ m/$sCAPTURE_REGEX/g );

    if ($sItemVal ne "") {
	TRACE("captured '$sItemVal' (by '$sCAPTURE_REGEX' from line '$sLine'[$nLineNbr])");
    } else {
	#TRACE("captured NOTHING (by '$sCAPTURE_REGEX' from line '$sLine'[$nLineNbr])");
    }

    return $sItemVal;
}


#================================================================
sub assureSomeHtmlStuffRemoval {
    my ($sLine) = @_;

    #$sLine =~ s/<.+?>//g; # note: non -greedy ($sTargetType, $sTargetFullName)= tryCaptureRecentExistingPathOrFileFullName"<...>" captures
    #$sLine =~ s/ //g;
    $sLine =~ s/<font.*?>//g; # note: non -greedy "<...>" captures
    $sLine =~ s/<\/font.*?>//g; 
    $sLine =~ s/<b>//g;
    $sLine =~ s/<\/b>//g;
    $sLine =~ s/\&\#\d+\;//g;
    #$sLine =~ s/ //g;

    return $sLine;
}


#================================================================
#----------------------------------------------------
sub getLineNbrByIncSearch {
#----------------------------------------------------
      my ($sTargetFileFullName,
	      $sLineWithNavigStr,
	      $sreNAVIG_CAPTURE,
	      $SPLITTER) = @_;

      my $rasTRACE=[];  # idea: trace messages are collected to an array for returning
      push(@$rasTRACE, "target file  = '$sTargetFileFullName'");
      push(@$rasTRACE, "pattern line = '$sLineWithNavigStr'");
      my $FALSE=0;
      my $TRUE=1;
      my $THIS_FILE_NAME = $0;
      my $nTextLineNbr = 1;   # first line number is 1 (one) !!!
      # Navig example: |sub\s+mainfunc|index|a=5|
      my $bNavigStrChainEndMatchOK = $FALSE;
      my %hKeyValPair = {};
      my $nNavigStrChainLastPartPos = 0;
      my $sTypeNavigStrChainFocusPartPos = 0;
      my $sNavigStr;
      my @asTargetFileLines;
      my $nTargetLineNbr = 0; # initial quess
      my @aNavigStrChain;
      my $sFocusLine;
      my $sNavigStrChainFocusPart;

#	push(@$rasTRACE);

      die "Failed to open file '$sTargetFileFullName'" unless open(TARGET_FILE,"<$sTargetFileFullName");
      die "Failed to read file '$sTargetFileFullName'" unless @asTargetFileLines=<TARGET_FILE>;
      close TARGET_FILE;
      
      #------------$sLine =~ m/$FILE_DETAIL_NAVIG_CAPTURE_R-------------------------------------------------------
      my ($sNavigStrChain) = ($sLineWithNavigStr =~ /$sreNAVIG_CAPTURE/);
      if (@aNavigStrChain	= split (/$SPLITTER/, $sNavigStrChain)) {
	      $nNavigStrChainLastPartPos = $#aNavigStrChain;
	      push(@$rasTRACE, "split '$sLineWithNavigStr' by '$SPLITTER'");   # note: data into array via reference
	      ##push(@$rasTRACE, "split pTRACE("file role ");arts: ".@aNavigStrChain);$sType
      } else {
	      push(@$rasTRACE, "failed to split '$sLineWithNavigStr' by '$SPLITTER'");   # note: data into array via reference
      }
      #----------------------------------------------------------------------------------------------------------
      foreach $sFocusLine (@asTargetFileLines) {
              $sFocusLine = assureComparableStr($sFocusLine);
	      ###push(@$rasTRACE, "focus line: '$sFocusLine'");
	      ###push(@$rasTRACE, "check line  '$Line'[$nTextLineNbr]");
	      if ($nNavigStrChainFocusPartPos <= $nNavigStrChainLastPartPos) {
		      $sNavigStrChainFocusPart = $aNavigStrChain[$nNavigStrChainFocusPartPos];
		      ##push(@$rasTRACE, "try match part '$sNavigStrChainFocusPart' [$nNavigStrChainFocusPartPos] to text");
		      ;
		      if ($sFocusLine =~ m/.*$sNavigStrChainFocusPart.*/g ) {
			      push(@$rasTRACE, "'$sNavigStrChainFocusPart' found at line '$sFocusLine' ($nTextLineNbr)");
			      $nNavigStrChainFocusPartPos++;
		      } else {
			      ##push(@$rasTRACE, "'$sNavigStrChainFocusPart' NOT found at line '$sFocusLine' ($nTextLineNbr)");
		      }
		      $nTextLineNbr++;
	      } else  {
		      push(@$rasTRACE, "all chain '$sNavigStrChain' parts found");
		      $bNavigStrChainEndMatchOK = $TRUE;
		      last;
	      }
      }
      #-----------------------------------------------------------------------------------
      if ($bNavigStrChainEndMatchOK == $TRUE) {
	      $nTargetLineNbr = $nTextLineNbr; 
	      TRACE("return type '$sType' by line '$sLine'");
      } else {
	      push(@$rasTRACE, "failed to find target by '@aNavigStrChain'");
      }
      push(@$rasTRACE, "target line number = $nTargetLineNbr");
      return ($nTargetLineNbr-1, $rasTRACE);  # note: returning of array reference
}

# wrappers with trace logging

#================================================================
sub tryCaptureInOutFileNames{
    my ($sLine, $nLineNbr, $sCAPTURE_REGEX, $bFinish) = @_;

    my $sCandidate ="";
    #$sLine =~ s/<.+?>//g; # note: non -greedy "<...>" captures
    #$sLine =~ s/ //g;
   $sLine =~ s/<font.*?>//g; # note: non -greedy "<...>" captures
   $sLine =~ s/<\/font.*?>//g; 
   $sLine =~ s/<b>//g;
   $sLine =~ s/<\/b>//g;
    #$sLine =~ s/ //g;

    ($sCandidate) = ($sLine =~ m/$sCAPTURE_REGEX/g );
    my $sType;
    if (-d $sCandidate) {
	$sType = 'PATH';
    } elsif (-f $sCandidate) {
	$sType = 'FILE';
    } else {
	if ($sCandidate ne "") {
	    $sType = 'SOME';
	}  else {
	    $sType = 'NONE';
	}
    }
    if (($sType ne 'NONE') || ($bFinish == 1)) {
	TRACE("captured type '$sType' string '$sCandidate' (by '$sCAPTURE_REGEX' from line '$sLine'[$nLineNbr])");
    }
    return $sInputFileFullName, $sOutputFileFullName;
}

#================================================================
sub duplicateFileNameByExtension {
    my ($sName, $sExtension) = @_;
    my $sNewName=""; # initial quess
    if ($sName =~ /(.*)\..*/) {
	  $sNewName = $1.".$sExtension";
	  if ( $sNewName eq $sName) {
	      TRACE ("file '$sNewName' exists already, so it is not created");
	      $sNewName="";
	  }
    } else {
	  TRACE("failed to copy file name from '$sName'");
    }
    return $sNewName; 
}

#================================================================
sub assureComparableStr {
    my ($sStr) = @_;


    $sStr =~ s/\'/\\'/g;
    $sStr =~ s/\$/\\\$/g;
    $sStr =~ s/\:/\\:/g;
    $sStr =~ s/\>/\\>/g;
    $sStr =~ s/\=/\\=/g;
    $sStr =~ s/\&gt\;//g;

    return $sStr;
}


#-----------------------------------------------------------------------
sub push__ {
	my ($raItems, $newItem)=@_;  # array reference as parameter
	print TRACE_LOG "push '$newItem' to array of: ";
	foreach $item (@{$raItems}) { # looping array items via array reference
		print TRACE_LOG "'$item', ";
	}
	push(@{$raItems}, $newItem);
	print TRACE_LOG "\n";	
}
#-----------------------------------------------------------------------
sub pop__{
	my ($raItems)=@_;
	$retItem = pop(@{$raItems});
	print TRACE_LOG "pop '$retItem' from array of: ";
	foreach $item (@{$raItems}) {
		print TRACE_LOG "'$item', ";
	}
	print TRACE_LOG "\n";
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
	print TRACE_LOG "peek '$retItem'\n";
	return $retItem;
}
#-----------------------------------------------------------------------
sub hashSet__ {
	my ($rHash, $key, $val, $sNameComment)=@_;  	# hash reference as parameter
	$rHash->{$key} = $val;  						# updating a hash when has reference is available
	print TRACE_LOG "<$sNameComment>{$key} = $val\n";
}
#------------------------------------------------------TRACE(Dumper-----------------
sub hashGet__ {
	my ($rHash, $key, $sNameComment)=@_;	# hash reference as parameter
	$val = $rHash->{$key};  	# accessing a hash when has reference is available
	if ($val eq "") {
		$val="EMPTY";
	}
	print TRACE_LOG "$val = <$sNameComment>{$key} \n";
	return $val;
}

#---------------------------------------------------------------------------------------
sub tryMatch { 
	my ($regex, $str) = @_;
	my $bStatus=0; # initial quess
	if ($str =~ m/$regex/g) {
	     $bStatus = 1;
	    TRACE("pattern '$regex' did match to line '$str'");
	} else {
	    TRACE("pattern '$regex' did not match to line '$str'");
	}
	return $bStatus;
}
#---------------------------------------------------------------------------------------
sub OUT_PRE { 
	my (@argv)=@_;
	
	$OutFile 			= shift @argv;
	$OutFile			=~s/\\/\//g;

	open(OUT_FILE, ">$OutFile") || print "Cannot open output file '$OutFile'\n";
	return (OUT_FILE);
}
#---------------------------------------------------------------------------------------
sub OUT_POST { 
	my ($OUT)=@_;
	
	close $OUT;
}
#---------------------------------------------------------------------------------------
sub OUT_INI{ 
	my ($OutFile)=@_;
	$OutFile	=~s/\\/\//g;
	open(OUT_FILE, ">$OutFile") || print "Cannot open output file '$OutFile'\n";
}
#---------------------------------------------------------------------------------------
sub OUT_END {  # 
	my ($OUT)=@_;
	close $OUT;
}
#---------------------------------------------------------------------------------------
sub OUT { 
	my ($str)=@_; # required parentheses !!!
    print OUT_FILE "$str \n";
}

#---------------------------------------------------------------------------------------
sub OUT_ONCE { 
	my ($str) = @_;
	foreach $s (@aCommentTexts) {
	    if ($s eq $str) { # e is written only once (to limit output file size)
	      return;
	    }
	}
	push(@aCommentTexts, $str);
	print OUT_FILE "$str\n";
}
#---------------------------------------------------------------------------------------
sub OUT_ONCE_IF { 
	my ($str, $regex) = @_;
	if ($str =~ m/$regex/g) {
	    foreach $s (@aCommentTexts) {
		if ($s eq $str) { # e is written only once (to limit output file size)
		  return;
		}
	    }
	    push(@aCommentTexts, $str);
	    print OUT_FILE "$str\n";
	} else {
	    TRACE("pattern '$regex' did not match to line '$str'");
	}
	  
}
#---------------------------------------------------------------------------------------
sub DOT_PRE { 
	my (@argv)=@_;
	$InpFile 			= shift @argv; 
	$GraphFile 			= shift @argv;
	$InpFile			=~s/\\/\//g;
	$GraphFile			=~s/\\/\//g;
	
	open(INP_FILE, "<$InpFile") || print "Cannot open input file '$InpFile'\n";
	open(DOT_FILE, ">$GraphFile") || print "Cannot open graph file '$GraphFile'\n";
	return (INP_FILE, DOT_FILE);
}
#---------------------------------------------------------------------------------------
sub DOT_POST { 
	my ($INP,$DOT)=@_;
	close $INP;
	close $DOT;
}
#---------------------------------------------------------------------------------------
sub DOT_INI{ 
	my ($GraphFile)=@_;
	$GraphFile	=~s/\\/\//g;
	open(DOT_FILE, ">$GraphFile") || print "Cannot open graph file '$GraphFile'\n";
}
#---------------------------------------------------------------------------------------
sub DOT_END {  # 
	my ($DOT)=@_;
	close $DOT;
}
#---------------------------------------------------------------------------------------
sub DOT { 
	my ($str)=@_; # required parentheses !!!
    print DOT_FILE "$str \n";
}

##################################################################################

sub sym { 
	my ($s)=@_;

	my $s= asc($s);
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
	my $s= asc($s);
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
	$s=~ s/ä/a/g;   #note: editor "Encode in ANSI" selected
	$s=~ s/Ä/A/g;   #   - to disable graphviz error condition 
	$s=~ s/ö/o/g;
	$s=~ s/Ö/O/g;
	$s=~ s/å/o/g;
	$s=~ s/Å/O/g;
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

sub phaseSET {
my ($sPhaseNew)=@_;
  if ($sPhaseNew ne $sPhaseNow) {
      TRACE ("phase changed from '$sPhaseNow' to '$sPhaseNew'");
  }
  $sPhasePrev = $sPhaseNow;
  $sPhaseNow = $sPhaseNew;
}


sub phaseGET {
my ($sPhase)=@_;
  
}

sub phaseIS {
  my ($sPhaseAsk)=@_;  

  if ($sPhaseAsk eq $sPhaseNow) {
    return 1;
  } else {
    return 0;
  }
}
#---------------------------------------------------------------------------------------
sub TRACE_INIT
{
	my ($sTraceFileName, $sComment) = @_;
	open(TRACE_LOG,">$sTraceFileName") || print "Cannot open trace file '$sTraceFileName' for '$sComment'\n";
	print TRACE_LOG "$sComment\n";
###	close TRACE_LOG;
}
#-----------------------------------------------------------------------
sub TRACE
{
	my ($Comment) = @_;
##	open(TRACE_LOG,">>$sTraceFileName") || print "Cannot open trace file '$sTraceFileName' for '$Comment'\n";
	###my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info
	print TRACE_LOG "$Comment\n";
##	close TRACE_LOG;
}
#-----------------------------------------------------------------------
sub TRACE_ARRAY {
	my ($Comment,@array) = @_;
##	open(TRACE_LOG,">>$sTraceFileName") || print "Cannot open trace file '$sTraceFileName' for '$Comment'\n";
	my ($package, $filename, $line, $subroutine) = caller(1);  # note: getting caller info
	print TRACE_LOG "$Comment array:".@array."\n";
	for $item (@array) {
		print TRACE_LOG "    $item\n";
	}				 
	
###	close TRACE_LOG;
}

#-----------------------------------------------------------------------
sub TRACE_END {
	print TRACE_LOG "TRACE ended\n";
	close TRACE_LOG;  # trace file closing transferred here
}
#-----------------------------------------------------------------------
sub __ { # element of active commenting
	my ($Comment) = @_;
	if (!grep(/$Comment/, @aCommentTexts)) { # every active comment is written only once (to limit log output)
		push(@aCommentTexts, $Comment);
		print TRACE_LOG "$Comment\n";
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
