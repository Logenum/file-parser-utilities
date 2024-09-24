
#printf "%4d-%02d-%02d %02d:%02d:%02d\n",$year+1900,$mon+1,$mday,$hour,$min,$sec;

package PERL_SCRIPTS;
#BEGIN { push @INC, $0 =~ /^(.*)\\.*/;}  # note: required to make Windows focus path referable !!!!!!!!!! 
BEGIN { push @INC, $0 =~ /^(.*)\/.*/;}  # note: required to make focus path referable !!!!!!!!!! 
use UTILS;

my $prevAvailStatus=-1; # initialization

open(IN_FILE, "$ARGV[0]") || print "Cannot open file $InpFile";
open(OUT_FILE, ">$ARGV[1]") || print "Cannot open file $InpFile";

while (<IN_FILE>) {
	if (/^(\d+).*available\s+(\d+).*/) { 
	      $time 		= $1;
	      $availStatus 	= $2;
	      ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);

	      if ($availStatus != $prevAvailStatus) {
		  $year = $year+1900;
		  $mon  = $mon+1;
		  $humanDate = "$year $mon,$mday,$hour:$min:$sec";
		  if (/.*(error.*)\s+\w+_.*/) {
			$error = $1;
		  } else {
			$error = "";
		  }

		  print OUT_FILE "   $humanDate:  $error  available = $availStatus\n";
		  $prevAvailStatus = $availStatus;

		  @aParts = split(/\s+/,$_);

		  
	      }


	}	
}
close IN_FILE;
close OUT_FILE;

1;
