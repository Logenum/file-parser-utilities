#!perl -w
# copied from https://gist.github.com/pdl/3939054
=head1 NAME
pl2py.pl
=head1 DESCRIPTION
Attempts to convert perl scripts to python with the awesome power of regular expressions.
=head1 BUGS
This will (probably) not actually produce runnable python files. But it saves a lot of work converting some perl to python.
More useful if your perl code is well-indented to start with (consider using a source formatter first).
=head1 AUTHOR
Daniel Perrett C<< dperrett@cambridge.org >>
=cut

my $sINDENT_STR = "\t";  # tabulator char

my $sInFileRelName = $ARGV[0];   # TODO: add conversions to "sys.argv[<N>]"
my $sOutFileRelName = $ARGV[1];
my $sTraceFileRelName = $ARGV[2];


open (TRACE_FILE, ">$sTraceFileRelName");

open (INPUT_PERL_FILE, "<$sInFileRelName");
# || print "Cannot open input file '$sInFileRelName'\n";
my @asAllLines = <INPUT_PERL_FILE>;
close INPUT_PERL_FILE;

open (OUTPUT_PYTHON_FILE, ">$sOutFileRelName"); 
#|| print "Cannot open output file '$sOutFileRelName'\n";

my $sCatch1;
my $state;
my $nLineNbr =0;
my $sLatestMatchObjSymbol ="";

my $m_oMatch=0;
for $sLine (@asAllLines)
{
	$nLineNbr++;
   
	$sLine = ifCommentedLine($sLine);
	$sLine = ifFunctionHeading($sLine);
	$sLine = ifLoopStart($sLine);
	$sLine = ifFileOpen($sLine);
	$sLine = ifFileClose($sLine);
	$sLine = ifVariableDefinition($sLine);
	$sLine = ifDollarChars($sLine); 
	
	
	$sLine = ifDefinitionCheck($sLine); 

	$sLine =~ s/(?!<\d)\.(?!\d)/+/g;

	if ($state->{'pod'} == 1)
	{
		$sLine =~ s/^=(?!cut)//g;
	}
	elsif ($sLine =~ s/^=(?!cut)/"""/)
	{
		$state->{'pod'} = 1;
	}
	if ($sLine =~ s/^=cut/"""/)
	{
		$state->{'pod'} = 0;
	}
	
	
	
	$sLine = ifModuleLevelDirectives($sLine);
	$sLine = ifLogicalOperators($sLine);

	
	$sLine = ifFileRead($sLine);
	$sLine = ifMemberReferences($sLine);

	$sLine =~ s/\{$/:/g;
	$sLine =~ s/\}//g;
	$sLine =~ s/;$//g;
	
	$sLine = ifRegexCapture($sLine, $nLineNbr);
	$sLine = ifGoLoopNext($sLine);

	
	$sLine = ifRegexMatch($sLine, $nLineNbr);
	$sLine = ifFileWrite($sLine);
	

	$sLine = ifArrayAppear($sLine);
	
	$sLine =~ s/\s+my\s+/ /g;  # ELu
	$sLine =~ s/\s+my\s+/ /g;  # ELu
	
	# if ($sLine =~ /.*=~.*\/.*\//) { # ELu
		# chomp $sLine;
		# $sLine = $sLine. " # TODO: replace with python syntax\n";
	# }
	
	# sNewTopicHeading =~ s/MM//
    # sNewTopicHeading = sNewTopicHeading.replace("MM","")
	
	$sLine = ifStrSubstitution($sLine);
	$sLine = ifCorrectionsNeeded($sLine);
	#print STDOUT $sLine;
	print OUTPUT_PYTHON_FILE $sLine;
}

