import os
import sys
import nose
# Changes the enviroment in backends/mongodb
os.environ['AMON_TEST_ENV'] = "True"

# To test the web app ( disable auth ), in the console
# AMON_TEST_ENV="TRUE" python amon/web/devserver.py

# Example usage
# python runtests  -w amon/

if __name__ == "__main__":
	try:
		suite = eval(sys.argv[1]) # Selected tests 
	except: 
		suite = None # All tests
		
	nose.run(suite)
