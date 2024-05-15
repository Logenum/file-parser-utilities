package GraphvizUtils;
use Data::Dumper;
use JSON;
use TraceUtils;
use EventUtils;
use v5.20;
# copied and edited here as a reference for manual conversion to Python
my $sOBJECT_TITLE = "OBJECT";

# -	Graphviz -specific line arrays generation
# both configurable and hard-coded logic to generate graphviz dot syntax lines
# from some formally repeated text lines 

# 160422: dictionary keys renamed: postfixes indicate now (lifecycle) "status" of corresponding value 

#========== GRAPHVIZ WWW LINKS =========================================
# http://www.graphviz.org/doc/info/shapes.html  				!: shapes
# http://www.graphviz.org/Gallery/undirected/fdpclust.html    	!: indented clusters
# http://wingraphviz.sourceforge.net/wingraphviz/language/colorname.htm  !: node colors
#
#=======================================================================
# NOTES:
# "...filled...fillcolor..." produces colored nodes with black frames
#
#
#=======================================================================
my $sCLUSTER_tpl = "subgraph cluster__cluster_name_ { style=filled; fillcolor=lemonchiffon1;label =\"_cluster_label_\"; _node_name_}";
# requires keyword "cluster"
# node names within a cluster are separated by ';' !!!

my $sPLAIN_NODE_tpl = "_node_name_ [label = \\\"_node_label_\\\" , _node_attr_]";
#my $sPLAIN_NODE_tpl = "_node_name_ [label =\\\"_node_label_\\\" _node_attr_]";
my $sRECORD_NODE_tpl = "_node_name_ [label =\\\"_node_label_||\\\" ,_node_attr_]";
my $sTAP_NODE_tpl = "_node_name_ \[label = \"_node_label_\",shape=circle, color=grey]"; # attributes: parentheses are not necessary
# circle 'height' = diameter in inches
my $sEDGE_tpl = "_node_name_a_ -> _node_name_b_ \[label =\"_edge_label_\", _entry_edge_attr_]"; 
 # TODO: add more choises
my $sSERVICE_NODE_DOT_TEMPLATES_json = "{\"CONSTRUCTOR\":\"$sRECORD_NODE_tpl\",
										\"SERVICE\":\"$sPLAIN_NODE_tpl\"}";  # for database, file, event etc.


#TODO: add horizontal class node template

my $sNOT_IN_USE = "NOT_IN_USE";

my $sDEFAULT_ATTR = "USE_DEFAULT_ATTR";

#===============================================================================
sub new { my ($class, $sDuty) = @_;
#===============================================================================

	
	my $self = {
		sDuty 							=> $sDuty,		# the role or purpose of THIS object
		sLatestLine 						=> "",  			# for debugging purposes
		sLatestCaptureRgx 				=> "", 	# for debugging purposes
		rxCaptureConfig 			=> 0,		
		sLatestContextFileName 				=> "NOT_INITIALIZED",
		sLatestContextFileNameAsSym 		=> "NOT_INITIALIZED",		
		sLatestActivityNodeName => "NOT_INITIALIZED",  # activity node ellipses are chained with default edge line
		sLatestStateNodeName => "NOT_INITIALIZED",  	  # state node boxes are mutually connected with thick edge line type
		sLatestServiceNodeName => "NOT_INITIALIZED",   # e.g. databases, interfaces, actors,...
		sLatestCommentNodeName => "NOT_INITIALIZED",  # specific node for comment because it can be added to Branch nodes
		sLatestChainNodeName => "NOT_INITIALIZED",    #  activity node or state node
		sLatestChainNodeType 				=> "ACTIVITY",    #  initialization
		sLatestCommentableNodeName 			=> "NOT_INITIALIZED",    #  activity node or state node or Service node
		nNodeUniqueSeqNbr 					=> 0,  	  #  instantiating part for node names
		nActivityEdgeUniqueSeqNbr 			=> 0,		  #  for edge order numbering
		nStateEdgeUniqueSeqNbr 				=> 0,		  #  for edge order numbering
	};
	bless $self, $class;
	MM::TRACE_SUB($sDuty);   
	MM::TRACE_RET();
	return $self;
}


