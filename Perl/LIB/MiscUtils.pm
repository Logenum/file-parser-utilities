use v5.20;
use JSON;
use Data::Dumper;
use TraceUtils;
my $sEMPTY_LINE = " ";

#==============================================================
# Perl misc links
#--------------------------------------------------------------
# http://affy.blogspot.fi/p5be/ch10.htm   !: Regular expressions

#==============================================================
sub toJson{ my ($rStruct, $sComment) = @_;
#==============================================================
	TRACE_SUB();
	
	my $json = JSON->new->allow_nonref;
	my $pretty_printed = $json->pretty->encode($rStruct); # produces indented, multi-line string 
	my $sJson = to_json($rStruct);   # produced one-line string
	TRACE("$sComment: '$sJson'");    # single-lined to trace log file, pretty-printed (=multi lined) to Trace bag log file
	if (defined $sComment) {
		TRACE_BAG($pretty_printed, $sComment);
	} else {
		TRACE_BAG($pretty_printed);
	}
	TRACE_RET();
	return $sJson;
}
#==============================================================
sub fromJson{ my ($sJsonStr, $sComment) = @_;
#==============================================================
	TRACE_SUB();
	TRACE_BAG("$sComment: '$sJsonStr'");
	TRACE("call from_json()");
	#TRACE("JSON = ".quotemeta($sJsonStr));
	my $rStruct = from_json($sJsonStr);
	TRACE_BAG("\$rStruct = ".Dumper($rStruct));
	#TRACE("\$sJson = ".Dumper($pretty_printed));
	#TRACE("\$sJson = ".$pretty_printed);
	TRACE_RET();
	return $rStruct;
}
#==============================================================
sub isValidJson { my ($sPossiblyJsonStr, $sComment) = @_;
#==============================================================
# http://cpansearch.perl.org/src/OVID/Test-JSON-0.11/lib/Test/JSON.pm
	my $bStatus;
    eval { from_json($sPossiblyJsonStr); }; # !!: perl function call for to generate possible error for subsequent handling 
    if ( my $error = $@ ) {   # !!: perl error handling
		TRACE_SUB();
		TRACE("$sComment: '$sPossiblyJsonStr' is NOT valid JSON string");
		TRACE_RET();
        $bStatus = 0;
    } else {
		TRACE_SUB();
		TRACE("$sComment: '$sPossiblyJsonStr' is valid JSON string");
		TRACE_RET();
        $bStatus = 1;
    }
	return $bStatus;
}
#==================================================================================
sub checkIfIgnoreLine{ my ($sInLine) = shift;
#==================================================================================
	if ($sInLine 	=~ /^\s*$/) 					{return 1;}	# skips totally empty lines
	#if ($sInLine 	=~ /^\s*\-.*/) 					{return 1;}	# skips 'french lines' starting lines
	return 0;
}
#================================================================
sub removePossibleComments { my ($sInStr) = @_;
#================================================================
	my $sOutStr;
	# TODO: add array of possible comment start strings as call parameter
	if ($sInStr =~ /^\s*#.*/) { # whole line '#' -comments
		$sOutStr = $sEMPTY_LINE;
	} elsif ($sInStr =~ /^\s*\/\/.*/) { # whole line '#' -comments
		$sOutStr = $sEMPTY_LINE;
	} elsif ($sInStr =~ /^(.*)#?.*/g) {   # line end '#' -comments
		$sOutStr = $1;
	} elsif ($sInStr =~ /^(.*)\/\/?.*/g) {  # line end '//' -comments
		$sOutStr = $1;
	} else {
		$sOutStr = $sInStr;
	}
	return $sOutStr;
}
#================================================================
sub tryRegexCaptureMatch {  my ($sText, $sRegex, $sComment) = @_;
#================================================================
	my @asCaptures;
	my $bStatus = 1; # initial quess
	
	#TRACE_SUB();
	if (@asCaptures = ($sText =~ /$sRegex/)) {
		#TRACE_SUB();
		TRACE("MATCH OK: '$sRegex' to '$sText' ROLE: '$sComment'");
		#TRACE_RET();
	} else {
		TRACE("match FAIL: '$sRegex' to '$sText' ROLE: '$sComment'");
		$bStatus=0;
	}
	#TRACE_RET();
	return $bStatus, \@asCaptures;
}
#===============================================================================
sub tryCapture { my ($sText, $sRegex, $sCaptureKeys) = @_;  
#===============================================================================
# TODO: change this function to MiscUtils
	# tries to capture values from given text by given regex
	# captured values are saved via hash keys which are listed in given string
	TRACE_SUB();
	
	my $bStatus = 0; 	# initial quess
	my $i=0;  
	my @asCaptures;
	my $sSaveKeys  		=~ s/\s//g;    # removes spaces
	my @asCaptureKeys 	= split('\$', $sCaptureKeys);  # '$' is assumed as key prefix
	shift @asCaptureKeys; # for removing empty item caused by split
	
	my $nKeysCnt = length @asCaptureKeys;
	if (@asCaptures = ($sText =~ /$sRegex/g)) {
		my $nCapturesCnt = length @asCaptures;
		if ($nKeysCnt != $nCapturesCnt) {
			TRACE("MISMATCH: '$nKeysCnt' values assumed by '$sCaptureKeys' but '$nCapturesCnt' values captured by '$sRegex'");
		} else {
			foreach my $sCaptureVal (@asCaptures) {
				setVal($asCaptureKeys[$i], $sCaptureVal);
				$i++;
			}
			$bStatus = 1;
		}
	}
	TRACE_RET();
	return $bStatus;
}
#================================================================
sub getByFirstOfRegexes {  my ($sText, $rasRegexes, $sComment) = @_;
#================================================================
	my @asCaptures;
	my $sRegex;
	my $bStatus = 1; # initial quess
	TRACE_SUB();
	foreach $sRegex (@$rasRegexes) {
		#TRACE_SUB();
		if (@asCaptures = ($sText =~ /$sRegex/)) {
			TRACE("MATCH OK: '$sRegex' to '$sText'");
			last;
		} else {
			#TRACE("match FAIL: '$sRegex' to '$sText'");
			$bStatus=0;
		}
	}
	TRACE_RET();
	return $bStatus, \@asCaptures;
}

