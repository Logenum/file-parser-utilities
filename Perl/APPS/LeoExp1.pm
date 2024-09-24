
#printf "%4d-%02d-%02d %02d:%02d:%02d\n",$year+1900,$mon+1,$mday,$hour,$min,$sec;

package PERL_SCRIPTS;
BEGIN { push @INC, $0 =~ /^(.*)\\.*/;}  # note: required to make focus path referable !!!!!!!!!! 
use UTILS;


my $InpFile;
my $OutFile;
my $nLineNbr;
my @charBlock=();

my $matchFound;


open(IN_FILE, "$ARGV[0]") || print "Cannot open file $InpFile";
open(OUT_FILE, ">$ARGV[1]") || print "Cannot open file my $OutFile";
my $searchRegex = $ARGV[2];

while (<IN_FILE>) {
    $wholeLine = $_;	
    @parts = split ('#',$wholeLine);

    if (@parts > 1) { @actLine = $parts[0];} else { $actLine = $wholeLine;}

    if ($actLine  =~ /\s*sub\s*(\w+)/g) {
	$focusMethod = $1;
    }

    @lineChars = $actLine;

    if ($actLine  =~ /$searchRegex/g) {
	$matchFound = 1;
    }
    if ($matchFound == 1) {

    } else {
	foreach @lineChars {
	    $char = $_;
	    if ($char eq "{") {
		@charBlock=();
	    }

    }
    


 
    if  ($actLine  =~ /\s*sub\s*(\w+)/g) {
	$focusSub = $1;
    }

    




    $nLineNbr++;
}		    

close IN_FILE;
close OUT_FILE;

#################################
sub decLimit {
  
  if ($val >= 1) {
      $val--;
  } else {
      $val =0;
  }
  return  $val;
}
#################################





1;




###############################################################

for each filename in file do
    open filename
    for each line do
	take active part
	if line contains 'sub' then
	    save sub name
	    set sub section started
	end
	for each char in line do
	    switch char
		case '{':
		    if match found is FALSE do
			inc par counter
			shift line start
			restart char match buffer pushing
		    end
		case '}':
		    dec par counter  # $val = decLimit($val);
		    
		    if par counter is ZERO then
			if match found is TRUE then
			      print sub name
			      print match buffer
			      clear match buffer
			      clear par counter
			end
		    end
		default:
		     push char
	    end
	    if match at line start do
		match found is TRUE
		save match line number
	    end
	end
	if match found is TRUE do
    end
end














