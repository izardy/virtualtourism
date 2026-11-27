#!/bin/sh
# Synthesises the nature ambience with ffmpeg (no third-party audio, so nothing to credit).
# Loops (seamless, played continuously, crickets gated on and off at random by Ambience.js):
#   crickets_a, crickets_b, waves, wind
# One-shots (scheduled at random by Ambience.js): bird_1..bird_4 by day, gecko and owl by night.
set -e
OUT="$(dirname "$0")/../app/static/audio/ambient"; mkdir -p "$OUT"; rm -f "$OUT/crickets.mp3"
enc() { ffmpeg -y -loglevel error -f lavfi -i "$1" -af "$2" -ac 1 -ar 22050 -b:a 48k "$OUT/$3.mp3"; }

# crickets A: 4.4 kHz, chirps of three pulses about twice a second (10 s loop)
enc "aevalsrc='0.5*pow(0.5+0.5*sin(2*PI*34*t),4)*lt(mod(t,0.47),0.1)*sin(2*PI*4400*t)':d=10:s=22050" "highpass=f=2500" crickets_a
# crickets B: 3.7 kHz trill with a slow swell (10 s loop)
enc "aevalsrc='0.4*pow(0.5+0.5*sin(2*PI*52*t),3)*(0.6+0.4*sin(2*PI*0.3*t))*sin(2*PI*3700*t+0.4*sin(2*PI*52*t))':d=10:s=22050" "highpass=f=2500" crickets_b
# waves: brown noise swelling every 10 s
enc "anoisesrc=d=20:c=brown:r=22050:a=0.9" "lowpass=f=1200,volume='0.25+0.75*pow(0.5+0.5*sin(2*PI*t/10),2)':eval=frame" waves
# wind: band-limited pink noise with slow gusts
enc "anoisesrc=d=20:c=pink:r=22050:a=0.6" "bandpass=f=400:w=300,volume=28dB,volume='0.4+0.6*(0.5+0.5*sin(2*PI*t/20))':eval=frame,alimiter=limit=0.7" wind

# birds. Each note is a sine sweep: phase = 2pi (f0 tt + (f1-f0) tt^2 / 2T), envelope sin(pi tt / T)
# bird 1: three rising whistles
enc "aevalsrc='lt(t,0.6)*lt(mod(t,0.2),0.13)*sin(PI*mod(t,0.2)/0.13)*0.6*sin(2*PI*(2600*mod(t,0.2)+1500*pow(mod(t,0.2),2)/(2*0.13)))':d=1.0:s=22050" "afade=t=out:st=0.8:d=0.2" bird_1
# bird 2: falling trill of fast notes
enc "aevalsrc='lt(t,0.9)*lt(mod(t,0.06),0.04)*sin(PI*mod(t,0.06)/0.04)*0.5*sin(2*PI*(5200-2200*t/0.9)*t)':d=1.2:s=22050" "afade=t=out:st=1.0:d=0.2" bird_2
# bird 3: two warbled notes, "tui-tui"
enc "aevalsrc='(between(t,0,0.25)*sin(PI*t/0.25)+between(t,0.4,0.65)*sin(PI*(t-0.4)/0.25))*0.55*sin(2*PI*3300*t+5*sin(2*PI*28*t))':d=0.9:s=22050" "afade=t=out:st=0.7:d=0.2" bird_3
# bird 4: long down-slurred whistle then a short up-note
enc "aevalsrc='(between(t,0,0.45)*sin(PI*t/0.45)*sin(2*PI*(3800*t-1400*t*t/0.9))+between(t,0.55,0.7)*sin(PI*(t-0.55)/0.15)*sin(2*PI*(2600*(t-0.55)+3000*pow(t-0.55,2))))*0.5':d=1.0:s=22050" "afade=t=out:st=0.8:d=0.2" bird_4
# gecko (cicak): six dry "chik" calls, harmonics around 2 kHz
enc "aevalsrc='lt(t,1.1)*lt(mod(t,0.18),0.045)*sin(PI*mod(t,0.18)/0.045)*0.5*(sin(2*PI*1900*t)+0.5*sin(2*PI*3800*t)+0.25*sin(2*PI*5700*t))':d=1.4:s=22050" "afade=t=out:st=1.2:d=0.2" gecko
# owl: "hoo ... hoo-hoo", 380 Hz with a slight fall
enc "aevalsrc='(between(t,0,0.45)*sin(PI*t/0.45)+between(t,0.9,1.2)*sin(PI*(t-0.9)/0.3)+between(t,1.3,1.75)*sin(PI*(t-1.3)/0.45))*0.6*sin(2*PI*(390*t-20*t*t))':d=2.0:s=22050" "lowpass=f=900,afade=t=out:st=1.8:d=0.2" owl
