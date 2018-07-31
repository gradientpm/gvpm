#pragma once

#include "format.h"

int PFM_ReadHeader(FILE *fp, int *width, int *height);
int PFM_ReadPixels(FILE *fp, float *data,  int scanline_width,
    int num_scanlines);
void PFM_FlipVertically(float *data, int width, int height);
int PFM_ReadHeader(FILE *fp, int *width, int *height);
int PFM_WritePixels(FILE *fp, float *data, int width,
       int height);
int PFM_WriteHeader(FILE *fp, int width, int height);

class FormatPFM : public Format {
public:
  FormatPFM(int w, int h, float* d):
    Format(w,h,d)
  {
  }
  FormatPFM(const std::string& path):
    Format(path)
  {
    read(path);
  }

  virtual void write(const std::string& path) {
    FILE* f = fopen(path.c_str(), "wb");
    PFM_WriteHeader(f, width, height);
    PFM_FlipVertically(data, width, height);
    PFM_WritePixels(f, data, width, height);
    PFM_FlipVertically(data, width, height); // Flip back
    fclose(f);
  }

  virtual void read(const std::string& path) {
    FILE* f = fopen(path.c_str(), "rb");
    if (f == NULL) {
      printf("ERROR: Unenable to open file: %s\n", path.c_str());
      return; // FIXME
    }

    if(!data) {
      free(data);
    }

    PFM_ReadHeader(f, &width, &height);
    data = (float *) malloc(sizeof(float) * 3 * width * height);
    PFM_ReadPixels(f, data, width, height);
    PFM_FlipVertically(data, width, height);

    fclose(f);
  }
};

int PFM_WriteHeader(FILE *fp, int width, int height) {
  /* Write the header */
  fprintf(fp, "PF\n"); // Make Error checking
  fprintf(fp, "%d %d\n", width, height);
  fprintf(fp, "-1\n"); // Assume LittleEndian
  return RGBE_RETURN_SUCCESS;
}

int PFM_WritePixels(FILE *fp, float *data, int width,
       int height) {
  int numpixels = width*height;
  float rgbe[3];

  while (numpixels-- > 0) {
    rgbe[0] = data[RGBE_DATA_RED];
    rgbe[1] = data[RGBE_DATA_GREEN];
    rgbe[2] = data[RGBE_DATA_BLUE];
    data += RGBE_DATA_SIZE;

    if (fwrite(rgbe, sizeof(rgbe), 1, fp) < 1)
      return rgbe_error(rgbe_write_error, NULL);
  }

  return RGBE_RETURN_SUCCESS;
}

int PFM_ReadHeader(FILE *fp, int *width, int *height) {
  char buf[128];
  if(fgets(buf, sizeof(buf) / sizeof(buf[0]), fp) == NULL)
    return rgbe_error(rgbe_read_error, NULL);
  if ((buf[0] != 'P') || (buf[1] != 'F')) {
    return rgbe_error(rgbe_read_error, NULL);
  }

  if (fgets(buf, sizeof(buf) / sizeof(buf[0]), fp) == 0)
    return rgbe_error(rgbe_read_error, NULL);
  if (sscanf(buf, "%d %d", width, height) < 2)
    return rgbe_error(rgbe_format_error, "missing image size specifier");

  if (fgets(buf, sizeof(buf) / sizeof(buf[0]), fp) == 0)
    return rgbe_error(rgbe_read_error, NULL);
  if ((buf[0] != '-') || (buf[1] != '1')) {
    return rgbe_error(rgbe_read_error, NULL);
  }
  return RGBE_RETURN_SUCCESS;
}

int PFM_ReadPixels(FILE *fp, float *data, int scanline_width,
    int num_scanlines) {

  int numpixels = scanline_width*num_scanlines;
  float rgbe[3];

  while (numpixels-- > 0) {
    if (fread(rgbe, sizeof(rgbe), 1, fp) < 1)
      return rgbe_error(rgbe_read_error, NULL);
    data[RGBE_DATA_RED] = rgbe[0];
    data[RGBE_DATA_GREEN] = rgbe[1];
    data[RGBE_DATA_BLUE] = rgbe[2];
    data += RGBE_DATA_SIZE;
  }

  return RGBE_RETURN_SUCCESS;
}

void PFM_FlipVertically(float *data, int width, int height) {
  int i;
  int j;
  int c;
  float tmp;

  for(j = 0; j < height/2; j++) {
    for(i = 0; i < width; i++) {
      for(c = 0; c < 3; c++) {
        tmp = data[(j*width+i)*3+c];
        data[(j*width+i)*3+c] = data[((height-(j+1))*width+i)*3+c];
        data[((height-(j+1))*width+i)*3+c] = tmp;
      }
    }
  }
}
