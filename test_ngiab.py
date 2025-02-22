from ngiab import NGIAB

if __name__ == "__main__":

    # data path inside docker container
    data_dir = '/data/AWI_16_2863657_007'

    print('Running Python wrapper for NGIAB ...')

    #test_ngiab = NGIAB(data_dir, serial_execution_mode=True)
    test_ngiab = NGIAB(data_dir)
    test_ngiab.run()
    pass
