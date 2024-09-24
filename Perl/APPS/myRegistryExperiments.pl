use Win32::Registry;
my $handle;

open (TRACE, ">PerlTrace.log");

my $RegisterName="mytest5";
my $KeyHandle;

my $ValByKey;
my $KeyName="mytest5";

my (@key_list, $key, %values);

#Notetab Clip register saving: ^!SaveRegValue HKEY_CURRENT_USER\mytest2:JustTest=^%p_NowDateTimeAsSymbolName%

$HKEY_CURRENT_USER->Open($RegisterName, $KeyHandle); # this call observed "myTest2" existence OK !!!

#$KeyHandle->QueryValue( $KeyName , $ValByKey);
#$ValByKey = $KeyHandle->GetValue("");

print "Register '$RegisterName': key '$KeyName' gives value '$ValByKey'\n";

$KeyHandle->GetKeys(\@key_list);
print "$RegisterName keys\n";
foreach $key (@key_list)
{
	$ValByKey = $KeyHandle->GetValue($Key);
	print "$key\n";
}

$KeyHandle->GetValues(\%values);
print "$RegisterName values\n";
foreach $value (%values)
{
	print "value: $value\n";
}

#$value = $hkey->GetValue("JustTest");
#print "$value";

$KeyHandle->Close();

# print TRACE "EnvVar: $EnvVar\n";

# while ($Line = <STDIN>) # catches painted text
# {
	# chop $Line; # otherwise a special char will appear
	# print "$Line";
# }

# close (TRACE);