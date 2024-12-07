# CLIwrap
🎉 The *"Spotify Wrapped"* feature for **your** terminal!

### How?
CLIwrap reads your shell's history file to serve you a recap of what commands you ran in your terminal!

### Supported Shells
- bash
- zsh
- csh/tcsh

### Installation
Installing **CLIwrap** is easy! You can pull this Git image, or create a new file and set everything up yourself. Because that it is a simple **bash** script, you don't need to run or build anything!

#### Run from file
First of all, create a new file named `cliwrap`:

```bash
$ touch cliwrap
```

Copy the content of the [`cliwrap`](CLIWRAP) file to your new file. After that, make sure that you have enabled execution permissons for this file:

```bash
$ sudo chmod +x /usr/local/bin/cliwrap
```

Now, try running it with by running the following command:

```bash
./cliwrap
```

Congrats! Now the script should be working. You can run it with the `-h` flag for more information.

#### Run from `/usr/local/bin`

To run it everywhere with a simple command, you can move the script into your `/usr/local/bin` directory.

After following the instructions from the `Run from file` header, run:

```bash
sudo mv cliwrap /usr/local/bin/
```

This will move the script to your executables directory. Now, you can run:

```bash
cliwrap
```

to get your wrapped everywhere!

### License
This project is licensed under the MIT License. You can check out the conditions [here.](LICENSE)
