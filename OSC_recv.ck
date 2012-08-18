fun void sweepUp(float initFreq, float timeLeft) {   // function definition
    SndBuf buf => Gain g => dac;   // alloc UG (not a good idea)
    g => Gain feedback => DelayL delay => g;
    0.5 => feedback.gain;
    "/Users/ludoviclaffineur/intentions/snare.wav" => buf.read;
    .5::second => delay.max => delay.delay;
    .3 => delay.gain;
    0 => buf.play; 
    initFreq => buf.play;
    //s =< dac;      // unchuck (for GC (later))
    timeLeft :: second => now;
}



// (launch with OSC_send.ck)

// the patch
//SndBuf buf => dac;
// load the file
//"/Users/ludoviclaffineur/intentions/snare.wav" => buf.read;
// don't play yet
//0 => buf.play; 

// create our OSC receiver
OscRecv recv;
// use port 6449
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/chuck, f, f" ) @=> OscEvent oe;

// infinite event loop
while ( true )
{
    // wait for event to arrive
    oe => now;

    // grab the next message from the queue. 
    while ( oe.nextMsg() != 0 )
    { 
        // getFloat fetches the expected float (as indicated by "f")
        //oe.getFloat() => buf.play;
        float timeLeft, frequency;
        oe.getFloat() => timeLeft;
        oe.getFloat() => frequency;
        spork ~ sweepUp(timeLeft, frequency);
        // print
        <<< "got (via OSC):", timeLeft, frequency>>>;
        // set play pointer to beginning
        //0 => buf.pos;
    }
}
