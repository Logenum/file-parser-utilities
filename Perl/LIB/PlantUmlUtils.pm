package PlantUmlUtils;
use Data::Dumper;
use JSON;
use TraceUtils;
use v5.20;
# created 151231
my $sOBJECT_TITLE = "OBJECT";
# TODO: add stuff 151231
# http://plantuml.com/sequence.html
#===============================================================================
# PlantUml Templates (=some practical part of vast number of possibilities)
#-------------------------------------------------------------------------------
# TODO: add move these to external (JSON) file (?)


my $sSeqD_ARROW_LINE_SOLID_RIGHT 		= "->";  		# _arrow_line_type_
my $sSeqD_ARROW_LINE_SOLID_LEFT 		= "<-";  		# _arrow_line_type_
my $sSeqD_ARROW_LINE_DOTTED_RIGHT 		= "-->";		# _arrow_line_type_
my $sSeqD_ARROW_LINE_DOTTED_LEFT 		= "<--";		# _arrow_line_type_

# IDEA: 'tpl' means 'template'
my $sSeqD_OBJ_DEF_tpl					= "_obj_type_ _obj_name_ #_color_name_";
my $sSeqD_OBJ_MES_tpl 					= "_obj_name_a_ _arrow_line_type_ _obj_name_b_ : _mes_label_";
my $sSeqD_OBJ_ACT_tpl 					= "activate _obj_name_ #_color_name_";
my $sSeqD_OBJ_DEACT_tpl 				= "deactivate _obj_name_";
my $sSeqD_DIAG_LEFT_INVIS_OBJ_tpl 		= "[_arrow_type_ _obj_name_";
my $sSeqD_DIAG_RIGHT_INVIS_OBJ_tpl 		= "_obj_name_ _arrow_line_type_]";
my $sSeqD_DIAG_STEP_DIVIDER_tpl			= "== _step_label_ ==";
my $sSeqD_DIAG_NOTE_tpl					= "note _rel_location_ _note_text_";

my @asSeqD_ALLOWED_OBJ_TYPES =("actor", "boundary", "control", "entity", "database");
#  - see http://plantuml.com/sequence.html

#===============================================================================
sub new { my ($class, $sContext) = @_;
#===============================================================================
	my $self = {
		sContext => $sContext,
		sSeqLatestObjName => "NOT_INITIALIZED",
		sSeqPrevObjName => "NOT_INITIALIZED",
		
	};
	bless $self, $class;
	MM::TRACE_SUB($sContext);
	MM::TRACE_RET();
	return $self;
}

#==========================================================================================

=cut

1;