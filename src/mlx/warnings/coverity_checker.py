from decouple import config, Config, RepositoryEnv

from mlx.coverity import CoverityDefectService
from urllib.error import URLError, HTTPError
from .regex_checker import CoverityChecker


class CoverityServerChecker(CoverityChecker):
    name = 'coverityserver'
    hostname = ''
    username = ''
    password = ''
    stream = ''

    def _fill_vars(self, configuration):
        '''
        Fill variables from Python decouple Config class
        Args:
            configuration (decouple.Config): Config class from python Decouple
        '''
        self.hostname = configuration('COVERITY_HOSTNAME', default=self.hostname)
        self.username = configuration('COVERITY_USERNAME', default=self.username)
        self.password = configuration('COVERITY_PASSWORD', default=self.password)
        self.stream = configuration('COVERITY_STREAM', default=self.stream)

    def __init__(self, verbose=False):
        ''' Constructor
        Args:
            verbose (bool): Enable/disable verbose logging
        '''
        self._fill_vars(config)
        self.filters = {
            "checker": "",
            "impact": "",
            "kind": "",
            "classification": "Pending,Bug,Intentional,Unclassified",
            "action": "",
            "component": "",
            "cwe": "",
            "cid": ""
            }

        super().__init__(verbose=verbose)

    def _extract_args(self, logfile):
        '''
        Function for extracting arguments from logfile
        Args:
            logfile (file): Logfile is actually a configuration file for Coverity checker
        Raises:
            ValueError when all needed variables are not set to their non-default values
        '''
        # Add here a function that populates variables from the logfile (probably .env logfile)
        # Maybe a suggestion is to simply load that env like file here
        try:
            self._fill_vars(Config(RepositoryEnv(str(logfile[0]))))
        except FileNotFoundError:
            pass
        if self.hostname == '' or self.username == '' or self.password == '' or self.stream == '':
            raise ValueError('Coverity checker requires COVERITY_HOSTNAME, COVERITY_USERNAME, COVERITY_PASSWORD and COVERITY_STREAM to be set in .env file or as environment variables')
        return

    def _connect_to_coverity(self):
        '''
        Login to Coverity server and retrieve project and stream information. This function
        requires _extract_args to be run before as all class arguments need to be set.
        '''
        print("Login to Coverity Server: https://%s" % (self.hostname))
        self.coverity_service = CoverityDefectService(self.hostname)
        self.coverity_service.login(self.username, self.password)
        if self.verbose:
            print("Verifying and retrieving stream from Coverity Server: https://%s" % (self.hostname))
        self.coverity_service.validate_stream(self.stream)
        self.coverity_service.retrieve_column_keys()
        self.coverity_service.retrieve_checkers()

    def check(self, logfile):
        '''
        Function for retrieving number of defects from Coverity server
        Args:
            content (str): some sort of configuration string
        '''
        self._extract_args(logfile)
        self._connect_to_coverity()
        print("Querying Coverity Server for defects on stream %s" % self.stream)
        try:
            defects = self.coverity_service.get_defects(self.stream, self.filters, [])
        except (URLError, HTTPError) as error:
            print('Coverity checker failed with %s' % error)
            return
        print(defects)
        self.count = defects["totalRows"]
