package StateUtils;
use v5.20;

# generic state saving object (with MM::TRACES) which can be instantiated to all flag-alike purposes
# all "events" last non-measurable short time, all "states" last measurable long time (see EventUtils.pm)
#===============================================================================
sub new { my $class = shift;
#===============================================================================
	MM::TRACE_SUB();  
	my $sState = shift;
	my $sContext = shift;
	
	my $self = {
		stState => $sState, 	# initial state
		stPrevState => $sState, # initial state
		context => $sContext, 	# that thing whose states are changed
		
	};
	bless $self, $class;
	
	MM::TRACE_SUB($sContext);
	MM::TRACE("'$sState' by 'initialization'");
	MM::TRACE_RET();
	return $self;
}
#===============================================================================
sub getContext { my ($self) = @_;
#===============================================================================
	return $self->{context};
}

#===============================================================================
sub setState { my ($self, $sNewState, $sEvent) = @_;   # generic function for changing processing state
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $sPrevState = $self->{stPrevState};
	$self->{stPrevState} = $self->{stState};
	$self->{stState} = $sNewState;
	
	if (defined $sEvent) {
		MM::TRACE("'$sPrevState' changed to '$sNewState' by '$sEvent'");
	} else {
		MM::TRACE("'$sPrevState' changed to '$sNewState'");
	}
	
	MM::TRACE_RET();	
}
#===============================================================================
sub getState { my ($self) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $sState = $self->{stState};
	MM::TRACE("$sState");
	MM::TRACE_RET();
	return $sState;
}
#===============================================================================
sub isState { my ($self, $sIsState) = @_; 
#===============================================================================
	#MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sState = $self->{stState};
	
	if ($sState eq $sIsState) {
	#	MM::TRACE("'$sContext': is '$sState'");
		$bStatus = 1;
	}  else {
	#	MM::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 0;
	}
	#MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub isNotState { my ($self, $sIsNotState) = @_; 
#===============================================================================
	#MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sState = $self->{stState};
	if ($sState ne $sIsNotState) {
		# MM::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 1;
	}  else {
		#MM::TRACE("'$sContext': is '$sState'");
		$bStatus = 0;
	}
	#MM::TRACE_RET();
	return $bStatus;
}	
#===============================================================================
sub isPrevState { my ($self, $sIsState) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sPrevState = $self->{stPrevState};
	
	if ($sPrevState eq $sIsState) {
		MM::TRACE("is '$sPrevState'");
		$bStatus = 1;
	}  else {
		MM::TRACE("is NOT '$sPrevState'");
		$bStatus = 0;
	}
	MM::TRACE_RET();
	return $bStatus;
}
# END OF CLASS
1;

