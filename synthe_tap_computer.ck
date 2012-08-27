// the patch
SndBuf buf2 => Envelope e => JCRev R => dac;

// load the file
"/Users/ludoviclaffineur/intentions/tap_computer.aif" => buf2.read;

// number of the device to open (see: chuck --probe)
0 => int device;
// get command line
if( me.args() ) me.arg(0) => Std.atoi => device;

// the midi event
MidiIn min;
// the message for retrieving data
MidiMsg msg;

OscRecv recv;
// use port 6449
6449 => recv.port;
// start listening (launch thread)
recv.listen();
20 =>  float timeLeft;
0.5 =>  float frequency;
0.5 =>  float reverb;
0 => int count;
// create an address in the receiver, store in new variable

// open the device
//if( !min.open( device ) ) me.exit();

// print out device that was opened
<<< "MIDI device:", min.num(), " -> ", min.name() >>>;

fun void grain(float duration , int position, float pitch, int randompos, float randpitch)
{ 
    recv.event( "/chuck, f, f, f" ) @=> OscEvent oe;
    int samples;
    buf2.samples() => samples;
    44100*position/1000 => position;
    44100*randompos/1000 => randompos;
    
    // can be changed to acheive a more varying
    // asynchronous envelope for each grain duration
    duration*Std.rand2f(0.45,0.5)::ms => e.duration;
    while( true )
    {   
        Std.rand2f(pitch+frequency-0.6,pitch+frequency+0.6) => buf2.rate;
        
        Std.rand2(position-70,position+80) => buf2.pos;
        1.5 => buf2.gain;
        reverb*0.05 => R.mix;

        if (count ==0 ){
            e.keyOn();
            duration*(count/5.0)::ms => now;
            e.keyOff();
            duration*5::ms => now; //density here changing!
            
        }
        else{
            e.keyOn();
            duration*5*(count/8)::ms => now;
            e.keyOff();
            duration*5::ms => now; //density here changing!
            
        }
     }
    
}



fun void OSCReceiveDispatch(){
    spork ~ set_parameters_listener();
    spork ~ set_count_listener();
}

fun void set_parameters_listener(){
    recv.event( "/chuck, f, f, f" ) @=> OscEvent oe;
    while (true){
        oe => now;                    // wait for message to come in
        while( oe.nextMsg() )  { 
            float t, f, r;
            oe.getFloat() => frequency;
            oe.getFloat() => timeLeft;
            oe.getFloat() => reverb;
            <<< "got (via OSC):", timeLeft, frequency, reverb >>>;
        }
    }
}

fun void set_count_listener(){
    recv.event( "/count, i" ) @=> OscEvent oe;
    while (true){
        oe => now;                    // wait for message to come in
        while( oe.nextMsg() )  { 
            float t, f, r;
            oe.getInt() => count;
            <<< "got (via OSC):", count  >>>;
        }
    }
}

0.015 => R.mix;

10 => float grain_duration; 
550 => int position; 

0.4 => float base_pitch;
0 => int rand_position;
0.0 => float rand_pitch;
spork ~ grain(grain_duration,position,base_pitch,rand_position,rand_pitch);
spork ~ set_parameters_listener();
spork ~ set_count_listener();
// time loop
while( true )
{
    1::ms => now;
}
