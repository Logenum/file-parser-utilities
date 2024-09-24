package EventUtils;
use v5.20;

# copied and modified from StateUtils module (151119)
# generic event saving object 
# all "events" last non-measurable short time, all "states" last measurable long time (see StateUtils.pm)
# event shall be cleared always after handling it

my $m_sNO_EVENT = "EV_NONE";

#===============================================================================
sub new { my $class = shift;
#===============================================================================
	MM::TRACE_SUB();  
	my $sEvent = shift;
	my $sContext = shift;
	
	my $self = {
		sEvent => $sEvent, 			# latest event, shall be cleared right after handling
		sEventSaved => $sEvent, 	# copy of latest event
		sEventSavedPrev => $sEvent, # copy of previous event
		context => $sContext, 	# that thing whose events are changed
	};
	bless $self, $class;
	
	MM::TRACE_SUB($sContext);
	MM::TRACE("'$sEvent' by 'initialization'");
	MM::TRACE_RET();
	return $self;
}
#===============================================================================
sub getContext { my ($self) = @_;
#===============================================================================
	return $self->{context};
}
#===============================================================================
sub doEvent { my ($self, $sNewEvent) = @_;   # generic function for setting new processing event
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $sEventSavedPrev = $self->{sEventSavedPrev};
	$self->{sEventSavedPrev} = $self->{sEventSaved};
	$self->{sEvent} = $sNewEvent;
	$self->{sEventSaved} = $sNewEvent;
	
	MM::TRACE("'$sEventSavedPrev' changed to '$sNewEvent'");
	MM::TRACE_RET();
	return $sNewEvent;
}

#===============================================================================
sub flushEvent { my ($self) = @_;
#===============================================================================
	# consumes the event away
	MM::TRACE_SUB($self->{context});
	my $sEvent = $self->{sEvent};
	$self->{sEvent} = $m_sNO_EVENT; # clears the event
	MM::TRACE("$sEvent");
	MM::TRACE_RET();
	return $sEvent;
}
#===============================================================================
sub askEvent { my ($self) = @_;
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $sEvent = $self->{sEvent};
	MM::TRACE("$sEvent");
	MM::TRACE_RET();
	return $sEvent;
}

#===============================================================================
sub wasEvent { my ($self, $sEvent) = @_; 
#===============================================================================
	#MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sLatestEvent = $self->{sEventSaved};
	
	if ($sLatestEvent eq $sEvent) {
	#	MM::TRACE("'$sContext': is '$sEvent'");
		$bStatus = 1;
	}  else {
	#	MM::TRACE("'$sContext': is NOT '$sEvent'");
		$bStatus = 0;
	}
	#MM::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub wasNotEvent { my ($self, $sWasNotEvent) = @_; 
#===============================================================================
	#MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sLatestEvent = $self->{sEventSaved};
	
	if ($sLatestEvent ne $sWasNotEvent) {
		# MM::TRACE("'$sContext': is NOT '$sEvent'");
		$bStatus = 1;
	}  else {
		#MM::TRACE("'$sContext': is '$sEvent'");
		$bStatus = 0;
	}
	#MM::TRACE_RET();
	return $bStatus;
}	
#===============================================================================
sub wasPrevEvent { my ($self, $sWasEvent) = @_; 
#===============================================================================
	MM::TRACE_SUB($self->{context});
	my $bStatus;
	my $sEventSavedPrev = $self->{sEventSavedPrev};
	
	if ($sEventSavedPrev eq $sWasEvent) {
		MM::TRACE("is '$sEventSavedPrev'");
		$bStatus = 1;
	}  else {
		MM::TRACE("is NOT '$sEventSavedPrev'");
		$bStatus = 0;
	}
	MM::TRACE_RET();
	return $bStatus;
}
# END OF CLASS
1;

