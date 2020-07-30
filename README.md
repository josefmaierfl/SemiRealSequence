# SemiRealSequence: Unlimited Semi-Real-World GT Data Generation Framework for Feature-Based Applications

- [Introduction](#introduction)
- [Different Scene Properties](#scene-properties)
- [Installation](#installation)
    - [Dependencies](#dependencies)
        - [Docker](#docker)
        - [System-wide Installation on Linux Systems](#system-dependencies)
    - [Data Generation using a Stand-Alone Executable](#executable)
    - [Executable for Annotating Ground Truth Matches (GTM) and Datasets](#annotation)
    - [Library](#library)
- [Quick Start: Configuration File](#config-file)
    - [Changing default directories when using Docker](#docker-path)
- [Image Folder Structure](#image-folder)
    - [Oxford](#oxford)
    - [KITTI](#kitti)
    - [MegaDepth](#megadepth)
- [Generated Data Structure](#data-structure)
- [Reading Generated Sequence, GTM, and Annotation Data](#read-data)
- [Interfacing the Library](#interface-lib)
    - [Calculation of Stereo Poses](#interface-stereo)
    - [Generation of Synthetic Static and Dynamic Scene Structure](#interface-3d)
    - [Generation of Feature Matches](#interface-matches)
- [Calculation of GTM and GT Optical Flow](#calculate-gtm)
- [Annotating Datasets](#annotation-start)
- [Bulk Configuration File and Data Generation](#multiple-config-files)
- [Random Testing and Data Generation](#random-test)
- [Publication](#publication)

## Introduction <a name="introduction"></a>

Ground truth (GT) data is essential for testing and training computer vision applications.
For this purpose, many real-world and synthetic datasets emerged in recent years.
Synthetic data provides perfect ground truth, which is hard to obtain for real-world data, but it lacks a realistic representation of the world.
This framework combines the best properties of both worlds, which allows us to generate potentially limitless yet realistic GT data for testing and training feature-based applications.
The framework generates synthetic semi-random **3D point clouds, stereo camera poses, and camera trajectories** according to given user requirements while using **real images** for generating sparse feature matches.
The latter are either generated by warping image patches or by utilizing GT matches from well-known datasets.
Homographies for warping image patches are calculated depending on generated 3D data to simulate piece-wise planar 3D structures.
The framework also enables the independent calculation of ground truth matches of various feature types from datasets providing GT flow, disparity, or depth information.
Functionality to calculate GT flow maps from mono depth data and a tool for annotating matches and used datasets is also included.

This repository includes a [library for integrating the framework](#library) into your own application as well as a [stand-alone executable](#executable) to generate data based on configuration files.

Generated data is stored in YAML or XML format which can be specified by the user.
For easy data interfacing, we provide a [C++ and Python interface](#read-data).

The software is tested on Ubuntu 18.04 but we provide a Docker-file for operating system independent usage.

## Different Scene Properties <a name="scene-properties"></a>

SemiRealSequence supports to specify different scene and camera pose properties:
* Virtual image size
* Stereo poses:
    * Specific and/or variation of values or intervals for 6DOF relative poses (i.e. rotation angles and translation)
    * Number of different poses within a generated sequence (corresponds to a set of multiple stereo frames and a 3D point cloud)
    * Type (continuous or volatile) and amount of change for every pose parameter
    * Desired average image overlap of stereo cameras
* Camera trajectories:
    * A specific trajectory providing node coordinates,
    * a flag for utilizing a random trajectory optionally specifying a main direction, or
    * a function (currently only ellipsoids) can be provided.
    * Camera orientation of first stereo cameras relative to camera movement
    * Camera velocity
* Static 3D point clouds and geometric matches:
    * A desired inlier ratio or interval
    * A relative inlier ratio variation rate
    * Number or interval of true positive (TP) stereo correspondences
    * A relative variation rate for number of TP
    * A minimum distance between correspondences in the first stereo image
    * Global depth ratios with respect to stereo cameras
* Dynamic 3D point clouds and geometric matches:
    * Initial and minimal (throughout the whole sequence) number of dynamic objects
    * Valid starting positions for initializing dynamic objects
    * Initial depths or distributions thereof
    * Movement directions
    * Velocities relative to camera movements (currently only straight moving objects are supported)
    * Relative occupied image area
    * Relative portion of geometric matches or intervals thereof compared to static scene elements
* Feature matches:
    * Portion of matches using user-provided images generated by warping and adding intensity noise to image patches
    * Portion (for every dataset) of Ground Truth Matches (GTM) to use from datasets:
        * [Oxford](http://www.robots.ox.ac.uk/~vgg/research/affine/)
        * [KITTI](http://www.cvlibs.net/datasets/kitti/eval_stereo_flow.php)
        * [MegaDepth](https://research.cs.cornell.edu/megadepth/)
    * Number if images to use from [ImageNet](http://www.image-net.org/) (supports filtering by IDs and buzzwords)
    * Amount of Gaussian intensity noise to add to matching image patches
    * Portion of gross error True Negative (TN) matches
    * Repeated pattern portions separately for stereo pairs and from frame to frame along the trajectory
    * Keypoint and descriptor type (All available within [OpenCV](https://docs.opencv.org/4.2.0/d5/d51/group__features2d__main.html) (including [contrib](https://docs.opencv.org/4.2.0/d7/d7a/group__xfeatures2d__experiment.html)) in addition to [BOLD](https://github.com/vbalnt/bold) and [RIFF](http://press.liacs.nl/publications/RIFF%20-%20Retina-inspired%20Invariant%20Fast%20Feature%20Descriptor.pdf))

Most parameters can be initialized randomly.
Details can be found in generated [configuration files](#config-file).

## Installation <a name="installation"></a>

We provide multiple possibilities to use this software:
* Stand-alone executables for
    * [generating semi-real-world stereo sequences based on configuration files](#config-file),
    * [calculation of Ground Truth Matches](#calculate-gtm) (GTM) for datasets [Oxford](http://www.robots.ox.ac.uk/~vgg/research/affine/), [KITTI](http://www.cvlibs.net/datasets/kitti/eval_stereo_flow.php), and [MegaDepth](https://research.cs.cornell.edu/megadepth/), in addition to optical flow for the MegaDepth dataset, and for
    * [annotating GTM and mentioned datasets](#annotation-start).
* Docker for afore mentioned executables
* A [library](#interface-lib) for generating semi-real-world stereo sequences that can be integrated into your own application

### Dependencies <a name="dependencies"></a>

#### Docker <a name="docker"></a>

For generating semi-real-world sequences using a stand-alone executable, [Docker](https://docs.docker.com/get-docker/) can be used.
After installing Docker, the corresponding Docker image can be built executing `./build_docker_base.sh` in the main directory of this repository.
On Windows, the image can be built by executing `docker build -t semi_real_sequence:1.0 .` in the main directory of this repository using Powershell.

#### System-wide Installation on Linux Systems <a name="system-dependencies"></a>

SemiRealSequence depends on the following libraries:
* Python 3.6.10
* Eigen 3.3.7
* Boost 1.71.0
* VTK 8.2.0
* PCL 1.11.0
* Ceres 1.14.0
* OpenCV 4.2.0

For installing above libraries, the following packages should be installed:
```bash
sudo apt-get update
sudo apt-get install software-properties-common apt-utils curl
Optional: curl https://pyenv.run | bash
Optional: env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install -v 3.6.10 && pyenv global 3.6.10
sudo apt-get install libreadline-dev libglib2.0-dev
sudo add-apt-repository 'deb http://security.ubuntu.com/ubuntu xenial-security main'
sudo apt-get update
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install wget \
    libtbb2 \
    libtbb-dev \
    libglew-dev \
    qt5-default \
    libxkbcommon-dev \
    libflann-dev \
    libpng-dev \
    libgtk-3-dev \
    libgtkglext1 \
    libgtkglext1-dev \
    libtiff-dev \
    libtiff5-dev \
    libtiffxx5 \
    libjpeg-dev \
    libjasper1 \
    libjasper-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libdc1394-22-dev \
    openexr \
    libatlas-base-dev \
    gfortran
sudo apt-get install libglu1-mesa-dev mesa-common-dev mesa-utils freeglut3-dev qt5-default
sudo apt-get install libgoogle-glog-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    libomp-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer1.0-dev \
    libmpc-dev
```
All mentioned libries (Boost,  OpenCV, ...) can be installed by executing `./build_thirdparty.sh` within directory `ci` of this repository.
If some of the libraries are already installed on your system, missing libraries can be installed using the corresponding script file within directory [ci](./ci).

In addition, needed Python packages can be installed by executing
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r ./py_test_scripts/requirements.txt
```

### Data Generation using a Stand-Alone Executable <a name="executable"></a>

If not using Docker, SemiRealSequence can be built by executing `./build_SemiRealSequence.sh`.
The executables can be found in directory `generateVirtualSequence/build`

### Executable for Annotating Ground Truth Matches (GTM) and Datasets <a name="annotation"></a>

If you do NOT want to generate semi-real-world sequences but use the integrated annotation framework to generate GTM and annotation data, the follwing steps should be performed:

#### With Docker:

`./build_docker_base.sh annotate`

For annotating data call `./run_docker_base.sh live EXE gtm [additional options]`

#### Without Docker:

`./build_SemiRealSequence.sh annotate`

or

```bash
cd generateVirtualSequence
mkdir build
cd build
cmake ../ -DCMAKE_BUILD_TYPE=Release -DUSE_MANUAL_ANNOTATION=ON
make -j "$(nproc)"
```
For annotating data use executable `virtualSequenceLib-GTM-interface` within directory `generateVirtualSequence/build`.

### Library <a name="library"></a>

To use SemiRealSequence within your own application, it can be built and installed by calling

`./build_SemiRealSequence.sh install`

or by performing the following steps:

```bash
cd generateVirtualSequence
mkdir build
cd build
cmake ../ -DCMAKE_BUILD_TYPE=Release -DOPTION_BUILD_TESTS=OFF -DOPTION_BUILD_EXAMPLES=OFF -DENABLE_CMD_INTERFACE=OFF -DENABLE_GTM_INTERFACE=OFF -DBUILD_SHARED_LIBS=OFF
make -j "$(nproc)"
sudo make install
```

To integrate it within CMake include the following into your `CMakeLists.txt`:

```
find_package(semi_real_sequence REQUIRED)

Optional: find_package(Eigen REQUIRED)
Optional: find_package(Boost 1.71.0 REQUIRED COMPONENTS thread filesystem regex system)
Optional: find_package(Ceres REQUIRED)

find_package(OpenCV 4.2.0 REQUIRED)
find_package(VTK 7.2 QUIET NO_MODULE)
if(NOT VTK_FOUND)
    find_package(VTK 8.2.0 REQUIRED NO_MODULE)
endif()
message(STATUS "VTK Version: ${VTK_VERSION}")
find_package(PCL 1.11.0 REQUIRED)

target_link_libraries(your_project_name
  ${OpenCV_LIBS}
  ${VTK_LIBRARIES}
  ${PCL_LIBRARY_DIRS}
  ${PCL_COMMON_LIBRARIES}
  ${PCL_GEOMETRY_LIBRARIES}
  ${PCL_VISUALIZATION_LIBRARIES}
  #${CERES_LIBRARIES}
  #${Boost_LIBRARIES}
  semi_real_sequence::generateVirtualSequenceLib)

target_include_directories(your_project_name
  PRIVATE
  ${DEFAULT_INCLUDE_DIRECTORIES}
  ${OpenCV_INCLUDE_DIRS}
  ${VTK_USE_FILE}
  ${PCL_INCLUDE_DIRS}
  #${CERES_INCLUDE_DIRS}
  #${Boost_INCLUDE_DIRS}
  #${Eigen_INCLUDE_DIR}
  semi_real_sequence::generateVirtualSequenceLib)
```

## Quick Start: Configuration File <a name="config-file"></a>

If [Docker](#docker) or [stand-alone executables](#executable) are used, a template configuration file can be generated by either executing `./run_docker_base.sh live --genConfTempl file` or `./generateVirtualSequence/build/virtualSequenceLib-CMD-interface --genConfTempl path/file`.
`path` stands for the full path and `file` for the filename that should be used for the configuration file.
The filename extension can either be `.yaml` or `.xml` to generate a template file in XML or YAML format.
For Docker, the generated configuration file can be found in folder `config` of the repository.

This file can either be used directly to generate data, or parameters can be adapted within the file.
A description of every parameter can be found in the file.

Before data can be generated, images and/or datasets must be accessible in one folder.
See [Image Folder Structure](#image-folder) for details.
This repository provides a few images in folder [images](./images) that will be used by default if no other image folder is specified or the images are replaced.

To start generating a sequence execute `./run_docker_base.sh live --conf_file file` or `./generateVirtualSequence/build/virtualSequenceLib-CMD-interface --conf_file path/file --img_path path_to_images --img_pref / --store_path output_path`.
For Docker, the generated 3D and matching data can be found in folder `data` of the repository.

### Changing default directories when using Docker <a name="docker-path"></a>

By running Docker with option `IMGPATH path_to_images` (i.e. `./run_docker_base.sh live IMGPATH path_to_images --conf_file file`) you can specify your own image path.
`path_to_images` stands for the full path of your images.

By running Docker with option `CONFIGPATH path` (i.e. `./run_docker_base.sh live CONFIGPATH path --conf_file file`) you can specify your own path for storing and loading configuration files.
`path` stands for the full path.

By running Docker with option `DATAPATH your_path` (i.e. `./run_docker_base.sh live DATAPATH your_path --conf_file file`) you can specify your own path for storing and loading generated sequences.
`your_path` stands for the full path for storing and loading generated sequences.

Options `IMGPATH`, `CONFIGPATH`, `DATAPATH`, and `EXE` must be placed before options with leading `--` and after `[live, shutdown]`.

## Image Folder Structure <a name="image-folder"></a>

For generating feature matches, images and/or datasets ([KITTI](http://www.cvlibs.net/datasets/kitti/eval_stereo_flow.php) and/or [MegaDepth](https://research.cs.cornell.edu/megadepth/)) must be present in one folder.
Images of any kind can be used (no need of corresponding GT data).
Furthermore, images from [ImageNet](http://www.image-net.org/) can be used by providing keywords and/or IDs within [configuration files](#config-file).
Images from ImageNet are automatically downloaded.

When executing SemiRealSequence, user-provided images can be filtered using option `--img_pref` by specifying sub-folders, pre- and/or and post-fixes.
For details call `./run_docker_base.sh live -h` or `./generateVirtualSequence/build/virtualSequenceLib-CMD-interface -h`.

If GTM from datasets KITTI (flow and disparity of years 2012 and 2015) and/or MegaDepth should be used, the datasets must be manually downloaded and copied into the image directory.

### Oxford <a name="oxford"></a>

The [Oxford dataset](http://www.robots.ox.ac.uk/~vgg/research/affine/) is automatically downloaded and extracted as soon as parameter `oxfordGTMportion: >0` is specified in the configuration file.

### KITTI <a name="kitti"></a>

Datasets from both years, [2012](http://www.cvlibs.net/download.php?file=data_stereo_flow.zip) and [2015](http://www.cvlibs.net/download.php?file=data_scene_flow.zip) have to be downloaded.
Create a folder `KITTI` and 2 sub-folders named `2012` and `2015` in your image-directory:
```bash
cd your_image_directory
mkdir KITTI
cd KITTI
mkdir 2012
mkdir 2015
```
Copy the corresponding extracted training datasets into the created folders:
```bash
cd download_folder
unzip data_stereo_flow.zip -d data_stereo_flow
cd data_stereo_flow/training
cp -r * /your_image_directory/KITTI/2012
cd ../..
unzip data_scene_flow.zip -d data_scene_flow
cd data_scene_flow/training
cp -r * /your_image_directory/KITTI/2015
```

### MegaDepth <a name="megadepth"></a>

Download the [MegaDepth v1 Dataset](https://research.cs.cornell.edu/megadepth/dataset/Megadepth_v1/MegaDepth_v1.tar.gz) (199GB) and [MegaDepth v1 SfM models](https://research.cs.cornell.edu/megadepth/dataset/MegaDepth_SfM/MegaDepth_SfM_v1.tar.xz) (667GB).
Be aware that downloading might take days depending on your internet connection.

Create a folder `MegaDepth` and 2 sub-folders `MegaDepth_v1` and `SfM` in your image-directory:
```bash
cd your_image_directory
mkdir MegaDepth
cd MegaDepth
mkdir MegaDepth_v1
mkdir SfM
```
After extracting downloaded MegaDepth_v1 data, move all numbered folders (i.e. `0000` to `5018`) into folder `your_image_directory/MegaDepth/MegaDepth_v1`.
After extracting downloaded SfM data, move all numbered folders (i.e. `0000` to `5018`) into folder `your_image_directory/MegaDepth/SfM`.

## Generated Data Structure <a name="data-structure"></a>

Depending on your chosen file format (`*.xml`, `*.yaml`, `*.xml.gz`, `*.yaml.gz`) data is stored in the default `data` folder (only if Docker is used) or in your specified directory.
After generating one or more sequences, this main data folder holds a file `sequInfos.[yaml/xml]` listing all generated sequences and corresponding short overviews of used parameters (e.g. corresponding folder name, number of different stereo configuration, statistics on pose parameters, inlier ratios, ...).
A description of every parameter can be found in the file.
Different generated sequences are separated by tags `parSetNr*` with index number `*` starting at 0.
This file is never compressed (`*.gz`).

### 3D Data Folders <a name="data-folder-3d"></a>

Each folder (hash value based on used parameters) within the main data folder holds 3D data of a full sequence and one or more corresponding feature match data folders.
These 3D data folders hold a file `sequPars.[extension]` which includes all parameters used to generate 3D data in addition to some 3D data like absolute camera poses.
A description of every parameter can be found in the file.

Files `sequSingleFrameData_*.[extension]` hold 3D data for every generated stereo frame with consecutive stereo frame number `*` starting at 0.
A description of every parameter can be found in the file.

File `pclCloud_staticWorld3DPts.pcd` holds static 3D point cloud data stored in PCL `*.pcd` format.
3D point data corresponding to single generated stereo frames is also included in `sequSingleFrameData_*.[extension]`.

Files `pclCloud_movObj3DPts_*.pcd` hold dynamic 3D point cloud data for every dynamic object and stereo frame.
This information is also included in `sequSingleFrameData_*.[extension]`.
An index for mapping `pclCloud_movObj3DPts_*.pcd` to a stereo frame is available in `sequSingleFrameData_*.[extension]`.

One 3D data folder can hold multiple feature match data folders (hash value based on used matching parameters) that share the same 3D data.
An overview on different feature match data folders including folder names and short parameter overviews (like feature type, repeatability error, intensity noise, ...) separated by tags `parSetNr*` can be found in `matchInfos.[yaml/xml]`.
A description of every parameter can be found in the file.
This file is never compressed (`*.gz`).

### Feature Match Data Folders <a name="data-folder-matches"></a>

Each folder (hash value based on used matching parameters) within 3D data folders holds correspondence (i.e. feature matches) data for every stereo frame separately stored in files `matchSingleFrameData_*.[extension]`.
`*` corresponds to consecutive stereo frame numbers equal to `sequSingleFrameData_*.[extension]`.
Stored data includes e.g. matches, keypoints, descriptors, inlier mask, dynamic object mask, homographies used to warp individual patches centered at keypoint locations, keypoint repeatability errors, ...

File `kpErrImgInfo.[extension]` holds statistics about keypoint repeatability errors, filenames and folders of used images, and a statistic on the execution time.

## Reading Generated Sequence, GTM, and Annotation Data <a name="read-data"></a>

We provide a ***C++ interface*** for reading generated data:

* [generateVirtualSequence/source/examples/generateVirtualSequencecmd/loadMatches.h](./generateVirtualSequence/source/examples/generateVirtualSequencecmd/loadMatches.h)

* [generateVirtualSequence/source/examples/generateVirtualSequencecmd/readPointClouds.h](./generateVirtualSequence/source/examples/generateVirtualSequencecmd/readPointClouds.h)

* [generateVirtualSequence/source/examples/generateVirtualSequencecmd/readGTM.h](./generateVirtualSequence/source/examples/generateVirtualSequencecmd/readGTM.h)

An example on how to use the interface can be found in [generateVirtualSequence/source/examples/generateVirtualSequencecmd](./generateVirtualSequence/source/examples/generateVirtualSequencecmd) and can be executed using generated data by calling `./run_docker_base.sh live EXE load --sequPath your_sequence_folder` or `./generateVirtualSequence/build/loadData --sequPath output_path/your_sequence_folder`.
For more details and additional options call `./run_docker_base.sh live EXE load -h` or `./generateVirtualSequence/build/loadData -h`.
When using Docker, all options specifying a file or path start with the first sub-folder of your main data, image, or configuration files directory (e.g. `--sequPath 13636473635092440529`, `--gtm_file Oxford/bark/GTM/ORB_GTd-ORB_img1-img2.yaml.gz`, `--file 13636473635092440529/4148949948977900531/matchSingleFrameData_0.yaml.gz`).

For changing default Docker data, image, or configuration files directories (on your operating system side) see [here](#docker-path).

A ***Python interface*** and example on how to generate and convert data for training and testing [NG-RANSAC](https://github.com/vislearn/ngransac) can be found [here](https://github.com/josefmaierfl/autocalib_test_package/tree/conversion).

## Interfacing the Library <a name="interface-lib"></a>

If you installed SemiRealSequence on your system as described [here](#library), you can integrate it into your own application.

Generating semi-real-world sequences is split into 3 parts:
* [Calculation of stereo poses](#interface-stereo): `./generateVirtualSequence/source/generateVirtualSequenceLib/include/getStereoCameraExtr.h`
* [Generation of synthetic static and dynamic scene structure in addition to camera poses](#interface-3d): `./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateSequence.h`
* [Generation of feature matches using real images](#interface-matches): `./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h`

Examples on how to interface to the library can be found in [generateVirtualSequence/source/CMD_Interface/main.cpp](./generateVirtualSequence/source/CMD_Interface/main.cpp) and [generateVirtualSequence/source/tests/genvirtsequlib-test/main.cpp](./generateVirtualSequence/source/tests/genvirtsequlib-test/main.cpp).

### Calculation of Stereo Poses <a name="interface-stereo"></a>

When creating an object of class `GenStereoPars` (within [generateVirtualSequence/source/generateVirtualSequenceLib/include/getStereoCameraExtr.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/getStereoCameraExtr.h)), the following vectors must be provided (size of each vector corresponds to desired number of different stereo configurations):
* Ranges for the x-components (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo translation vectors
* Ranges for the y-components (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo translation vectors
* Ranges for the z-components (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo translation vectors
* Ranges for rotation about x-axis (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo rotation
* Ranges for rotation about y-axis (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo rotation
* Ranges for rotation about z-axis (`std::vector<std::vector<double>>(n, std::vector<double>(2))`) of relative stereo rotation
* Desired image overlap
* Virtual image size

Afterwards member function `optimizeRtf()` can be called to estimate stereo poses followed by reading calculated values (`getEulerAngles, getCamPars`).

### Generation of Synthetic Static and Dynamic Scene Structure <a name="interface-3d"></a>

If only synthetic static and dynamic scene structure in addition to camera poses (no feature matches) should be generated, create an object of class `genStereoSequ` (within [generateVirtualSequence/source/generateVirtualSequenceLib/include/generateSequence.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateSequence.h)) and provide:
* struct `StereoSequParameters` (detailed descriptions of every member can be found in `./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateSequence.h`)
* Camera matrices of first and second cameras in addition to user-specified or estimated (see [above](#interface-stereo)) relative stereo poses R & t (`std::vector<cv::Mat>`)

Afterwards member function `startCalc()` can be called to generate 3D data.

Otherwise, see [Generation of Feature Matches](#interface-matches).

### Generation of Feature Matches <a name="interface-matches"></a>

To generate synthetic static and dynamic scene structure in addition to camera poses and feature matches based on real images, create an object of class `genMatchSequ` (within [generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h)) and provide:
* struct `StereoSequParameters` (detailed descriptions of every member can be found in `./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateSequence.h`)
* Camera matrices of first and second cameras in addition to user-specified or estimated (see [above](#interface-stereo)) relative stereo poses R & t (`std::vector<cv::Mat>`)
* struct `GenMatchSequParameters` (detailed descriptions of every member can be found in [generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h))

Afterwards member function `generateMatches()` can be called to generate 3D data and feature matches.

To load synthetic static and dynamic scene structure in addition to camera poses generated earlier and generate feature matches using loaded data, create an object of class `genMatchSequ` (within [generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h)) and provide:
* struct `GenMatchSequParameters` (detailed descriptions of every member can be found in [generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h](./generateVirtualSequence/source/generateVirtualSequenceLib/include/generateMatches.h))
* Path (`string`) to the stored 3D data (`[previous output path of generated data]/[hash value corresponding to folder name of generated 3D data]`)

Afterwards member function `generateMatches()` can be called to generate feature matches.

## Calculation of GTM and GT Optical Flow  <a name="calculate-gtm"></a>

Typically, Ground Truth Matches (GTM) and GT optical flow for the MegaDepth dataset are calculated on-the-fly when generating sequences with SemiRealSequence and [configuration file](#config-file) parameters `oxfordGTMportion: >0`, `kittiGTMportion: >0`, and/or `megadepthGTMportion: >0`.
To calculate them without generating a sequence, you can call `./run_docker_base.sh live EXE gtm --kitti --oxford --mega --del_pool` or `./generateVirtualSequence/build/virtualSequenceLib-GTM-interface --img_path path_to_images --kitti --oxford --mega --del_pool`.
For more details and additional options call `./run_docker_base.sh live EXE gtm -h` or `./generateVirtualSequence/build/virtualSequenceLib-GTM-interface -h`.

For changing the default Docker image directory (on your operating system side) see [here](#docker-path).

Calculated GTM and optical flow are stored in corresponding dataset folders within your image folder (see [Image Folder Structure](#image-folder)).

ToDo: Link to download optical flow data and GTM with ORB features

## Annotating Datasets <a name="annotation-start"></a>

For annotating datasets and GTM, SemiRealSequence must be compiled as described [here](#annotation).
To start annotating e.g. the MegaDepth dataset, call `./run_docker_base.sh live EXE gtm --mega --del_pool` or `./generateVirtualSequence/build/virtualSequenceLib-GTM-interface --img_path path_to_images --mega --del_pool`.
For more details and additional options call `./run_docker_base.sh live EXE gtm -h` or `./generateVirtualSequence/build/virtualSequenceLib-GTM-interface -h`.
A basic description on how to annotate data is shown in the framework.
Additional details and options are displayed by pressing `h` within active annotation tool window.

For changing the default Docker image directory (on your operating system side) see [here](#docker-path).

Be aware that annotation results are only stored after an image pair was completely processed/annotated (holds for all datasets).
Annotation can be aborted and resumed after each image pair except for MegaDepth.
If the annotation of a MegaDepth sub-set (i.e. numbered directories `0000` to `5018` and sub-directories (e.g. `dense0`, `dense1`, ...)) is aborted, the application skips this sub-set in the next run and resumes with the next sub-set.

Annotation results can be found in:
```
path_to_images/Oxford/[bark, bikes, ...]/GTM/[keypoint type]_GTd-[descriptor type]_[image name 1]-[image name 2].yaml.gz
path_to_images/KITTI/[2012, 2015]/[disp_noc, flow_noc, disp_noc_0]/GTM/[keypoint type]_GTd-[descriptor type]_[image name 1]-[image name 2].yaml.gz
path_to_images/MegaDepth/MegaDepth_v1/[0000 to 5018]/[dense0, dense1, ...]/GTM/[keypoint type]_GTd-[descriptor type]_[image name 1]-[image name 2].yaml.gz
```
Results can be loaded using the provided [C++ interface](#read-data) or by using [PyYAML](https://pyyaml.org/) (an example on how to load OpenCV matrices (stored in YAML format) in Python can be found [here](https://github.com/josefmaierfl/autocalib_test_package/tree/conversion)).
To process only automatic and manual annotation data, loaded annotation data vectors should be filtered using only elements marked with character `M` or `A` in vector/list `autoManualAnnot`.

## Bulk Configuration File and Data Generation <a name="multiple-config-files"></a>

We used SemiRealSequence to extensively test a [relative stereo pose estimation pipeline](https://github.com/josefmaierfl/matchinglib_poselib).
Thus, we developed a Python framework to read multiple [configuration files](#config-file) holding different parameter settings and performing parameter sweeps on some other parameters (like inlier ratio, depth distributions, ...) leading to a large set of new configuration files that were used to generate semi-real-world stereo sequences with different properties.
The Python framework supports to read configuration files and generate sequences in parallel (up to number of available CPUs).
If using GTM from datasets Oxford, KITTI, and/or MegaDepth within SemiRealSequence, GTM should be generated in advance as generating GTM is only allowed (system-wide mutex) for one process at a time.

We offer 2 frameworks that support multiple parameter sweeps and parallel processing of SemiRealSequence:
* [Testing of a relative stereo pose estimation pipeline](https://github.com/josefmaierfl/autocalib_test_package)
* [Data generation for testing and training NG-RANSAC](https://github.com/josefmaierfl/autocalib_test_package/tree/conversion)

Sweeping different parameters as already implemented in afore mentioned frameworks can easily be performed by adapting Python files within [https://github.com/josefmaierfl/autocalib_test_package/tree/conversion/ngransac_prepare](https://github.com/josefmaierfl/autocalib_test_package/tree/conversion/ngransac_prepare).

If Docker is used to start SemiRealSequence, script `./run_docker_base.sh` provides functionality to shut the operating system down after all sequences were generated by setting the first argument to `shutdown` (usage: `./run_docker_base.sh shutdown [remaining options]`).
Otherwise, use `./run_docker_base.sh live [remaining options]`.

## Random Testing and Data Generation <a name="random-test"></a>

For testing SemiRealSequence, we provide an executable which randomly generates 3D data and feature matches.
To start testing the library, call `./run_docker_base.sh live EXE test` or `./generateVirtualSequence/build/generateVirtualSequenceLib-test --img_path path_to_images --img_pref / --store_path output_path`.
For more details and additional options call `./run_docker_base.sh live EXE test -h` or `./generateVirtualSequence/build/generateVirtualSequenceLib-test -h`.
For Docker, the generated 3D and matching data can be found in folder `data` of the repository.
For changing default Docker data or image directories (on your operating system side) see [here](#docker-path).

## Citation <a name="publication"></a>

Coming soon
<!--
Please cite the following paper if you use SemiRealSequence or parts of this code in your own work.

```
@inproceedings{maier2020semireal,
  title={Unlimited Semi-Real-World Ground Truth Generation for Feature-Based Applications},
  author={Maier, Josef},
  booktitle={ACCV},
  year={2020}
}
```
-->