#===============================================================================
sub convJsonToCaptureCfg { my ($self, $raCfgDataAsJson) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{sDuty});
	MM::TRACE_BAG($raCfgDataAsJson,"comment");  # contains JSON and possible non-JSON comment lines
	#TODO: add removal of possible comment lines
	# http://stackoverflow.com/questions/23886471/perl-using-grep-to-delete-element-of-array-that-match-a-pattern-and-do-not-matc
	my @asJson =  grep {! /^\s*#.*/} @$raCfgDataAsJson; # removes lines starting with '#'  (= my comment notation)
	# removes lines starting with '#'  (= not valid JSON line)
	my $sJson = join(' ',@asJson);  # possible comments removed
	my $rxConfigData 	= MM::fromJson($sJson, "node type tag catchers");
	MM::TRACE_BAG($rxConfigData,"complex config data");
	$self->{rxCaptureConfig} = $rxConfigData;
	MM::TRACE_RET();
}


#===============================================================================
sub getInOutFileNamesByCfgData { my ($self) = @_;
#===============================================================================
	my $sInFileFullName = "NOT_DEFINED";
	my $sOutFileFullName = "NOT_DEFINED";
	my $rhCapture;
	MM::TRACE_SUB($self->{sDuty});
	my $rahCaptureConfigs = $self->{rxCaptureConfig};
	
	foreach $rhCapture (@$rahCaptureConfigs) {
		if (exists $rhCapture->{aOriginFileNameStr}) {
			$sInFileFullName = $rhCapture->{aOriginFileNameStr};
		}
		if (exists $rhCapture->{aResultFileNameStr}) {
			$sOutFileFullName = $rhCapture->{aResultFileNameStr};
		}
	}
	MM::TRACE_RET();
	return ($sInFileFullName, $sOutFileFullName);
}

#===============================================================================
sub getContext { my ($self) = @_;
#===============================================================================
	return $self->{sDuty};
}

#===============================================================================
sub getNodeUniqueSeqNbr { my ($self) = @_;
#===============================================================================
	my $nId = $self->{nNodeUniqueSeqNbr};
	$nId++;
	$self->{nNodeUniqueSeqNbr}=$nId;
	return $nId;
}



#===============================================================================
sub getActivityEdgeUniqueSeqNbr { my ($self) = @_;
#===============================================================================
	my $nId = $self->{nActivityEdgeUniqueSeqNbr};
	$nId++;
	$self->{nActivityEdgeUniqueSeqNbr}=$nId;
	return $nId;
}
#===============================================================================
sub getStateEdgeUniqueSeqNbr { my ($self) = @_;
#===============================================================================
	my $nId = $self->{nStateEdgeUniqueSeqNbr};
	$nId++;
	$self->{nStateEdgeUniqueSeqNbr}=$nId;
	return $nId;
}
#===============================================================================
sub setContext { my ($self, $sName) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{sDuty});
	$self->{sLatestContextFileName} = $sName;
	$self->{sLatestContextFileNameAsSym} = MM::sym($sName);
	MM::TRACE("file='$sName'");
	MM::TRACE_RET();
}
#===============================================================================
sub getContextFileName { my ($self) = @_;
#===============================================================================
	return $self->{sLatestContextFileName};
}
#===============================================================================
sub getContextFileNameAsSym { my ($self) = @_;
#===============================================================================
	return $self->{sLatestContextFileNameAsSym};
}
#===============================================================================
sub addActivityNode { my ($self, $sName) = @_;
#===============================================================================
	$self->{sLatestActivityNodeName} = $sName;
	$self->{sLatestChainNodeName} = $sName;
	$self->{sLatestCommentableNodeName} = $sName;
}
#===============================================================================
sub getLatestActivityNode { my ($self) = @_;
#===============================================================================
	return $self->{sLatestActivityNodeName};
}
#===============================================================================
sub setStateNode { my ($self, $sName) = @_;
#===============================================================================
	$self->{sLatestStateNodeName} = $sName;
	$self->{sLatestChainNodeName} = $sName;
	$self->{sLatestCommentableNodeName} = $sName;
}
#===============================================================================
sub getLatestStateNode { my ($self) = @_;
#===============================================================================
	return $self->{sLatestStateNodeName};
}
#===============================================================================
sub setServiceNode { my ($self, $sName) = @_;
#===============================================================================
	$self->{sLatestServiceNodeName} = $sName;
	$self->{sLatestCommentableNodeName} = $sName;
}
#===============================================================================
sub getLatestServiceNode { my ($self) = @_;
#===============================================================================
	return $self->{sLatestServiceNodeName};
}