#================================================================
sub matchFirstOf {  my ($sText, $rasRegexes) = @_;
#================================================================
	my $sRegex;
	my $bStatus = 1; # initial quess
	TRACE_SUB();
	foreach $sRegex (@$rasRegexes) {
		#TRACE_SUB();
		if ($sText =~ /$sRegex/) {
			TRACE("MATCH OK: '$sRegex' to '$sText'");
			last;
		} else {
			#TRACE("match FAIL: '$sRegex' to '$sText'");
			$bStatus=0;
		}
	}
	TRACE_RET();
	return $bStatus;
}

#===============================================================================
sub captureTags{ my ($sTargetStr, $sTagFrameCaptureRegex, $sTagCoreCaptureRegex) = @_;  
#===============================================================================
#  collects all given pattern tags from given string
	my @asAllTagFrames;  # complete tags with frames
	my @asAllTagCores;   # symbol names within tag frames (e.g. keys for some hash)
	my $nItemsCnt = 0; # initial quess
	my $sDump;
	MM::TRACE_SUB();
    @asAllTagFrames = $sTargetStr =~ m/$sTagFrameCaptureRegex/g;
	@asAllTagCores 	= $sTargetStr =~ m/$sTagCoreCaptureRegex/g;
	MM::TRACE("try capture tag frames by '$sTagFrameCaptureRegex' from '$sTargetStr'");
	$sDump = Dumper(@asAllTagFrames);
	MM::TRACE_BAG($sDump, "tag frames");
	MM::TRACE("try capture tag cores by '$sTagCoreCaptureRegex' from '$sTargetStr'");
	$sDump = Dumper(@asAllTagCores);
	MM::TRACE_BAG($sDump,"tag cores");
	my $nCoresCnt = @asAllTagCores;
	my $nFramesCnt = @asAllTagFrames;
	if ($nFramesCnt == 0) {
		MM::TRACE("string '$sTargetStr' did not contain any tag frames by '$sTagFrameCaptureRegex'");
	} elsif ( $nFramesCnt != $nCoresCnt) {
		MM::TRACE("string '$sTargetStr': '$nFramesCnt' frames by '$sTagFrameCaptureRegex' but '$nCoresCnt' cores by '$sTagFrameCaptureRegex'")
	} else { # equal amount of frames and cores
		$nItemsCnt = $nFramesCnt;
	}
	MM::TRACE_RET();
	return $nItemsCnt, \@asAllTagFrames, \@asAllTagCores;
}

#==============================================================
sub escapeTagFrame { my ($sStr) = @_; 
#==============================================================
	# - modifies string so, that it can be better used for further substitutions
	$sStr =~  s/\[/\\[/g;
	$sStr =~  s/\%/\\%/g;
	$sStr =~  s/\]/\\]/g;
	return $sStr;
}

