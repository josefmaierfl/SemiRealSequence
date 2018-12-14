/**********************************************************************************************************
FILE: generateSequence.h

PLATFORM: Windows 7, MS Visual Studio 2015, OpenCV 3.2

CODE: C++

AUTOR: Josef Maier, AIT Austrian Institute of Technology

DATE: March 2018

LOCATION: TechGate Vienna, Donau-City-Stra�e 1, 1220 Vienna

VERSION: 1.0

DISCRIPTION: This file provides some helper functions.
**********************************************************************************************************/

#pragma once

#include "glob_includes.h"
#include "opencv2/highgui/highgui.hpp"
#include <random>

#include <Eigen/Dense>

#include "generateVirtualSequenceLib\generateVirtualSequenceLib_api.h"

/* --------------------------- Defines --------------------------- */

/* --------------------------- Classes --------------------------- */

/* --------------------- Function prototypes --------------------- */

//Initializes the random number generator with a seed based on the current time
void randSeed(std::default_random_engine& rand_generator);

//Get a random number within a given range
double getRandDoubleValRng(double lowerBound, double upperBound, std::default_random_engine rand_generator = std::default_random_engine((unsigned int)std::rand()));

//construct a rotation matrix from angles given in RAD
cv::Mat GENERATEVIRTUALSEQUENCELIB_API eulerAnglesToRotationMatrix(double x, double y, double z);

//Returns true, if any element of the boolean (CV_8UC1) Mat vector is also true
bool any_vec_cv(cv::Mat bin);

//Returns true, if every element of the double (CV_64FC1) Mat vector is a finite number (no element is infinity nor NaN)
bool isfinite_vec_cv(cv::Mat bin);

//Generates the 3D direction vector for a camera at the origin and a given pixel coordinate
cv::Mat getLineCam1(cv::Mat K, cv::Mat x);

//Generates a 3D line (start coordinate & direction vector) for a second camera within a stereo alignment (cam not at the origin) and a given pixel coordinate
void getLineCam2(cv::Mat R, cv::Mat t, cv::Mat K, cv::Mat x, cv::Mat& a, cv::Mat& b);

//Calculate the z - distance of the intersection of 2 3D lines or the mean z - distance at the shortest perpendicular between 2 skew lines in 3D.
double getLineIntersect(cv::Mat b1, cv::Mat a2, cv::Mat b2);

//Solves a linear equation of th form Ax=b
bool solveLinEqu(cv::Mat& A, cv::Mat& b, cv::Mat& x);

//Converts a (Rotation) matrix to a (Rotation) quaternion
void MatToQuat(const Eigen::Matrix3d & rot, Eigen::Vector4d & quat);

//Checks if a 3x3 matrix is a rotation matrix
bool isMatRotationMat(cv::Mat R);

//Checks if a 3x3 matrix is a rotation matrix
bool isMatRotationMat(Eigen::Matrix3d R);

//Calculates the difference (roation angle) between two rotation quaternions.
double rotDiff(Eigen::Vector4d & R1, Eigen::Vector4d & R2);

//Calculates the difference (roation angle) between two rotation matrices.
double rotDiff(cv::Mat R1, cv::Mat R2);

//Calculates the product of a quaternion and a conjugated quaternion.
void quatMultConj(const Eigen::Vector4d & Q1, const Eigen::Vector4d & Q2, Eigen::Vector4d & Qres);

//Normalizes the provided quaternion.
void quatNormalise(Eigen::Vector4d & Q);

//Calculates the angle of a quaternion.
double quatAngle(Eigen::Vector4d & Q);

//Round every entry of a matrix to its nearest integer
cv::Mat roundMat(cv::Mat m);

/* -------------------------- Functions -------------------------- */

//Checks, if determinants, etc. are too close to 0
inline bool nearZero(double d)
{
	//Decide if determinants, etc. are too close to 0 to bother with
	const double EPSILON = 1e-4;
	return (d<EPSILON) && (d>-EPSILON);
}