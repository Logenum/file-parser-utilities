
#------------------------------------------------------------------------
# $Id: notetools.pm,v 1.43 2007/05/13 13:31:13 EJL Exp EJL $
#------------------------------------------------------------------------


package OWN::notetools;

use vars qw($VERSION @ISA @EXPORT $PERL_SINGLE_QUOTE);
$VERSION = "3.21";

require 5.000;

use Exporter;

@ISA = qw(Exporter);

@EXPORT = qw(	initDebugLog
                resetDebugLog
				enableDebugLog
				disableDebugLog
				debugLog
				debugLogPos
				debugLogLineNbr
				debugLogNtb
				debugForNtb
                debugAddNtbOutlineFileStart
				openReadFile
				popOpenReadFile
				popOpenReadFileFL
				openWriteFile
				openAppendFile
				popOpenWriteFile
                popOpenAppendFile
				popOpenWriteFileFL
				getDateTimeAsNotetabFormat
				getDateAsShortFormat
				splitWholeFileName
                splitStrBySeparatorList
                getStrByFileLines
				getStrByKeyStr
				getKeyStrByStr
				FileReadLine
				FilePeekLine
				FileGetTypeByExtension
				FileAppendWithTimeStamp
				NotetabAddFileToFile
				NotetabFileListToQueryClip
				NotetabPathlessFileListToQueryClip
				NotetabInterpretLine
				DotOutputInit
                DotStayEdgeToTargetOutput
                DotStepEdgeToTargetOutput
                DotStickerNodeOutput
				DotSetNodeForm
				DotSetEdgeForm
                DotShortSourceOutput
				DotSourceOutput
				DotTargetOutput
				DotEdgeOutput
                DotFullyLabeledEdgeOutput
                DotExactOutput
				DotComment
                DotClusterNodeEdgeToSingleLineOutput
                LineGetStartColumn
                LineGetAlphanumericStartColumn
                LineCheckIfComment
                GraphCheckIfEdgeLine
                GraphTagCheckIfItemLine
                GraphTagCheckIfNodeAttributeLine
                GraphTagCheckIfEdgeLine
                GraphTagGetWithLineTrim
                GraphTagCheck_J_S_E_T_J
				doValidDotSymbolName
				doValidDotLabelText
				getDotEdgeTypeByVttArrow
				VttGetWholeSymbolText
                VttGetTrimSymbolText
				VttGetSymbolTextLine
				VttGetArrowData
				DosNameToString
				DecStrToVal
				DecStrToBinStr
                StrSplitToWordsByMaxLen
                StrSplitByLineFeeds
                findFirstClangReservedWord);

my $TRUE=1;
my $FALSE=0;
my $SavedNtbFocusHeading;
my $SavedPreviousLine;
my $MY_DOT_OUT_FILE;
my $DebugPrevDotNodeName;    # for internal usage of script logs
my $PrevDotNodeLabel;
my $PrevDotNodeName;
my $PrevDotSourceNodeName;
my $VttSymbolDefaultText = "Text";
my $LogLineIndentColPos = 0;    
my $INDENT_INC_LEN = 4;         # text indention increment size

my @a_CLangReservedWords=
	("auto","break","case","char","continue","default","do","double","else","extern","float","for",
	 "goto","if","int","long","register","return","short","sizeof","static","struct","switch","typedef",
	 "union","unsigned","while");

#===================================================================
########## debug log functions ###########################
#===================================================================
sub initDebugLog
{
	my($RawDebugFile,$Status) = @_;

	$LibFile = __FILE__;
	$DebugFile = $RawDebugFile;
	#$DebugFile = ~s/\\/\//g;  # note: does corrupt name !!!?
	$mod_DebugFile = $DebugFile; 	# note: also backward slashes are valid in perl path names !!!
	open(DEBUG_LOG, ">>$mod_DebugFile"); 	# note: saved at module level ("my" has only {...} -scope)
	# debug log initialization opening is of type APPEND !!!!!!!!!!!!
	# - allows also caller Clip/bat loggings into same debug log file
	#print DEBUG_LOG "Parameter line: @_\n";
	#print DEBUG_LOG "Raw debug log file: $RawDebugFile\n";
	#print DEBUG_LOG "debug log file: $DebugFile\n";
	#print DEBUG_LOG "debug log file: $mod_DebugFile\n";
	#print DEBUG_LOG "debug log functions: \[$LibFile\] \n";
	close DEBUG_LOG;
}
#========================================================================
sub resetDebugLog
{
    # for clearing debug log file to make new start-up
	open(DEBUG_LOG, ">$mod_DebugFile"); 	# note: saved at module level ("my" has only {...} -scope)
	close DEBUG_LOG;
}
#========================================================================
sub enableDebugLog
{
	$mod_DebugLogAccessStatus = 1;
}
#========================================================================
sub disableDebugLog
{
	$mod_DebugLogAccessStatus = 0;
}
#========================================================================
sub debugLog
{
	my($Text) = @_;
	if ($mod_DebugLogAccessStatus == 0) {return; }# jump to function end
	#$Text = ~s/\//\\/g;
	open(DEBUG_LOG, ">>$mod_DebugFile") || die "Cannot open file";
	print DEBUG_LOG "$Text\n";
	#print DEBUG_LOG "Handle = *DEBUG_LOG\n";
	close DEBUG_LOG;
}
#========================================================================
sub debugLogPos
{
	my($FileName,$LineNbr,$Comment) = @_;
	if ($mod_DebugLogAccessStatus == 0) {return; }# jump to function end
	open(DEBUG_LOG, ">>$mod_DebugFile") || die "Cannot open file";
	print DEBUG_LOG "$Comment  (POS: $FileName - $LineNbr)\n";
	close DEBUG_LOG;
}
#========================================================================
sub debugLogLineNbr
{
	my($LineNbr,$Comment) = @_;
	if ($mod_DebugLogAccessStatus == 0) {return; }# jump to function end
	open(DEBUG_LOG, ">>$mod_DebugFile") || die "Cannot open file";
	print DEBUG_LOG "($LineNbr) $Comment\n";
	close DEBUG_LOG;
}
#========================================================================
sub debugLogNtb
{
	my($WholeFileName,$LineNbr,$Comment) = @_;
	if ($mod_DebugLogAccessStatus == 0) {return; }# jump to function end
	open(DEBUG_LOG, ">>$mod_DebugFile") || die "Cannot open file";
	disableDebugLog();
	if ($WholeFileName eq __FILE__)
	{
		# library file and log file are in different directories
		$File = $WholeFileName;
		$File=~s/\//\\/g;
	}
	else
	{
		# script file and log file are in same directory, so path is not needed
		($Path,$File) = splitWholeFileName($WholeFileName);
	}
	enableDebugLog();
    
    if ($Comment =~ m{.*BEGIN:(.*)})
    {
        $IndentStr = " " x $LogLineIndentColPos;
        $LogLineIndentColPos += $INDENT_INC_LEN;
        $CommentEnd= $1;
    }
    elsif ($Comment =~ m{.*END:(.*)})
    {
        if ($LogLineIndentColPos >= $INDENT_INC_LEN)
        {
            $LogLineIndentColPos -= $INDENT_INC_LEN;
        }
        $CommentEnd= $1;
        $IndentStr = " " x $LogLineIndentColPos;
    }
    else
    {
         $IndentStr = " " x $LogLineIndentColPos;
    }
    
    $LogLine = $IndentStr.$Comment;
    
    $LogTextEndPos = length($LogLine);
    $FillerStr = " " x (60-$LogTextEndPos);
	print DEBUG_LOG "$LogLine$FillerStr // [$File\:\:$LineNbr\^L]\n";
	close DEBUG_LOG;
}
#========================================================================
sub debugForNtb
{
	my($Comment,$WholeFileName,$LineNbr) = @_;
	debugLogNtb($WholeFileName,$LineNbr,$Comment);
}
#========================================================================
sub debugAddNtbOutlineFileStart
{
	if ($mod_DebugLogAccessStatus == 0) {return; } # jump to function end
	open(DEBUG_LOG, ">>$mod_DebugFile") || die "Cannot open file";
	print DEBUG_LOG "= V4 Outline MultiLine NoSorting TabWidth=30\n\n";
    print DEBUG_LOG "H=\"LOG TOPIC\"\n\n";
	close DEBUG_LOG;
}
#========================================================================



#===================================================================
######### General functions ########################################
#===================================================================


sub openReadFile
{
	my($Name,$CallerFile,$CallLine) = @_;
	$PeekSaved = $FALSE;
	my $SOME_FILE; # note: variable capsulated in a function
	$Name=~s/\\/\//g;
	chomp $Name;
	debugForNtb("try open read file: $Name",$CallerFile,$CallLine);
	open($SOME_FILE, "<$Name") || debugForNtb("Cannot open input file $Name",$CallerFile,$CallLine);


	return $SOME_FILE; # note: return capsulated value
}
#-----------------------------------------------------------
sub openWriteFile
{
	my($Name,$CallerFile,$CallLine) = @_;
	my $SOME_FILE;
	$Name=~s/\\/\//g;
	chomp $Name;
	debugForNtb("try open write file: $Name",$CallerFile,$CallLine);
	open($SOME_FILE, ">$Name") || debugForNtb("Cannot open output file $Name",$CallerFile,$CallLine);
	
	return $SOME_FILE;
}
#========================================================================
sub openAppendFile
{
	my($Name,$CallerFile,$CallLine) = @_;
	my $SOME_FILE;
	$Name=~s/\\/\//g;
	debugForNtb("try open append file: $Name",$CallerFile,$CallLine);
	open($SOME_FILE, ">>$Name") || debugForNtb("Cannot open append file $Name",$CallerFile,$CallLine);
	chomp $Name;
	###debugLog("Append file $Name opened, handle: $SOME_FILE");

	return $SOME_FILE;
}


sub popOpenReadFile
{
	# Calling:  popOpenReadFile(*CONFIGURATION_FILE);
	my($MY_CONF_FILE) = @_;
	my $DATA_FILE;
	$FileName=<$MY_CONF_FILE>;
	$FileName=~s/\\/\//g;
	chomp($FileName);
	debugForNtb("try pop-open read file: $FileName",__FILE__,__LINE__);
	open($DATA_FILE, "<$FileName") || debugForNtb("Cannot pop open input file $FileName",__FILE__,__LINE__);

	return $DATA_FILE, $FileName;
}

sub popOpenReadFileFL
{
	# Calling:  popOpenReadFile(*CONFIGURATION_FILE);
	my($MY_CONF_FILE,$CallerFile,$CallLine) = @_;
	my $DATA_FILE;
	$FileName=<$MY_CONF_FILE>;
	$FileName=~s/\\/\//g;
	chomp($FileName);
	debugForNtb("try pop-open read file: $FileName",$CallerFile,$CallLine);
	open($DATA_FILE, "<$FileName") || debugForNtb("Cannot pop open input file $FileName",$CallerFile,$CallLine);

	return $DATA_FILE;
}
sub popOpenWriteFile
{
	my($MY_CONF_FILE) = @_;
	my $DATA_FILE;
	$FileName=<$MY_CONF_FILE>;
	$FileName=~s/\\/\//g;
	chomp($FileName);
	debugForNtb("try pop-open write file: $FileName",__FILE__,__LINE__);

	open($DATA_FILE, ">$FileName") || debugForNtb("Cannot pop open output file $FileName",__FILE__,__LINE__);

	return $DATA_FILE;
}
sub popOpenAppendFile
{
	my($MY_CONF_FILE) = @_;
	my $DATA_FILE;
	$FileName=<$MY_CONF_FILE>;
	$FileName=~s/\\/\//g;
	chomp($FileName);
	debugForNtb("try pop-open append file: $FileName",__FILE__,__LINE__);

	open($DATA_FILE, ">>$FileName") || debugForNtb("Cannot pop open output file $FileName",__FILE__,__LINE__);

	return $DATA_FILE;
}
sub popOpenWriteFileFL
{
	my($MY_CONF_FILE,$CallerFile,$CallLine) = @_;
	my $DATA_FILE;
	$FileName=<$MY_CONF_FILE>;
	$FileName=~s/\\/\//g;
	chomp($FileName);
	debugForNtb("try pop-open write file: $FileName",$CallerFile,$CallLine);

	open($DATA_FILE, ">$FileName") || debugForNtb("Cannot pop open output file $FileName",$CallerFile,$CallLine);

	return $DATA_FILE;
}

