# dam_Logic_overflow

## Points: 300

login:

admin' --

```
Rung 000: ---| I0.0 (sensor1_high) |---| I0.1 (sensor2_high) |---( M0.0 (water_confirmed) )---
Rung 001: ---| M0.0 (water_confirmed) |---|/ I0.2 (alarm_active) |---( M0.1 (safe_to_open) )---
Rung 002: ---| M0.1 (safe_to_open) |---[TON T0 5s]---( M0.2 (timer_done) )---
Rung 003: ---| M0.2 (timer_done) |---|/ I0.3 (emer_stop) |--
                                                 |
                                                 +---( Q0.0 (open_dam) )---
                                                 |
                                    ---| I0.4 (manual_override) |--
```
