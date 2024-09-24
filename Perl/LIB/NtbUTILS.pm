package PERL_SCRIPTS;

# note: caller files shall contain lines: "package <this package>;" and "use NtbUTILS;"
 
################################################################################
sub DOT_PRE { 
	my (@argv)=@_;
	
	$InpFile 			= shift @argv; 
	$GraphFile 			= shift @argv;
	$InpFile			=~s/\\/\//g;
	$GraphFile			=~s/\\/\//g;

	open(INP_FILE, "<$InpFile") || print "Cannot open file $InpFile";
	open(DOT_FILE, ">$GraphFile") || print "Cannot open file $GraphFile";
	
	return (INP_FILE, DOT_FILE);
}

sub DOT_POST { 
	my ($INP,$DOT)=@_;

	close $INP;
	close $DOT;
}

sub DOT { 
	my ($str)=@_; # required parentheses !!!
    print DOT_FILE "$str\n";
}

##################################################################################

sub sym { 
	my ($s)=@_;
	$s= asc($s);
	$s =~ s/\W/_/g;
	$s =~ s/^\d/_/g;
	return $s;
}
sub str {
	my ($s)=@_;
	$s= asc($s);
	$s=~ s/\\/\\\\\\\\/;
	return $s;
}


sub lbl  {
    my($s) = @_;
    $s= asc($s);
	$s =~ s/\\/\\ /g;
	$s =~ s/\//\/ /g;
	$s =~ s/_/\_ /g;
    @Parts = split(/\s+/, $s);
	
	$maxPartLen = 10;
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

1;