#===============================================================================
sub getLatestChainNode { my ($self) = @_;  # state node or activity node
#===============================================================================
	return $self->{sLatestChainNodeName};
}
#===============================================================================
sub getLatestChainNodeType { my ($self) = @_;  # state node or activity node
#===============================================================================
	return $self->{sLatestChainNodeType};
}
#===============================================================================
sub addCommentNode { my ($self, $sName) = @_;
#===============================================================================
	$self->{sLatestCommentNodeName} = $sName;
	$self->{sLatestCommentableNodeName} = $sName;
}
#===============================================================================
sub getLatestCommentableNode { my ($self) = @_;
#===============================================================================
	return $self->{sLatestCommentableNodeName};
}


#===============================================================================
sub getItemDataIfLineMatch { my ($self, $sLine) = @_;
#===============================================================================
# tries to capture given line by given regex
# if all patterns captured, replaces all numeric order tags in given templates with corresponding captured values 
	MM::TRACE_SUB($self->{sDuty});
	my $rhCapture;
	my $sCaptureRgx;
	my $sNodeType;
	my $sNodeLabel;
	my $sNodeAttr;
	my $sTapNodeLabel;
	my $sEntryEdgeLabel;  		# label for input edge to node
	my $sEntryEdgeAttr; 
	my $sDutyLabel; 	# for lines which may contain file name
	my $bStatus=0;  # initial quess: 
	my @asCaptures;
	my $sCapture;
	my $nCapturesCnt;
	my $nCaptureTagPos=0;
	
	my $rhCaptureConfigUpdatedCopy;	# contains updated templates etc. 
	my $sNodeLabelTemplate;
	my $sEntryEdgeLabelTemplate;

	my $sTapNodeLabelTemplate;
	my $rhCapture;
	
	my $rahCaptureConfigs = $self->{rxCaptureConfig};
	
	foreach $rhCapture (@$rahCaptureConfigs) {
	
		if (! exists $rhCapture->{aCaptureRgx}) {
			MM::TRACE("item does not contain key 'aCaptureRgx'");
			if (! exists $rhCapture->{aOriginFileNameStr}) {  # e.g a log file
				
			}
			next;
		}
		$sCaptureRgx = $rhCapture->{aCaptureRgx};
		MM::TRACE("try match '$sCaptureRgx' to line '$sLine'");
		if (@asCaptures = ($sLine =~ /$sCaptureRgx/g)) {
			$bStatus=1;
			# TODO: edit these key names to match those in [c:\the\MILL\YARD\APPS\Python\OtlToJsonForGraphConf.py] 160420
			$nCapturesCnt = length @asCaptures;
			$sNodeType 						= $rhCapture->{aNodeTypeStr};
			$sNodeLabelTemplate				= $rhCapture->{aNodeLabelTpl};
			
			if (exists $rhCapture->{aNodeAttrStr}) {
				$sNodeAttr	= $rhCapture->{aNodeAttrStr};
			} else {
				$sNodeAttr = $sDEFAULT_ATTR;
			}
			if (exists $rhCapture->{aEntryEdgeAttrStr}) {
				$sEntryEdgeAttr	= $rhCapture->{aEntryEdgeAttrStr};
			} else {
				$sEntryEdgeAttr = $sDEFAULT_ATTR;
			}
			$sEntryEdgeLabelTemplate		= $rhCapture->{aEntryEdgeLabelTpl};		
			$sTapNodeLabelTemplate			= $rhCapture->{aTapNodeLabelTpl};  # exist only in service node
			MM::TRACE("node type '$sNodeType' from line '$sLine' by regex '$sCaptureRgx'");
			$sNodeLabel 		= $sNodeLabelTemplate;
			$sEntryEdgeLabel 	= $sEntryEdgeLabelTemplate;
			$sTapNodeLabel 		= $sTapNodeLabelTemplate;
			
			$self->{sLatestLine} 		= $sLine;   		# for debugging purposes
			$self->{sLatestCaptureRgx} 	= $sCaptureRgx;  	# for debugging purposes
			
			$rhCaptureConfigUpdatedCopy->{aNodeTypeStr} 		= $sNodeType;  # value will be updated from "template" to "string"
			$rhCaptureConfigUpdatedCopy->{aNodeAttrStr} 		= $sNodeAttr;
			$rhCaptureConfigUpdatedCopy->{aEntryEdgeAttrStr} 	= $sEntryEdgeAttr;			
			
			foreach $sCapture (@asCaptures) {
				# replaces possible percentage -tagged fields in all template strings  	 
				$nCaptureTagPos++;
				$sNodeLabel 		=~ s/%$nCaptureTagPos%/$sCapture/g;
				$sEntryEdgeLabel 	=~ s/%$nCaptureTagPos%/$sCapture/g;
				$sTapNodeLabel 		=~ s/%$nCaptureTagPos%/$sCapture/g;
			}
			
			MM::TRACE("---- Checking, if templates are filled OK ----");
			if ($sNodeLabel =~ /.*%\d+%/g) {
				MM::TRACE("inadequately filled node label template '$sNodeLabel'");
				$rhCaptureConfigUpdatedCopy->{aNodeLabelStr} = $sNOT_IN_USE;
				$bStatus = 0;
			}  else {
				$rhCaptureConfigUpdatedCopy->{aNodeLabelStr} = $sNodeLabel;
			}
			if ($sEntryEdgeLabel =~ /.*%\d+%/g) {
				MM::TRACE("inadequately filled entry edge label template '$sEntryEdgeLabel'");
				$rhCaptureConfigUpdatedCopy->{aEntryEdgeLabelStr} = $sNOT_IN_USE;
				$bStatus = 0;
			} else {
				$rhCaptureConfigUpdatedCopy->{aEntryEdgeLabelStr} = $sEntryEdgeLabel;
			}
			if ($sTapNodeLabel =~ /.*%\d+%/g) {
				MM::TRACE("inadequately filled auto node label template '$sTapNodeLabel'");
				$rhCaptureConfigUpdatedCopy->{aTapNodeLabelStr} = $sNOT_IN_USE;
				$bStatus = 0;
			} else {
				$rhCaptureConfigUpdatedCopy->{aTapNodeLabelStr} = $sTapNodeLabel;
			}
			
			last;
		}
	}
	if ($bStatus == 1) {
		MM::TRACE("type/node/edge/tap = '$sNodeType'/'$sNodeLabel'/'$sEntryEdgeLabel'/'$sTapNodeLabel'");
	} 
	MM::TRACE_RET();
	return ($rhCaptureConfigUpdatedCopy);
}

