import unittest

class TestJupyter(unittest.TestCase):
    def test_jupyter_run(self):
        import subprocess
        result = subprocess.run('jupyter --version',
                                capture_output=True,
                                text=True,
                                shell=True,
                                check=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('jupyter_server   : 2.13.0', result.stdout)
        self.assertIn('jupyterlab       : 4.4.0', result.stdout)
        pass

    def __del__(self):
        print('cleanup ...')
    pass

class TestNGIAB(unittest.TestCase):
    def test_ngiab_install(self):
        import subprocess
        result = subprocess.run('/dmod/bin/ngen',
                                capture_output=True,
                                text=True,
                                check=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('NGen Framework', result.stdout)
        self.assertIn('NetCDF', result.stdout)
        self.assertIn('Fortran', result.stdout)
        self.assertIn('Python', result.stdout)
        pass

    def test_ngiab_serial(self):
        import subprocess
        result = subprocess.run('/dmod/bin/ngen-serial',
                                capture_output=True,
                                text=True,
                                check=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('NGen Framework', result.stdout)
        self.assertIn('NetCDF', result.stdout)
        self.assertIn('Fortran', result.stdout)
        self.assertIn('Python', result.stdout)
        self.assertIn('ngen-serial', result.stdout)
        pass

    def test_ngiab_parallel(self):
        import subprocess
        result = subprocess.run('/dmod/bin/ngen-parallel',
                                capture_output=True,
                                text=True,
                                check=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('NGen Framework', result.stdout)
        self.assertIn('NetCDF', result.stdout)
        self.assertIn('Fortran', result.stdout)
        self.assertIn('Python', result.stdout)
        self.assertIn('Parallel build', result.stdout)
        pass

    def test_ngiab_partition_generator(self):
        import subprocess
        result = subprocess.run('/dmod/bin/partitionGenerator',
                                capture_output=True,
                                text=True
                                #check=True
                                )
        self.assertEqual(result.returncode, 255)
        #self.assertIn('features from layer divides using ID column', result.stdout)
        self.assertIn('/dmod/bin/partitionGenerator <catchment_data_path> <nexus_data_path> <partition_output_name> <number of partitions> <catchment_subset_ids> <nexus_subset_ids>', result.stdout)
        pass
    
    def test_ngiab_run(self):
        #self.assertEqual(add(-1, -2), -3)
        pass
    
class TestTeehr(unittest.TestCase):
    pass

class TestNGIABDataPreprocess(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
