Name: Muath Alzamil
Email: muathalzamil@csu.fullerton.edu , moath.a.alzamil@gmail.com 
Programming Language Used: Python

How To Execute:
---------------
To execute this program, please have Python 3.8 installed.
After 3.8 is installed, the following actions should be done.
	1. Open up the project in two windows, one window should be for the Client folder, one for the Server folder.
	2. Place items in the folder were you want them to be (i.e. put text files that you want the server to have in the Server folder).
	3. Open 2 command/terminal windows and navigate them to the Client and Server folders
	4. Type in to start both sides. *Note* The Server must start before the client, otherwise it will not work.:
	
		python serv.py 1234
		python cli.py <hostname> 1234

	5. Do the put, get, quit, or ls commands on the Client window.
	6. Observe the results.
	7. Repeat steps 5-6 until done.

Special Notes:
--------------
As far as I know, everything should work fine.  
The server calls gethostname() so it defaults to wherever (computer) this program is called. 
If the ls command does not work (because of Windows), change line 117 in serv.py from:

	data = subprocess.check_output('ls', shell=True)

To the following:

	data = subprocess.check_output('dir', shell=True) 

