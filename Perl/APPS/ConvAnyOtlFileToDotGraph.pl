#!/usr/bin/perl

BEGIN {push @INC,"E:/KIT/PERL/LIB"}

use LogenUtils; # must be to access the "<BAG>" library file 
use strict;
use warnings;

use feature "switch";
=nut
Every topic is a source node
Source Node is plotted IF
	Next topic line is found OR 
	First link line is found
Edge and Target Node are plotted IF
	Link line is found
	IF target node is NOT focus document node THEN
		create target node
			target node symbol is "File"
			
			
FOR each line DO


=cut	

my $sTOPIC_CONTEXT_CATCH_rgx = "^.*-CONTEXT:\\s*(\\w+).*\$";


my @asTOPIC_ATTRIBUTE_CATCHES_rgx = 	("^.*-TYPE:\\s*(\\w+).*\$",
										 "^.*-ROLE:\\s*(\\w+).*\$");

my @asTOPIC_LINK_CATCHES_rgx = ("^\\s*\\[(.*)\\].*(\\w+).*\$",
							   "^\\s*(\\w+).*\\[(.*)\\]\\s*\$", 
							   "^\\s*\\[(.*)\\]\\s*\$");
							   

my @asEXTERNAL_LINK_CATCHES_rgx = ("^.*explorer.exe\\\"\\s+(.*)\\].*\$",
									"^\\s*(www\..*)\$");
							   
							   

my @asTopicNames=(); 

my %hBvalues; # buffered values
my %hSvalues;
my %hEvalues;
my %hTvalues;


my $sServiceUrl;
my $sServiceFileName;
my $sPossibleLink;

# TODO: change: 191107
# -	extraction: values are stored in a hash
# -	reporting: 	template tags are replaced by values from extraction hash

# https://www.graphviz.org/doc/info/attrs.html

# TODO: modify 191104:
#	-	nodes: 
#		-	topic names
#			-	possible cluster name is located just below
#	-	links:
#		-	other topics in same file
#		-	file and URL links ---> specific "external" nodes
#      ["explorer.exe" C:\TMP]
#	-	associations:
#		-	on same or next line of link
#	-	attributes:	
#		-	below topic names
#	-	comment nodes:
#		-	tagged text lines anywhere


INITLOGEN($0);  # -obs: "$0" contains focus script plain name (for trace file naming)



my ($sOtlFileName, $sDotFileName) = extractArguments(\@ARGV);

my $IN_FILE = openReadFile($sOtlFileName);
my $OUT_FILE = openWriteFile($sDotFileName);

if (fileErrors()) {
	QUITLOGEN("file access error");
} 

my $sDotLine="";
dutyH(\%hBvalues, "source node data entry"); # buffered values
dutyH(\%hSvalues, "source node data save");
dutyH(\%hEvalues, "edge data");
dutyH(\%hTvalues, "target node data save");


my @asAllLinesIn = <$IN_FILE>;
my $sFirstLineIn = shift @asAllLinesIn; # gets and removes first line

if ($sFirstLineIn !~ m/$g_sOTL_FILE_FIRST_LINE_MATCH_rgx/g){
	QUITLOGEN("no match to '$sFirstLineIn' by '$g_sOTL_FILE_FIRST_LINE_MATCH_rgx' so '$sOtlFileName' is NOT an OTL file !");
}

#============ collects all topic names =================
foreach my $sLine (@asAllLinesIn) {
	if ($sLine =~ m/$g_sOTL_TOPIC_NAME_CATCH_rgx/g) {
		TRACE("Topic Name: '$1'");
		push @asTopicNames,$1;
	}
} 

writeToFile($g_sDOT_GRAPH_HEADER_tpl, $OUT_FILE);

setFlag("fgIsFirstTopic");


