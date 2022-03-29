<h1 align"center">
	<br>
	FitScrypt Mac Notifications
	<br>
</h1>
<h4>An unofficial token tracker by Grrstine</h4>

<p align="center">
  <a href="#how-to-install">How To Install</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

This is a pre-release of the FitScrypt ($FIT) Mac notifications, for the FitScrypt DAO

## How To Install 
There are a number of ways to get this to run in the background. If you have a clever way to run this outside of the following .sh command, let's get in touch.

**1.** Create a init_script.sh file with the following contents
```bash
#!/bin/bash

echo Script Name: "$0"
echo Total Number of Argument Passed: "$#"
while true; do python /FitScryptWatch/main.py $* & sleep 30 ; done
echo Press ENTER to stop...
read end
```

**2.** **A)** Replace the location of the script in init_script.sh to wherever you saved the FitScryptWatch folder (*ie. ~/FitScryptWatch/main.py*)

2. **B)** Verify you can run python, install python 3.x separately the following command has no response.
```bash
$ which python

>>> Expected response
> /usr/local/bin/python
```

**3.** Install python modules
```bash
$ pip install notify-py
```
- **Note:** there may be other python packages missing from your system. You run similar commands for each module you are missing.

3. Make the file executable
```bash
$ chmod +x init_script.sh
```

**4.** Generate an API Key on bscscan.com under your personal account. [Generate BSCScan API Keys](https://bscscan.com/myapikey)  
- *Note:* This could take a day to become valid. When I first generated my first api token, it did not work until a day later.  
  
**5.** Add the following one line of code  to your shell profile (*ie. profile.sh, .zshrc, etc*) so that it sits as your environment variable.  
```bash
export bscscan_api_key="YOUR_BSCSCAN_API"  
```

**6.** Run the file
```bash
$ ./init_script.sh
```

## Troubleshooting
One other step is to make sure the notificator is executable, while the terminal is in the project root, run the following:
```bash
$ chmod +x ./resource/fit/FitScrypt\ Alerts.app
```

## Credits
  
Notifications forked from [Notifcator](https://github.com/vitorgalvao/notificator)

## License

MIT
