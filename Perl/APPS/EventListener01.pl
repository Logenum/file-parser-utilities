
BEGIN {push @INC, "C:\\Perl\\cpan\\build\\SDL-2.544-rtUqxl\\lib";}

 use SDL::Event;  # for the event object itself
 use SDL::Events; # functions for event queue handling

 SDL::init(SDL_INIT_VIDEO);
 my $event = SDL::Event->new();

 while(1)
 {
     SDL::Events::pump_events();

     if(SDL::Events::poll_event($event))
     {
        if($event->type == SDL_MOUSEBUTTONDOWN)
        {
            # now you can handle the details
            $event->button_which;
            $event->button_button;
            $event->button_x;
            $event->button_y;
        }

        last if $event->type == SDL_QUIT;
     }

     # your screen drawing code will be here
 }