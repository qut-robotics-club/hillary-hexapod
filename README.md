# hyper-controller

Monorepo for live-streaming control for a bunch of RPi QUTRC Robots (hexapods, omnibots, 6DOF-arms)

Current local IP of the Pi on the hexapod on the QUT network is `172.19.9.138`.
This is subject to change at any time the QUT dhcp server rolls over (although the network seems extremely large this year)

To connect to the pi wirelessly, power it up by flipping the switch on the bot and ensuring the battery is charged.

You can then use the command (Windows or Linux):

```
ssh pi@172.19.9.138
```

And then put the current password: `rustisthebest` in
