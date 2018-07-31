#include <Python.h>
#include <stdio.h>
#include <math.h>
#include <vector>
#include <iostream>
#include <omp.h>

// Boost python
#include <boost/python.hpp>

#include "config.h"
#include "imageerrors.h"
#include "format/format.h"

double* convertListIntoArray(PyObject *imgHDR, int nbPixels, float mult) {
  double * data = new double[3 * nbPixels];
  for (int i = 0; i < nbPixels; ++i) {
    for (int j = 0; j < 3; ++j) {
      data[i * 3 + j] = (double) PyFloat_AsDouble(
          PyTuple_GetItem(PyList_GetItem(imgHDR, i), j)) * mult;
    }
  }
  return data;
}

unsigned char* convertListIntoArrayMask(PyObject *imgMask, int nbPixels) {
  unsigned char* data = new unsigned char[nbPixels];
  for (int i = 0; i < nbPixels; ++i) {
    if ((float) PyFloat_AsDouble(PyTuple_GetItem(PyList_GetItem(imgMask, i), 0))
        != 0
        || (float) PyFloat_AsDouble(
            PyTuple_GetItem(PyList_GetItem(imgMask, i), 1)) != 0
        || (float) PyFloat_AsDouble(
            PyTuple_GetItem(PyList_GetItem(imgMask, i), 2)) != 0) {
      data[i] = 1;
    } else {
      data[i] = 0;
    }
  }
  return data;
}

static PyObject * rgbe_rmse(int width, int height, PyObject *imgHDR1,
    PyObject *imgHDR2, float mult = 1.f, int typeMetric = 0, PyObject *imgMask =
        NULL) {

  // Check parameters
  if (typeMetric < 0 || typeMetric > 4) {
    printf("Error when reading the arguments, aborting.\n");
    return NULL;
  }
#if VERBOSE
  printf("Reading of the parameters successful, mult is %f\n", mult);
#endif

  // Read all images
  double * imgHDR1Data = convertListIntoArray(imgHDR1, width * height, mult);
  double * imgHDR2Data = convertListIntoArray(imgHDR2, width * height, mult);
  unsigned char * imgMaskData = 0;
  if (imgMask != 0 && imgMask != Py_None) {
    imgMaskData = convertListIntoArrayMask(imgMask, width * height);
  }

  // Compute the difference and fill diff image
  unsigned char * imgDiffData = new unsigned char[width * height * 3];
  float error = metric(imgHDR1Data, imgHDR2Data, imgMaskData, imgDiffData,
      width, height, (EErrorMetric) typeMetric);

  // We write back the difference image to a python object
  // And pack the results
  PyObject * imgDiff = PyList_New(width * height);
  for (int i = 0; i < width * height; ++i) {
    PyList_SetItem(imgDiff, i,
        Py_BuildValue("(i,i,i)", imgDiffData[i * 3], imgDiffData[i * 3 + 1],
            imgDiffData[i * 3 + 2]));
  }
  PyObject * resultsPy = Py_BuildValue("fO", error, imgDiff);
  Py_DECREF(imgDiff);

  // Free memory
  delete[] imgDiffData;
  delete[] imgHDR1Data;
  delete[] imgHDR2Data;
  if (imgMaskData)
    delete[] imgMaskData;

  // We return the rmse and the difference image
  return resultsPy;
}

static PyObject * rgbe_rmse_all(int width, int height, PyObject *imgHDR1,
    PyObject *imgHDR2, float mult = 1.f, PyObject *imgMask = NULL) {
#if VERBOSE
  printf("Reading of the parameters successful, mult is %f\n", mult);
#endif

  // Read all images
  double * imgHDR1Data = convertListIntoArray(imgHDR1, width * height, mult);
  double * imgHDR2Data = convertListIntoArray(imgHDR2, width * height, mult);
  unsigned char * imgMaskData = 0;
  if (imgMask != 0 && imgMask != Py_None) {
    imgMaskData = convertListIntoArrayMask(imgMask, width * height);
  }

  float errors[6];
  for (int idError = 0; idError < 6; idError++) {
    // We compute the RMSE
    float error = metric(imgHDR1Data, imgHDR2Data, imgMaskData, NULL, width,
        height, (EErrorMetric) idError);
    errors[idError] = error;
  }

  PyObject * resultsPy = Py_BuildValue("ffffff", errors[0], errors[1],
      errors[2], errors[3], errors[4], errors[5]);

  // Free memory
  delete[] imgHDR1Data;
  delete[] imgHDR2Data;
  if (imgMaskData)
    delete[] imgMaskData;

  // We return the rmse and the difference image
  return resultsPy;
}

