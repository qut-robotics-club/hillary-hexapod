# hyper-controller

Monorepo for live-streaming control for a bunch of RPi QUTRC Robots (hexapods, omnibots, 6DOF-arms)

Current local IP of the Pi on the hexapod on the QUT network is `172.19.44.211`.
This is subject to change at any time the QUT dhcp server rolls over (although the network seems extremely large this year)

To connect to the pi wirelessly, power it up by flipping the switch on the bot and ensuring the battery is charged.

You can then use the command (Windows or Linux):

```
ssh pi@172.19.44.211
```

And then put the current password: `rustisthebest` in

## SSH shortcuts (linux only?)

To save you from having to remember the password or IP when ssh'ing,
if you are on linux you can save the local raspberry pi host as a configured host by editing `~/.ssh/config`
on your development PC, adding a host config like so:

```
Host hillary
    HostName 172.19.44.211
    User pi
```

Now run this command and input the password for the last time to get the rpi to trust your machine every time you SSH in:

```
ssh-copy-id hillary
```

Now all programs that use SSH internally don't have to ask you for the password,

## Live development

The key to successful robotics development is setting in place good feedback loops. IE:

Code -> Test -> Evaluate -> Code...

The trick is to minimise the amount of time it takes to do all 3.
When dealing with robotic control, unmodelled characteristics are very common and will often throw a spanner in the works,
so its important to iterate quickly! We support a few solutions for this out of the box:

### With Jupyterlab

JupyterLab is a python/notebook, in-browser IDE. It is accessible through the hyper-controller web-application in the menu.

JupyterLab and supporting python packages provide widgets that effortlessly interact with your python code.
This allows you to construct animated visualizations & online models based on live data, view and manipulate live video streams and other sensors.

### With SSHFS

This is the option you want if you have a nicely customised editor setup, such as vscode with lots of plugins.
Particularly useful for leveraging type annotation which was added in Python3.5.

If doing development in vscode or another dev-machine editor, you can mount the corresponding project folder of the project
you are working on on the raspberry Pi using `sshfs`. This allows for quick iteration as you don't need to keep uploading
your code as you make updates, and can work off the pi directly.

```
cd ~/projects
sshfs hillary:/home/pi/hyper-controller live_hyper-controller
code live_hyper-controller
```

Using Jupyterlab to edit your experimentation code while editing an SSHFS folder
in VSCode provides the best development experience I've seen with robotics.
