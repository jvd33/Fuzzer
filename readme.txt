
README:
1. Install the python requests package and beautifulsoup using pip by typing
"pip install requests" followed by "pip install beautifulsoup4" in the command line
2. Download xampp-portable from http://yogi.se.rit.edu/~swen-331/bigfiles/xampp-portable.zip
3. Run setup_xampp.bat
4. Run apache_start.bat
5. Run catalina_start.bat
6. Run mysql_start.bat
7. In the terminal, type python Fuzz.py [discover | test] url OPTIONS
8. Fuzzing log is located in Fuzzer\src\output.txt

Additional Usage Information:


COMMANDS:
  discover  Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
  test      Discover all inputs, then attempt a list of exploit vectors on those inputs. Report potential vulnerabilities.

OPTIONS:
  --custom-auth=string     Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa). Optional.

  Discover options:
    --common-words=file    Newline-delimited file of common words to be used in page guessing and input guessing. Required.

  Test options:
    --vectors=file         Newline-delimited file of common exploits to vulnerabilities. Required.
    --sensitive=file       Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. Required.
    --random=[true|false]  When off, try each input to each page systematically.  When on, choose a random page, then a random input field and test all vectors. Default: false.
    --slow=500             Number of milliseconds considered when a response is considered "slow". Default is 500 milliseconds

Examples:
  # Discover inputs
  fuzz discover http://localhost:8080 --common-words=mywords.txt

  # Discover inputs to DVWA using our hard-coded authentication
  fuzz discover http://localhost:8080 --common-words=mywords.txt

  # Discover and Test DVWA without randomness
  fuzz test http://localhost:8080 --custom-auth=dvwa --common-words=words.txt --vectors=vectors.txt --sensitive=creditcards.txt --random=false

http://www.se.rit.edu/~swen-331/projects/fuzzer/
Author: Joe Diment jvd5839@rit.edu
Author: Adam Audycki apa73952rit.edu

Current features:
Custom authentication
Finding all URLs in the HTML source
Guessing URLs on the domain
Parsing URLs into their parameters
Finding cookies
Finding all form field data
