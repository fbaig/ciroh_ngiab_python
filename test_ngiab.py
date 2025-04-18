from pyngiab import PyNGIAB

if __name__ == "__main__":

    # data path inside docker container
    data_dir = '/data/AWI_16_2863657_007'

    print('Running Python wrapper for NGIAB ...')

    #test_ngiab = PyNGIAB(data_dir, serial_execution_mode=True)
    test_ngiab = PyNGIAB(data_dir)
    test_ngiab.run()
    pass