#===============================================================================
sub buildStateNodeDotLines { my ($self, $rhUpdatedConfig) = @_;
#===============================================================================
	# dot line group building logic when "STATE" -tagged line processed
	MM::TRACE_SUB($self->{sDuty});
	my $sStateNodeLabel = $rhUpdatedConfig->{aNodeLabelStr};
	my $sNodeAttr = $rhUpdatedConfig->{aNodeAttrStr};
	my $sEntryEdgeAttr = $rhUpdatedConfig->{aEntryEdgeAttrStr};
	my $nSeqNbr = $self->getStateEdgeUniqueSeqNbr();
	
	my $sLine = $self->{sLatestLine};
	my $sRgx = $self->{sLatestCaptureRgx};
	
	
	if ($sNodeAttr eq $sDEFAULT_ATTR) {
		$sNodeAttr = "shape=box";
	}
	
	if ($sEntryEdgeAttr eq $sDEFAULT_ATTR) {
		$sEntryEdgeAttr = "dir=forward, style=bold";
	}
	
	my @asDotSyntaxLines 	= ();
	my $sFilledTemplate;
	my $sStateNodeName = MM::sym($sStateNodeLabel);   # no automatic individual part to activity node names
	my $sStateNodeLabel = MM::lbl($sStateNodeLabel); # for sure
	my $sLatestChainNodeName = $self->getLatestChainNode();
	my $sLatestChainNodeType = $self->getLatestChainNodeType();
	my $sLatestStateNodeName = $self->getLatestStateNode();
	my $sLatestActivityNodeName = $self->getLatestActivityNode();
	$sFilledTemplate = $sPLAIN_NODE_tpl;
	$sFilledTemplate =~ s/_node_name_/$sStateNodeName/g;
	$sFilledTemplate =~ s/_node_label_/$sStateNodeLabel/g;
	$sFilledTemplate =~ s/_node_attr_/$sNodeAttr/g;
	
	push(@asDotSyntaxLines, "\n// ******* STATE NODE ********************");
	push(@asDotSyntaxLines, "\n// DETECTION: regex/line = '$sRgx'/'$sLine'");
	push(@asDotSyntaxLines, $sFilledTemplate);
	push(@asDotSyntaxLines, "// build edge from previous state node to this state node");
	$sFilledTemplate = $sEDGE_tpl;
	if ($sLatestStateNodeName eq "NOT_INITIALIZED") {   # no state detected yet 
		MM::TRACE("ignoring state transition from '$sLatestStateNodeName' to '$sStateNodeName'");
	} else {
		$sFilledTemplate =~ s/_node_name_a_/$sLatestStateNodeName/g;
		$sFilledTemplate =~ s/_entry_edge_attr_/$sEntryEdgeAttr/g;
		$sFilledTemplate =~ s/_node_name_b_/$sStateNodeName/g;
		$sFilledTemplate =~ s/_edge_label_/$nSeqNbr/g;
		push(@asDotSyntaxLines, $sFilledTemplate)
	}
;
	push(@asDotSyntaxLines, "// build edge from previous activity node to this state node");
	$sFilledTemplate = $sEDGE_tpl;
	$sFilledTemplate =~ s/_node_name_a_/$sLatestActivityNodeName/g;
	$sFilledTemplate =~ s/_node_name_b_/$sStateNodeName/g;
	$sFilledTemplate =~ s/_edge_label_//g;
	$sFilledTemplate =~ s/_entry_edge_attr_/style=dashed/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	
	$self->setStateNode($sStateNodeName);
	MM::TRACE_RET();
	return \@asDotSyntaxLines;
}
#=
#===============================================================================
sub buildServiceNodeDotLines { my ($self, $rhUpdatedConfig) = @_;
#===============================================================================
	# dot line group building logic when "SERVICE" -tagged line processed
	MM::TRACE_SUB($self->{sDuty});
	my $sServiceNodeLabel 		= $rhUpdatedConfig->{aNodeLabelStr};
	my $sTapNodeLabel 			= $rhUpdatedConfig->{aTapNodeLabelStr};
	my $sServiceNodeType 		= $rhUpdatedConfig->{aNodeTypeStr};
	my $sNodeAttr 				= $rhUpdatedConfig->{aNodeAttrStr};
	my $sEntryEdgeAttr 			= $rhUpdatedConfig->{aEntryEdgeAttrStr};
	my @asDotSyntaxLines 		= ();
	my $sLatestFileNameAsSym 	=$self->{sLatestContextFileNameAsSym};
	my $sDutyFileAsLabel 	=$self->getContextFileName();
	my $sLatestChainNodeName 	= $self->getLatestChainNode();
	my $sLatestChainNodeType 	= $self->getLatestChainNodeType();
	my $rhDotTemplates 			= MM::fromJson($sSERVICE_NODE_DOT_TEMPLATES_json,"dot templates as JSON");
	my $sFilledTemplate;
	my $sServiceNodeName;
	my $sTapNodeName;
	
	if ($sNodeAttr eq $sDEFAULT_ATTR) {
		$sNodeAttr = "shape=ellipse";
	}
	if ($sEntryEdgeAttr eq $sDEFAULT_ATTR) {
		$sEntryEdgeAttr = "dir=forward, style=bold";
	}
	my $sLine 	= $self->{sLatestLine};
	my $sRgx 	= $self->{sLatestCaptureRgx};
	
	
	
	MM::TRACE("Type/Label/TapNodeLabel = '$sServiceNodeType'/'$sServiceNodeLabel'/'$sTapNodeLabel'");
	# builds auto doer node for Service node
	
	push(@asDotSyntaxLines, "\n// ******* SERVICE NODE ***********************");
	push(@asDotSyntaxLines, "\n// DETECTION: regex/line = '$sRgx'/'$sLine'");
	push(@asDotSyntaxLines, "//------ builds tap node ------------");
	$sTapNodeName = $self->getNodeUniqueSeqNbr();
	$sTapNodeName = $sLatestFileNameAsSym."_".$sTapNodeName;  # activity node is within file
	$self->addActivityNode($sTapNodeName);
	$sFilledTemplate = $sTAP_NODE_tpl;
	$sFilledTemplate =~ s/_node_name_/$sTapNodeName/g;
	$sFilledTemplate =~ s/_node_label_/$sTapNodeLabel/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	push(@asDotSyntaxLines, "//------ inserts auto acti onnode to cluster ------------");
	$sFilledTemplate = $sCLUSTER_tpl;
	$sFilledTemplate =~ s/_cluster_name_/$sLatestFileNameAsSym/g;
	$sFilledTemplate =~ s/_cluster_label_/$sDutyFileAsLabel/g;
	$sFilledTemplate =~ s/_node_name_/$sTapNodeName/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	push(@asDotSyntaxLines, "//------ builds edge from latest state or activity node to tap node ------------");
	$sFilledTemplate=$sEDGE_tpl;
	$sFilledTemplate =~ s/_node_name_a_/$sLatestChainNodeName/g;
	$sFilledTemplate =~ s/_node_name_b_/$sTapNodeName/g;
	$sFilledTemplate =~ s/_edge_label_//g;
	$sFilledTemplate =~ s/_entry_edge_attr_/style=dashed/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	push(@asDotSyntaxLines, "//------ builds Service node '$sServiceNodeType' ------------");
	$sFilledTemplate = $$rhDotTemplates{$sServiceNodeType};
	MM::TRACE("empty template = $sFilledTemplate");
	$sServiceNodeName = MM::sym($sServiceNodeLabel);   # no automatic individual part to Service node names
	$sServiceNodeLabel = MM::lbl($sServiceNodeLabel);  # for sure
	$sFilledTemplate =~ s/_node_name_/$sServiceNodeName/g;  	
	$sFilledTemplate =~ s/_node_label_/$sServiceNodeLabel/g;
	$sFilledTemplate =~ s/_node_attr_/$sNodeAttr/g; 	
	push(@asDotSyntaxLines, $sFilledTemplate);
	
	push(@asDotSyntaxLines, "//------ builds edge from tap node to Service node ------------");
	$sFilledTemplate=$sEDGE_tpl;
	$sFilledTemplate =~ s/_node_name_a_/$sTapNodeName/g;
	$sFilledTemplate =~ s/_node_name_b_/$sServiceNodeName/g;
	$sFilledTemplate =~ s/_edge_label_//g;
	$sFilledTemplate =~ s/_entry_edge_attr_/$sEntryEdgeAttr/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	$self->setServiceNode($sServiceNodeName);
	MM::TRACE_RET();
	return \@asDotSyntaxLines;
}
#===============================================================================
sub buildActivityNodeDotLines { my ($self, $rhUpdatedConfig) = @_;
#===============================================================================

	# dot line group building logic when "ACTIVITY" -tagged line processed
	my $sFilledTemplate;
	my $sActivityNodeName;
	my $sActivityNodeFullName;
	my $nSeqNbr;
	my $sEdgeLineType="unknown";
	my $sFilledTemplate;
	MM::TRACE_SUB($self->{sDuty});
	my $sDutyFileAsName =$self->getContextFileNameAsSym();
	my $sDutyFileAsLabel =$self->getContextFileName();
	my @asDotSyntaxLines 	= ();
	my $sLatestChainNodeName 	= $self->getLatestChainNode();
	my $sLatestChainNodeType = $self->getLatestChainNodeType();
	my $sLine = $self->{sLatestLine};
	my $sRgx = $self->{sLatestCaptureRgx};
	
	my $sActivityNodeLabel = $rhUpdatedConfig->{aNodeLabelStr};
	my $sNodeAttr = $rhUpdatedConfig->{aNodeAttrStr};
	my $sEntryEdgeAttr = $rhUpdatedConfig->{aEntryEdgeAttrStr};
	
	if ($sNodeAttr eq $sDEFAULT_ATTR) {
		$sNodeAttr = "shape=ellipse";
	}
	if ($sEntryEdgeAttr eq $sDEFAULT_ATTR) {
		$sEntryEdgeAttr = "dir=forward, style=bold";
	}
	
	$sActivityNodeName = MM::sym($sActivityNodeLabel);   # no automatic individual part to activity node names
	$sActivityNodeLabel = MM::lbl($sActivityNodeLabel);  # for sure
	$sActivityNodeFullName = $sActivityNodeName."_in_".$sDutyFileAsName;
	
	
	push(@asDotSyntaxLines, "\n// ******* ACTIVITY NODE ***********************");
	push(@asDotSyntaxLines, "\n// DETECTION: regex/line = '$sRgx'/'$sLine'");
	push(@asDotSyntaxLines, "//------ builds cluster containing activity node------------");
	$sFilledTemplate = $sCLUSTER_tpl;
	$sFilledTemplate =~ s/_cluster_name_/$sDutyFileAsName/g;
	$sFilledTemplate =~ s/_cluster_label_/$sDutyFileAsLabel/g;
	$sFilledTemplate =~ s/_node_name_/$sActivityNodeFullName/g;
	
	push(@asDotSyntaxLines, $sFilledTemplate);
	
	push(@asDotSyntaxLines, "//------ builds activity node ------------");
	MM::TRACE("activity node label = '$sActivityNodeLabel'");
	$nSeqNbr = $self->getActivityEdgeUniqueSeqNbr();
	# builds activity node
	$sFilledTemplate = $sPLAIN_NODE_tpl;
	$sFilledTemplate =~ s/_node_name_/$sActivityNodeFullName/g;  	
	$sFilledTemplate =~ s/_node_label_/$sActivityNodeLabel/g;
	$sFilledTemplate =~ s/_node_attr_/$sNodeAttr/g;	
	MM::TRACE("filled template = '$sFilledTemplate'");
	push(@asDotSyntaxLines, $sFilledTemplate);
	
    push(@asDotSyntaxLines, "//------ builds edge to activity node ------------");
	$sFilledTemplate=$sEDGE_tpl;
	$sFilledTemplate =~ s/_node_name_a_/$sLatestChainNodeName/g;
	$sFilledTemplate =~ s/_node_name_b_/$sActivityNodeFullName/g;
	if ($sLatestChainNodeType eq "STATE") {
		$sEdgeLineType = "dashed";
	} elsif ($sLatestChainNodeType eq "ACTIVITY") {
		$sEdgeLineType = "solid";
	} else {
		MM::TRACE("error: invalid chain node type '$sLatestChainNodeType'");
	}
	push(@asDotSyntaxLines, "// _entry_edge_attr_ ='$sEntryEdgeAttr'");
	$sFilledTemplate =~ s/_edge_label_/$nSeqNbr/g;
	$sFilledTemplate =~ s/_entry_edge_attr_/$sEntryEdgeAttr/g;
	MM::TRACE("filled template = '$sFilledTemplate'");
	push(@asDotSyntaxLines, $sFilledTemplate);
	$self->addActivityNode($sActivityNodeFullName);
	MM::TRACE_RET();
	return \@asDotSyntaxLines;
}
#===============================================================================
sub buildCommentNodeDotLines { my ($self, $rhUpdatedConfig) = @_;
#===============================================================================
	# dot line group building logic when "COMMENT" -tagged line processed
	MM::TRACE_SUB($self->{sDuty});
	my $sCommentNodeLabel = $rhUpdatedConfig->{aNodeLabelStr};
	my $sNodeAttr = $rhUpdatedConfig->{aNodeAttrStr};
	my $sEntryEdgeAttr = $rhUpdatedConfig->{aEntryEdgeAttrStr};
	my $sLatestFileNameAsSym =$self->{sLatestContextFileNameAsSym};
	my @asDotSyntaxLines 	= ();
	my $sFilledTemplate;
	my $sLatestCommentableNode 	= $self->getLatestCommentableNode();
	if ($sNodeAttr eq $sDEFAULT_ATTR) {
		$sNodeAttr = "shape=box";
	}
	if ($sEntryEdgeAttr eq $sDEFAULT_ATTR) {
		$sEntryEdgeAttr = "dir=back, style=dashed";
	}
	
	my $sLine = $self->{sLatestLine};
	my $sRgx = $self->{sLatestCaptureRgx};
	push(@asDotSyntaxLines, "\n// ******* COMMENT NODE ***********************");
	push(@asDotSyntaxLines, "\n// DETECTION: regex/line = '$sRgx'/'$sLine'");
	my $sCommentNodeName = MM::sym($sCommentNodeLabel);   # no automatic individual part to activity node names
	my $sCommentNodeLabel = MM::lbl($sCommentNodeLabel); # for sure
	my$sCommentNodeFullName = $sLatestFileNameAsSym."_".$sCommentNodeName;
	
	# build comment node 
	push(@asDotSyntaxLines, "//------ builds comment node ------------");
	$sFilledTemplate = $sPLAIN_NODE_tpl;
	$sFilledTemplate =~ s/_node_name_/$sCommentNodeFullName/g;
	$sFilledTemplate =~ s/_node_label_/$sCommentNodeLabel/g;
	$sFilledTemplate =~ s/_node_attr_/$sNodeAttr/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	# build edge from commentable node to comment node
	push(@asDotSyntaxLines, "//------ builds edge between comment and commentable nodes ------------");
	$sFilledTemplate=$sEDGE_tpl;
	$sFilledTemplate =~ s/_node_name_a_/$sLatestCommentableNode/g;
	$sFilledTemplate =~ s/_node_name_b_/$sCommentNodeFullName/g;
	$sFilledTemplate =~ s/_entry_edge_attr_/$sEntryEdgeAttr/g;
	push(@asDotSyntaxLines, $sFilledTemplate);
	
	MM::TRACE_RET();
	return \@asDotSyntaxLines;
}