#====================================================
sub splitWholeFileName
#----------------------------------------------------
{
	my($WholeFileName) = @_;
	disableDebugLog();
	debugLog("===== start script 'splitWholeFileName' {");
	if (($PathName,$FileName) = ($WholeFileName =~ /(.*\\)(.*)$/ig))
	{
		debugLog("'$WholeFileName' split to '$PathName' and '$FileName'");
	}
	else
	{
		$PathName = "NO_PATH_NAME";
		$FileName = $WholeFileName;
		debugLog("no path part; '$WholeFileName' may be a plain file name");
	}
	debugLog("===== end script 'splitWholeFileName' }");
	enableDebugLog();
	return $PathName, $FileName;
}

#====================================================
sub splitStrBySeparatorList
#   Reads through string char by char
#   When separator is found, collected chars set
#   and separator are saved as array items
#   Finally whole array is returned
#----------------------------------------------------
{
   # TODO: 2006-04-04
   # my($String, $Separators) = @_;
    #{
     
    
    
    #}
    #return @SplitArray;
}

#=====================================================
sub getStrByFileLines
#   Reads given file lines and returns single string
#   - LF characters are replaced by given delimiter
#----------------------------------------------------
{
   # TODO: 2006-04-16
   # my($WholeListFileName, $Separator) = @_;
   #$STR_MAP_FILE 			= openReadFile($StrMapFile);
    #{
     
    
    
    #}
    #return $FileNames;
}

#====================================================
sub getStrByKeyStr
# searches right-side (=TARGET) string, when left-side string (=KEY) is given
#----------------------------------------------------
{
	my($StrMapFile,$KeyStr) = @_;

	$KeyStr =~ tr/a-z/A-Z/; # note: convert to upper case

	debugLog("===== start script 'getStrByKeyStr' {");
	disableDebugLog();

	#debugLog("try find key string '$KeyStr' in map file '$StrMapFile'");
	$STR_MAP_FILE 				= openReadFile($StrMapFile);
	$FIELD_DELIMITER 			= ";";
	$MapFound 				= $FALSE;		# initial quess: nothing will be found
	$LineCount 				= 0;

	while (<$STR_MAP_FILE>)
	{
		if (($FileKeyStr,$Waste,$TargetStr) = /(.*)($FIELD_DELIMITER)(.*)/ig)
		{
			$FileKeyStr =~ tr/a-z/A-Z/; # note: convert to upper case

			if ($FileKeyStr eq $KeyStr)
			{
				debugLog("Map found: '$KeyStr' ---> '$TargetStr'");
				$MapFound = $TRUE;
				last;	# note: break out from while -loop
			}
			else
			{
				debugLog("'$FileKeyStr' NO match with '$KeyStr'");
			}
		}
		else
		{
			debugLog("Valid map not found at line ($LineCount) '$_'");
		}
		$LineCount++;
	}
	if ($MapFound == $FALSE)
	{
		debugLog("script 'getStrByKeyStr': target string NOT found, so set it equal to key '$KeyStr'");
		$TargetStr = $KeyStr;
	}
	else
	{
		debugLog("Found target '$TargetStr' for key '$KeyStr'");
	}


	close $STR_MAP_FILE;

	enableDebugLog();
	debugLog("===== end script 'getStrByKeyStr' }");
	return $TargetStr;
}


#====================================================
sub getKeyStrByStr
# searches left-side (=KEY) string, when right-side string (=TARGET) is given
#----------------------------------------------------
{
	my($StrMapFile,$FindTargetStr) = @_;

	$FindTargetStr =~ tr/a-z/A-Z/; # note: convert to upper case

	debugLog("BEGIN script: getKeyStrByStr('$StrMapFile','$FindTargetStr') {");
	disableDebugLog();
	$STR_MAP_FILE 				= openReadFile($StrMapFile);
	$FIELD_DELIMITER 			= ";";
	$MapFound 				= $FALSE;		# initial quess: nothing will be found
	$LineCount 				= 0;

	while (<$STR_MAP_FILE>)
	{
		if (($KeyStr,$Waste,$TargetStr) = /(.*)($FIELD_DELIMITER)(.*)/ig)
		{

			$TargetStr =~ tr/a-z/A-Z/; # note: convert to upper case
			if ($FindTargetStr eq $TargetStr)
			{
				debugLog("Map found: '$KeyStr' <--- '$TargetStr'");
				$MapFound = $TRUE;
				last;	# note: break out from while -loop
			}
			else
			{
				#debugLog("'$TargetStr' NO match with '$FindTargetStr'");
			}
		}
		else
		{
			debugLog("Valid map not found at line ($LineCount) '$_'");
		}
		$LineCount++;
	}
	if ($MapFound == $FALSE)
	{
        enableDebugLog();
		debugLog("key string NOT found, so set it equal to target string '$FindTargetStr'");
		$KeyStr = $FindTargetStr;
	}
	else
	{   
        enableDebugLog();
		debugLog("Found key '$KeyStr' for target string '$FindTargetStr'");
	}
	close $STR_MAP_FILE;
	#enableDebugLog();
	debugLog("END script: 'getKeyStrByStr' }");
	return $KeyStr;
}

#====================================================
sub FileReadLine
#----------------------------------------------------
{
	my($READ_FILE) = @_;
	if ($PeekSaved == $FALSE)
	{
		$ReadLine=<$READ_FILE>;
		#chomp $ReadLine;  causes EOF found almost immediately !!!?
		$Line = $ReadLine;
		debugLog("read (from file): '$Line'");
	}
	else
	{
		$Line = $PeekLine;
		$PeekSaved = $FALSE;
		debugLog("read (from save): '$Line'");
	}
	return $Line;
}

#====================================================
sub FilePeekLine
#----------------------------------------------------
{
	my($READ_FILE) = @_;
	if ($PeekSaved == $FALSE)
	{
		$PeekLine=<$READ_FILE>;
		#chomp $PeekLine;  causes EOF found almost immediately !!!?
		$Line = $PeekLine;
		$PeekSaved = $TRUE;
		debugLog("peek (from file): '$Line'");
	}
	else
	{
		$Line = $PeekLine;
		debugLog("peek (from save): '$Line'");
	}
	return $Line;
}

#====================================================
sub FileGetTypeByExtension
#----------------------------------------------------
{
	my($FileName) = @_;

	debugLog("===== start script 'FileGetTypeByExtension' {");

	if ($FileName =~ /\.doc/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_MS_WORD";
	}
	elsif($FileName =~ /\.xls/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_MS_EXCEL";
	}
	elsif($FileName =~ /\.jpg/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_WWW_BROWSER";
	}
	elsif($FileName =~ /\.png/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_WWW_BROWSER";
	}
	elsif($FileName =~ /\.ppt/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_WWW_BROWSER";
	}
	elsif($FileName =~ /\.pdf/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_WWW_BROWSER";
	}
	elsif($FileName =~ /\.vtt/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_VISUAL_THOUGHT";
	}
    elsif($FileName =~ /\.vthought/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_VISUAL_THOUGHT";
	}
	elsif($FileName =~ /\.exe/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_DOS_EXE";
	}
	elsif($FileName =~ /\.pl|\.pm/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_SYNTAX_EDITOR";
	}
	elsif($FileName =~ /\.bat/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_DOS_BAT";
	}
	elsif($FileName =~ /\.cpp/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_CPP_SOURCE";
	}
	elsif($FileName =~ /\.hpp/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_CPP_INCLUDE";
	}
	elsif($FileName =~ /\.c/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_C_SOURCE";
	}
	elsif($FileName =~ /\.h/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_INCLUDE";
	}
	elsif($FileName =~ /\.p51/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_PLM_SOURCE";
	}
	elsif($FileName =~ /\.mm/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_FREE_MIND";
	}
    elsif($FileName =~ /\.gan/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_GANTT_PROJECT";
	}
    elsif($FileName =~ /\.ins/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_INSPIRATION";
	}
	elsif($FileName =~ /\.py/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_USE_SYNTAX_EDITOR";
	}
    elsif($FileName =~ /\.rtf/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_RICH_TEXT"; 
	}
    elsif($FileName =~ /\.dot/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_ATT_DOT"; 
	}
    elsif($FileName =~ /\.SLDPRT/gi)
	{
		$FILE_TYPE = "FILE_TYPE_IS_SOLID_WORKS"; 
	}
	else
	{
		$FILE_TYPE = "FILE_TYPE_IS_UNKNOWN";
	}
	debugLog("file $FileName is of type '$FILE_TYPE'");
	debugLog("===== end script 'FileGetTypeByExtension' }");
	return $FILE_TYPE;
}



#====================================================
sub FileAppendWithTimeStamp
#----------------------------------------------------
{
	my($TargetFileName,$AddFileName) = @_;

	$CurrentDateTime = getDateTimeAsNotetabFormat();
	$TARGET_FILE = openAppendFile($TargetFileName);
	$ADD_FILE = openReadFile($AddFileName);
	debugLog("append file '$AddFileName' to the end of file '$TargetFileName'");
	print $TARGET_FILE "\n_________________________________________\n"; # delimiter (40 underscores)
	print $TARGET_FILE $CurrentDateTime."\n";

	while (<$ADD_FILE>)
	{
		print $TARGET_FILE $_;
	}

	close $ADD_FILE;
	close $TARGET_FILE;
}
#===================================================================
######### Notetab functions ########################################
#===================================================================

#-------------------------------
sub getDateTimeAsNotetabFormat
#-------------------------------
{
	@RawDateTime = localtime(time);	# note: these are built-in functions

	$yy = $RawDateTime[5] - 100;  		# year since 1900
	if ($yy <= 9) {$yy = "0"."$yy";}

	$mm = $RawDateTime[4] + 1;			# January is ZERO
	if ($mm <= 9) {$mm = "0"."$mm";}

	$dd = $RawDateTime[3];
	if ($dd <= 9) {$dd = "0"."$dd";}

	$hh = $RawDateTime[2];
	if ($hh <= 9) {$hh = "0"."$hh";}

	$nn = $RawDateTime[1];
	if ($nn <= 9) {$nn = "0"."$nn";}

	$ss = $RawDateTime[0];
	if ($ss <= 9) {$ss = "0"."$ss";}

	$DateTime = "($yy$mm$dd-$hh$nn$ss)";

	return $DateTime;
}

#-------------------------------
sub getDateAsShortFormat
#-------------------------------
{
	@RawDate = localtime(time);	# note: these are built-in functions

	$yy = $RawDate[5] - 100;  		# year since 1900
	if ($yy <= 9) {$yy = "0"."$yy";}

	$mm = $RawDate[4] + 1;			# January is ZERO
	if ($mm <= 9) {$mm = "0"."$mm";}

	$dd = $RawDate[3];
	if ($dd <= 9) {$dd = "0"."$dd";}

	$Date = "$yy$mm$dd";

	return $Date;
}

