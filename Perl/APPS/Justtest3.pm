#===============================================================================
sub isState { my ($self, $sIsState) = @_; 
#===============================================================================
	#PERL_SCRIPTS::TRACE_SUB();
	kukkuu
	my $bStatus;
	my $sState = $self->{stState};
	my $sContext = $self->{context};	
	if ($sState eq $sIsState) {
	#	PERL_SCRIPTS::TRACE("'$sContext': is '$sState'");
		$bStatus = 1;
	}  else {
	#	PERL_SCRIPTS::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 0;
	}
	#PERL_SCRIPTS::TRACE_RET();
	return $bStatus;
}
#===============================================================================
sub isNotState { my ($self, $sIsNotState) = @_; 
#===============================================================================
	#PERL_SCRIPTS::TRACE_SUB();
	my $bStatus;
	my $sState = $self->{stState};
	my $sContext = $self->{context};	
	if ($sState ne $sIsNotState) {
		# PERL_SCRIPTS::TRACE("'$sContext': is NOT '$sState'");
		$bStatus = 1;
	}  else {
		#PERL_SCRIPTS::TRACE("'$sContext': is '$sState'");
		$bStatus = 0;
	}
	#PERL_SCRIPTS::TRACE_RET();
	return $bStatus;
}	
