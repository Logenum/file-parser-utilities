
use GraphViz::Data::Grapher;
local $/;
my $structFileName = $ARGV[0];
my $graphFileName = $ARGV[1];

open (INP, $structFileName);# || say "Cannot open read file '$structFileName'";
open (OUT, ">$graphFileName");# || say "Cannot open write file '$graphFileName'";

my $struct = <INP>;

#my $graph = GraphViz::Data::Grapher->new([3,4,5],"Hello");

my $graph = GraphViz::Data::Grapher->new($struct);

print $graph->as_text;