#===============================================================================
sub tryBuildDotLinesByCaptures { my ($self, $sLine) = @_;   # ACTion, STAte and SERvice
#===============================================================================
	# the "main" function of this module
	# tries to capture STATE, ACTIVITY, SERVICE or COMMENT node tag or keyword from given line
	# if captured, uses hard coded rules to build edge relations between latest and previous nodes
	# returns a reference to array of 0...N dot graph syntax lines
	my @asDotSyntaxLines = ();  # initialization
	my $rasDotSyntaxLines;
	my $bNodeTypeIdentified = 0;
	my $sNodeType;
	my $sNodeLabelStr;
	my $rhUpdatedConfig;
	my $bRetStatus = 1;  # initial quess: dot lines will be generated
	
	MM::TRACE_SUB($self->{sDuty}); 
	# http://stackoverflow.com/questions/12008455/how-to-loop-over-an-array-of-arrays-as-reference

	$rhUpdatedConfig 	= $self->getItemDataIfLineMatch($sLine);
	$sNodeType 			= $rhUpdatedConfig->{aNodeTypeStr};
	$sNodeLabelStr 		= $rhUpdatedConfig->{aNodeLabelStr};
	
	MM::TRACE_BAG(Dumper($rhUpdatedConfig));
	
	if ($sNodeType eq "CONTEXT") {			
		$self->setContext($sNodeLabelStr); 
		$bRetStatus = 0;   #dot lines are NOT generated
	} elsif ($sNodeType eq "COMMENT") {			
		$rasDotSyntaxLines = $self->buildCommentNodeDotLines($rhUpdatedConfig); 
	} elsif ($sNodeType eq "ACTIVITY") {			
		$rasDotSyntaxLines = $self->buildActivityNodeDotLines($rhUpdatedConfig); 
	} elsif ($sNodeType eq "STATE") {
		$rasDotSyntaxLines = $self->buildStateNodeDotLines($rhUpdatedConfig);
		#http://perldoc.perl.org/perldiag.html
	} elsif ($sNodeType eq "SERVICE") {  
	# TODO: change to handle "constructor" and "external service node"
		$rasDotSyntaxLines = $self->buildServiceNodeDotLines($rhUpdatedConfig);
	} elsif ($sNodeType eq "IGNORE") { # appropriate regexes can be used to skip the line 
		$bRetStatus = 0;
	} else {
		$bRetStatus = 0;
	}
	MM::TRACE("\$bRetStatus = $bRetStatus");
	MM::TRACE_RET();
	return ($bRetStatus, $rasDotSyntaxLines);	
}


# END OF CLASS
1;
