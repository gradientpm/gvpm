#pragma once

#include <Python.h>

#define EXT_UNKNOW  -1
#define EXT_RGBE  0
#define EXT_PFM   1

void upper_string(char *string) {
  while (*string) {
    if (*string >= 'a' && *string <= 'z') {
      *string = *string - 32;
    }
    string++;
  }
}

int helper_get_ext(const char* path) {
  char * pathTmp;
  char * posPoint;

  pathTmp = strdup(path);
  upper_string(pathTmp);
  posPoint = strrchr(pathTmp, '.');

  if (posPoint == NULL) {
    return EXT_UNKNOW;
  }

  if (strcmp(posPoint, ".PFM") == 0) {
    return EXT_PFM;
  } else if (strcmp(posPoint, ".HDR") == 0) {
    return EXT_RGBE;
  } else if (strcmp(posPoint, ".RGBE") == 0) {
    return EXT_RGBE;
  }

  free(pathTmp);

  return EXT_UNKNOW;
}

class Format {
protected:
  int width;
  int height;
  float* data;

public:
  Format(int w, int h, float* d):
    width(w), height(h), data(d)
  {
  }
  Format(const std::string& path):
    width(0), height(0), data(NULL)
  {
  }

  virtual ~Format() {
    if(data) {
      free(data);
    }
  }

  virtual void write(const std::string& path) = 0;
  virtual void read(const std::string& path) = 0;

  int getWidth() const {
    return width;
  }
  int getHeight() const {
    return height;
  }
  float* getData() const {
    return data;
  }

  // returns ((width, height), listImage)
  PyObject* pack() const {
    int totPixel;
    PyObject* pixels = PyList_New(width * height);

    for (int i = 0; i < width * height; i++) {
      PyList_SetItem(pixels, i,
          Py_BuildValue("(f,f,f)", data[i * 3], data[i * 3 + 1],
              data[i * 3 + 2]));
    }

    PyObject* resultsPy = Py_BuildValue("((i,i),O)", width, height, pixels);
    Py_DECREF(pixels); // For avoid memory leaks

    return resultsPy;
  }

  double* toDouble(float mult=1.f) const {
    double * v = new double[width*height*3];
    for(int i = 0; i < width*height*3; i++) {
      v[i] = data[i]*mult;
    }
    return v;
  }
};

#include "rgbe.h"
#include "pfm.h"

Format* loadImage(const std::string& path) {
  int ext = helper_get_ext(path.c_str());
  if (ext == EXT_UNKNOW) {
    printf("ERROR: Unkown extension, QUIT: %s\n", path.c_str());
    return NULL;
  }

  Format* f = NULL;
  // Header reading
  if (ext == EXT_RGBE) {
    f = new FormatRGBE(path);
  } else if (ext == EXT_PFM) {
    f = new FormatPFM(path);
  } else {
    printf("ERROR: No Reader, QUIT: %s\n", path.c_str());
  }
  return f;
}


