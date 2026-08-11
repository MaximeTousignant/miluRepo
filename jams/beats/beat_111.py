"""Un beat 4/4 à 111 bpm, écrit en MIDI — canal 10, percussions General MIDI.

Aucune dépendance : le format SMF est assez simple pour se plier à la main.

Usage : ./.venv/bin/python jams/beats/beat_111.py
Sortie : jams/beats/beat_111.mid
"""

import struct
from pathlib import Path

PPQ = 480  # ticks par noire
BPM = 111
BARS = 8
SIG = 4  # 4/4
DRUM_CH = 9  # canal 10 en base 1

KICK, SNARE, HAT, HAT_OPEN = 36, 38, 42, 46


def vlq(n):
    """Quantité de longueur variable — l'encodage des delta-temps MIDI."""
    out = bytearray([n & 0x7F])
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def chunk(tag, data):
    return tag + struct.pack(">I", len(data)) + data


events = []  # (tick, ordre, octets) — ordre : note-off avant note-on à tick égal


def note(beat_pos, pitch, vel, length=0.12):
    t0 = int(beat_pos * PPQ)
    t1 = t0 + max(1, int(length * PPQ))
    events.append((t1, 0, bytes([0x80 | DRUM_CH, pitch, 0x40])))
    events.append((t0, 1, bytes([0x90 | DRUM_CH, pitch, vel])))


for bar in range(BARS):
    b0 = bar * SIG

    # Grosse caisse : 1 et 3, plus un contretemps qui pousse les mesures paires
    note(b0 + 0.0, KICK, 112)
    note(b0 + 2.0, KICK, 100)
    if bar % 2 == 1:
        note(b0 + 2.75, KICK, 78)

    # Caisse claire : 2 et 4, le squelette du backbeat
    note(b0 + 1.0, SNARE, 104)
    note(b0 + 3.0, SNARE, 104)
    if bar % 4 == 3:  # relance en fin de phrase
        note(b0 + 3.5, SNARE, 68)
        note(b0 + 3.75, SNARE, 84)

    # Charleston : croches, ouvert sur le « et » du 4
    for k in range(SIG * 2):
        pos = b0 + k * 0.5
        if k == 7:
            note(pos, HAT_OPEN, 88, length=0.45)
        else:
            note(pos, HAT, 92 if k % 2 == 0 else 70)

track = bytearray()
track += b"\x00" + b"\xff\x58\x04" + bytes([SIG, 2, 24, 8])  # 4/4
track += b"\x00" + b"\xff\x51\x03" + struct.pack(">I", round(60_000_000 / BPM))[1:]
track += b"\x00" + b"\xff\x03" + vlq(len(b"beat 111")) + b"beat 111"

prev = 0
for tick, _, data in sorted(events):
    track += vlq(tick - prev) + data
    prev = tick
track += vlq(int(BARS * SIG * PPQ) - prev) + b"\xff\x2f\x00"  # fin de piste

header = struct.pack(">HHH", 0, 1, PPQ)  # format 0, 1 piste
out = Path(__file__).with_name("beat_111.mid")
out.write_bytes(chunk(b"MThd", header) + chunk(b"MTrk", bytes(track)))

print(f"{out.name} — {BARS} mesures 4/4 @ {BPM} bpm — {len(events)//2} notes")
