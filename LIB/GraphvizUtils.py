import os, sys
import os.path
import re
import time
import datetime
import json

from TextStoreUtils import *
from StateUtils import *

# -------- Example: ----------------------------------------------
# 	JSON string:		["foo", {"bar": ["baz", null, 1.0, 2]}]
# 	Python dictionary: 	['foo', {'bar': ('baz', None, 1.0, 2)}]
# https://docs.python.org/2.7/library/json.html
# ----------------------------------------------------------------

class clTripodGraph (clTextStore):

	sCLUSTER_tpl = "subgraph cluster__cluster_name_ { style=filled; fillcolor=lemonchiffon1;label =\"_cluster_label_\"; _node_name_}"
	# requires keyword "cluster"
	# node names within a cluster are separated by ';' !!!

	sPLAIN_NODE_tpl = "_node_name_ [label = \\\"_node_label_\\\" , _node_attr_]"
	#my $sPLAIN_NODE_tpl = "_node_name_ [label =\\\"_node_label_\\\" _node_attr_]"
	sRECORD_NODE_tpl = "_node_name_ [label =\\\"_node_label_||\\\" ,_node_attr_]"
	sTAP_NODE_tpl = "_node_name_ \[label = \"_node_label_\",shape=circle, color=grey]"; # attributes: parentheses are not necessary
	# circle 'height' = diameter in inches
	sEDGE_tpl = "_node_name_a_ -> _node_name_b_ \[label =\"_edge_label_\", _entry_edge_attr_]" 
	 # TODO: add more choises
	sSERVICE_NODE_DOT_TEMPLATES_json = "{\"CONSTRUCTOR\":\"$sRECORD_NODE_tpl\",\"SERVICE\":\"$sPLAIN_NODE_tpl\"}";  # for database, file, event etc.

	#TODO: add horizontal class node template

	sNOT_IN_USE = "NOT_IN_USE"

	sDEFAULT_ATTR = "USE_DEFAULT_ATTR"

	#=========================================================
	def __init__(me, sDuty, fhTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		me.fhTrace = fhTrace
		me.sDuty = sDuty
		clTextStore.__init__(me, me.sDuty, me.fhTrace)
	# TODO: add code edited from GraphvizUtils.pm
	
	
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
	sub tryBuildDotLinesByCaptures (me, sLine) # ACTion, STAte and SERvice
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

#=
class clFreeGraph:
	# TODO: add code