static PyObject * rgbe_rmse_all_images(int width, int height,
    PyObject *imagesPath, PyObject *imgHDR2, float mult = 1.f,
    PyObject *imgMask = NULL) {

  // Read all images passed
  std::vector<std::string> images;
  int nbImages = PyList_Size(imagesPath);
  for (int i = 0; i < nbImages; i++) {
    images.push_back(
        boost::python::extract<std::string>(PyList_GetItem(imagesPath, i)));
  }

  // Read the reference image and mask
  double * imgHDRRef = convertListIntoArray(imgHDR2, width * height, mult);
  unsigned char * imgMaskData = 0;
  if (imgMask != 0 && imgMask != Py_None) {
    imgMaskData = convertListIntoArrayMask(imgMask, width * height);
  }

  const int NBMETRIC = 7;

  // Launch the computation
  std::vector<std::vector<float> > metrics(images.size());

#pragma omp parallel for
  for (int i = 0; i < (int) images.size(); i++) {
    // Open the image
    Format* f = loadImage(images[i]);
    if (f != NULL && f->getWidth() == width && f->getHeight() == height) {
      double * imageHDRDouble = f->toDouble();
      // Else, compute the metric
      for (int idError = 0; idError < NBMETRIC; idError++) {
        // We compute the RMSE
        float error = metric(imageHDRDouble, imgHDRRef, imgMaskData, NULL,
            width, height, (EErrorMetric) idError);
        metrics[i].push_back(error);
      }
      delete[] imageHDRDouble;
    } else {
      // If there is an error on the image reading
      for (int i = 0; i < NBMETRIC; i++) {
        metrics[i].push_back(-1.f); // Invalid number
      }
    }

    delete f;
    std::cout << images[i] << ": ( " << metrics[i][0] << "; " << metrics[i][1]
        << "; " << metrics[i][2] << "; " << metrics[i][3] << "; "
        << metrics[i][4] << "; " << metrics[i][5] << "; " << metrics[i][6] << ")\n";
  }

  // Free memory
  delete[] imgHDRRef;
  if (imgMaskData)
    delete[] imgMaskData;

  // Construct the python results
  PyObject * resPy = PyList_New(images.size());
  for(int i = 0; i < images.size(); i++) {
    PyList_SetItem(resPy, i, Py_BuildValue("fffffff", metrics[i][0], metrics[i][1],
        metrics[i][2], metrics[i][3], metrics[i][4], metrics[i][5],metrics[i][6]));
  }

  return resPy;
}

static PyObject * rgbe_rmse_all_images_percentage(int width, int height, float percentage,
                                       PyObject *imagesPath, PyObject *imgHDR2, float mult = 1.f) {

  // Read all images passed
  std::vector<std::string> images;
  int nbImages = PyList_Size(imagesPath);
  for (int i = 0; i < nbImages; i++) {
    images.push_back(
      boost::python::extract<std::string>(PyList_GetItem(imagesPath, i)));
  }

  if(percentage > 1.f || percentage <= 0.f) {
    std::cerr << "Invalid percentage: " << percentage << "\n";
    return 0;
  }

  // Read the reference image and mask
  double * imgHDRRef = convertListIntoArray(imgHDR2, width * height, mult);
  unsigned char * imgMaskData = 0; // No mask for now

  const int NBMETRIC = 7;

  // Launch the computation
  std::vector<std::vector<float> > metrics(images.size());

#pragma omp parallel for
  for (int i = 0; i < (int) images.size(); i++) {
    // Open the image
    Format* f = loadImage(images[i]);
    if (f != NULL && f->getWidth() == width && f->getHeight() == height) {
      double * imageHDRDouble = f->toDouble(mult);
      // Else, compute the metric
      for (int idError = 0; idError < NBMETRIC; idError++) {
        // Compute error pixel wise
        std::vector<float> pixelErrors(f->getWidth()*f->getHeight(), 0.0f);
        for (int i = 0; i < width * height; ++i) {
          pixelErrors[i] = metricPix(imageHDRDouble, imgHDRRef, i, (EErrorMetric) idError);
        }

        // Sort the metric vector
        // and compute the metric for the percentage of selected pixels
        std::sort(pixelErrors.begin(), pixelErrors.end());
        float error = 0.f;
        for (int i = 0; i < width * height * percentage; ++i) {
          error += pixelErrors[i];
        }
        error = errorNorm(error, width * height * percentage, (EErrorMetric) idError);

        // We compute the RMSE
        metrics[i].push_back(error);
      }
      delete[] imageHDRDouble;
    } else {
      // If there is an error on the image reading
      for (int i = 0; i < NBMETRIC; i++) {
        metrics[i].push_back(-1.f); // Invalid number
      }
    }

    delete f;
    std::cout << images[i] << ": ( " << metrics[i][0] << "; " << metrics[i][1]
              << "; " << metrics[i][2] << "; " << metrics[i][3] << "; "
              << metrics[i][4] << "; " << metrics[i][5] << "; " << metrics[i][6] << ")\n";
  }

  // Free memory
  delete[] imgHDRRef;
  if (imgMaskData)
    delete[] imgMaskData;

  // Construct the python results
  PyObject * resPy = PyList_New(images.size());
  for(int i = 0; i < images.size(); i++) {
    PyList_SetItem(resPy, i, Py_BuildValue("fffffff", metrics[i][0], metrics[i][1],
                                           metrics[i][2], metrics[i][3], metrics[i][4], metrics[i][5],metrics[i][6]));
  }

  return resPy;
}

BOOST_PYTHON_MODULE(fast)
{
  using namespace boost::python;

  // Read methods
  boost::python::def("rmse", rgbe_rmse);
  boost::python::def("rmse_all", rgbe_rmse_all);
  boost::python::def("rmse_all_images", rgbe_rmse_all_images);
  boost::python::def("rmse_all_images_percentage", rgbe_rmse_all_images_percentage);
}