#-------------------------------
sub NotetabAddFileToFile
#-------------------------------
{
	my($ResultFile, $WorkFile, $AddTextFile, $HeadingsFile) = @_;

	$TRUE	=1;
	$FALSE	=0;
	$HeadingPartSeparator = "#";
	#--- read CALL parameters

	$RESULT_FILE 	= openReadFile($ResultFile); 	# note: file handle as function return value
	$WORK_FILE 		= openWriteFile($WorkFile); 	# note: file handle as function return value
	$ADD_TEXT_FILE 	= openReadFile($AddTextFile); 	# note: file handle as function return value

	if ($HeadingsFile ne "EMPTY_PARAMETER")   # note: string comparison: "not equal"
	{
		$HEADING_STRUCTURE_FILE 		= openReadFile($HeadingsFile); 	# note: file handle as function return value
		@HeadingHierarchy 				= <$HEADINGS_FILE>;
		$HeadingStructureNavigation 	= $TRUE;
	}
	else
	{   # text shall be added to the end of file result file
		debugLog("heading structure file does not exist");
		$HeadingStructureNavigation = $FALSE;
	}


	if ($HeadingStructureNavigation == $TRUE)
	{
		# TODO: add text insertion below given heading (heading is created, if necessary)
	}
	else
	{ # no heading structure given: just add file to the end of file
		while (<$RESULT_FILE>)
		{ # copies final target file contents to temporary work file
			chomp;
			print $WORK_FILE "$_\n";
		}
		$TimeStamp = getDateTimeAsNotetabFormat();

		# adding new stuff to the end of temporary work file
		print $WORK_FILE "---------------------------------------\n";
		print $WORK_FILE "$TimeStamp\n";
		while (<$ADD_TEXT_FILE>)
		{
			chomp;
			print $WORK_FILE "$_\n";
		}
	}

	if ($HeadingsFile ne "")   # note: string comparison: "not equal"
	{
		close $HEADING_STRUCTURE_FILE;
	}
	else
	{
		debugLog("heading structure file was not opened, so it is not closed either");
	}
	close $ADD_TEXT_FILE;
	close $WORK_FILE;
	close $RESULT_FILE;

	$BackupFile = $ResultFile.$TimeStamp."bup"; # note: string concatenation

	rename $ResultFile, $BackupFile; 			# note: file renaming (creates backup)
	rename $WorkFile, $ResultFile; 			# note: renames work file to result file
}
#-------------------------------------------
sub NotetabFileListToQueryClip
#-------------------------------------------
# converts an array of file names to a Notetab CLIP selection list
# output example: %File%=^?{File="FILE1"|"FILE2"|"FILE3"}
#-------------------------------------------
{
	my($QueryComment, @FileList) = @_;
	debugLogPos(__FILE__, __LINE__,"function started");

	debugLog("query comment: $QueryComment");
	$ClipLine = "\^\?\{(T=L)$QueryComment="; # note: Notetab multi-line selection listbox
	$LastFilePos = $#FileList;   # note: array size

	for ($i=0; $i < $LastFilePos; $i++)
	{
		$FileName = $FileList[$i];
		chomp $FileName;
		debugLog("array file $i/$LastFilePos: $FileName");

		$ClipLine = $ClipLine."$FileName|";
	}

	$FileName = $FileList[$LastFilePos];
	chomp $FileName;
	debugLog("array file $LastFilePos/$LastFilePos: $FileName");
	$ClipLine = $ClipLine."$FileName}";

	return $ClipLine;

}

#-------------------------------------------
sub NotetabPathlessFileListToQueryClip
#-------------------------------------------
# converts an array of file names to a Notetab CLIP selection list
# output example: %File%=^?{File="FILE1"|"FILE2"|"FILE3"}
# All file names are supposed to exist in same directory
# 	because only one path name is returned
#-------------------------------------------
{
	$FocusFileNameDefaultConst = "_Focus File";
	my($QueryComment, @FileList) = @_;
	debugLogPos(__FILE__, __LINE__,"function started");

	debugLog("query comment: $QueryComment");

	$LastFilePos = $#FileList;   # note: array size
	# TODO: add insertion of "_Focus file" -alike string as first item of list
	#$ClipLine = "\^\?\{$QueryComment=";

	for ($i=0; $i < $LastFilePos; $i++)
	{
		$WholeFileName = $FileList[$i];
		chomp $WholeFileName;
		($PathName,$FileName) = splitWholeFileName($WholeFileName);

		debugLog("array file $i/$LastFilePos: $FileName");
		debugLog("array path $i/$LastFilePos: $PathName");

		$ClipLine = $ClipLine."$FileName|";
	}
	$ClipLine = "$FocusFileNameDefaultConst|$ClipLine";

	# unshift @FileList,$FocusFileNameDefaultConst;  # note: pushing item to array start
	;debugLog("first array in item: $FileList[0]");
	$WholeFileName = $FileList[$LastFilePos];
	chomp $WholeFileName;
	($PathName,$FileName) = splitWholeFileName($WholeFileName);

	debugLog("array file $LastFilePos/$LastFilePos: $FileName");
	debugLog("array path $LastFilePos/$LastFilePos: $PathName");
	$ClipLine = $ClipLine."$FileName}";

	$ClipLineHeading = "\^\?\{(T=L)$QueryComment ($PathName)=";
	$ClipLine = $ClipLineHeading.$ClipLine;

	return $ClipLine, $PathName;

}

