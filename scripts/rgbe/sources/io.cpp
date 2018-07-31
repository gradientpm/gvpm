#include <Python.h>
#include <stdio.h>
#include <math.h>
#include <math.h>
#include <malloc.h>
#include <string.h>
#include <ctype.h>

#define VERBOSE_DEBUG 0

// Boost python
#include <boost/python.hpp>

// Readers format
#include "format/format.h"

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
// Helper methods
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

float* convertImage(int width, int height, PyObject *imagePy) {
  float* image = (float *) malloc(sizeof(float) * 3 *width*height);
  for (unsigned int i = 0; i < width*height; i++) {
    for (unsigned int j = 0; j < 3; j++) {
      // XXX Protect the reading
      image[i * 3 + j] = (float) PyFloat_AsDouble(
          PyTuple_GetItem(PyList_GetItem(imagePy, i), j));
    }
  }
  return image;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
// Write Techniques
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

/// write Radiance files
static PyObject *
rgbe_write_hdr(const std::string& path, int width, int height, PyObject *imagePy) {
  float* image = convertImage(width, height, imagePy);
  FormatRGBE f(width, height, image);
  f.write(path);

  return Py_BuildValue("b", 0);
}

/// write PFM files
static PyObject *
rgbe_write_pfm(const std::string& path, int width, int height, PyObject *imagePy) {
  float* image = convertImage(width, height, imagePy);
  FormatPFM f(width, height, image);
  f.write(path);

  return Py_BuildValue("b", 0);
}

/// write HDR files
// Automatically choose the format
static PyObject *
rgbe_write(const std::string& path, int width, int height, PyObject *imagePy) {
  // Read extension
  int ext = helper_get_ext(path.c_str());
  if (ext == EXT_UNKNOW) {
    printf("ERROR: Unkown extension, QUIT: %s\n", path.c_str());
    return Py_BuildValue("b", 1);
  }

  // Write the format by calling the dedicated function
  if (ext == EXT_RGBE) {
    return rgbe_write_hdr(path, width, height, imagePy);
  } else if (ext == EXT_PFM) {
    return rgbe_write_pfm(path, width, height, imagePy);
  } else {
    printf("ERROR: No writter, QUIT: %s\n", path.c_str());
    return Py_BuildValue("b", 1);
  }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
// Read Techniques
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

/// read HDR files
static PyObject *
rgbe_read_hdr(const std::string& path) {
  FormatRGBE f(path);
  return f.pack();
}

/// read HDR files
static PyObject *
rgbe_read_pfm(const std::string& path) {
  FormatPFM f(path);
  return f.pack();
}

/// read HDR files
static PyObject *
rgbe_read(const std::string& path) {
  int ext = helper_get_ext(path.c_str());
  if (ext == EXT_UNKNOW) {
    printf("ERROR: Unkown extension, QUIT: %s\n", path.c_str());
    return Py_BuildValue("(i,i)", 0, 0);
  }

  // === Read info
  if (ext == EXT_RGBE) {
    return rgbe_read_hdr(path);
  } else if (ext == EXT_PFM) {
    return rgbe_read_pfm(path);
  } else {
    printf("ERROR: No Reader, QUIT: %s\n", path.c_str());
    return Py_BuildValue("(i,i)", 0, 0);
  }
}

static PyObject *
rgbe_read_tonemap(const std::string& path, float gamma = 2.2f, float exposure = 0.0f) {
  Format* f = loadImage(path);
  // Header reading
  if (f == NULL) {
    return Py_BuildValue("(i,i)", 0, 0);
  }

  // List creation
  PyObject* pixels = PyList_New(f->getWidth() * f->getHeight());
  exposure = powf(2, exposure);
  float* image = f->getData();
  for (int i = 0; i < f->getWidth()*f->getHeight(); i++) {
    PyList_SetItem(pixels, i,
        Py_BuildValue("(i,i,i)",
            (int) (powf(image[i * 3] * exposure, 1.f / gamma) * 255),
            (int) (powf(image[i * 3 + 1] * exposure, 1.f / gamma) * 255),
            (int) (powf(image[i * 3 + 2] * exposure, 1.f / gamma) * 255)));
  }

  PyObject* resultsPy = Py_BuildValue("((i,i),O)", f->getWidth(), f->getHeight(), pixels);
  Py_DECREF(pixels);

  return resultsPy;
}

BOOST_PYTHON_MODULE(io)
{
  using namespace boost::python;

  // Read methods
  boost::python::def("read", rgbe_read);
  boost::python::def("read_pfm", rgbe_read_pfm);
  boost::python::def("read_hdr", rgbe_read_hdr);

  // Special read methods
  boost::python::def("read_tonemap", rgbe_read_tonemap);

  // Write methods
  boost::python::def("write", rgbe_write);
  boost::python::def("write_pfm", rgbe_write_pfm);
  boost::python::def("write_hdr", rgbe_write_hdr);
}

