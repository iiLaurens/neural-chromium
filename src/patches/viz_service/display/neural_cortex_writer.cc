// Copyright 2026 The Neural-Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "components/viz/service/display/neural_cortex_writer.h"

#include <cstring>
#include "base/time/time.h"
#include "base/logging.h"

namespace viz {

namespace {
// Match Python: Local\NeuralChromium_VisualCortex_V3
#if BUILDFLAG(IS_WIN)
const wchar_t* kVisualCortexMapName = L"Local\\NeuralChromium_VisualCortex_V3";
const size_t kVisualCortexSize = 16 * 1024 * 1024; // 16MB (Increased for 4K)
#endif
}

NeuralCortexWriter::NeuralCortexWriter() = default;

NeuralCortexWriter::~NeuralCortexWriter() {
#if BUILDFLAG(IS_WIN)
  if (map_view_) UnmapViewOfFile(map_view_);
  if (map_handle_) CloseHandle(map_handle_);
#endif
}

void NeuralCortexWriter::Init() {
#if BUILDFLAG(IS_WIN)
  // Create File Mapping with NULL DACL for Low Integrity access (GPU/Renderer)
  // This allows the Python agent (Medium Integrity) to read High/AppContainer processes.
  SECURITY_DESCRIPTOR sd;
  InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
  SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
  SECURITY_ATTRIBUTES sa;
  sa.nLength = sizeof(sa);
  sa.lpSecurityDescriptor = &sd;
  sa.bInheritHandle = FALSE;

  map_handle_ = CreateFileMappingW(
      INVALID_HANDLE_VALUE, &sa, PAGE_READWRITE, 0, kVisualCortexSize, kVisualCortexMapName);
  
  if (map_handle_) {
    // If it already exists, GetLastError() returns ERROR_ALREADY_EXISTS.
    // That works fine, we just map it.
    LOG(ERROR) << "[VisualCortex] Created/Opened FileMapping. Handle=" << map_handle_ << " Error=" << ::GetLastError();
    map_view_ = MapViewOfFile(map_handle_, FILE_MAP_WRITE, 0, 0, kVisualCortexSize);
    if (map_view_) {
         VisualCortexHeader* header = static_cast<VisualCortexHeader*>(map_view_);
         if (header->magic_number != 0x4E455552) {
             memset(header, 0, sizeof(VisualCortexHeader));
             header->magic_number = 0x4E455552;
             header->version = 1;
             header->format = 1; // RGBA
             LOG(ERROR) << "[VisualCortex] Initialized New Header.";
         } else {
             LOG(ERROR) << "[VisualCortex] Linked to Existing Header. FrameIndex=" << header->frame_index;
         }
    } else {
         LOG(ERROR) << "[VisualCortex] Failed to MapViewOfFile: " << ::GetLastError();
    }
  } else {
      LOG(ERROR) << "[VisualCortex] Failed to CreateFileMapping: " << ::GetLastError();
  }
#endif
}

void NeuralCortexWriter::Write(const SkPixmap& pixmap) {
#if BUILDFLAG(IS_WIN)
  if (!map_view_) {
      Init(); // Try lazy init
      if (!map_view_) return;
  }
  
  VisualCortexHeader* header = static_cast<VisualCortexHeader*>(map_view_);
  int width = pixmap.width();
  int height = pixmap.height();
  
  size_t data_size = pixmap.computeByteSize();
  if (sizeof(VisualCortexHeader) + data_size > kVisualCortexSize) {
      // Too big
      LOG(ERROR) << "[VisualCortex] Frame Too Big! " << data_size;
      return;
  }
  
  // Copy pixels
  uint8_t* dst = static_cast<uint8_t*>(map_view_) + sizeof(VisualCortexHeader);
  const void* src = pixmap.addr();
  
  if (src && data_size > 0) {
       // Lock-free write. We rely on frame_index update at the end.
       // Readers might see tearing, but at 60fps it's negligible for AI.
       memcpy(dst, src, data_size);
       
       // Update Header
       header->width = width;
       header->height = height;
       header->row_bytes = pixmap.rowBytes();
       header->timestamp_us = base::Time::Now().ToDeltaSinceWindowsEpoch().InMicroseconds();
       
       // Atomically signal update
       InterlockedIncrement64((volatile LONG64*)&header->frame_index);

       if (header->frame_index % 60 == 0) {
           LOG(ERROR) << "[VisualCortex] Wrote Frame " << header->frame_index << " (" << width << "x" << height << ")";
       }
  } else {
      LOG(ERROR) << "[VisualCortex] Empty Pixmap Source!";
  }
#endif
}

}  // namespace viz