#-------------------------------------------
sub NotetabInterpretLine
#-------------------------------------------
# Interprets line contents, to generate:
# -	line type for further actions
# -	parsed strings with specific meaning
#
#-------------------------------------------
{
my($LineContents, $FocusPathFile, $PATH_MAP_FILE) = @_;

$__SCRIPT__ = "NotetabInterpretLine";
$TRUE=1;
$FALSE=0;
$THIS_FILE = __FILE__;

$PATH_FILE_DELIM = "\:"; 	# TODO: move these definitions to Perl library (#)
$FILE_LINK_DELIM = "\'";
$LINK_SUB_DELIM = "\'";
$FILE_TOPIC_DELIM = "\:\:";
$AUTO_LINK_NBR_STR_LEN = 6;
$AUTO_LINK_START_IND="A";
$AUTO_LINK_END_IND="B";
$INITIAL_QUESS_STR="NOT_IN_USE";


#--- read CALL parameters
debugForNtb("#################################################",__FILE__,__LINE__); # 50 characters
debugForNtb("BEGIN script $__SCRIPT__ {",__FILE__,__LINE__);
debugForNtb("=================================================",__FILE__,__LINE__); # 50 characters
chomp $FocusPathFile;

($FocusPath,$FocusFile) = splitWholeFileName($FocusPathFile);

debugForNtb("script   INPUT: focus file     '$FocusPathFile'",__FILE__,__LINE__);
debugForNtb("script   INPUT: selection      '$LineContents'",__FILE__,__LINE__);
debugForNtb("script   INPUT: path map file  '$PATH_MAP_FILE'",__FILE__,__LINE__);
debugForNtb("-------------------------------------------------",__FILE__,__LINE__); # 50 characters
debugForNtb("focus path:'$FocusPath'",__FILE__,__LINE__);
debugForNtb("focus file:'$FocusFile'",__FILE__,__LINE__);


$FocusHeading	="NOT_IN_USE"; # initial quess
$FocusSubheading ="NOT_IN_USE"; # initial quess

$SelLineType	="NOT_IN_USE"; # initial quess
$SelFileType	="NOT_IN_USE"; # initial quess
$SelPath		="NOT_IN_USE"; # initial quess
$SelFile		="NOT_IN_USE"; # initial quess
$SelLink		="NOT_IN_USE"; # initial quess
$SelSublink		="NOT_IN_USE"; # initial quess
$SelLinkType	="NOT_IN_USE"; # initial quess
$ModSelLink		="NOT_IN_USE"; # initial quess
$LinkComment    ="NOT_IN_USE"; # initial quess

$PathMap		="NOT_IN_USE"; # initial quess
$FileMap		="NOT_IN_USE"; # initial quess
$LinkMap		="NOT_IN_USE"; # initial quess
$ModifiedLinkMap="NOT_IN_USE"; # initial quess
$SublinkMap     ="NOT_IN_USE"; # initial quess

chomp $LineContents;
$_ = $LineContents;

$Via01=0;
$Via02=0;
$Via03=0;

$BracketedLinkFound = $TRUE;		# initial quess


	debugForNtb("==========================",__FILE__,__LINE__);
	debugForNtb("interpret line '$_'",__FILE__,__LINE__);
	debugForNtb("--------------------------",__FILE__,__LINE__);
	
    $FocusFileType		  = FileGetTypeByExtension($FocusPathFile);
    # - for sure, if nothing else matches
    
	if (($W0,$W1,$W2) = /(.*)(V4 Outline MultiLine NoSorting)(.*)/ig)
	{
		$SelLineType 	= "NTB_LINE_TYPE_FIRST_LINE";
		debugForNtb("Notetab outline first line found in file '$FocusFile'",__FILE__,__LINE__);
		$Via01=__LINE__;
		$BracketedLinkFound = $FALSE;
	}
	elsif (($W0,$Heading,$W1) = /(H=\")(.{3,})(\")/ig)
	{

		debugForNtb("new heading '$Heading' saved to replace '$SavedNtbFocusHeading' (file: '$FocusFile')",__FILE__,__LINE__);
		$SavedNtbFocusHeading 	= $Heading;

		# - when Notetab topic heading is found, it is saved in library-level static variable
		$SelLineType 			= "NTB_LINE_TYPE_IS_TOPIC_HEADING";

		$BracketedLinkFound 	= $FALSE;
		$Via01=__LINE__;
	}
	elsif (/¯¯/g)
	{
		$FocusSubheading = $SavedPreviousLine;
		debugForNtb("Notetab subheading '$FocusSubheading found",__FILE__,__LINE__);
	}
	elsif (($W0,$RawPathMap,$W1,$RawFileMap,$W2,$RawLinkMap,$W3,$RawSublinkMap,$W4) =
		/(\[)(.{3,})($PATH_FILE_DELIM)(.{3,})($FILE_LINK_DELIM)(.{3,})($LINK_SUB_DELIM)(.{3,})(\])/ig)
	{
		$FocusHeading = $SavedNtbFocusHeading;
		$PathMap 	= $RawPathMap;
		$FileMap 	= $RawFileMap;
		$LinkMap 	= $RawLinkMap;
		$SublinkMap = $RawSublinkMap;

		$SelLineType = "NTB_LINE_TYPE_IS_PFLS";
		$Via01=__LINE__;
	}
	elsif (($W0,$RawPathMap,$W1,$RawFileMap,$W2,$RawLinkMap,$W3) =
		/(\[)(.{3,})($PATH_FILE_DELIM)(.{3,})($FILE_LINK_DELIM)(.{3,})(\])/ig)
	{
		$PathMap 	= $RawPathMap;
		$FileMap 	= $RawFileMap;
		$LinkMap 	= $RawLinkMap;
		$SelLineType = "NTB_LINE_TYPE_IS_PFLx";
		$Via01=__LINE__;
	}
	elsif (($W1,$RawFileMap,$W2,$RawLinkMap,$W3,$RawSublinkMap,$W4) =
		/(\[)(.{3,})($FILE_LINK_DELIM)(.{3,})($LINK_SUB_DELIM)(.{3,})(\])/ig)
	{
		$FileMap 		= $RawFileMap;
		$LinkMap 		= $RawLinkMap;
		$SublinkMap 	= $RawSublinkMap;
		$SelLineType 	= "NTB_LINE_TYPE_IS_xFLS";
		$Via01=__LINE__;
	}
	elsif (($W0,$RawPathMap,$W1) = /(\[)(.{3,})($PATH_FILE_DELIM\])/ig)
	{
		# examples:
		# 	- [PATH123:]
		$PathMap = $RawPathMap;
		$SelLineType = "NTB_LINE_TYPE_IS_Pxxx";
		$Via01=__LINE__;
	}
	elsif (($W1,$FileName,$W2,$TopicName,$W3) =
		/(\[)(.{3,})($FILE_TOPIC_DELIM)(.{3,})(\])/ig)
	{
		$FileMap 	= $FileName;
		$LinkMap 	= $TopicName;
		$SelLineType = "NTB_LINE_TYPE_IS_xFTx";
		# = file+topic
		$Via01=__LINE__;
	}
	elsif (($W0,$RawPathMap,$W1,$RawFileMap,$W2) =
			/(\[)(.{3,})($PATH_FILE_DELIM)(.{3,})(\])/ig)
	{

		$PathMap 		= $RawPathMap;
		$FileMap 		= $RawFileMap;
		$SelPathName 	= getStrByKeyStr($PATH_MAP_FILE,$PathMap);
		$SelFileName 	= getStrByKeyStr($PATH_MAP_FILE,$FileMap);
		$WholeName 		= $SelPathName.$SelFileName;

		$SelFileType		  = FileGetTypeByExtension($WholeName);
		##### $TypeOfFileInFocusStr = FileGetTypeByExtension($WholeName); bug fixed (050913-084453)
		$SelLineType = "NTB_LINE_TYPE_IS_PFxx";
		$Via01=__LINE__;
	}

	elsif (($W1,$RawFileMap,$W2,$RawLinkMap,$W3) =
		/(\[)(.{3,})($FILE_LINK_DELIM)(.{3,})(\])/ig)
	{
		$FileMap 	= $RawFileMap;
		#$FileMap 	= $FocusFile;
		$LinkMap 	= $RawLinkMap;
		$SelLineType = "NTB_LINE_TYPE_IS_xFLx";
		$Via01=__LINE__;
	}
	elsif (($W2,$RawLinkMap,$W3,$RawSublinkMap,$W4) =
		/(\[)(.{3,})($LINK_SUB_DELIM)(.{3,})(\])/ig)
	{
		#$FileMap	= $FocusFile;

		$LinkMap 	= $RawLinkMap;
		$SublinkMap = $RawSublinkMap;
		$SelLineType = "NTB_LINE_TYPE_IS_xxLS";
		$Via01=__LINE__;
	}
	elsif (($W0,$RawLinkMap,$W1) = /(\[$PATH_FILE_DELIM)(.{3,})(\])/ig)
	{
		$LinkMap 	= $RawLinkMap;
		# examples:
		# 	- [:wordfile.doc]
		# 	- [:ntbfile]
		$SelLineType = "NTB_LINE_TYPE_IS_xFxx";
		$Via01=__LINE__;
	}


	elsif (($W0,$RawLinkMap,$W1) = /(\[$FILE_LINK_DELIM)(.{3,})(\])/ig)
	{
		# examples:
		# 	- ['kukkuu]
		$LinkMap = $RawLinkMap;
		$SelLineType = "NTB_LINE_TYPE_IS_xxLx";
		$Via01=__LINE__;
	}
	elsif (($W0,$SomeName,$W1) = /(\[)(.{3,})(\])/ig)
	{
		# examples:
		# 	- [c:\docs\wordfile.doc]
		# 	- [ntbfile]
		#	- [diagram.vtt]

		$SelLineType = "NTB_LINE_TYPE_IS_xFxx";
		($PathName,$FileName) = splitWholeFileName($SomeName);
		$SelFileType = FileGetTypeByExtension($FileName);

		$PathMap 	= 	$PathName;
		$FileMap 	= 	$FileName;
		$Via01=__LINE__;
	}
	else
	{
		$BracketedLinkFound = $FALSE;
        $SelLineType = "NTB_LINE_TYPE_IS_PLAIN_TEXT";
		debugForNtb("line '$LineContents' contents is interpreted to be '$SelLineType'",__FILE__,__LINE__);
	
		($SelPath,$SelFile) = splitWholeFileName($LineContents);
		$SelFileType 		= FileGetTypeByExtension($LineContents);
		$Via01=__LINE__;
        debugForNtb("file name '$SelFile' is interpreted to be '$SelFileType'",__FILE__,__LINE__);
		if ($SelFileType eq "FILE_TYPE_IS_UNKNOWN")
		{
			$Via02=__LINE__;
		}
	}

	#-----------------------------------------------------------------
	if ($BracketedLinkFound == $TRUE)
	{
		$Via03=__LINE__;
		$SelLinkType = "LINK_STR_IS_ORDINARY";   # another initial quess

		if (($W0,$LinkComment) = /(\[.*\])(.{3,})/ig)
		{
			debugForNtb("Comment text found at bracket link line: '$LinkComment'",__FILE__,__LINE__);
		}
		if (($PathName eq "NO_PATH_NAME")||($PathName eq "NOT_IN_USE"))
		{
			debugForNtb("path map is '$PathName', so update it to focus path '$FocusPath'",__FILE__,__LINE__);
			$PathMap = $FocusPath;
		}

		if (($PathMap eq "") || ($PathMap eq "NOT_IN_USE"))
		{
			$PathMap = $FocusPath;
			debugForNtb("path map is '$PathMap', so update it to focus path '$FocusPath'",__FILE__,__LINE__);
		}

		if (($FileMap eq "")||($FileMap eq "NOT_IN_USE"))
		{
			$FileMap = $FocusFile;
			debugForNtb("file map is '$FileMap', so update it to focus file '$FocusFile'",__FILE__,__LINE__);
		}

		if ($LinkMap =~ /$AUTO_LINK_START_IND\d{$AUTO_LINK_NBR_STR_LEN}/)
		{
			#$PathMap 		 = $FocusPath; # auto named link: path is always focus path
			$FocusHeading 	 = $SavedNtbFocusHeading;
			$ModifiedLinkMap = $LinkMap;

			$ModifiedLinkMap =~ s/$AUTO_LINK_START_IND/$AUTO_LINK_END_IND/g;
			debugForNtb("Automatic link name '$LinkMap' found in file '$FocusFile' , so other end is '$ModifiedLinkMap'",__FILE__,__LINE__);
			$SelLinkType = "LINK_STR_IS_AUTO_START";
		}
		elsif ($LinkMap =~ /$AUTO_LINK_END_IND\d{$AUTO_LINK_NBR_STR_LEN}/)
		{
			#$PathMap 		 = $FocusPath; # auto named link: path is always focus path
			$FocusHeading 	 = $SavedNtbFocusHeading;
			$ModifiedLinkMap = $LinkMap;

			$ModifiedLinkMap =~ s/$AUTO_LINK_END_IND/$AUTO_LINK_START_IND/g;
			debugForNtb("Automatic link name '$LinkMap' found in file '$FocusFile', so other end is '$ModifiedLinkMap'",__FILE__,__LINE__);
			$SelLinkType = "LINK_STR_IS_AUTO_END";
		}
		else
		{
			$ModifiedLinkMap = $LinkMap;
			debugForNtb("'$LinkName' is NOT automatic name",__FILE__,__LINE__);
		}
        
        disableDebugLog();
		$SelPath		= getStrByKeyStr($PATH_MAP_FILE,$PathMap);
		$SelFile 		= getStrByKeyStr($PATH_MAP_FILE,$FileMap);
		$SelLink 		= getStrByKeyStr($PATH_MAP_FILE,$LinkMap);
		$ModSelLink 	= getStrByKeyStr($PATH_MAP_FILE,$ModifiedLinkMap);
		$SelSublink		= getStrByKeyStr($PATH_MAP_FILE,$SublinkMap);
        enableDebugLog();
		
		debugForNtb("script   PATH Via01:",__FILE__,$Via01);
		
		#debugForNtb("script   PATHS: __LINE__        $Via01, $Via02, $Via03",__FILE__,__LINE__);
		debugForNtb("-------------------------------------------------",__FILE__,__LINE__); # 50 characters
		debugForNtb("focus file           '$FocusFile'",__FILE__,__LINE__);
		debugForNtb("focus heading        '$SavedNtbFocusHeading'",__FILE__,__LINE__);
		debugForNtb("focus subheading     '$FocusSubheading'",__FILE__,__LINE__);
		debugForNtb("paint line type      '$SelLineType'",__FILE__,__LINE__);
		debugForNtb("paint file type      '$SelFileType'",__FILE__,__LINE__);
		debugForNtb("paint path name      '$SelPath' (<-'$PathMap')",__FILE__,__LINE__);
		debugForNtb("paint file name      '$SelFile' (<-'$FileMap')",__FILE__,__LINE__);
		debugForNtb("paint link str       '$SelLink' (<-'$LinkMap')",__FILE__,__LINE__);
		debugForNtb("paint sublink        '$SelSublink' (<-'$SublinkMap')",__FILE__,__LINE__);
		debugForNtb("paint link type      '$SelLinkType'",__FILE__,__LINE__);
		debugForNtb("paint link str(mod)  '$ModSelLink' (<-'$ModifiedLinkMap')",__FILE__,__LINE__);
		debugForNtb("paint comment        '$LinkComment'",__FILE__,__LINE__);
	}
	else
	{
		debugForNtb("!!!!!!! NO BRACKETS IN LINE '$LineContents', SO RETURNS INITIALIZED VALUES !!!!!!!!!! ",__FILE__,__LINE__); # 50 characters
	}

	$SavedPreviousLine = $_;

	debugForNtb("==================================================",__FILE__,__LINE__); # 50 characters
	debugForNtb("END script $__SCRIPT__ }",__FILE__,__LINE__);
	debugForNtb("#################################################",__FILE__,__LINE__); # 50 characters
	return
			$FocusPath,
			$FocusFile,
			$SavedNtbFocusHeading,
			$FocusSubheading,
			$SelLineType,  # = (ordinary|auto link start|auto link end)
			$SelFileType,
			$SelPath,
			$SelFile,
			$SelLink,
			$SelSublink,
			$SelLinkType,
			$ModSelLink,
			$LinkComment;


}
#===================================================================
######### Graphviz preparation functions ###########################
#===================================================================

sub DotStepEdgeToTargetOutput
{
    # "step" means: target node is not set to new source node  
    debugForNtb("BEGIN: 'DotStepEdgeToTargetOutput()'",__FILE__,__LINE__);
    my($EdgeLabel,$TargetNodeLabel,$ClusterName) = @_;
    #$SourceNodeName = DotSourceOutput($ClusterName,$PrevDotNodeLabel);
    $TargetNodeName = DotTargetOutput($ClusterName,$TargetNodeLabel);
    DotEdgeOutput($PrevDotNodeName,$TargetNodeName,$EdgeLabel);
    
    $PrevDotNodeName    = $TargetNodeName;
    $PrevDotNodeLabel   = $TargetNodeLabel;
    debugForNtb("END: 'DotStepEdgeToTargetOutput()'",__FILE__,__LINE__);
}

sub DotStayEdgeToTargetOutput
{
    # "stay" means: source node is not changed
    my($EdgeLabel,$TargetNodeLabel,$ClusterName) = @_;
    #$SourceNodeName = DotSourceOutput($ClusterName,$PrevDotNodeLabel);
    $TargetNodeName = DotTargetOutput($ClusterName,$TargetNodeLabel);
    DotEdgeOutput($PrevDotNodeName,$TargetNodeName,$EdgeLabel);
}



sub DotStickerNodeOutput
{
    my($StickerNodeLabel) = @_;
    #$SourceNodeName = DotSourceOutput("NO_CLUSTER",$PrevDotNodeLabel);
    $TargetNodeName = DotTargetOutput("NO_CLUSTER",$StickerNodeLabel);
    DotEdgeOutput($PrevDotNodeName, $TargetNodeName,"comment");
}
#============================================================
sub DotShortSourceOutput
{
   my($SrcClusterLabel, $SrcNodeName, $SrcNodeLabel,$FileLine) = @_;
   debugForNtb("SOURCE labels: cluster-node = '$SrcClusterLabel'-'$SrcNodeLabel'", __FILE__, __LINE__);


   chomp($SrcClusterLabel);
   chomp($SrcNodeName);
   chomp($SrcNodeLabel);

 
   $SrcClusterName=$SrcClusterLabel;
   ######$SrcNodeName=$SrcNodeLabel;
   
   if ($FileLine ne "")
   {
        $SrcNodeLabel = $SrcNodeLabel."\\n ($FileLine)";
   }
   
   $SrcNodeLabel = StrSplitToWordsByMaxLen($SrcNodeLabel,"\\n",20);
   $SrcClusterName=doValidDotSymbolName($SrcClusterName);
   $SrcNodeName=doValidDotSymbolName($SrcNodeName);
   #==================================================================
   $WholeSrcName=$SrcNodeName; # no cluster name added to node name
   #==================================================================
   
   	if (($SrcClusterLabel ne "NO_CLUSTER") && ($SrcClusterLabel ne ""))
	{
		$WholeSrcLabel=$SrcNodeLabel;
		$DotLine = "subgraph cluster_".$SrcClusterName." {label=\"".$SrcClusterLabel."\";".$WholeSrcName."};\n";
		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb(">>>>> DOT source cluster line: $DotLine",__FILE__,__LINE__);
		$DotLine = $WholeSrcName." [label=\"".$WholeSrcLabel."\"$MyDotNodeAttribSet]\;\n";
		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb(">>>>> DOT source node line: $DotLine",__FILE__,__LINE__);
	}
	else
	{
		debugForNtb("source cluster label is 'NO_CLUSTER'",__FILE__,__LINE__);
		$WholeSrcLabel=$SrcNodeLabel;
   		$DotLine = $WholeSrcName." [label=\"".$WholeSrcLabel."\"$MyDotNodeAttribSet]\;\n";
   		print $MY_DOT_OUT_FILE "$DotLine";
	}
    
   $PrevDotNodeName    = $WholeSrcName;
   #DotComment("-  dot source node (line $FileLine)");
   return $WholeSrcName;
}
#============================================================
sub DotSourceOutput
{
   my($SrcClusterLabel, $SrcNodeLabel,$FileLine) = @_;
   debugForNtb("SOURCE labels: cluster-node = '$SrcClusterLabel'-'$SrcNodeLabel'",__FILE__,__LINE__);


   chomp($SrcClusterLabel);
   chomp($SrcNodeLabel);

 
   $SrcClusterName=$SrcClusterLabel;
   $SrcNodeName=$SrcNodeLabel;
   
   $SrcNodeLabel = $SrcNodeLabel."\\n ($FileLine)";
   
   $SrcNodeLabel = StrSplitToWordsByMaxLen($SrcNodeLabel,"\\n",20);
   $SrcClusterName=~s/\W/_/g;
   $SrcNodeName=~s/\W/_/g;

   	if (($SrcClusterLabel ne "NO_CLUSTER") && ($SrcClusterLabel ne ""))
	{
		$WholeSrcName=$SrcClusterName."_".$SrcNodeName;
		$WholeSrcLabel=$SrcNodeLabel;

		$DotLine = "subgraph cluster_".$SrcClusterName." {label=\"".$SrcClusterLabel."\";".$WholeSrcName."};\n";
		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb(">>>>> DOT source cluster line: $DotLine",__FILE__,__LINE__);
		$DotLine = $WholeSrcName." [label=\"".$WholeSrcLabel."\"$MyDotNodeAttribSet]\;\n";
		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb("DOT source node line: $DotLine",__FILE__,__LINE__);
	}
	else
	{
		debugForNtb("source cluster label is 'NO_CLUSTER'",__FILE__,__LINE__);
		$WholeSrcLabel=$SrcNodeLabel;
		$WholeSrcName=$SrcNodeName;
   		$DotLine = $WholeSrcName." [label=\"".$WholeSrcLabel."\"$MyDotNodeAttribSet]\;\n";
   		print $MY_DOT_OUT_FILE "$DotLine";
	}
    
   $PrevDotNodeName    = $WholeSrcName;
   #DotComment("-  dot source node (line $FileLine)");
   return $WholeSrcName;
}
#============================================================
sub DotTargetOutput
{
	my($TrgClusterLabel, $TrgNodeLabel, $FileLine) = @_;

    debugForNtb("BEGIN: 'DotTargetOutput()'",__FILE__,__LINE__);
	chomp($TrgNodeLabel);
	chomp($TrgClusterLabel);
	$TrgNodeName=$TrgNodeLabel;
	$TrgNodeName=~s/\W/_/g;
    $TrgNodeLabel = $TrgNodeLabel."\\n ($FileLine)";
    $TrgNodeLabel = StrSplitToWordsByMaxLen($TrgNodeLabel,"\\n",20);

	if (($TrgClusterLabel ne "NO_CLUSTER") && ($TrgClusterLabel ne ""))
	{
   		$TrgClusterName=$TrgClusterLabel;
   		$TrgClusterName=~s/\W/_/g;

   		$WholeTrgName=$TrgClusterName."_".$TrgNodeName;
   		$WholeTrgLabel=$TrgNodeLabel;

   		$DotLine = "subgraph cluster_".$TrgClusterName." {label=\"".$TrgClusterLabel."\";".$WholeTrgName."};\n";
   		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb(">>>>> DOT target cluster line: $DotLine",,__FILE__,__LINE__);
   		$DotLine = $WholeTrgName." [label=\"".$WholeTrgLabel."\"$MyDotNodeAttribSet]\;\n";
		debugForNtb(">>>>> DOT target node line: $DotLine",__FILE__,__LINE__);
   		print $MY_DOT_OUT_FILE "$DotLine";
	}
	else
	{

		debugForNtb(">>>>> DOT target cluster line: '$TrgClusterLabel'",__FILE__,__LINE__);
		$WholeTrgLabel=$TrgNodeLabel;
		$WholeTrgName=$TrgNodeName;
   		$DotLine = $WholeTrgName." [label=\"".$WholeTrgLabel."\"$MyDotNodeAttribSet]\;\n";
   		print $MY_DOT_OUT_FILE "$DotLine";
		debugForNtb(">>>>> DOT target node line: $DotLine",__FILE__,__LINE__);
	}

   #DotComment("-  dot target node (line $FileLine)");
   debugForNtb("END: 'DotTargetOutput()'",__FILE__,__LINE__);
   return $WholeTrgName;
}
#============================================================
sub DotEdgeOutput
{
	my($SrcNodeName, $TrgNodeName, $Comment, $FileLine) = @_;
    debugForNtb("BEGIN: 'DotEdgeOutput()'",__FILE__,__LINE__);
    
    if (($SrcNodeName eq "") || ($TrgNodeName eq ""))
    {
        debugForNtb("INVALID DATA ($FileLine): edge not drawn from '$SrcNodeName' to '$TrgNodeName'",__FILE__,__LINE__);
        debugForNtb("END: 'DotEdgeOutput()'",__FILE__,__LINE__);
        return;
    }
    
    
  
    if ($Comment ne "")
    {
        $Comment = $Comment."\\n ($FileLine)";
        $Comment = StrSplitToWordsByMaxLen($Comment,"\\n",20);
    }
    else
    {
        if ($SrcNodeName eq $TrgNodeName)
        {
            debugForNtb("Edge not drawn back to same node '$SrcNodeName'",__FILE__,__LINE__);
            debugForNtb("END: 'DotEdgeOutput()'",__FILE__,__LINE__);

            return;
        }
    }
 
	$DotLine = $SrcNodeName." -> ".$TrgNodeName." [label=\"$Comment\"$MyDotEdgeAttribSet]\;\n";

	print $MY_DOT_OUT_FILE "\n$DotLine";
    chomp $DotLine; 
	debugForNtb(">>>>> DOT edge: $DotLine",__FILE__,__LINE__);
	#debugLogPos(__FILE__,__LINE__,"EDGE: '$SrcNodeName' -> '$TrgNodeName'");
    #DotComment("-  dot edge (line $FileLine)");
    debugForNtb("END: 'DotEdgeOutput()'",__FILE__,__LINE__);

}

#============================================================
sub DotFullyLabeledEdgeOutput
{
    # adds also head and tail -labels
	my($SrcNodeName, 
        $SourceJointLabel, 
        $EdgeLabel, 
        $TargetJointLabel, 
        $TrgNodeName, 
        $DataFileLineNbr,
        $CallerFileLineNbr) = @_;
    
    $SrcNodeName = doValidDotSymbolName($SrcNodeName);
    $TrgNodeName = doValidDotSymbolName($TrgNodeName);
    
    if ($SrcNodeName eq "")
    {
        $SrcNodeName = "ERROR_source_node_is_empty";
    }
         
    if ($TrgNodeName eq "")
    {
        $TrgNodeName = "ERROR_target_node_is_empty";
    }

    $EndLabelsDef = "taillabel=\"$SourceJointLabel\",headlabel=\"$TargetJointLabel\""; # note: graphviz
    #$Comment = $Comment."\\n ($DataFileLineNbr)";
    #$Comment = StrSplitToWordsByMaxLen($Comment,"\\n",20);
    
	$DotLine = $SrcNodeName." -> ".$TrgNodeName." [label=\"$EdgeLabel\",$EndLabelsDef $MyDotEdgeAttribSet]\;";
	#print $MY_DOT_OUT_FILE "\n$DotLine \n         // DATA: $DataFileLineNbr CALL: $CallerFileLineNbr\n";
    print $MY_DOT_OUT_FILE "\n$DotLine \n";
    debugForNtb(">>>>> DOT edge output: $DotLine",__FILE__,__LINE__);
	
}

sub DotClusterNodeEdgeToSingleLineOutput
{
   my($SourceClusterLabel,
      $SourceNodeLabel,
      $EdgeLabel,
      $TargetClusterLabel,
      $TargetNodeLabel,
      $Comment) = @_;

      if ($SourceClusterLabel eq "")    {$SourceClusterLabel = "SOURCE CLUSTER IS EMPTY";}
      if ($SourceNodeLabel eq "")       {$SourceNodeLabel = "SOURCE NODE IS EMPTY";}
      if ($TargetClusterLabel eq "")    {$TargetClusterLabel = "TARGET CLUSTER IS EMPTY";}
      if ($TargetNodeLabel eq "")       {$TargetNodeLabel = "TARGET NODE IS EMPTY";}
 
      $SourceClusterLabel   = doValidDotLabelText($SourceClusterLabel);
      $SourceNodeLabel      = doValidDotLabelText($SourceNodeLabel);
      $TargetClusterLabel   = doValidDotLabelText($TargetClusterLabel);
      $TargetNodeLabel      = doValidDotLabelText($TargetNodeLabel);

      $SourceClusterName    = doValidDotSymbolName($SourceClusterLabel);
      $SourceNodeName       = doValidDotSymbolName($SourceNodeLabel);
      $TargetClusterName    = doValidDotSymbolName($TargetClusterLabel);
      $TargetNodeName       = doValidDotSymbolName($TargetNodeLabel);
      
      
      my $SourceCluster 
        = "subgraph cluster_".$SourceClusterName." {label=\"$SourceClusterLabel\"; $SourceNodeName};";
      
      my $SourceNode
        = $SourceNodeName." [label=\"$SourceNodeLabel\"]\;";
        
      my $TargetCluster 
        = "subgraph cluster_".$TargetClusterName." {label=\"$TargetClusterLabel\"; $TargetNodeName};";

      my $TargetNode
        = $TargetNodeName." [label=\"$TargetNodeLabel\"]\;";
        
      my $Edge 
        = $SourceNodeName." -> ".$TargetNodeName." [label=\" $EdgeLabel\"]\;";
        
      print $MY_DOT_OUT_FILE "$SourceCluster $SourceNode $TargetCluster $TargetNode $Edge // $Comment\n";
}
#============================================================
sub DotExactOutput
{
	my($AnyText) = @_;

	print $MY_DOT_OUT_FILE $AnyText;
}
#------------------------------------------

#============================================================
sub DotComment
{
	my($Comment) = @_;

	print $MY_DOT_OUT_FILE "        // $Comment\n";
    

}
#------------------------------------------


#============================================================
sub DotOutputInit
{
	my($DOT_OUT_FILE) = @_;
    $MY_DOT_OUT_FILE = 	$DOT_OUT_FILE;
    $PrevDotNodeName = "start";
    $PrevDotNodeLabel = "start";
}
#------------------------------------------
#============================================================
sub DotSetNodeForm
{
	my($Color,$Style,$Shape) = @_;
	$MyDotNodeAttribSet="";

	if ($Shape ne "")
	{
		if ($MyDotNodeAttribSet ne "")
		{
			$MyDotNodeAttribSet = $MyDotNodeAttribSet."\,";
		}
		else
		{
			$MyDotNodeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotNodeAttribSet = $MyDotNodeAttribSet."shape=".$Shape;
	}
 	if ($Style ne "")
	{
		if ($MyDotNodeAttribSet ne "")
		{
			$MyDotNodeAttribSet = $MyDotNodeAttribSet."\,";
		}
		else
		{
			$MyDotNodeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotNodeAttribSet = $MyDotNodeAttribSet."style=".$Style;
	}
	if ($Color ne "")
	{
		if ($MyDotNodeAttribSet ne "")
		{
			$MyDotNodeAttribSet = $MyDotNodeAttribSet."\,";
		}
		else
		{
			$MyDotNodeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotNodeAttribSet = $MyDotNodeAttribSet."color=".$Color;
	}
	if ($MyDotNodeAttribSet ne "")
	{
		###$DotOutLine = "\n\nnode \[$MyDotNodeAttribSet\]\;\n\n";
		###print $MY_DOT_OUT_FILE "$DotOutLine";   
	}

    #DotComment("DEBUG: set node attributes to '$MyDotNodeAttribSet'");
    debugForNtb("node attributes set to '$MyDotNodeAttribSet'",__FILE__,__LINE__);

}
#------------------------------------------
sub DotSetEdgeForm
{
	my($Dir,$ArrowHeadType,$ArrowTailType,$LineType,$ArrowSize) = @_;
	$MyDotEdgeAttribSet="";
	if ($Dir ne "")
	{
		$MyDotEdgeAttribSet=","; # delimiter after "label" -field
		$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."dir=$Dir";
        # VALUES: back,###
	}
 	if ($ArrowHeadType ne "")
	{
		if ($MyDotEdgeAttribSet ne "")
		{
			$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."\,";
		}
		else
		{
			$MyDotEdgeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."arrowhead=$ArrowHeadType";
        # VALUES: odiamond, ###
	}
    if ($ArrowTailType ne "")
	{
		if ($MyDotEdgeAttribSet ne "")
		{
			$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."\,";
		}
		else
		{
			$MyDotEdgeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."arrowtail=$ArrowTailType";
        # VALUES: odiamond, ###
	}
	if ($LineType ne "")
	{
		if ($MyDotEdgeAttribSet ne "")
		{
			$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."\,";
		}
		else
		{
			$MyDotEdgeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."style=$LineType";
	}
    if ($ArrowSize ne "")
	{
		if ($MyDotEdgeAttribSet ne "")
		{
			$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."\,";
		}
		else
		{
			$MyDotEdgeAttribSet=","; # delimiter after "label" -field
		}
		$MyDotEdgeAttribSet = $MyDotEdgeAttribSet."arrowsize=$ArrowSize";
	}
	if ($MyDotEdgeAttribSet ne "")
	{
		###$DotOutLine = "\n\nedge \[$MyDotEdgeAttribSet\]\;\n\n";
		###print $MY_DOT_OUT_FILE "$DotOutLine";
	}
}
#------------------------------------------

sub doValidDotSymbolName
{
	# converts ".,:;<space>" and others to underscores "_"
	my($Text) = @_;
	$Text=doValidDotLabelText($Text);
	$Text=~s/\W/_/g;
    $Text=~s/^\d.*/_$Text/g;
    #$Text="_".$Text;  # for sure to handle cases where first character is '0'...'9'
	return $Text;
}


sub doValidDotLabelText
{
	# converts scandics to closest chars etc

    
	my($Text) = @_;
	$Text=~s/"//g; 		# removes double quotes
	$Text=~s/\/\///g; 	# removes possible slash-slash -comments
	$Text=~s/ä/a/g;
	$Text=~s/Ä/A/g;
	$Text=~s/ö/o/g;
	$Text=~s/Ö/o/g;
	$Text=~s/\0xE4/a/g;
	$Text=~s/\\/\\\\/g;
    
    if ($Text eq "")
    {
        $Text="TEXT IS EMPTY";
    }
	return $Text;
}


#===================================================================
######### Graphviz preparation functions ###########################
#===================================================================

my %my_VttShapeTypeToDotMap =
(

	# TODO: add types
);


my %my_VttArrowTypeToDotMap =
(
	"StandardArrow" 		=> "normal",
	"FlatArrow" 			=> "normal",
	"HollowDiamondArrow" 	=> "odiamond",
	"HollowCircleArrow"		=> "odot",
	"CircleArrow"			=> "dot"
	#"ThinFlatArrow"		=> ###
	# TODO: add more types
);

sub getDotEdgeTypeByVttArrow
{
	my($VttType) = @_;
	$DotType = $my_VttArrowTypeToDotMap{$VttType};

	if ($DotType eq "")
	{
		debugLog("hash key $VttType gave empty string");
		$DotType = "none";
	}

	return $DotType;
}

#--------------------------------------------------------------------
sub LineGetStartColumn
#-------------------------------------------------------------------
{
    my($Line,$FileName,$FileLine) = @_;
    
    $LineStartPos = 0;
    if ($Line =~ m{(\s+)?                  # just white chars
                    (.*)                  # rest of line
                   .*}xms)
    {         
        $LinePre = $1;
        $LineText = $2;
        $LinePre    =~ s/\t/    /g;   # convert tabs to multiple spaces   
        $LineStartPos       = length($LinePre);
    
        debugForNtb("start column: $LineStartPos; line text: '$LineText'", $FileName, $FileLine); 
    }
    else
    {
        $LineStartPos   = 0;
        $LineText       = $Line;
    }
    return ($LineStartPos, $LineText);
}
#--------------------------------------------------------------------
sub LineGetAlphanumericStartColumn
#-------------------------------------------------------------------
{
    my($Line,$FileName,$FileLine) = @_;
    
    $SymbolNameStartPos = -1; # initial quess
    $SymbolName = "";
    if ($Line =~ m{(\W+)                 
                   (\w+)
                   (.*)}xms)
    {         
        $SymbolPre  = $1;
        $SymbolName = $2;
        $SymbolNameStartPos       = length($SymbolPre);

        debugForNtb("SymbolName/start pos = '$SymbolName'/$SymbolNameStartPos found at line '$Line'",__FILE__,__LINE__);
    }
    
    return ($SymbolNameStartPos, $SymbolName);
}
#--------------------------------------------------------------------
sub LineCheckIfComment
#-------------------------------------------------------------------
{
    my($Line, $CommentStartStr) = @_;
    debugForNtb("BEGIN: check if comment line",__FILE__,__LINE__);
    
    $DataPart           = "";
    $CommentPart        = "";
    $CommentStartPos    = 0;
    $FlagIsStartComment = 0;
    
    if ($Line =~ m{(\s+)                  # just white chars 
                   $CommentStartStr
                   (.*)}xms)
    {         
        $CommentPre = $1;
        $CommentPre    =~ s/\t/    /g;   # convert tabs to multiple spaces   
        $CommentStartPos       = length($CommentPre);
        $CommentPart = $2;
        $FlagIsStartComment     = 1;
        debugForNtb("comment text/start pos = '$CommentPart'/$CommentStartPos found at line '$Line'",__FILE__,__LINE__);
    
    }
    elsif ($Line =~ m{(.+)              
                     $CommentStartStr   
                     (.*)}xms)
    {         
       $DataPart    = $1; 
       $CommentPart = $2;
    }
    else
    {
        $DataPart = $Line;
    }
    
    debugForNtb("END:",__FILE__,__LINE__);
    return($FlagIsStartComment, $DataPart, $CommentPart, $CommentStartPos);
}

#--------------------------------------------------------------------
sub GraphTagCheckIfItemLine
#
# returns cluster or node key/value pair if found in given line
#-------------------------------------------------------------------
{
	my($Line, $LineEndGraphIndArray) = @_;

    debugForNtb("BEGIN: GraphTagCheckIfItemLine()",__FILE__,__LINE__);
    $StartPos   = 0;
    $KeyStr     = "";
    $ValStr     = "";
    $Tag        = "";
    
    $ThingFound = $TRUE;   # initial quess
    
    
    if ($Line =~ m{(\W*)                        # possible non-word chars
                    (\d{1,2}\.)                 # decimal digits 0. - 99. at line start
                    \s+                         # one or more white char separators before graph line indicator
                    (\w.*?)                     # any string
                     \s*                        # zero or more white chars
                    ([$LineEndGraphIndArray])   # single, specific char as graph line indicator
                     \s*$                       # zero or more white chars at line end
                    }xms)
    { 
        $KeyStr     = $2;
        $ValStr     = $3;
        $Tag        = $4;
        $LineNbr    = __LINE__;
    } 
    elsif ($Line =~ m{(\W*)                    # possible non-word chars
                    (\w.*?)                     # any string 
                    \s*                         # one or more white char separators before graph line indicator
                    \((.*)\)                    # any string in parentheses
                    \s*                         # zero or more white chars
                    ([$LineEndGraphIndArray])   # single, specific char as graph line indicator
                     \s*$                       # zero or more white chars at line end
                    }xms)
    { 
        $KeyStr     = $3;
        $ValStr     = $2;
        $Tag        = $4;
        $LineNbr    = __LINE__;
    } 
    elsif ($Line =~ m{(\W*)                    # possible non-word chars
                    (\w.*?)                     # any string 
                    \s*                         # possible white char separators before graph line indicator
                    ([$LineEndGraphIndArray])   # single, specific char as graph line indicator
                    \s*$                        # zero or more white chars at line end
                    }xms)
    { 
        $KeyStr     = $2;
        $ValStr     = $2;
        $Tag        = $3;
        $LineNbr    = __LINE__;
    } 
    else
    {
        debugForNtb("no static item found in line '$Line'",__FILE__,__LINE__);
        $ThingFound = $FALSE;
    }

    if ($ThingFound == $TRUE)
    {
    
        debugForNtb("heading offset '$1' found in line '$Line'",__FILE__,__LINE__);
        $PossibleHeadingOffset = $1;
        $PossibleHeadingOffset        =~ s/\t/    /g;   # convert tabs to multiple spaces
        
        $StartPos   = length($PossibleHeadingOffset);
        debugForNtb(" Tag/key/val/start pos (line: $LineNbr)= '$Tag'/'$KeyStr'/'$ValStr'/$StartPos",__FILE__,__LINE__);
    }
    debugForNtb("END:",__FILE__,__LINE__);
    return($Tag, $KeyStr, $ValStr, $StartPos);
}
#--------------------------------------------------------------------
sub GraphTagCheckIfNodeAttributeLine
#--------------------------------------------------------------------
{
    
	my($Line) = @_;
    $Color = "";
    $Style = "";
    $Shape = "";
    
    if ($Line =~ m{.*                    
                node\slook:     # heading keywords
                \s*             # zero or more white chars
                (\w+)           # node name
                \s+             # one or more white chars
                (\w+)           # node style
                \s+             # one or more white chars
                (\w+)           # node shape                
                }xms)
    { 
        $Color     = $1;
        $Style     = $2;
        $Shape     = $3; 
        debugForNtb("node attributes found: color/style/shape = '$Color'/'$Style'/'$Shape' in line '$Line'",__FILE__,__LINE__);
    } 
    else
    {
        #debugForNtb("No node attributes found in line '$Line', 1/2/3 = '$1'/'$2'/'$3'",__FILE__,__LINE__);
        $ThingFound = $FALSE;
    }
    return ($Color, $Style, $Shape);
}

#--------------------------------------------------------------------
sub GraphCheckIfEdgeLine
#
# possible cases:
# '<source node>' edge text '<target node>'
#  no graph tags used ! 
#
#
#
#--------------------------------------------------------------------
{
    my($Line, $rh_NodeLabelByNodeName) = @_;
    # TODO: add check, if any of collected node names are embedded non-taggedly in given line
    debugForNtb("BEGIN: GraphCheckIfEdgeLine()",__FILE__,__LINE__);
    
    # my  %hNodeLabelByName  = %$rh_NodeLabelByNodeName;
    my $Status             = 0; # initial quess
    my $CaseLine           = 0;
    my $Tag                = "";
    my $SourceNodeKey      = "";
    my $SourceJointText    = "";
    my $EdgeText           = ""; 
    my $TargetJointText    = "";
    my $TargetNodeKey      = "";
    
    if ($Line =~ m{(.*)
                   \((.*)\s+to\s+(.*)\) 
                   .*
                   }xms)
    {
        debugForNtb("edge multiplicity found:'$Line'",__FILE__,__LINE__);
        $Line            = $1;
        $SourceJointText = $2;
        $TargetJointText = $3;
    }
    else
    {
        debugForNtb("edge multiplicity NOT found:'$Line'",__FILE__,__LINE__);
    }
    
    foreach(keys %$rh_NodeLabelByNodeName)
    {
        my $NodeName = $_;
        my $NodeLabel = $$rh_NodeLabelByNodeName{$NodeName};  
        
        if  ($Line =~ /\'$NodeName\'/)
        {
             debugForNtb("hyphened node name ''$NodeName'' found in line '$Line', so add nothing",__FILE__,__LINE__);
        }
        elsif ($Line =~ /$NodeName/)
        {
            debugForNtb("non-hyphened node name '$NodeName' found in line '$Line', so add hyphens",__FILE__,__LINE__);
            $Line =~s/$NodeName/\'$NodeName\'/;
          
        }
        else
        {
            debugForNtb("node name '$NodeName' not found in line '$Line'",__FILE__,__LINE__);
        }
    }
    
    
    if ($Line =~ m{(.*?) 
                   '(.*?)'                      # note: no backslash needed for single quote char
                   \s+?
                   (\w+.*?)                     # edge text  ? prevents capturing too much             
                   '(.*?)'                      # target node
                   \s*                    
                   }xms)
    {    # example: "'AAA' bbb 'CCC'"
         $PossibleHeadingOffset= $1;
         $SourceNodeKey = $2;
         $EdgeText      = $3;
         $TargetNodeKey = $4;
         $CaseLine      = __LINE__; 
         $Status = 1;
         debugForNtb("S-E-T found in line '$Line'",__FILE__,__LINE__);
    }
    
    elsif ($Line =~ m{(.*?)
                   '(.*?)'                      # note: no backslash needed for single quote char
                   \s+?
                   (.*)                         # edge text: rest of line            
                   \s*                    
                   }xms)
    {    # example: "'AAA' bbb bbb bb"
         $PossibleHeadingOffset= $1;
         $SourceNodeKey = $2;
         $EdgeText      = $3;
         $TargetNodeKey = "";
         $CaseLine      = __LINE__; 
         $Status = 1;
         debugForNtb("S-E found in line '$Line'",__FILE__,__LINE__);
    }
    elsif ($Line =~ m{(.*?)
                   (\w+.*?)                     # edge text  ?            
                   '(.*?)'                      # target node
                   \s*                    
                   }xms)
    {    # example: "bbb bbb bb 'CCC'"
         $SourceNodeKey = "";
         $PossibleHeadingOffset= $1;
         $EdgeText      = $2;
         $TargetNodeKey = $3;
         $CaseLine      = __LINE__; 
         $Status = 1;
         debugForNtb("E-T found in line '$Line'",__FILE__,__LINE__);
    } 

  
    else
    {
       debugForNtb("edge stuff NOT found in line '$Line'",__FILE__,__LINE__);
    }

    chomp $_;  
    if ($CaseLine > 0)
    {
        debugForNtb("heading offset '$1' found in line '$_'",__FILE__,__LINE__);
        $PossibleHeadingOffset        =~ s/\t/    /g;   # convert tabs to multiple spaces
        $StartPos   = length($PossibleHeadingOffset);
        debugForNtb("EDGE LINE FOUND:($CaseLine): source/joint/edge/joint/target/tag = $SourceNodeKey / $SourceJointText/ $EdgeText / $TargetJointText/ $TargetNodeKey / $Tag ",__FILE__,__LINE__);
    } 
    else
    {
        debugForNtb("edge line NOT found: 1/2/3/4/line = '$1'/'$2'/'$3'/'$4'/'$Line'",__FILE__,__LINE__);
    }
    
    debugForNtb("END:",__FILE__,__LINE__);
    return ($Status, $SourceNodeKey,$SourceJointText, $EdgeText, $TargetJointText, $TargetNodeKey,$StartPos);
}


#--------------------------------------------------------------------
sub GraphTagCheckIfEdgeLine
#
# possible cases:
# '<source node>' edge text '<target node>'
#
#
#
#
#--------------------------------------------------------------------
{
    my($Line, $r_NodeNamesData, $LineEndGraphIndArray) = @_;
    
    debugForNtb("try find edge in line '$Line'",__FILE__,__LINE__);
    my $Status             = 0; # initial quess
    my $CaseLine           = 0;
    my $Tag                = "";
    my $SourceNodeKey      = "";
    my $SourceJointText    = "";
    my $EdgeText           = ""; 
    my $TargetNodeKey      = "";
    my $TargetJointText    = "";
    
    

    
    if ($Line =~ m{(.*)([$LineEndGraphIndArray])\s*}xms)
    {   # example: "'AAA' bbb 'CCC'
        $Line = $1;
        $Tag  = $2;  
    }
    else
    {
        debugForNtb("edge line NOT found: 1/2/line = '$1'/'$2'/'$Line'",__FILE__,__LINE__);
        return ($Status, $Tag, $SourceNodeKey, $SourceJointText, $EdgeText, $TargetNodeKey, $TargetJointText);
    }
    
    if ($Line =~ m{(.*)
                   \((.*)\s+to\s+(.*)\) 
                   .*
                   }xms)
    {
        debugForNtb("edge multiplicity found:'$Line'",__FILE__,__LINE__);
        $Line            = $1;
        $SourceJointText = $2;
        $TargetJointText = $3;
    }
    else
    {
        debugForNtb("edge multiplicity NOT found:'$Line'",__FILE__,__LINE__);
    }
    
    
    if ($Line =~ m{\s*?
                   '(.*?)'                      # note: no backslash needed for single quote char
                   \s+?
                   (\w+.*?)                     # edge text  ? prevents capturing too much             
                   '(.*?)'                      # target node
                   \s*                    
                   }xms)
    {    # example: "'AAA' bbb 'CCC'"
         $SourceNodeKey = $1;
         $EdgeText      = $2;
         $TargetNodeKey = $3;
         $CaseLine      = __LINE__; 
         $Status = 1;
         debugForNtb("S-E-T found in line '$Line'",__FILE__,__LINE__);
    }
    else
    {
       debugForNtb("S-E-T NOT found in line '$Line'",__FILE__,__LINE__);
    }

       
    if ($CaseLine > 0)
    {
        debugForNtb("EDGE LINE FOUND:($CaseLine): source/joint/edge/joint/target/tag = $SourceNodeKey / $EdgeText / $TargetNodeKey / $Tag ",__FILE__,__LINE__);
    } 
    else
    {
        debugForNtb("edge line NOT found: 1/2/3/4/line = '$1'/'$2'/'$3'/'$4'/'$Line'",__FILE__,__LINE__);
    }
    return ($Status, $Tag, $SourceNodeKey,$SourceJointText, $EdgeText, $TargetJointText, $TargetNodeKey);
}

#--------------------------------------------------------------------
sub GraphTagGetWithLineTrim
#-------------------------------------------------------------------
{
	my($Line, $LineEndGraphIndArray) = @_;
    
    $Tag = "not_valid";             # initial quess
    $TrimmedText = "not_valid";     # initial quess
    $HeadingLen = 0;                # initial quess 
    
    if ($Line =~ m{(.*?)                            # any string 
                        \s+                         # one or more white char separators before graph line indicator
                        ([$LineEndGraphIndArray])   # single, specific char as graph line indicator
                        \s*                         # zero or more white chars
                        }xms)
    { 
        $LineText   = $1;
        $Tag        = $2;
        debugForNtb("Tag/text/line= '$Tag'/'$LineText'/'$Line'",__FILE__,__LINE__);
    } 
    else
    {
            return($Tag, $TrimmedText, $HeadingLen);
    }
    
    
    
    if ($LineText =~ m{(.*?)                # any string before first alphanumeric char
                        \s*                 # zero or more white chars    
                       (\w{1}.*)            # string start with alphanumeric char 
                       }xms)
    { 
       
        $LineHeadingTrash   = $1;
        $TrimmedText        = $2;
        $TrimmedText        =~ s/\s+/ /g;   # convert all multiple spaces into a single space
        $HeadingLen = length($LineHeadingTrash); 
        debugForNtb("trimmed/startpos/line= '$TrimmedText'/'$HeadingLen'/'$LineText'",__FILE__,__LINE__);
    } 
    elsif ($LineText =~ m{.*?              # any string before first alphanumeric char 
                        (\w{1}.*)           # string start with alphanumeric char 
                        }xms)
    { 
       
        $TrimmedText        = $1;
        $TrimmedText        =~ s/\s+/ /g; # convert all multiple spaces into a single space
        debugForNtb("Tag/trimmed/startpos/line = '$Tag'/'$TrimmedText'/'$HeadingLen'/'$LineText'",__FILE__,__LINE__);
    } 
    else
    {

       debugForNtb("no match at line '$LineText', 1/2/3 = '$1'/'$2'/'$3'",__FILE__,__LINE__);
    }
    return($Tag, $TrimmedText, $HeadingLen);
}

#==================================================================================
sub GraphTagCheck_J_S_E_T_J
#----------------------------------------------------------------------------------
{
    my($TextLine) = @_;
    
   
    
    if ($TextLine =~ m{(.+?)           # any string before first upper case started black string 
                                        # - '?' assures finding FIRST capitalized string 
                        \s+             # white char separators
                        ([A-Z]\S+)      # first upper case started black string
                        \s+             # white char separators                        
                        (.+)            # any string before last upper case started black string
                        \s+             # white char separators
                        ([A-Z]\S+)      # last upper case started black string
                        \s+             # white char separators
                        (.+)            # any string after last upper case started black string 
                        }xms)           
                       
    { 
        ($SourceJointLabel, $SourceNodeName, $EdgeLabel, $TargetNodeName, $TargetJointLabel) = ($1,$2,$3,$4,$5);
    }
    
    if ($TargetJointLabel ne "")
    {
         return $SourceJointLabel, $SourceNodeName, $EdgeLabel, $TargetNodeName, $TargetJointLabel;
    }
    else
    {
        return "","","","","";
    }  
}


#==================================================================================
sub GraphTagCheck_J_S_E_t_j
#----------------------------------------------------------------------------------
{
    my($TextLine) = @_;
    
   
    
    if ($TextLine =~ m{(.+?)           # any string before first upper case started black string 
                                        # - '?' assures finding FIRST capitalized string 
                        \s+             # white char separators
                        ([A-Z]\S+)      # first upper case started black string
                        \s+             # white char separators                        
                        (.+)            # any string before last upper case started black string
                        \s+             # white char separators
                        ([A-Z]\S+)      # last upper case started black string
                        \s+             # white char separators
                        (.+)            # any string after last upper case started black string 
                        }xms)           
                       
    { 
        ($SourceJointLabel, $SourceNodeName, $EdgeLabel, $TargetNodeName, $TargetJointLabel) = ($1,$2,$3,$4,$5);
    }
    
    if ($TargetJointLabel ne "")
    {
         return $SourceJointLabel, $SourceNodeName, $EdgeLabel, $TargetNodeName, $TargetJointLabel;
    }
    else
    {
        return "","","","","";
    }
    
}

#===================================================================
######### Visual thought file parsing methods ######################
#===================================================================

#--------------------------------------------------------------------
sub VttGetWholeSymbolText
# loops through several lines
#-------------------------------------------------------------------
{
	my($DATA_FILE, $Line) = @_;

	#@SymbolText = (); 		# note: table clearing
	$SymbolText = "";
	$Over = $FALSE;

	while ($Over != $TRUE)
	{
		($LineText, $Over) = VttGetSymbolTextLine($Line);

		#push(@SymbolText, $Line); # note: adding string into a list
		if ($Over != $TRUE)
		{
			$Line=<$DATA_FILE>; # reads next line
			$SymbolText = $SymbolText . $LineText . "\\"."n"; # note: string concatenation
		}
	}
	$FirstOverflowLine = $Line;

	$OverflowRead = $TRUE;

	debugLog("Whole symbol text: $SymbolText");
	return $SymbolText, $OverflowRead, $FirstOverflowLine;
	#return @SymbolText, $FirstOverflowLine;
}

#--------------------------------------------------------------------
sub VttGetTrimSymbolText
# loops through several lines
#-------------------------------------------------------------------
{
	my($DATA_FILE, $Line) = @_;

	$SymbolText = "";
	$Over = $FALSE;

	while ($Over != $TRUE)
	{
		($LineText, $Over) = VttGetSymbolTextLine($Line);
        
		if ($Over != $TRUE)
		{
            if  (($LineText =~ /\w/ig) 
                    and 
                ($LineText !~ /$VttSymbolDefaultText/)) # note: matches non-empty line
            { 
                debugLog("line '$LineText' is NOT empty or default, so use it");
                $SymbolText = $SymbolText . $LineText . "\\"."n"; # note: string concatenation
            }
            else
            {
                debugLog("line '$LineText' is ignored");
                # line was empty, so ignored
            }
            $Line=<$DATA_FILE>; # reads next line
		}
        else
        {
            
        
        }
	}
	$FirstOverflowLine = $Line;

	$OverflowRead = $TRUE;

	debugLog("Whole symbol text: $SymbolText");
	return $SymbolText, $OverflowRead, $FirstOverflowLine;
	#return @SymbolText, $FirstOverflowLine;
}



#___________________________________________________________________
sub VttGetSymbolTextLine
{
	my($Line) = @_;
	#----------------------------------------
	# example-types of parse focus lines:
	#
	# "\cf0\plain\pard\qc <text>})"
	# "\cf0\plain\pard\qc {\fs20 <text>"
	# "\cf0\plain\pard\qc {\fs20 <text>}})"
	# "\cf0\plain\pard <text>})"
	# "\cf0\plain\pard {\fs20   }{\b\ul\f1  <text>}"   // note: underlined text
	# "{\ul This is underlined text}"
	#----------------------------------------
	$WentOver=$FALSE;

	debugLog("=================================================");
	debugLog("Symbol text: line before substitutions: $Line");
	$OriginalLine = $Line;

	$Line =~s/\\qc//g;
	$Line =~s/\}//g;
	$Line =~s/\)//g;
	$Line =~s/\{//g;

	$Line =~s/\\b\\ul\\f1//g;
	$Line =~s/\\ul//g;
	$Line =~s/\\f1//g;
	$Line =~s/fs\d\d//g;

	$Line =~s/\\//g;

	debugLog("Symbol text: line after substitutions: $Line");

	if (($Waste1,$SymbolTextLine) = ($Line =~ /(.*fs\d\d\s)(.*)/))
	{	# "fonted" case
		$LineNbr = __LINE__;
	}
	elsif (($Waste1,$SymbolTextLine) = ($Line =~ /(.*pard\s)(.*)/))
	{	# "plain" case
		$LineNbr = __LINE__;
	}
	elsif (($Waste1,$SymbolTextLine) = ($Line =~ /(.*par\s)(.*)/))
	{	# ### case
		$LineNbr = __LINE__;
	}
	else
	{
		$LineNbr = __LINE__;

		$SymbolTextLine="***** Failed to parse line: $OriginalLine";
		debugLog($SymbolTextLine);

		$SymbolTextLine	= 	$OriginalLine;
		$WentOver		=	$TRUE;
	}

	debugLog("Symbol text: after parsing ($LineNbr): $SymbolTextLine");
	debugLog("-------------------------------------------------");

	return $SymbolTextLine, $WentOver;
}

#===========================================================
sub VttGetArrowData
{
#-----------------------------------------------------------
#   (drawStartArrowhead F)
#   (drawEndArrowhead F)
#   (startArrowhead "StandardArrow")
#   (endArrowhead "StandardArrow")
#-----------------------------------------------------------
	my($DATA_FILE,$Line) = @_;

	debugLog("Arrow property line: $Line");
	($W1,$StartStatus,$W2) = ($Line =~ /(\(drawStartArrowhead\s)(.)(\))/);
	$Line=<$DATA_FILE>; # reads next line
	debugLog("Arrow property line: $Line");
	($W1,$EndStatus,$W2) = ($Line =~ /(\(drawEndArrowhead\s)(.)(\))/);
	$Line=<$DATA_FILE>; # reads next line
	debugLog("Arrow property line: $Line");
	($W1,$StartType,$W2) = ($Line =~ /(\(startArrowhead\s\")(.*)(\"\))/);
	$Line=<$DATA_FILE>; # reads next line
	debugLog("Arrow property line: $Line");
	($W1,$EndType,$W2) = ($Line =~ /(\(endArrowhead\s\")(.*)(\"\))/);

	debugLog("Arrow data parsed: $StartStatus, $EndStatus, $StartType, $EndType");

	return $StartStatus,$EndStatus,$StartType,$EndType;

}
#============================================================
sub DosNameToString
# converts path/file name into a valid symbol name string
{
	# converts ".,:;<space>" and others to underscores "_"
	my($Text) = @_;
	$Name=doValidDotLabelText($Text); # call to
	$Name=~s/\W/_/g;
	return $Name;
}

#--------------------------------------------------------------------
sub DecStrToVal  # 051220: copied from  "atoi" in http://perl.plover.com/IAQ...
#--------------------------------------------------------------------
{
	my($DecStr) = @_;
	my $t;
	debugLog("convert string '$DecStr' to value",__FILE__,__LINE__);
	foreach my $d (split(//, shift()))
	{
		$t = $t * 10 + $d;
	}
	debugLog("conversion result is $t",__FILE__,__LINE__);
	return $t;
}
#--------------------------------------------------------------------
sub DecStrToBinStr  
#--------------------------------------------------------------------
{
	my($DecNbr) = @_;
	debugLog("convert number $DecNbr to binary string",__FILE__,__LINE__);
	$Val 	= DecStrToVal($DecNbr);
	$BinStr = sprintf("%b", $Val);
	debugLog("conversion result is '$BinStr'",__FILE__,__LINE__);
    return $BinStr; 
}

#--------------------------------------------------------------------
sub StrSplitToWordsByMaxLen
#--------------------------------------------------------------------
{
    my($SourceStr, $SplitterStr, $MaxPartLen) = @_;
    #debugForNtb("split string: '$SourceStr' by '$SplitterStr'",__FILE__,__LINE__);
    @Parts = split(/\s+/, $SourceStr);
    
    $ResultStr = "";
    $NextStepPos = $MaxPartLen;
    
    foreach (@Parts)
    {
        $ResultStr = $ResultStr." ".$_;
        $TotalLen = length($ResultStr);
        
        if ($TotalLen > $NextStepPos)
        {
            $ResultStr      = $ResultStr.$SplitterStr;
            $TotalLen       = length($ResultStr);
            $NextStepPos    = $TotalLen + $MaxPartLen;
        }
    }
    
    #debugForNtb("splitted string: '$ResultStr'",__FILE__,__LINE__);
    return $ResultStr;
}

#--------------------------------------------------------------------
sub StrSplitByLineFeeds
#--------------------------------------------------------------------
{
    my($SourceStr, $MaxPartLen) = @_;
    #debugForNtb("split string: '$SourceStr' by '$SplitterStr'",__FILE__,__LINE__);
    $SourceStrLen       = length($SourceStr);
    
    $ResultStr = "";
    $PartLen = 0;
    
    for ($i=0;$i< $SourceStrLen; $i++)
    {
        $Char = substr($SourceStr,$i,1);
        $PartLen++;
        $ResultStr = $ResultStr."$Char";
        if ($PartLen > $MaxPartLen)
        {
            if ((($Char =~ /\w+/ig) && ($CharPrev =~ /\W+/ig))
                || 
            (($CharPrev =~ /\w+/ig) && ($Char =~ /\W+/ig)))
            { # word boundary occurred
                $ResultStr  = $ResultStr."\\n";
                $PartLen    = 0;
            }
        }
        $CharPrev = $Char;
    }
    
    #debugForNtb("splitted string: '$ResultStr'",__FILE__,__LINE__);
    return $ResultStr;
}

#--------------------------------------------------------------------
sub findFirstClangReservedWord
#--------------------------------------------------------------------
{
   my($CheckStr, $FileName, $LineNbr) = @_;
   my $FirstFoundStr = "";
   debugForNtb("check if '$CheckStr' contains any C-language reserved word", $FileName, $LineNbr);
   
   foreach(@a_CLangReservedWords)
   {
       $ReservedWord = $_;
       
       #debugForNtb("try find '$ReservedWord' in '$CheckStr'", $FileName, $LineNbr);
       if ($CheckStr =~ /\b$ReservedWord\b/)
       {
            $FirstFoundStr = $_;
            debugForNtb("reserved word '$ReservedWord' found", $FileName, $LineNbr);
            last;
       }
   }
   return ($FirstFoundStr);
}

1;
__END__

=head1 NAME

OWN::notetools -

=head1 SYNOPSIS
EJL: this library is copied and modified from "Text::ParseWords" (050224-090748)

  use OWN::notetools;

=head1 DESCRIPTION

=head1 EXAMPLES

The sample program:

=over 4

=item 0

=back


=head1 AUTHORS

=cut