my $nRegexPos=0;
#============ process all lines =================
foreach my $sLine (@asAllLinesIn) {
		#=================================================
		# Event generation region
		#=================================================
		$sLine =~ s/#.*//g;    # removes possible line-tail comment
		
		if ($sLine =~ m/^\s*$/g) {
			next;
		}
		TRACE("line: '$sLine'");
		if (CATCH($sLine, $g_sOTL_TOPIC_NAME_CATCH_rgx)) {
			produceEvent("evTopicHeading");
			useH(\%hBvalues);
			putH('Name', sym($A));
			putH('Style', ", style=filled");
			putH('Fillcolor', ", fillcolor=green");
			putH('Label', "label=\"".lbl($A)."\"");	
		} else {  # links
			if (CATCHFIRST($sLine, \@asEXTERNAL_LINK_CATCHES_rgx)){
				my $sTargetNode = "";
				my $sEdgeLabel = "";
				useH(\%hTvalues);
				if ($gPOS == 1) {
					produceEvent("evExternalLink");
					$sTargetNode = $A;
					$sEdgeLabel = "label=\"directory\"";
					putH('Anyattr',",dir=\"forward\"",\%hEvalues);
					putH('Shape',", shape=parallelogram");
				} elsif ($gPOS == 2) {
					produceEvent("evExternalLink");
					$sTargetNode = $A;
					$sEdgeLabel = "label=\"WWW link\"";
					putH('Anyattr',",dir=\"forward\"",\%hEvalues);
					putH('Shape',", shape=circle");
				} else {
					TRACE("TODO: add handling for regex position '$nRegexPos'");
				}
				putH('Name', sym($sTargetNode));
				putH('Label',"label=\"".lbl($sTargetNode)."\"");
				putH('Label',$sEdgeLabel,\%hEvalues);
				putH('Sname',$hSvalues{'Name'},\%hEvalues);
				putH('Tname',sym($sTargetNode),\%hEvalues);
			} elsif  (CATCHFIRST($sLine, \@asTOPIC_LINK_CATCHES_rgx)) {   # allways plot edge and target
				my $sTargetNode = "";
				my $sEdgeLabel = "";
				useH(\%hEvalues);
				if ($gPOS == 1) {
					produceEvent("evTopicLink");
					$sTargetNode = $A;
					$sEdgeLabel = $B;
					putH('Dir',",dir=\"forward\"");
				} elsif ($gPOS == 2) {
					produceEvent("evTopicLink");
					$sTargetNode = $B;
					$sEdgeLabel = $A;
					putH('Dir',",dir=\"back\"");
				} elsif ($gPOS == 3) {
					produceEvent("evTopicLink");
					$sTargetNode = $A;
					putH('Dir',",dir=\"none\"");
				} else {
					TRACE("TODO: add handling for regex position '$nRegexPos'");
				}	
				
				putH('Label',"label=\"".lbl($sEdgeLabel)."\"");
				putH('Sname',$hSvalues{'Name'});
				putH('Tname', $sTargetNode);
				
				#writeToFile(processTitleCaseTagsTemplate($sTargetNodePlotTpl, \%hTvalues), $OUT_FILE);
			} elsif  (CATCHFIRST($sLine, \@asTOPIC_ATTRIBUTE_CATCHES_rgx)) {  # no plot, just collecting attributes for source node
				useH(\%hSvalues);
				my $sTopicType		= $A;
				if ($sTopicType eq "CLASS") {
					putH('Shape', ",shape=record");
					my $sLabelText = getH('Label');
					putH('Label', "label=\"$sLabelText| | \"");
					produceEvent("evTopicAttr");
				} elsif ($sTopicType eq "COMPONENT") {
					produceEvent("evTopicAttr");
				} else {
				
				}
				#----------------------------------------------	
			} elsif  (CATCH($sLine, $sTOPIC_CONTEXT_CATCH_rgx)) {  # creates target node and edge
				produceEvent("evTopicContext");
				useH(\%hTvalues);
				putH('Name', sym($A));
				putH('Shape',",shape=box");
				#----------------------------------------------	
				useH(\%hEvalues);
				putH('Sname',$hSvalues{'Name'});
				putH('Tname', $hTvalues{'Name'});
				putH('Label',"");
				putH('Anyattr', ",fontsize=1,dir=\"forward\",type=solid, arrowhead=odiamond, taillabel=1");
			} else {  # do nothing	
			
			} 	
		}
		#==============================================
		# Event handler region
		#=================================================
		my $sEvent = consumeIfEvent();
		my $sDotLine;
			if ($sEvent eq "") {
				next; 
			}
			if ($sEvent eq "evTopicHeading") { #=================================
				resetFlag("fgFocusTopicSrcNodePlotDone");
				if (isFlag("fgIsFirstTopic")) {
					resetFlag("fgIsFirstTopic"); # no output
				} else {
					if (isFlagNot("fgFocusTopicSrcNodePlotDone")) {
						$sDotLine = processTitleCaseTagsTemplate($g_sDOT_NODE_PLOT_tpl, \%hSvalues);
						writeToFile(commentIfInvalidGraphvizLine($sDotLine), $OUT_FILE);
					}
				}
				cloneH(\%hBvalues,\%hSvalues);
			} elsif ($sEvent eq "evTopicAttr") { #====================================
				TRACE("attribute saved, will be assigned to some later plot");
			} elsif ( 	$sEvent eq "evExternalLink" ||  #============================
						$sEvent eq "evTopicLink" ||
						$sEvent eq "evTopicContext")  {
				if (isFlagNot("fgFocusTopicSrcNodePlotDone")) {
					$sDotLine = processTitleCaseTagsTemplate($g_sDOT_NODE_PLOT_tpl, \%hSvalues);
					writeToFile(commentIfInvalidGraphvizLine($sDotLine), $OUT_FILE);
					setFlag("fgFocusTopicSrcNodePlotDone"); 
				}
				$sDotLine = processTitleCaseTagsTemplate($g_sDOT_EDGE_PLOT_tpl, \%hEvalues);
				writeToFile(commentIfInvalidGraphvizLine($sDotLine), $OUT_FILE);
				$sDotLine = processTitleCaseTagsTemplate($g_sDOT_NODE_PLOT_tpl, \%hTvalues);
				writeToFile(commentIfInvalidGraphvizLine($sDotLine), $OUT_FILE);
				
			} elsif ($sEvent eq "TBD: implement later") { #========================
			} else {
				TRACE("undefined event '$sEvent', handling ignored");
			}
			
		}


writeToFile($g_sDOT_GRAPH_FOOTER_tpl, $OUT_FILE);

close $IN_FILE;
close $OUT_FILE;

QUITLOGEN();


=comments




=cut