#==============================================================
sub removePossibleEscapesEtc { my ($rasLines) = @_;
#==============================================================
	my @asLines;
	my $sLine;
	TRACE_SUB();
	foreach $sLine (@$rasLines) {
		$sLine =~ s/\\"/\"/g;
		push(@asLines, $sLine);
	}
	TRACE_RET();
	return \@asLines;
}
#==============================================================
sub trimThrough { my ($s)=@_;
#==============================================================
	# - removes all leading and trailing spaces
	# - converts remaining multiple spaces to single spaces
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	$s =~ s/\s+/ /g;
	$s =~ s/\R/ /g;	 # cr/lf to spaces
	$s =~ s/\$VAR\d+\s\=//g; 
	return $s;
}
#==============================================================
sub trimRims {
#==============================================================
	# - removes all leading and trailing spaces
	my ($s)=@_;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	return $s;
}
#==============================================================
sub sym { my ($sSym)=@_;
#==============================================================
	

	#TRACE_SUB();
	#$sSym= asc($s);
	$sSym =~ s/\W/_/g;
	$sSym =~ s/^\d/_/g;
	if ($sSym eq "") {
		$sSym="EMPTY";
	#	TRACE("Error: symbol name is $sSym");
	}
	#TRACE("'$s' is converted to '$sSym'");
	#TRACE_RET();
	return $sSym;
}
#-----------------------------------------------------------------------
sub str { my ($s)=@_;
	
	#$s= asc($s);
	$s=~ s/\\/\\\\\\\\/;
	if ($s eq "") {
		$s="EMPTY";
		TRACE("Error: label is $s");
		return $s;
	}
	return $s;
}
#-----------------------------------------------------------------------
sub lbl  { my ($sLbl)=@_;
    #my($s) = @_;
	#my $sLbl;
	#TRACE_SUB();
    ###$sLbl= asc($s);
	#$sLbl= $s;
	#TRACE("labellable string before modifications: '$sLbl'");
	$sLbl =~ s/\\/\\\\\\\\/g;
	#TRACE("labellable string after possible backslashes added printable: '$sLbl'");
	$sLbl =~ s/\\\\\\\\/\\\\\\\\ /g; # spaces added to make split candidate positions
	$sLbl =~ s/\//\/ /g;
	$sLbl =~ s/_/\_ /g;
	$sLbl =~ s/\"/ /g;
    #TRACE("labellable string after cutting spaces adding: '$sLbl'");
	if ($sLbl eq "") {
		$sLbl ="EMPTY";
		#TRACE("Error: label is $sLbl");
		return $sLbl;
	}
    my @Parts = split(/\s+/, $sLbl);
	my $maxPartLen = 32;
    my $ResultStr = "";
    my $NextStepPos = $maxPartLen;
    foreach (@Parts) {
        $ResultStr = $ResultStr." ".$_;
        my $TotalLen = length($ResultStr);
        
        if ($TotalLen > $NextStepPos) {
            $ResultStr      = $ResultStr.'\\\\n';
            $TotalLen       = length($ResultStr);
            $NextStepPos    = $TotalLen + $maxPartLen;
        }
    }
    #TRACE("labelled string before removing cutting spaces '$ResultStr'");
    $ResultStr =~ s/\\\\ /\\\\/g;  # to return non-splitted positions to original
	$ResultStr =~ s/\\n /\\n/g;  # to return non-splitted positions to original
	$ResultStr =~ s/\/ /\//g;
	$ResultStr =~ s/_ /\_/g;
	#TRACE("string '$s' labelled to '$ResultStr'");
	#TRACE_RET();
   	return $ResultStr;
}
#==============================================================
sub isExistingFileName { my ($sFileFullName) = @_;
#==============================================================
	my $bStatus;
	if ( -e $sFileFullName) {
		$bStatus = 1;
	} else {
		$bStatus = 0;
		TRACE_SUB();
		TRACE("'$sFileFullName' is NOT existing file name");
		TRACE_RET();
	}
}
#==============================================================
sub assureFullFileName { my ($sPossiblyPathlessFileName, $sPath) = @_;
#==============================================================
	my $sFullFileName;
	TRACE_SUB();
	my $sFileName = $sPossiblyPathlessFileName;
	if ($sFileName=~ /^s*\w\:/g) {
		$sFullFileName =  $sFileName;
		TRACE("file name '$sFileName' contains already full path");
	} else {
		#TRACE("file name is combination of '$m_sAppPath' and '$sFileName'");
		$sFullFileName =$sPath.$sFileName;
	}
	$sFullFileName =~ s/\\+/\//;  # possible backward slashes to forward slashes for more robust file openings
	if ( -e $sFullFileName) {
		
	} else {
		TRACE("file '$sFullFileName' does not exist");
	}
	TRACE_RET();
	return ($sFullFileName);
}
#==============================================================
sub getDataByType { my ($xAnything) = @_;
#==============================================================
	#    http://perldoc.perl.org/functions/ref.html
	# assures non-hexadecimal string for trace log purposes
	my $sAnythingAsStr = ""; # initial quess 
	my $sDataType = "UNKNOWN"; # initial quess
	#TRACE_SUB();
	if ($xAnything eq "") {
		
	}  else {
		unless (ref($xAnything)) {
			if (MM::isValidJson($xAnything)) {
				$sDataType 	= "JSON";   # not any reference
			} else {
				$sDataType 	= "VALUE";   # not any reference
			}
			$sAnythingAsStr = $xAnything;
		} else {
			$sDataType = ref ($xAnything);
			if ($sDataType eq "ARRAY") {
				$sAnythingAsStr = Dumper(@{$xAnything});
				$sAnythingAsStr =~ s/\n/ /g;  # trimmed to a single line
			} elsif ($sDataType eq "HASH") {
				$sAnythingAsStr = Dumper(%{$xAnything});
				$sAnythingAsStr =~ s/\n/ /g;   # trimmed to a single line
			} else {		
				$sAnythingAsStr = $xAnything;
			}
		}
	}
	#TRACE_RET();
	$sAnythingAsStr = trimThrough($sAnythingAsStr);
	return ($sAnythingAsStr, $sDataType);
}
1;
=comment




=cut