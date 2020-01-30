"""
Reads configuration files and changes the option distortCamMat
"""
import sys, re, numpy as np, argparse, os, pandas as pd


def change_configs(input_path, distortCamMat):
    # Load file names
    files_i = os.listdir(input_path)
    if len(files_i) == 0:
        raise ValueError('No files found.')
    files = []
    for i in files_i:
        fnObj = re.search(r'_initial\.', i, re.I)
        if fnObj:
            files.append(i)
    if len(files) == 0:
        raise ValueError('No files including _init found.')
    for file in files:
        tmp = file.replace('.yaml', '_tmp.yaml')
        pfnew = os.path.join(input_path, tmp)
        pfold = os.path.join(input_path, file)
        if os.path.isfile(pfnew):
            raise ValueError('File ' + pfnew + ' already exists.')
        write_config_file(pfold, pfnew, distortCamMat)
        os.remove(pfold)
        os.rename(pfnew, pfold)


def write_config_file(finput, foutput, distortCamMat):
    with open(foutput, 'w') as fo:
        with open(finput, 'r') as fi:
            li = fi.readline()
            line1_found = False
            line2_found = False
            while li:
                lobj = re.search('distortCamMat:', li)
                if lobj:
                    line1_found = True
                    fo.write(li)
                elif line1_found:
                    line1_found = False
                    line2_found = True
                    rpstr = r'\g<1>{}'.format('%.3f' % distortCamMat[0])
                    li1 = re.sub(r'(\s*first:\s*)[0-9.]+',
                                 rpstr, li)
                    fo.write(li1)
                elif line2_found:
                    line2_found = False
                    rpstr = r'\g<1>{}'.format('%.3f' % distortCamMat[1])
                    li1 = re.sub(r'(\s*second:\s*)[0-9.]+',
                                 rpstr, li)
                    fo.write(li1)
                else:
                    fo.write(li)
                li = fi.readline()


def main():
    parser = argparse.ArgumentParser(description='Reads configuration files and changes the option truePosRange '
                                                 'based on the information in the file name')
    parser.add_argument('--path', type=str, required=True,
                        help='Directory holding template configuration files')
    parser.add_argument('--distortCamMat', type=float, nargs='+', required=True,
                        help='Specifies the percentage range or fixed percentage value that is '
                             'used to distort the GT camera matrices')
    args = parser.parse_args()
    if not os.path.exists(args.path):
        raise ValueError('Directory ' + args.path + ' holding template scene configuration files does not exist')
    if len(args.distortCamMat) == 1:
        distortCamMat = [args.distortCamMat[0], args.distortCamMat[0]]
    elif len(args.distortCamMat) == 2:
        distortCamMat = args.distortCamMat
    else:
        raise ValueError('Wrong number of arguments for distortCamMat')
    change_configs(args.path, distortCamMat)


if __name__ == "__main__":
    main()
