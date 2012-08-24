// the patch
SndBuf buf2 => Envelope e => JCRev R => dac;

// load the file
"/Users/ludoviclaffineur/intentions/tap_machine.aif" => buf2.read;

// number of the device to open (see: chuck --probe)
0 => int device;
// get command line
if( me.args() ) me.arg(0) => Std.atoi => device;

// the midi event
MidiIn min;
// the message for retrieving data
MidiMsg msg;

// open the device
//if( !min.open( device ) ) me.exit();

// print out device that was opened
<<< "MIDI device:", min.num(), " -> ", min.name() >>>;

fun void grain(float duration , int position, float pitch, int randompos, float randpitch)
{ 
    int samples;
    buf2.samples() => samples;
    44100*position/1000 => position;
    44100*randompos/1000 => randompos;
    
    // can be changed to acheive a more varying
    // asynchronous envelope for each grain duration
    duration*Std.rand2f(0.45,0.5)::ms => e.duration;
    float freq;
    while( true )
    {   
        Std.rand2f(pitch-0.5,pitch+0.5) => buf2.rate;
        Std.rand2(position-200,position+200) => buf2.pos;
        0.4 => buf2.gain;
        e.keyOn();
        duration*0.5::ms => now;
        e.keyOff();
        duration*0.2::ms => now; //density here changing!
    }
}

0 => R.mix;

900 => float grain_duration; 
4420 => int position; 
1 => float base_pitch;
0 => int rand_position;
0.0 => float rand_pitch;

spork ~ grain(grain_duration,position,base_pitch,rand_position,rand_pitch);

// time loop
while( true )
{
    1::ms => now;
}
