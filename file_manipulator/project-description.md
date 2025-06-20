# 📁 File Manipulator – High-Level Requirements

## Overview

The File Manipulator is a core backend service responsible for processing files (PDF, PNG, JPEG, SVG) based on commands received from the AI agent. It handles all low-level transformations, such as merging documents, converting formats, or deleting specific pages, and returns the resulting file to the user through the chat system.

---

## Objectives

- Receive structured commands with file(s) as input.
- Perform safe, reliable, and fast file manipulations.
- Return the modified file to the storage layer or calling component.
- Ensure temporary storage and secure cleanup.

---

## Functional Requirements

### ✅ Supported Operations

#### PDF
- Merge multiple PDFs (✅ Implemented for local files via CLI)
- Delete specific pages (✅ Implemented for local files via CLI)
- Extract specific pages
- Reorder pages
- Split PDFs

#### Images (PNG, JPEG)
- Convert formats (e.g., PNG to JPEG) (✅ Implemented for local files via CLI: PNG ↔ JPEG)
- Convert PDF to PNG (✅ Implemented for local files via CLI)
- Convert PNG to PDF (✅ Implemented for local files via CLI)
- Resize or compress images
- Crop
- Strip metadata

#### SVG
- Convert to PNG or JPEG
- Sanitize/clean metadata
- Optimize file size

---

## Inputs

- File(s): Local PDF files placed in a `files` directory, selected via a CLI.
- Instruction: User input via CLI prompts.
(Future: via cloud object storage (S3, GCS) and structured JSON or command object (e.g., `{ "action": "merge", "files": [URL1, URL2] }`))

---

## Outputs

- Modified file: Saved to a local `results` directory.
(Future: temporary signed URL or buffer)
- Metadata (format, size, duration)

---

## Constraints

- File size limits (e.g., max 20 MB per file)
- Request timeout (max 10–15 seconds per operation)
- Stateless design — no long-term file retention

---

## Security Requirements

- Files must be handled securely using signed URLs or direct encrypted storage access.
- All temporary files must be deleted immediately after use.
- Input validation required for file type and structure.

---

## Non-Functional Requirements

- High reliability and error tolerance (invalid file format, corrupt files).
- Modular, extensible code for new file types or transformations.
- Can run isolated for security (e.g., in a Docker sandbox).
