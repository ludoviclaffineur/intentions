fun void sweepUp(float initFreq, float timeLeft, float reverb) {   // function definition
    SndBuf buf => Gain g => Dyno limiter => dac;   // alloc UG (not a good idea)
    limiter.limit();
    0.05 =>buf.gain;
    0.2 => limiter.thresh;
    10::ms => limiter.attackTime;
    5::second => limiter.releaseTime;
    g => Gain feedback => DelayL delay => g;
    reverb => feedback.gain;
    "/Users/ludoviclaffineur/intentions/snare.wav" => buf.read;
    .5::second => delay.max => delay.delay;
    reverb => delay.gain;
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
recv.event( "/chuck, f, f, f" ) @=> OscEvent oe;

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
        float timeLeft, frequency, reverb;
        oe.getFloat() => timeLeft;
        oe.getFloat() => frequency;
        oe.getFloat() => reverb;
        spork ~ sweepUp(timeLeft, frequency, reverb);
        // print
        <<< "got (via OSC):", timeLeft, frequency , reverb>>>;
        // set play pointer to beginning
        //0 => buf.pos;
    }
}