close OUTPUT_PYTHON_FILE;
close TRACE_FILE;

	
#===============================================
sub ifRegexCapture { my ($sTheLine, $nLineNbr) = @_;  # checks match, and captures values
#====================================================
#
	#	if (($sIndent, $sFunctionName, $sCallParams) = ($sTheLine =~ m/^(\s+)sub\s+(\w+)\s*\{.*\((.*)\).*/g)){
	#    - conversion result: "<variable_N> = oMatch.group(<N>)"  
	#   if ($sTheLine =~ m/^(\s*)open\s*\(\s*(.*)\,.*\"(\S+)\$(\w+).*/g) {
	#   - conversion result: "<variable_N> = oMatch.group(<N>)"
	# @asDefVars = ( $sTheLine =~ m/(\$\d)/g); # TODO: add this handling
	# http://stackoverflow.com/questions/16416574/filling-a-list-with-regular-expression-results-python
	# http://www.python-course.eu/re_advanced.php
	my $sRetLinesAsSingleStr ="";
	my $nGroupNbr = 0;
	my @asRetLines;
	my $sCatcher = "";
	#if ($sTheLine =~ m/^(\s*)\((\w+).*=\s*\(\s*(\w+)\s*=~\s*\/(.*)\/.*/) {
	if ($sTheLine =~ m/^(\s*)if\s+\((.*)\s+=\s*\(\s*(\S+)\s*=~\s*.*\/(.*)\/.*/g) { # 'if' prefix is assumed
		my $sIndentStr 		= $1;
		my $sCatchersRawSeq = $2;
		my $sCatchTarget 	= $3;
		my $sRegexStr 		= $4;
		
		$sCatchersRawSeq =~ s/\(//g;
		$sCatchersRawSeq =~ s/\)//g;
		
		my @asCatchers = split(',', $sCatchersRawSeq);   # contains 1....N catchers
		$m_oMatch = "match_".$nLineNbr;
		$asRetLines[0] = "$sIndentStr$oMatch = re.match(\"$sRegexStr\", $sCatchTarget)";
		$asRetLines[1] = $sIndentStr."if ".$m_oMatch.":";
		
		foreach $sCatcher(@asCatchers) {
			$sCatcher =~ s/ //g; # removes spaces here because split doesn't do it 
			my $sStr = $sINDENT_STR.$sIndentStr.$sCatcher." = ".$m_oMatch.".group(".$nGroupNbr.")";
			$nGroupNbr = $nGroupNbr+1;
			push @asRetLines, $sStr;
		}
		$sRetLinesAsSingleStr = join ("\n", @asRetLines)."\n";
	} else {
		$sRetLinesAsSingleStr  = $sTheLine;
	}	
	return $sRetLinesAsSingleStr;
}

#===============================================
sub ifRegexMatch { my ($sTheLine, $nLineNbr) = @_;  # checks match, but does not capture values
#====================================================
	my @asRetLines;
	my $sRetLinesAsSingleStr="";
	if ($sTheLine =~ m/^(\s*)if\s*\(\s*(\w+)\s*=~\s*m\/(.*)\/.*/g) { # ELu
		$m_oMatch = "match_".$nLineNbr;;
		$asRetLines[0] = $1.$m_oMatch." = re.match(\"".$3."\", ".$2.")";
		$asRetLines[1] = $1."if ".$m_oMatch." :";
		$sRetLinesAsSingleStr = join ("\n", @asRetLines)."\n";
	} else {
		$sRetLinesAsSingleStr  = $sTheLine;
	}
	return $sRetLinesAsSingleStr;
}



#====================================================
sub ifStrSubstitution { my ($sTheLine) = @_;
#====================================================
#  $sLine =~ s/\bmy ([\w]+)\s*=/$1 =/g;
#$sLine =~ s/\s+{(['"])(.*)\1}/.$2/g;
	
	if ($sTheLine =~ m/^(\s*)(\S+)\s*=~\s*s\/(.*)\/(.*)\/.*/g) {  # string substitution
		$sTheLine = $1.$2." = ".$2.".replace(\"".$3."\", \"".$4."\")\n";
	} 
	return $sTheLine;
}
#===============================================
sub ifDefinitionCheck { my ($sTheLine) = @_;
#===============================================

	# if (! defined $sVar) {
	# ---> if 'sVar' not in locals():
	
	# if (defined $sVar) {
	# ---> if 'sVar' in locals():
	
	if ( $sTheLine =~ m/^(\s*)if\s*\(\s*\!\s*defined\s*\$(\w+)\s*/){ # ELu
		$sTheLine =$1." if \'".$2."\' in locals():";
	}
	if ( $sTheLine =~ m/^(\s*)if\s*\(\s*defined\s*\$(\w+)\s*/) {
		$sTheLine=$1."if \'".$2."\' not in locals():";
	} 	
	return $sTheLine;	
}

#===============================================
sub ifDollarChars { my ($sTheLine) = @_;
#===============================================
# TODO: add specific handling for variable names embedded in strings
#  removes dollar characters if are not default variables.
#  if are default varables, replaces them with "oMatch.group[<number>]"
	my $sRetLinesAsSingleStr="";
	my @asDefVars = ();
	my $sDefVar = "";
	my $nPos=0;
	my $sPythonSyntax="";
	#my $sLineIndent = ( $sTheLine =~ m/^(\s*).*$/g))
	@asDefVars = ( $sTheLine =~ m/(\$\d)/g); # captures all default variables
	
	
	#print STDOUT "sTheLine = $sTheLine\n";
	if (@asDefVars > 0){ 
		foreach $sDefVar (@asDefVars) {
			print STDOUT "sDefVar = $sDefVar\n";
			($nPos) = ($sDefVar =~ m/^\$(\d)/g);

			$sDefVar = "\\".$sDefVar;
			print STDOUT "nPos = $nPos\n";
			$sPythonSyntax = $m_oMatch."\.group\[".$nPos."\]";
			print STDOUT "sPythonSyntax = $sPythonSyntax\n";
			$sTheLine =~ s/$sDefVar/$sPythonSyntax/g;
		}
		print STDOUT "sTheLine = $sTheLine\n";
		$sRetLinesAsSingleStr=$sTheLine;
	} else {
		$sRetLinesAsSingleStr = $sTheLine;
		#$sRetLinesAsSingleStr =~ tr/$//d;
		$sRetLinesAsSingleStr =~ tr/$//d;
	}
	
	print STDOUT "sRetLinesAsSingleStr = $sRetLinesAsSingleStr\n";
	return $sRetLinesAsSingleStr;	

}

#===============================================
sub ifFunctionHeading{ my ($sTheLine) = @_;
#===============================================
	if (($sIndent, $sFunctionName, $sCallParams) = ($sTheLine =~ m/^(\s*)sub\s+(\w+)\s*\{.*\((.*)\).*/g)){
		$sTheLine = $sIndent."def ".$sFunctionName."(".$sCallParams."):\n";
	}
	return $sTheLine;
}

#===============================================
sub ifLoopStart{ my ($sTheLine) = @_;
#===============================================
	if (($sIndent, $sScalarVar, $sArrayVar) = ($sTheLine =~ m/^(\s*)for\s+(\S+)\s*\(\s*(\S+)\s*\).*/g)){
	# TODO: add other loop types
		$sTheLine = $sIndent."for ".$sScalarVar." (".$sArrayVar."):";
	}
	return $sTheLine;
}

#===============================================
sub ifVariableDefinition{ my ($sTheLine) = @_;
#===============================================
	if ($sTheLine =~ m/^(\s*)my\s+\@(\w+)/g) { # array variable
		$sTheLine = $1.$2."=[]\n";
	}
	if ($sTheLine =~ m/^(\s*)my\s+\$(\w+)/g) { # scalar variable
		$sTheLine = $1.$2."=\"\"\n";
	}
	return $sTheLine;
}
#===============================================
sub ifArrayAppear{ my ($sTheLine) = @_;
#===============================================
	if ($sLine =~ m/^(.*)\@(\w+.*)/g) {
		$sTheLine = $1.$2."\n";
	}
	return $sTheLine;
}

#===============================================
sub ifFileOpen { my ($sTheLine) = @_;
#====================================================
	my $sRetLinesAsSingleStr="";
	my @asRetLines;
	my $sType ="";
	if ($sTheLine =~ m/^(\s*)open\s*\(\s*(.*)\,.*\"(\S+)\$(\w+).*/g) { # ELu
		if ($3 eq ">") 	
			{$sType = "w";}
		if ($3 eq ">>") 
			{$sType = 'w+';}
		if ($3 eq "<") 	
			{$sType = 'r';}
		#TODO: add try-catch stuff
		my $sLine = $1.$2." = open(".$4.", ',".$sType."')\n";
		$sRetLinesAsSingleStr = $sLine;
	} else {
		$sRetLinesAsSingleStr = $sTheLine;
	}
	return $sRetLinesAsSingleStr;
}

#===============================================
sub ifFileRead{ my ($sTheLine) = @_;
#===============================================
	if ($sTheLine =~ m/^(.*)\@(\w+)\s*=\s*\<(\w+)\>\s*\;.*/g) { # ELu
		$sTheLine = $1.$2." = ".$3.".readlines()\n";
	}
	return $sTheLine;
}

#===============================================
sub ifFileWrite{ my ($sTheLine) = @_;
#===============================================
	if ($sLine =~ m/^(\s+)print\s+(\w+)\s+(.*)/g) { # ELu
		$sLine = $1.$2."write(".$3.")\n";
	}
	return $sTheLine;
}

#===============================================
sub ifFileClose{ my ($sTheLine) = @_;
#===============================================
	if ($sTheLine =~ m/^(\s*)close\s+(\w+).*/g) { # ELu
		$sTheLine = $1.$2.".close()\n";
	}	
	return $sTheLine;
}
#===============================================
sub ifGoLoopNext{ my ($sTheLine) = @_;
#===============================================
	if ($sTheLine =~ m/^(\s+)last(\W+.*)/g) { # ELu
		$sTheLine = $1."break\n";
	}
	return $sTheLine;
}
#===============================================
sub ifExitLoop{ my ($sTheLine) = @_;
#===============================================

}

#===============================================
sub ifCommentedLine{ my ($sTheLine) = @_;
#===============================================
	$sTheLine =~ s/^\s+#.*//g;
	return $sTheLine;
}


#===============================================
sub ifLogicalOperators { my ($sTheLine) = @_;
#===============================================
	$sTheLine =~ s/^\beq\b/==/g;
	$sTheLine =~ s/^\bge\b/>=/g;
	$sTheLine =~ s/^\ble\b/=</g;
	$sTheLine =~ s/^\bne\b/!=/g;
	$sTheLine =~ s/^\bgt\b/>/g;
	$sTheLine =~ s/^\blt\b/</g;
	$sTheLine =~ s/^\|\|/or/g;
	$sTheLine =~ s/^&&/and/g;
	$sTheLine =~ s/!/ not /g;
	return $sTheLine;
}

#===============================================
sub ifMemberReferences { my ($sTheLine) = @_;
#===============================================
	$sTheLine =~ s/->\{/./g;
	$sTheLine =~ s/->\[/./g;
	$sTheLine =~ s/->/./g;
	$sTheLine =~ s/::/./g;
	return $sTheLine;
}

#===============================================
sub ifModuleLevelDirectives { my ($sTheLine) = @_;
#===============================================
	$sTheLine =~ s/^\s*package (.*?);/class $1:/g;
	$sTheLine =~ s/^\s*use /import /g;
	$sTheLine =~ s/^\bundef\b/None/g;
	return $sTheLine;
}

#===============================================
sub ifCorrectionsNeeded { my ($sTheLine) = @_;
#===============================================

	$sTheLine =~ s/\+group\[/\.group\[/g; 
	$sTheLine =~ s/\;\s*$//g;
	$sTheLine =~ s/::/:/g;  
	$sTheLine =~ s/;\s*#/ #/g; 
	$sTheLine =~ s/^\s*://g;
	$sTheLine =~ s/\+\"\+\"\+/\+\"\.\"\+/g; 
	return $sTheLine;
	
	#TODO: add lines when observed	 
}

