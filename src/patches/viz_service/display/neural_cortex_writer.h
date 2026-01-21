// Copyright 2026 The Neural-Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef COMPONENTS_VIZ_SERVICE_DISPLAY_NEURAL_CORTEX_WRITER_H_
#define COMPONENTS_VIZ_SERVICE_DISPLAY_NEURAL_CORTEX_WRITER_H_

#include <memory>
#include "base/memory/raw_ptr.h"
#include "build/build_config.h"
#include "third_party/skia/include/core/SkPixmap.h"

#if BUILDFLAG(IS_WIN)
#include <windows.h>
#endif

namespace viz {

struct VisualCortexHeader {
  uint32_t magic_number; // 0x4E455552 ('NEUR')
  uint32_t version;      // 1
  uint32_t width;
  uint32_t height;
  uint32_t format;       // 1 = RGBA
  uint32_t padding;      // Explicit padding
  uint64_t frame_index;
  int64_t timestamp_us;
  uint32_t row_bytes;
  uint8_t reserved[128];
};

class NeuralCortexWriter {
 public:
  NeuralCortexWriter();
  ~NeuralCortexWriter();

  void Init();
  void Write(const SkPixmap& pixmap);

 private:
#if BUILDFLAG(IS_WIN)
  HANDLE map_handle_ = nullptr;
  base::raw_ptr<void> map_view_ = nullptr;
#endif
};

}  // namespace viz

#endif  // COMPONENTS_VIZ_SERVICE_DISPLAY_NEURAL_CORTEX_WRITER_H_
