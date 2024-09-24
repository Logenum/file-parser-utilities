#!/usr/bin/perl
use warnings;
use strict;
use Glib;
use Glib qw/TRUE FALSE/;

# thanks to muppet for this

use Term::ReadKey;
$|++;
ReadMode('cbreak');

my $main_loop = Glib::MainLoop->new;

Glib::Idle->add(
        sub{
            my $char;
            if (defined ($char = ReadKey(0)) ) {
            print "$char->", ord($char),"\n";    
            #process key presses here
            }
          return TRUE; #keep this going
          });
       
$main_loop->run;
ReadMode('normal'); # restore normal tty settings 
